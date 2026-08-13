"""Console script entry point for dictate CLI.

This wraps the dictate functionality to be callable as a console script.
"""

import sys
import time

import pyperclip

from local_dictation.adapters.recorder import Recorder
from local_dictation.core.transcriber import transcribe

DEFAULT_SECONDS = 5


def main() -> None:
    """Record for a fixed duration, transcribe locally, copy result to clipboard."""
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SECONDS

    recorder = Recorder()
    print(f"Recording for {seconds:.1f}s... speak now.")
    recorder.start()
    time.sleep(seconds)
    audio = recorder.stop()
    print("Recording stopped, transcribing...")

    language, text = transcribe(audio)
    pyperclip.copy(text)

    print(f"detected language: {language}")
    print(f"text: {text}")
    print("(copied to clipboard)")


if __name__ == "__main__":
    main()
