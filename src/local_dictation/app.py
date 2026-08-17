"""Menu-bar app: the configured trigger (see trigger.py; default Control+Option+Cmd+D)
toggles recording; on stop, the clip is transcribed locally and auto-pasted into the
frontmost app via AppleScript/System Events (clipboard as fallback, and always left there
afterward -- see paste.py). A brief icon flash signals a successful dictation. A floating
HUD (hud.py) shows the transcribed text near the cursor whenever the paste didn't land, so
there's always an immediate, visible way to grab the text -- no permission dependency.
System notifications are reserved for the cases that are actually actionable (focus
changed before paste, or a paste permission problem). A "Copy Last Dictation" menu item
recovers the most recent transcription regardless of clipboard state.

Usage: local-dictation (via console script) or python -m local_dictation.app
"""

import logging
import os
import sys
import time

import pyperclip
import rumps
try:
    import setproctitle
except ImportError:  # Lets source checkouts display a useful warning before dependencies install.
    setproctitle = None
from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
from PyObjCTools import AppHelper

from local_dictation import config
from local_dictation.adapters import paste
from local_dictation.adapters.hotkey import DictationController
from local_dictation.adapters.hud import Hud
from local_dictation.adapters.trigger import create_trigger
from local_dictation.worker import TranscriptionWorker

log = logging.getLogger(__name__)

IDLE_ICON = "\U0001F3A4"  # microphone
RECORDING_ICON = "\U0001F534"  # red circle
DONE_ICON = "✅"  # check mark, brief flash on successful dictation
NO_SPEECH_ICON = "\U0001F507"  # muted speaker, brief flash when nothing was transcribed
TRANSCRIBING_ICON = "\u23f3"
FAILURE_ICON = "\u26a0\ufe0f"

PREVIEW_LENGTH = 60
POLL_INTERVAL_SECONDS = 0.1
STATUS_CHECK_INTERVAL_SECONDS = 2.0
FLASH_DURATION_SECONDS = 1.0

# paste_status values that mean the text did NOT land automatically -- the HUD (and, for
# the two actionable ones, a notification) shows so the user always has an immediate,
# visible way to grab it.
_NOT_PASTED = (
    paste.SKIPPED_FOCUS_CHANGED,
    paste.PASTE_FAILED_PERMISSION,
    paste.PASTE_FAILED_OTHER,
)


