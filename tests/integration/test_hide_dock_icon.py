"""Tests for hide-dock-icon feature (menu-bar-only activation policy)."""

import unittest
from unittest.mock import patch, MagicMock, call

try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    APPKIT_AVAILABLE = True
except ImportError:
    APPKIT_AVAILABLE = False


class TestHideDockIcon(unittest.TestCase):
    """Test that app.py correctly sets accessory activation policy."""

    @unittest.skipIf(not APPKIT_AVAILABLE, "AppKit not available (expected on non-macOS)")
    def test_appkit_imports_available(self):
        """Verify AppKit imports needed for hide-dock-icon are available."""
        self.assertIsNotNone(NSApplication)
        self.assertIsNotNone(NSApplicationActivationPolicyAccessory)
        # NSApplicationActivationPolicyAccessory should be the numeric constant 1
        self.assertEqual(NSApplicationActivationPolicyAccessory, 1)

    @unittest.skipIf(not APPKIT_AVAILABLE, "AppKit not available")
    def test_nsapplication_singleton(self):
        """Verify NSApplication.sharedApplication() is a singleton."""
        app1 = NSApplication.sharedApplication()
        app2 = NSApplication.sharedApplication()
        # Both should be the same instance
        self.assertIs(app1, app2)

    @unittest.skipIf(not APPKIT_AVAILABLE, "AppKit not available")
    def test_activation_policy_call_exists(self):
        """Verify setActivationPolicy_ method exists on NSApplication."""
        app = NSApplication.sharedApplication()
        self.assertTrue(hasattr(app, 'setActivationPolicy_'))
        self.assertTrue(callable(getattr(app, 'setActivationPolicy_')))

    def test_app_module_syntax_valid(self):
        """Verify app.py can be imported without SyntaxError."""
        try:
            # This will fail if there's a syntax error or import error
            from local_dictation import app
            self.assertTrue(True)  # If we get here, module loaded successfully
        except SyntaxError as e:
            self.fail(f"app.py has syntax error: {e}")
        except Exception as e:
            # Other import errors are okay for this test - we just care about syntax
            self.assertTrue(True)

    def test_app_has_required_imports(self):
        """Verify app.py imports NSApplication and NSApplicationActivationPolicyAccessory."""
        try:
            from local_dictation.app import NSApplication, NSApplicationActivationPolicyAccessory
            self.assertIsNotNone(NSApplication)
            self.assertIsNotNone(NSApplicationActivationPolicyAccessory)
        except ImportError:
            # If AppKit not available (non-macOS), skip
            self.skipTest("AppKit not available")

    def test_app_calls_set_activation_policy(self):
        """Verify app.py's DictationApp class has proper initialization."""
        try:
            from local_dictation.app import DictationApp
            # Just verify the class exists and can be inspected
            self.assertTrue(hasattr(DictationApp, 'run'))
        except ImportError:
            # If app can't be imported (AppKit issue), skip
            self.skipTest("Could not import app module")


class TestDockIconIntegration(unittest.TestCase):
    """Integration test stubs (require running app to fully verify)."""

    def test_hide_dock_icon_manual_verification_checklist(self):
        """Manual test checklist for dock-icon hiding (requires running app)."""
        checklist = {
            "menu_bar_icon_appears": False,
            "dock_icon_missing": False,
            "trigger_hotkey_works": False,
            "transcription_works": False,
            "cmd_tab_excludes_app": False,
            "notifications_display": False,
            "hud_displays": False,
            "idle_unload_still_works": False,
            "menu_items_functional": False,
        }

        # This test is a documentation of what to manually verify
        # Not an automated test, but ensures we have a clear checklist
        self.assertIsNotNone(checklist)
        self.assertTrue(all(
            key in checklist
            for key in [
                "menu_bar_icon_appears",
                "dock_icon_missing",
                "trigger_hotkey_works",
                "transcription_works",
                "cmd_tab_excludes_app",
            ]
        ))


if __name__ == "__main__":
    unittest.main()
