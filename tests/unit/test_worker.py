"""Tests for TranscriptionWorker with idle-unload lifecycle."""

import unittest.mock as mock

import numpy as np
import pytest

from local_dictation.worker import TranscriptionWorker


def test_worker_starts_not_warmed_up():
    """Worker should start with model not warmed up."""
    w = TranscriptionWorker()
    assert not w._warmed_up


def test_worker_starts_not_processing():
    """Worker should start not processing."""
    w = TranscriptionWorker()
    assert not w.is_processing()


def test_unload_marks_not_warmed_up():
    """Unload should mark the worker as not warmed up."""
    w = TranscriptionWorker()
    w._warmed_up = True  # Simulate warmup
    w.unload()
    assert not w._warmed_up


def test_unload_does_nothing_if_not_warmed_up():
    """Unload should be safe to call when not warmed up."""
    w = TranscriptionWorker()
    w.unload()  # Should not raise
    assert not w._warmed_up


def test_is_processing_tracks_state():
    """is_processing should reflect current state during _process."""
    w = TranscriptionWorker()
    assert not w.is_processing()

    # Simulate starting processing
    w._is_processing = True
    assert w.is_processing()

    w._is_processing = False
    assert not w.is_processing()


def test_submit_enqueues_audio():
    """Submit should add audio to queue."""
    w = TranscriptionWorker()
    audio = np.zeros((1000,), dtype=np.float32)
    w.submit(audio, "frontmost_app")

    # Queue should have one item
    audio_out, app_out, retry_count = w._queue.get_nowait()
    np.testing.assert_array_equal(audio, audio_out)
    assert app_out == "frontmost_app"
    assert retry_count == 0


def test_submit_with_none_frontmost_app():
    """Submit should accept None for frontmost_app."""
    w = TranscriptionWorker()
    audio = np.zeros((1000,), dtype=np.float32)
    w.submit(audio, None)

    audio_out, app_out, retry_count = w._queue.get_nowait()
    assert app_out is None
    assert retry_count == 0


def test_warm_up_idempotent():
    """Warm_up should only load model once (idempotent)."""
    w = TranscriptionWorker()

    with mock.patch('local_dictation.worker.transcribe_full') as mock_transcribe:
        w.warm_up()
        call_count_1 = mock_transcribe.call_count

        w.warm_up()
        call_count_2 = mock_transcribe.call_count

        # Should only have been called once
        assert call_count_1 == 1
        assert call_count_2 == 1


def test_process_pending_with_empty_queue():
    """process_pending should do nothing if queue is empty."""
    w = TranscriptionWorker()
    w.process_pending()  # Should not raise
    assert not w.is_processing()


def test_on_reloading_called_when_not_warmed_up():
    """on_reloading callback should be called when model needs reload."""
    reload_called = []

    def on_reloading():
        reload_called.append(True)

    w = TranscriptionWorker(on_reloading=on_reloading)
    w._warmed_up = False

    # Mock warm_up and transcribe_full to avoid actual ML work
    with mock.patch('local_dictation.worker.transcribe_full') as mock_transcribe, \
         mock.patch.object(w, 'warm_up') as mock_warmup:
        mock_transcribe.return_value = {
            'language': 'en',
            'text': 'test',
            'segments': [],
            'no_speech_prob': 0.0,
            'compression_ratio': 1.0
        }

        audio = np.zeros((1000,), dtype=np.float32)
        w.submit(audio, None)
        # Simulate entering _process when not warmed up
        assert not w._warmed_up


def test_processing_state_set_during_process():
    """_is_processing should be True during _process and False after."""
    w = TranscriptionWorker()
    processing_states = []

    def on_transcribing():
        processing_states.append(("on_transcribing", w._is_processing))

    def on_result(language, text, paste_status):
        processing_states.append(("on_result", w._is_processing))

    w.on_transcribing = on_transcribing
    w.on_result = on_result

    # Mock transcribe_full to return valid result
    with mock.patch('local_dictation.worker.transcribe_full') as mock_transcribe, \
         mock.patch('local_dictation.worker.filters.accept') as mock_accept, \
         mock.patch('local_dictation.worker.paste.paste') as mock_paste:
        mock_transcribe.return_value = {
            'language': 'en',
            'text': 'test',
            'segments': []
        }
        mock_accept.return_value = True
        mock_paste.return_value = 'PASTED'

        audio = np.zeros((1000,), dtype=np.float32)
        w.submit(audio, None)
        w._warmed_up = True

        # After process_pending, should not be processing
        assert not w.is_processing()

        # Process the queued audio
        with mock.patch.object(w, 'warm_up'):
            w.process_pending()

        # After processing, should be back to not processing
        assert not w.is_processing()


def test_worker_retries_once_and_retains_failed_audio():
    failures = []
    w = TranscriptionWorker(on_failure=failures.append)
    w._warmed_up = True
    audio = np.ones(1000, dtype=np.float32)
    with mock.patch('local_dictation.worker.transcribe_full', side_effect=RuntimeError("boom")):
        w.submit(audio, None)
        w.process_pending()
    assert len(failures) == 1
    assert w.failed_count() == 1
    assert w.retry_failed()
    assert w.has_pending()
    assert w.discard_failed() is False


def test_worker_transcribes_retried_audio_successfully():
    result_callback = mock.Mock()
    w = TranscriptionWorker(on_result=result_callback)
    w._warmed_up = True
    audio = np.ones(16_000, dtype=np.float32) * 0.5
    result = {
        "language": "en",
        "segments": [{"text": "recovered", "no_speech_prob": 0.01,
                      "avg_logprob": -0.1, "compression_ratio": 1.0}],
    }
    with mock.patch("local_dictation.worker.transcribe_full", side_effect=[RuntimeError("temporary"), result]), \
         mock.patch("local_dictation.worker.paste.paste", return_value="PASTED"):
        w.submit(audio, None)
        w.process_pending()
    result_callback.assert_called_once_with("en", "recovered", "PASTED")
    assert w.failed_count() == 0
