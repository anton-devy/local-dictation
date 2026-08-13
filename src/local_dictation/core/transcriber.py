"""Local Whisper transcription with automatic English/German detection.

Returns the full mlx_whisper result (including per-segment no_speech_prob, avg_logprob,
and compression_ratio) so filters.py can apply hallucination-confidence thresholds.
"""

from local_dictation import config  # noqa: F401  (sets HF_HUB_DISABLE_PROGRESS_BARS before mlx_whisper import)

import numpy as np


def transcribe_full(audio: np.ndarray) -> dict:
    """Transcribe a 16kHz mono float32 buffer. Returns the raw mlx_whisper result dict."""
    import mlx_whisper

    return mlx_whisper.transcribe(audio, path_or_hf_repo=config.MODEL, language=None, verbose=None)


def transcribe(audio: np.ndarray) -> tuple[str, str]:
    """Convenience wrapper: returns (language, text) with no confidence filtering."""
    result = transcribe_full(audio)
    return result["language"], result["text"].strip()


def unload_model() -> None:
    """Unload the transcription model from memory to reduce idle footprint."""
    try:
        import gc
        import mlx.core as mx
        # Access mlx_whisper's internal ModelHolder and clear the cached model
        from mlx_whisper.transcribe import ModelHolder
        ModelHolder.model = None
        ModelHolder.model_path = None
        gc.collect()
        mx.clear_cache()
        mx.metal.clear_cache()
    except (ImportError, AttributeError, RuntimeError):
        pass  # Best-effort cleanup on MLX versions without one of these APIs.
