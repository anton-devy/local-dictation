"""Integration tests for local transcription against real audio fixtures.

These tests require the mlx-whisper model to be loaded, so they are marked
as slow integration tests. They verify that the local transcription pipeline
works correctly with known audio samples.

Usage: pytest tests/integration/test_transcription_fixtures.py -v
"""

import pytest
from pathlib import Path

try:
    import mlx_whisper
    MLXWHISPER_AVAILABLE = True
except ImportError:
    MLXWHISPER_AVAILABLE = False

from local_dictation import config

MODEL = config.MODEL
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"

# Audio fixtures with expected language
FIXTURES = [
    {
        "filename": "english_sample.wav",
        "expected_lang": "en",
        "description": "English audio sample",
    },
    {
        "filename": "german_sample.wav",
        "expected_lang": "de",
        "description": "German audio sample",
    },
]


def _fixture_path(filename: str) -> Path:
    """Resolve a fixture audio path, skipping the test if it hasn't been generated."""
    path = FIXTURES_DIR / filename
    if not path.exists():
        pytest.skip(f"{filename} missing — run fixtures/generate.sh")
    return path


@pytest.mark.integration
class TestTranscriptionFixtures:
    """Test transcription against real audio fixtures."""

    @pytest.mark.skipif(not MLXWHISPER_AVAILABLE, reason="mlx_whisper not installed")
    def test_fixtures_directory_exists(self):
        """Fixtures directory should exist."""
        assert FIXTURES_DIR.exists(), f"Fixtures directory not found: {FIXTURES_DIR}"

    @pytest.mark.skipif(not MLXWHISPER_AVAILABLE, reason="mlx_whisper not installed")
    def test_all_fixture_files_exist(self):
        """All expected fixture files should be present."""
        for fixture in FIXTURES:
            path = FIXTURES_DIR / fixture["filename"]
            assert path.exists(), f"Fixture file not found: {path}"

    @pytest.mark.skipif(not MLXWHISPER_AVAILABLE, reason="mlx_whisper not installed")
    @pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f["filename"])
    def test_transcribe_fixture_language_detection(self, fixture):
        """Test that language is correctly detected for each fixture.

        Verifies that mlx_whisper correctly auto-detects the language
        of each fixture audio file.
        """
        path = _fixture_path(fixture["filename"])

        # Transcribe the audio using mlx_whisper directly
        result = mlx_whisper.transcribe(
            str(path), path_or_hf_repo=MODEL, language=None, verbose=None
        )
        detected_lang = result["language"]

        # Verify language was correctly detected
        assert detected_lang == fixture["expected_lang"], (
            f"Expected language {fixture['expected_lang']}, "
            f"but got {detected_lang} for {fixture['filename']}"
        )

    @pytest.mark.skipif(not MLXWHISPER_AVAILABLE, reason="mlx_whisper not installed")
    @pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f["filename"])
    def test_transcribe_full_fixture(self, fixture):
        """Test full transcription result structure.

        Verifies that full transcription result contains all expected fields.
        """
        path = _fixture_path(fixture["filename"])

        # Transcribe the audio
        result = mlx_whisper.transcribe(
            str(path), path_or_hf_repo=MODEL, language=None, verbose=None
        )

        # Verify result has expected structure
        assert "text" in result, "Result missing 'text' field"
        assert "language" in result, "Result missing 'language' field"
        assert "segments" in result, "Result missing 'segments' field"

        # Verify text is non-empty
        assert result["text"].strip(), f"Empty text from {fixture['filename']}"

        # Verify language matches expectation
        assert result["language"] == fixture["expected_lang"], (
            f"Expected language {fixture['expected_lang']}, "
            f"but got {result['language']}"
        )

        # Verify segments structure
        segments = result["segments"]
        assert isinstance(segments, list), "Segments should be a list"
        if segments:
            # Each segment should have key fields
            for segment in segments:
                assert "id" in segment, "Segment missing 'id' field"
                assert "text" in segment, "Segment missing 'text' field"


@pytest.mark.integration
@pytest.mark.skipif(not MLXWHISPER_AVAILABLE, reason="mlx_whisper not installed")
def test_transcription_pipeline_smoke_test():
    """Smoke test: verify the transcription pipeline can load and run without crashing.

    This doesn't verify correctness, just that the system doesn't crash when
    processing a real audio fixture.
    """
    fixture = FIXTURES[0]
    path = _fixture_path(fixture["filename"])

    # Try to transcribe - just check it doesn't crash
    try:
        result = mlx_whisper.transcribe(
            str(path), path_or_hf_repo=MODEL, language=None, verbose=None
        )
        # Verify we got a result structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "text" in result, "Result missing text field"
        assert "language" in result, "Result missing language field"
    except Exception as e:
        pytest.fail(f"Transcription pipeline crashed: {e}")
