"""Guards against hallucinated or empty output from short/silent recordings.

mlx_whisper.transcribe() can return confidently-worded hallucinations ("Thank you.") on
near-silent audio -- its own no_speech_prob/avg_logprob skip logic doesn't catch all of
these. This applies stricter, tunable thresholds before accepting a result.
"""

import numpy as np

from local_dictation import config

SAMPLE_RATE = 16_000


def clip_is_too_quiet_or_short(audio: np.ndarray) -> bool:
    """Cheap pre-transcription gate: duration and RMS energy."""
    if audio.size == 0:
        return True
    duration_seconds = audio.shape[0] / SAMPLE_RATE
    if duration_seconds < config.MIN_RECORDING_SECONDS:
        return True
    rms = float(np.sqrt(np.mean(np.square(audio))))
    return rms < config.RMS_SILENCE_THRESHOLD


def _worst_case_signals(result: dict) -> tuple[float, float, float]:
    """Aggregate per-segment confidence signals to their most-hallucination-prone values."""
    segments = result.get("segments") or []
    if not segments:
        # No segments at all is itself a strong no-speech signal.
        return 1.0, -999.0, 0.0
    no_speech_prob = max(seg.get("no_speech_prob", 0.0) for seg in segments)
    avg_logprob = min(seg.get("avg_logprob", 0.0) for seg in segments)
    compression_ratio = max(seg.get("compression_ratio", 0.0) for seg in segments)
    return no_speech_prob, avg_logprob, compression_ratio


def result_is_hallucination(result: dict) -> bool:
    """Stricter confidence check than Whisper's own internal skip logic (see design.md)."""
    no_speech_prob, avg_logprob, compression_ratio = _worst_case_signals(result)
    if no_speech_prob > config.NO_SPEECH_PROB_THRESHOLD and avg_logprob < config.AVG_LOGPROB_THRESHOLD:
        return True
    if compression_ratio > config.COMPRESSION_RATIO_THRESHOLD:
        return True
    return False


def accept(audio: np.ndarray, result: dict) -> bool:
    """True if this clip's transcription should be used; False if it should be discarded."""
    if clip_is_too_quiet_or_short(audio):
        return False
    text = result.get("text", "").strip()
    if not text:
        return False
    if result_is_hallucination(result):
        return False
    return True


def accepted_text(audio: np.ndarray, result: dict) -> str | None:
    """Return usable text, dropping only low-confidence result segments.

    Whisper already divides long input into segments.  Treating their worst confidence as
    the confidence of the whole recording loses otherwise valid long dictations.
    """
    if clip_is_too_quiet_or_short(audio):
        return None
    accepted_segments = []
    for segment in result.get("segments") or []:
        if not segment.get("text", "").strip():
            continue
        if result_is_hallucination({"segments": [segment]}):
            continue
        accepted_segments.append(segment["text"].strip())
    text = " ".join(accepted_segments).strip()
    return text or None
