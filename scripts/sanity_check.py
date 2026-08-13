"""One-off gate: confirm mlx-whisper can transcribe English and German locally
with correct auto-detected language, before any recording/hotkey/UI code is built.

Usage: python sanity_check.py
"""

from pathlib import Path

import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"
FIXTURES = Path(__file__).parent / "fixtures"

SAMPLES = [
    ("english_sample.wav", "en"),
    ("german_sample.wav", "de"),
]


def main() -> None:
    for filename, expected_lang in SAMPLES:
        path = FIXTURES / filename
        print(f"\n--- {filename} (expecting language={expected_lang}) ---")
        result = mlx_whisper.transcribe(str(path), path_or_hf_repo=MODEL, language=None)
        detected = result["language"]
        text = result["text"].strip()
        status = "OK" if detected == expected_lang else "MISMATCH"
        print(f"detected language: {detected} [{status}]")
        print(f"text: {text}")


if __name__ == "__main__":
    main()
