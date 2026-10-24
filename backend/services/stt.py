"""Local speech-to-text with faster-whisper. Audio never leaves the server."""
import os
import tempfile
import threading

import config

_lock = threading.Lock()
_model = None


def load_model():
    """Load the Whisper model once, at backend startup."""
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from faster_whisper import WhisperModel
                _model = WhisperModel(config.WHISPER_MODEL_SIZE, device=config.WHISPER_DEVICE)
    return _model


def transcribe_audio_bytes(audio_bytes: bytes, suffix: str = ".webm") -> str:
    """Save to a temp file, transcribe, then delete the file in a finally block."""
    model = load_model()
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    try:
        with open(path, "wb") as f:
            f.write(audio_bytes)
        segments, _info = model.transcribe(path, language="en")
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
