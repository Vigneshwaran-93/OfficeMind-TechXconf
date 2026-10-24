import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session as DbSession

import config
from backend.db import get_db
from backend.models import User, Session as SessionModel, UserPreference
from backend.schemas import ChatTextRequest, ChatResponse, TtsRequest
from backend.auth import get_current_user
from backend.services import session_store, masking, llm, safety, stt, tts
from backend.services.context import build_system_instruction

router = APIRouter(prefix="/chat", tags=["chat"])


def _mask_term_list(db: DbSession, user_id: int) -> list[str]:
    rows = db.query(UserPreference).filter(
        UserPreference.user_id == user_id, UserPreference.kind == "mask_term"
    ).all()
    return [r.value for r in rows]


def _handle_turn(session_id: int, user_id: int, raw_text: str, db: DbSession, want_audio: bool) -> ChatResponse:
    db_session = db.get(SessionModel, session_id)
    if not db_session or db_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    state = session_store.get(session_id)
    if state is None:
        raise HTTPException(status_code=400, detail="Session not active. Start a session first.")

    sid = str(session_id)
    mask_terms = _mask_term_list(db, user_id)

    if not raw_text or not raw_text.strip():
        reply = "I didn't quite catch that — could you say it again or type it?"
        return ChatResponse(user_text_display="", reply_display=reply, reply_audio_b64=None)

    masked_user = masking.mask_text(raw_text, session_id=sid, user_mask_terms=mask_terms).masked_text
    user_display = masking.unmask_for_display(masked_user, sid)

    crisis = safety.check_crisis(masked_user)
    harassment = safety.check_harassment(masked_user) if not crisis else False

    preferences = db.query(UserPreference).filter(UserPreference.user_id == user_id).all()
    triggers = [p.value for p in preferences if p.kind == "trigger"]
    context = json.loads(db_session.context_json) if db_session.context_json else {}
    system_instruction = build_system_instruction(context, preferences)
    if harassment:
        system_instruction += safety.HARASSMENT_SYSTEM_NOTE

    if crisis:
        reply_masked = safety.crisis_response()
    else:
        try:
            reply_masked = llm.generate_reply(system_instruction, state["history"], masked_user)
        except RuntimeError:
            raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured yet.")
        except Exception:
            reply_masked = "I'm having trouble responding right now. Could you try again in a moment, or switch to text?"

        if safety.contains_trigger_words(reply_masked, triggers):
            try:
                reply_masked = llm.generate_reply(
                    system_instruction + safety.TRIGGER_REGEN_NOTE, state["history"], masked_user
                )
            except Exception:
                pass

    session_store.append_turn(session_id, "user", masked_user, user_display)
    reply_display = masking.unmask_for_display(reply_masked, sid)
    session_store.append_turn(session_id, "model", reply_masked, reply_display)

    audio_b64 = None
    if want_audio and not crisis:
        speech_text = masking.generic_for_speech(reply_masked)
        try:
            audio_b64 = tts.synthesize_speech_b64(speech_text)
        except Exception:
            audio_b64 = None

    return ChatResponse(
        user_text_display=user_display,
        reply_display=reply_display,
        reply_audio_b64=audio_b64,
        crisis=crisis,
        harassment=harassment,
    )


@router.post("/text", response_model=ChatResponse)
def chat_text(req: ChatTextRequest, user: User = Depends(get_current_user), db: DbSession = Depends(get_db)):
    return _handle_turn(req.session_id, user.id, req.message, db, want_audio=False)


@router.post("/voice", response_model=ChatResponse)
async def chat_voice(
    session_id: int = Form(...),
    audio: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    audio_bytes = await audio.read()
    try:
        transcript = stt.transcribe_audio_bytes(audio_bytes, suffix=".webm")
    except Exception:
        transcript = ""
    return _handle_turn(session_id, user.id, transcript, db, want_audio=True)


@router.post("/tts")
def chat_tts(req: TtsRequest):
    audio_b64 = tts.synthesize_speech_b64(req.text)
    if audio_b64 is None:
        return {"audio_b64": None, "provider": "browser"}
    return {"audio_b64": audio_b64, "provider": "gemini"}
