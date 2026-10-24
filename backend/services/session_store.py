"""In-memory per-session conversation state (masked history, context, display
transcript). Session_id here is the DB Session.id, scoped to this process —
fine for a single-process hackathon deployment."""
import threading

_lock = threading.Lock()
_sessions: dict[int, dict] = {}


def start(session_id: int, context: dict, user_id: int):
    with _lock:
        _sessions[session_id] = {
            "context": context,
            "user_id": user_id,
            "history": [],  # [{"role": "user"/"model", "text": masked_text}]
            "display": [],  # [{"role": "user"/"model", "text": unmasked_text}]
        }


def get(session_id: int) -> dict | None:
    return _sessions.get(session_id)


def append_turn(session_id: int, role: str, masked_text: str, display_text: str):
    state = _sessions.get(session_id)
    if state is None:
        return
    state["history"].append({"role": role, "text": masked_text})
    state["display"].append({"role": role, "text": display_text})


def end(session_id: int):
    with _lock:
        _sessions.pop(session_id, None)
