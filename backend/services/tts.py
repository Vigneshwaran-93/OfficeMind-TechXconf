"""Text-to-speech via Gemini TTS. Returns None on failure so callers fall back
to browser speechSynthesis."""
import base64
import io
import logging
import wave

from google import genai
from google.genai import types

import config

logger = logging.getLogger("officemind.tts")

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        config.require_llm_config()
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _pcm_to_wav_bytes(pcm_bytes: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def synthesize_speech_b64(text: str) -> str | None:
    """Returns base64-encoded WAV audio, or None if TTS is disabled/unavailable."""
    if config.TTS_PROVIDER != "gemini" or not text.strip():
        return None
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=config.GEMINI_TTS_MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=config.GEMINI_TTS_VOICE)
                    )
                ),
            ),
        )
        part = response.candidates[0].content.parts[0]
        pcm_bytes = part.inline_data.data
        wav_bytes = _pcm_to_wav_bytes(pcm_bytes)
        return base64.b64encode(wav_bytes).decode("ascii")
    except Exception:
        logger.exception("Gemini TTS failed; frontend will fall back to browser speech synthesis")
        return None
