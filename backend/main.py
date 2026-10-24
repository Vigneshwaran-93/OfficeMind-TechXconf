import json
import logging
from pathlib import Path

from fastapi import FastAPI

import config
from backend.routers import auth, preferences, sessions, chat

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL, logging.INFO))

app = FastAPI(title="OfficeMind API")

app.include_router(auth.router)
app.include_router(preferences.router)
app.include_router(sessions.router)
app.include_router(chat.router)

_QUESTIONS_PATH = Path(__file__).resolve().parent / "data" / "questions.json"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/questions")
def get_questions():
    return json.loads(_QUESTIONS_PATH.read_text(encoding="utf-8"))


@app.on_event("startup")
def preload_models():
    """Load Whisper once at startup, not per request. Masking analyzer loads
    lazily on first use to keep app startup fast when voice isn't used yet."""
    try:
        from backend.services import stt
        stt.load_model()
    except Exception:
        logging.getLogger("officemind").warning("Whisper model failed to preload; will retry on first use.")
