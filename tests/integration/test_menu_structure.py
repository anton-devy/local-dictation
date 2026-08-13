"""Test to verify menu structure matches rumps' registration order."""

import unittest
from unittest.mock import MagicMock, patch

from local_dictation import config  # noqa: F401 (triggers tqdm lock setup)
import rumps


class TestMenuStructure(unittest.TestCase):
    """Verify the menu has exactly one Quit option after rumps registration."""

    @patch("local_dictation.app.TranscriptionWorker")
    @patch("local_dictation.app.create_trigger")
    @patch("local_dictation.app.DictationController")
    def test_quit_menu_item_unique_after_registration(
        self, mock_controller_class, mock_trigger_class, mock_worker_class
    ):
        """Verify there is exactly one 'Quit' menu item after rumps registration.

        This test replicates the order of operations in App.run():
        1. First, @rumps.clicked registrations run (which can create menu items)
        2. Then, the quit_button parameter item is added (if quit_button is not None)

        The bug would be two "Quit" items if quit_button="Quit" while @rumps.clicked("Quit")
        is also present. This test catches that by simulating the registration order.
        """
        mock_trigger = MagicMock()
        mock_trigger_class.return_value = mock_trigger
        mock_worker = MagicMock()
        mock_worker_class.return_value = mock_worker
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller

        from local_dictation.app import DictationApp

        app = DictationApp()

        # Replicate App.run()'s registration order without entering the event loop
        # Step 1: Run all @rumps.clicked registrations (like App.run() does at line 1197)
        for registration_func in rumps.clicked.__dict__.get("*buttons", []):
            registration_func(app)  # This simulates what App.run() does

        # Step 2: If quit_button is set, add it to the menu (like initializeStatusBar does)
        if app.quit_button is not None:
            app._menu.add(app.quit_button)

        # Now count "Quit" items in the menu structure
        # The menu is a dict-like object where items are stored by title
        quit_items = [item for item in app._menu.values() if getattr(item, "title", None) == "Quit"]

        self.assertEqual(
            len(quit_items),
            1,
            f"Expected exactly one 'Quit' menu item after registration, but found {len(quit_items)}. "
            f"This suggests a conflict between quit_button parameter and @rumps.clicked('Quit').",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
