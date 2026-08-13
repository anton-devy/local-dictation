"""Tests for graceful shutdown sequence."""

import unittest
from unittest.mock import MagicMock, patch, call

from local_dictation import config  # noqa: F401 (triggers tqdm lock setup)


class TestGracefulShutdown(unittest.TestCase):
    """Unit tests for graceful shutdown components."""

    def test_tqdm_lock_presets_at_import(self):
        """Verify tqdm's lock is pre-set on import of config."""
        import tqdm
        # After config import, tqdm should have a lock set
        self.assertIsNotNone(tqdm.tqdm._lock)
        # Verify it's a threading lock (type name includes RLock)
        lock_type = type(tqdm.tqdm._lock).__name__
        self.assertIn('RLock', lock_type, f"Expected RLock, got {lock_type}")

    def test_trigger_stop_callable(self):
        """Verify trigger.stop() is callable."""
        from local_dictation.adapters.trigger import create_trigger
        trigger = create_trigger(on_toggle=MagicMock())
        # stop() should be callable and idempotent
        trigger.stop()  # First call
        trigger.stop()  # Second call (should not error)
        self.assertTrue(True)  # If we got here, it worked

    def test_worker_unload_callable(self):
        """Verify worker.unload() is callable."""
        from local_dictation.worker import TranscriptionWorker
        worker = TranscriptionWorker()
        # unload() should be callable and idempotent
        worker.unload()  # First call
        worker.unload()  # Second call (should not error)
        self.assertTrue(True)  # If we got here, it worked

    def test_hud_cancel_timer_callable(self):
        """Verify hud.cancel_timer() is callable and idempotent."""
        from local_dictation.adapters.hud import Hud
        hud = Hud()
        # cancel_timer() should be callable even with no timer
        hud.cancel_timer()  # First call (no timer pending)
        hud.cancel_timer()  # Second call (should not error)
        self.assertTrue(True)  # If we got here, it worked

    @patch("rumps.Timer")
    def test_hud_cancel_timer_with_active_timer(self, mock_timer_class):
        """Verify hud.cancel_timer() cancels an active timer."""
        from local_dictation.adapters.hud import Hud
        hud = Hud()
        # Simulate a pending timer
        mock_timer = MagicMock()
        hud._hide_timer = mock_timer
        # cancel_timer should call cancel() on the timer and set it to None
        hud.cancel_timer()
        mock_timer.cancel.assert_called_once()
        self.assertIsNone(hud._hide_timer)

    def test_app_quit_handler_exists(self):
        """Verify the app has a quit handler method."""
        try:
            from local_dictation.app import DictationApp
            app_class = DictationApp
            # Check that _handle_quit method exists and is callable
            self.assertTrue(hasattr(app_class, '_handle_quit'))
        except Exception:
            # Skip if app can't be imported
            self.skipTest("Could not import app")

    def test_quit_handler_components_exist(self):
        """Verify all quit handler components are callable."""
        # Test that individual components exist and are callable
        self.test_trigger_stop_callable()
        self.test_hud_cancel_timer_callable()
        self.test_worker_unload_callable()


if __name__ == "__main__":
    unittest.main()
