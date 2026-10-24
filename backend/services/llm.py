"""Gemini chat calls via the google-genai SDK. Model names come from config, never hard-coded."""
import json
import re
import threading

from google import genai
from google.genai import types

import config

_lock = threading.Lock()
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                config.require_llm_config()
                _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def generate_reply(system_instruction: str, history: list[dict], user_message: str) -> str:
    """history: list of {"role": "user"|"model", "text": "..."} already masked."""
    client = _get_client()
    contents = []
    for turn in history[-12:]:
        role = "user" if turn["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=turn["text"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    response = client.models.generate_content(
        model=config.GEMINI_CHAT_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            max_output_tokens=300,
        ),
    )
    return (response.text or "").strip()


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_action_plan(system_instruction: str, history: list[dict]) -> dict:
    """One Gemini call that returns JSON only: summary, suggested_words, next_step,
    optional suggested_preference. Falls back to a plain message if parsing fails."""
    client = _get_client()
    transcript = "\n".join(f"{t['role']}: {t['text']}" for t in history[-12:])
    instruction = (
        system_instruction
        + "\n\nThe conversation is ending. Based on the transcript below, respond with JSON ONLY "
        "(no markdown, no code fences) with exactly these keys: "
        '"summary" (a short neutral summary of the situation), '
        '"suggested_words" (a ready-to-use script or message draft the user could say or send), '
        '"next_step" (one single concrete, manageable action), '
        'and optionally "suggested_preference" (a short like/dislike you noticed, or omit it).'
        f"\n\nTranscript:\n{transcript}"
    )
    response = client.models.generate_content(
        model=config.GEMINI_CHAT_MODEL,
        contents=[types.Content(role="user", parts=[types.Part(text=instruction)])],
        config=types.GenerateContentConfig(temperature=0.4, max_output_tokens=400),
    )
    raw = _strip_code_fences(response.text or "")
    try:
        data = json.loads(raw)
        return {
            "summary": data.get("summary", "").strip() or "We talked through your situation together.",
            "suggested_words": data.get("suggested_words", "").strip(),
            "next_step": data.get("next_step", "").strip() or "Take one small step when you're ready.",
            "suggested_preference": (data.get("suggested_preference") or "").strip() or None,
        }
    except (json.JSONDecodeError, AttributeError):
        return {
            "summary": "We talked through your situation together.",
            "suggested_words": raw[:300],
            "next_step": "Take one small step when you're ready.",
            "suggested_preference": None,
        }


def classify_ambiguous_safety(masked_text: str) -> dict:
    """Short Gemini classification call used when keyword checks are ambiguous."""
    client = _get_client()
    prompt = (
        "Classify this masked workplace message. Respond with JSON only: "
        '{"crisis": true|false, "harassment": true|false}. '
        '"crisis" means signs of self-harm, suicide, or immediate danger. '
        '"harassment" means bullying, harassment, discrimination, or unsafe working conditions.\n\n'
        f"Message: {masked_text}"
    )
    response = client.models.generate_content(
        model=config.GEMINI_CHAT_MODEL,
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=50),
    )
    try:
        data = json.loads(_strip_code_fences(response.text or "{}"))
        return {"crisis": bool(data.get("crisis")), "harassment": bool(data.get("harassment"))}
    except (json.JSONDecodeError, AttributeError):
        return {"crisis": False, "harassment": False}
