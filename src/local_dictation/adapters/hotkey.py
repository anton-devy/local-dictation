"""Toggle-driven dictation controller: the configured trigger (see trigger.py) starts
recording, the next trigger stops it and hands the clip off for transcription.

This module only owns the recording toggle lifecycle. Transcription runs in worker.py's
serialized background queue -- DictationController just calls on_clip_ready(audio) with
the finished clip and doesn't know or care how it gets transcribed.

Requires macOS Input Monitoring and Accessibility permission for the trigger's event tap
(see trigger.py), and Microphone permission for audio capture. See README.md for setup.
"""

from .recorder import Recorder


class DictationController:
    """Owns the toggle -> record -> hand-off flow, with optional UI hooks."""

    def __init__(self, on_recording_start=None, on_recording_stop=None, on_clip_ready=None):
        self.recorder = Recorder()
        self._recording = False
        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        self.on_clip_ready = on_clip_ready

    @property
    def recording(self) -> bool:
        return self._recording

    def toggle(self) -> None:
        """Called once per trigger activation: starts recording, or stops it if already
        recording."""
        if self._recording:
            self._stop()
        else:
            self._start()

    def _start(self) -> None:
        self._recording = True
        self.recorder.start(on_max_duration_reached=self._stop)
        if self.on_recording_start:
            self.on_recording_start()

    def _stop(self) -> None:
        if not self._recording:
            return
        self._recording = False
        audio = self.recorder.stop()
        if self.on_recording_stop:
            self.on_recording_stop()
        if self.on_clip_ready:
            self.on_clip_ready(audio)


def main() -> None:
    """Standalone smoke test: the configured trigger toggles recording; transcription runs
    on this (main) thread via a simple polling loop, matching app.py's rumps.Timer
    approach."""
    import time

    import config
    import paste as paste_module
    from trigger import create_trigger
    from worker import TranscriptionWorker

    def on_result(lang, text, paste_status):
        print(f"[{lang}] {text}\n(paste: {paste_status})")

    print("Loading model...")
    worker = TranscriptionWorker(
        on_transcribing=lambda: print("transcribing..."),
        on_result=on_result,
        on_rejected=lambda: print("(no speech detected, nothing pasted)"),
    )
    worker.warm_up()

    print(f"Trigger: {config.TRIGGER}. Activate it to start recording, again to stop. Ctrl+C to quit.")
    controller = DictationController(
        on_recording_start=lambda: print("recording started..."),
        on_recording_stop=lambda: print("recording stopped."),
        on_clip_ready=lambda audio: worker.submit(audio, paste_module.frontmost_app_identifier()),
    )
    trigger = create_trigger(on_toggle=controller.toggle)
    trigger.start()
    try:
        while True:
            worker.process_pending()
            time.sleep(0.05)
    except KeyboardInterrupt:
        trigger.stop()


if __name__ == "__main__":
    main()
