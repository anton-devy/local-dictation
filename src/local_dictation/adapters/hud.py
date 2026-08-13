"""A brief, non-activating floating panel showing the transcribed text near the cursor.

Needs zero additional permissions -- it's a plain window-server window, not input
synthesis or the Accessibility API. Every mechanism for actually inserting text into
another app's field (synthesized Cmd+V, synthesized Unicode keystrokes, direct
Accessibility-API text insertion, even routing through AppleScript/System Events) shares
the same Accessibility permission gate -- there is no bypass. This HUD is the fallback
tier for when that gate isn't satisfied (or focus changed, or auto-paste is disabled):
instead of the transcription silently landing on the clipboard with only a menu-bar icon
flash as feedback, it's shown right where the user is looking, so a manual Cmd+V is a
near-zero-friction next step rather than a "did anything even happen?" guess.
"""

import threading

import AppKit
from PyObjCTools import AppHelper

WIDTH = 420
PADDING_X = 16
PADDING_Y = 12
FONT_SIZE = 14
DISPLAY_SECONDS = 2.5
CURSOR_GAP = 24
PREVIEW_LENGTH = 200


class Hud:
    """Call show(text) from the main thread. Safe to call repeatedly -- each call
    restarts the display timer and replaces the shown text."""

    def __init__(self):
        self._panel = None
        self._label = None
        self._hide_timer: threading.Timer | None = None

    def _ensure_panel(self) -> None:
        if self._panel is not None:
            return

        style = AppKit.NSWindowStyleMaskNonactivatingPanel | AppKit.NSWindowStyleMaskBorderless
        panel = AppKit.NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            AppKit.NSMakeRect(0, 0, WIDTH, 1),
            style,
            AppKit.NSBackingStoreBuffered,
            False,
        )
        panel.setLevel_(AppKit.NSFloatingWindowLevel)
        panel.setOpaque_(False)
        panel.setBackgroundColor_(AppKit.NSColor.clearColor())
        panel.setIgnoresMouseEvents_(True)  # never steals clicks/focus
        panel.setHasShadow_(True)
        panel.setHidesOnDeactivate_(False)
        panel.setCollectionBehavior_(AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces)

        label = AppKit.NSTextField.alloc().initWithFrame_(AppKit.NSMakeRect(0, 0, WIDTH, 1))
        label.setEditable_(False)
        label.setSelectable_(False)
        label.setBezeled_(False)
        label.setDrawsBackground_(True)
        label.setBackgroundColor_(AppKit.NSColor.colorWithWhite_alpha_(0.10, 0.94))
        label.setTextColor_(AppKit.NSColor.whiteColor())
        label.setFont_(AppKit.NSFont.systemFontOfSize_(FONT_SIZE))
        label.cell().setWraps_(True)
        panel.setContentView_(label)

        self._panel = panel
        self._label = label

    def show(self, text: str) -> None:
        """Show `text` near the current cursor position for a couple of seconds."""
        self._ensure_panel()
        self._cancel_hide()

        preview = text if len(text) <= PREVIEW_LENGTH else text[:PREVIEW_LENGTH] + "…"
        text_width = WIDTH - PADDING_X * 2
        self._label.setFrame_(AppKit.NSMakeRect(0, 0, text_width, 1000))
        self._label.setStringValue_(preview)
        self._label.cell().setWraps_(True)
        fitted_height = self._label.cell().cellSizeForBounds_(
            AppKit.NSMakeRect(0, 0, text_width, 1000)
        ).height

        panel_height = fitted_height + PADDING_Y * 2
        self._label.setFrame_(AppKit.NSMakeRect(PADDING_X, PADDING_Y, text_width, fitted_height))

        mouse = AppKit.NSEvent.mouseLocation()
        x = mouse.x - WIDTH / 2
        y = mouse.y - panel_height - CURSOR_GAP

        screen = AppKit.NSScreen.mainScreen().frame()
        x = max(screen.origin.x + 8, min(x, screen.origin.x + screen.size.width - WIDTH - 8))
        y = max(screen.origin.y + 8, y)

        self._panel.setFrame_display_(AppKit.NSMakeRect(x, y, WIDTH, panel_height), True)
        self._panel.orderFrontRegardless()

        self._hide_timer = threading.Timer(DISPLAY_SECONDS, self._hide_from_timer)
        self._hide_timer.daemon = True
        self._hide_timer.start()

    def _hide_from_timer(self) -> None:
        # threading.Timer fires on its own thread; marshal the actual AppKit call back
        # to the main thread.
        AppHelper.callAfter(self._hide)

    def _hide(self) -> None:
        if self._panel is not None:
            self._panel.orderOut_(None)

    def _cancel_hide(self) -> None:
        if self._hide_timer is not None:
            self._hide_timer.cancel()
            self._hide_timer = None

    def cancel_timer(self) -> None:
        """Public method to cancel any pending auto-hide timer. Idempotent and safe to call
        even if no timer is active."""
        self._cancel_hide()
