"""Shared pytest fixtures for local-dictation tests."""

import unittest.mock as mock

import pytest


@pytest.fixture
def fake_clipboard():
    """Mock clipboard that captures copy operations without touching the real clipboard."""
    with mock.patch("pyperclip.copy") as mock_copy:
        yield mock_copy


@pytest.fixture
def mock_rumps_app():
    """Provide a mock rumps.App for testing without launching the full GUI."""
    with mock.patch("rumps.App") as MockApp:
        app = MockApp.return_value
        app.menu = []
        app.title = ""
        app.icon = ""
        yield app


@pytest.fixture
def mock_recorder():
    """Mock audio recorder to avoid actual microphone access in tests."""
    with mock.patch("local_dictation.adapters.recorder.Recorder") as MockRecorder:
        recorder = MockRecorder.return_value
        recorder.start = mock.Mock()
        recorder.stop = mock.Mock(return_value=b"fake audio data")
        yield recorder


@pytest.fixture
def mock_config():
    """Mock config module for testing with known values."""
    with mock.patch("local_dictation.config") as mock_cfg:
        mock_cfg.IDLE_TIMEOUT_MINUTES = 10
        mock_cfg.AUTO_PASTE = True
        mock_cfg.TRIGGER = "combo"
        mock_cfg.TRIGGER_KEY = "d"
        mock_cfg.TRIGGER_MODIFIERS = {"control", "shift"}
        mock_cfg.MODEL = "mlx-community/whisper-large-v3-turbo"
        yield mock_cfg