class DictationApp(rumps.App):
    def __init__(self):
        super().__init__(name="local-dictation", title=IDLE_ICON, quit_button=None)

        self.last_transcription: str | None = None
        self.last_paste_status: str | None = None
        self._flash_timer: rumps.Timer | None = None
        self._idle_timer: rumps.Timer | None = None
        self._last_activity_time: float = 0  # timestamp of last transcription submit
        self.hud = Hud()

        self.status_item = rumps.MenuItem("Status: starting…")
        self.copy_last_item = rumps.MenuItem("Copy Last Dictation", callback=self._copy_last_dictation)
        self.retry_failed_item = rumps.MenuItem("Retry Failed Dictation", callback=self._retry_failed)
        self.discard_failed_item = rumps.MenuItem("Discard Failed Dictation", callback=self._discard_failed)
        self.menu = [self.status_item, self.copy_last_item, self.retry_failed_item,
                     self.discard_failed_item, rumps.MenuItem("Quit")]

        self.worker = TranscriptionWorker(
            on_result=self._on_result,
            on_rejected=self._on_rejected,
            on_reloading=self._on_reloading,
            on_transcribing=self._on_transcribing,
            on_failure=self._on_failure,
        )

        # DictationController's start/stop callbacks fire on the trigger's own thread (see
        # trigger.py), so they must be marshaled to the main thread via AppHelper.callAfter.
        # _on_result/_on_rejected, by contrast, are called from worker.process_pending(),
        # which _poll_worker below already drives on the main thread -- no marshaling
        # needed there.
        self.controller = DictationController(
            on_recording_start=lambda: AppHelper.callAfter(self._on_recording_start),
            on_recording_stop=lambda: AppHelper.callAfter(self._on_recording_stop),
            on_clip_ready=self._on_clip_ready,
        )
        self.trigger = create_trigger(on_toggle=self.controller.toggle)

    def _on_clip_ready(self, audio) -> None:
        # Runs on the trigger's thread, right when recording stops -- capture the
        # frontmost app now, since that's the moment the focus-changed paste guard cares
        # about.
        frontmost = paste.frontmost_app_identifier()
        self.worker.submit(audio, frontmost)
        self._reset_idle_timer()
        AppHelper.callAfter(self._show_steady_state)

    def _on_recording_start(self) -> None:
        self._cancel_flash()
        self.title = RECORDING_ICON

    def _on_recording_stop(self) -> None:
        self._show_steady_state()

    def _on_transcribing(self) -> None:
        self._show_steady_state()

    def _show_steady_state(self) -> None:
        if self.controller.recording:
            self.title = RECORDING_ICON
        elif self.worker.has_pending():
            self.title = TRANSCRIBING_ICON
        elif self.worker.failed_count():
            self.title = FAILURE_ICON
        else:
            self.title = IDLE_ICON

    def _flash(self, glyph: str) -> None:
        """Briefly show `glyph` in the menu bar, then revert to idle (unless a new
        recording has started in the meantime, in which case leave it alone)."""
        self._cancel_flash()
        self.title = glyph
        self._flash_timer = rumps.Timer(self._end_flash, FLASH_DURATION_SECONDS)
        self._flash_timer.start()

    def _end_flash(self, timer) -> None:
        timer.stop()
        self._flash_timer = None
        self._show_steady_state()

    def _cancel_flash(self) -> None:
        if self._flash_timer is not None:
            self._flash_timer.stop()
            self._flash_timer = None

    def _reset_idle_timer(self) -> None:
        """Reset the idle timeout whenever a transcription is submitted."""
        self._last_activity_time = time.time()
        if self._idle_timer is None and config.IDLE_TIMEOUT_MINUTES > 0:
            # Start the idle timer (check every 10 seconds if we've hit the timeout)
            self._idle_timer = rumps.Timer(self._check_idle_timeout, 10.0)
            self._idle_timer.start()

    def _check_idle_timeout(self, _timer) -> None:
        """Check if idle timeout has elapsed and unload the model if so."""
        if config.IDLE_TIMEOUT_MINUTES == 0:
            # Idle-unload is disabled
            return

        if self.controller.recording or self.worker.has_pending():
            # Don't unload while transcription is in progress
            return

        elapsed_minutes = (time.time() - self._last_activity_time) / 60.0
        if elapsed_minutes >= config.IDLE_TIMEOUT_MINUTES:
            # Timeout has elapsed; unload the model
            log.info("Idle timeout reached (%.1f minutes), unloading model", elapsed_minutes)
            self.worker.unload()

    def _on_result(self, language: str, text: str, paste_status: str) -> None:
        self.last_transcription = text
        self.last_paste_status = paste_status
        self._reset_idle_timer()

        if paste_status not in _NOT_PASTED:
            # PASTED or SKIPPED_DISABLED: common/expected case, no notification, just a
            # brief confirmation flash.
            self._flash(DONE_ICON)
            return

        # Anything that didn't land automatically: always show the HUD right where the
        # user is looking, so grabbing the text is a near-zero-friction Cmd+V regardless
        # of why auto-paste didn't happen.
        self.hud.show(text)

        if paste_status == paste.SKIPPED_FOCUS_CHANGED:
            rumps.notification(
                title="local-dictation",
                subtitle="Focus changed — not pasted",
                message="Your dictation is on the clipboard; paste it manually.",
            )
        elif paste_status == paste.PASTE_FAILED_PERMISSION:
            rumps.notification(
                title="local-dictation",
                subtitle="Paste permission needed",
                message="Allow local-dictation to control System Events "
                "(System Settings → Privacy & Security → Automation). "
                "Your dictation is on the clipboard for now.",
            )
        elif paste_status == paste.PASTE_FAILED_OTHER:
            rumps.notification(
                title="local-dictation",
                subtitle="Paste failed",
                message="Your dictation is on the clipboard; paste it manually.",
            )

    def _on_rejected(self) -> None:
        # Frequent (accidental/short toggles), not actionable beyond "try again" -- a
        # flash is enough, a notification would be disproportionate.
        self._flash(NO_SPEECH_ICON)
        self._reset_idle_timer()

    def _on_failure(self, error: str) -> None:
        self._show_steady_state()
        rumps.notification(title="local-dictation", subtitle="Transcription failed",
                           message="Retry or discard the retained recording from the menu.")

    def _retry_failed(self, _sender) -> None:
        if self.worker.retry_failed():
            self._show_steady_state()

    def _discard_failed(self, _sender) -> None:
        if self.worker.discard_failed():
            self._show_steady_state()

    def _on_reloading(self) -> None:
        # Model was unloaded due to idle timeout and is now being reloaded.
        # Show a brief UI cue so the user understands the brief delay.
        self.hud.show("Reloading model…")

    def _copy_last_dictation(self, _sender) -> None:
        if self.last_transcription is not None:
            pyperclip.copy(self.last_transcription)
            rumps.notification(title="local-dictation", subtitle="Copied last dictation", message="")
        else:
            rumps.notification(title="local-dictation", subtitle="No dictation yet", message="")

    @rumps.clicked("Quit")
    def _handle_quit(self, _sender) -> None:
        # Graceful shutdown sequence: stop threads, cancel timers, unload resources.
        log.info("Quit initiated, running shutdown sequence")
        self.trigger.stop()
        if self._idle_timer is not None:
            self._idle_timer.stop()
            self._idle_timer = None
        self.hud.cancel_timer()
        self.worker.unload()
        rumps.quit_application()

    @rumps.timer(POLL_INTERVAL_SECONDS)
    def _poll_worker(self, _timer) -> None:
        # process_pending() must always run on this same thread (the main thread) --
        # see worker.py and design.md for why transcription can't run off-thread.
        self.worker.process_pending()

    @rumps.timer(STATUS_CHECK_INTERVAL_SECONDS)
    def _poll_status(self, _timer) -> None:
        # Input Monitoring backs the trigger's event tap and has a reliable live-trust
        # check (is_tap_enabled). Paste now goes through AppleScript/System Events, which
        # has no equivalent pre-flight "is this granted" API -- osascript's own
        # success/failure on the last real attempt is the only honest signal, so that's
        # what's shown instead of guessing ahead of time.
        if not self.trigger.is_tap_enabled():
            self.status_item.title = "Status: grant Input Monitoring (trigger off)"
        elif self.worker.failed_count():
            self.status_item.title = "Status: transcription failed — retry available"
        elif self.last_paste_status is None:
            self.status_item.title = "Status: ready"
        elif self.last_paste_status in _NOT_PASTED:
            self.status_item.title = f"Status: last paste — {self.last_paste_status}"
        else:
            self.status_item.title = "Status: OK"

    def run(self):
        # Diagnostic: which exact interpreter identity is running (TCC ties permission
        # grants to code identity, and that identity has already proven unstable once for
        # a bare venv Python interpreter -- see design.md's Round 4). accessibility_trusted
        # is logged for reference only; it's not used to gate anything.
        real_executable = os.path.realpath(sys.executable)
        log.info("startup: sys.executable=%r resolved=%r", sys.executable, real_executable)
        log.info("startup: accessibility_trusted()=%s", paste.accessibility_trusted())

        self.worker.warm_up()
        self.trigger.start()
        log.info("trigger armed (%s)", config.TRIGGER)

        # Hide from Dock, keep menu-bar only (accessory activation policy)
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        super().run()


def main() -> None:
    if setproctitle is not None:
        setproctitle.setproctitle("local-dictation")
    DictationApp().run()


if __name__ == "__main__":
    main()
