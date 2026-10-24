"""Single configuration module for both the Flask frontend and FastAPI backend."""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _require(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        sys.exit(f"Missing required environment variable: {name}. Set it in .env (see .env.example).")
    return value


GEMINI_API_KEY = _get("GEMINI_API_KEY")
GEMINI_CHAT_MODEL = _get("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
GEMINI_TTS_MODEL = _get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
GEMINI_TTS_VOICE = _get("GEMINI_TTS_VOICE", "Kore")
GOOGLE_APPLICATION_CREDENTIALS = _get("GOOGLE_APPLICATION_CREDENTIALS")

TTS_PROVIDER = _get("TTS_PROVIDER", "gemini")
WHISPER_MODEL_SIZE = _get("WHISPER_MODEL_SIZE", "base")
WHISPER_DEVICE = _get("WHISPER_DEVICE", "cpu")
SPACY_MODEL = _get("SPACY_MODEL", "en_core_web_lg")

DATABASE_URL = _get("DATABASE_URL", "sqlite:///./officemind.db")

JWT_SECRET = _get("JWT_SECRET", "change-me")
JWT_EXPIRE_MINUTES = int(_get("JWT_EXPIRE_MINUTES", "720"))
FLASK_SECRET_KEY = _get("FLASK_SECRET_KEY", "change-me")

BACKEND_URL = _get("BACKEND_URL", "http://127.0.0.1:8000")
FRONTEND_PORT = int(_get("FRONTEND_PORT", "5000"))
BACKEND_PORT = int(_get("BACKEND_PORT", "8000"))

MAX_AUDIO_SECONDS = int(_get("MAX_AUDIO_SECONDS", "60"))
LOG_LEVEL = _get("LOG_LEVEL", "INFO")


def require_llm_config():
    """Call this only where a Gemini call is about to be made, so the rest of the
    app (UI, DB, auth, masking) still works without a key during early setup.
    Raises RuntimeError (not SystemExit) so callers can catch it per-request
    instead of it propagating up and killing the whole server process."""
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to .env and restart the backend."
        )


if JWT_SECRET == "change-me":
    sys.exit("JWT_SECRET must be set in .env to a random secret value.")
