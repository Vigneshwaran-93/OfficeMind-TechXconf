"""Safety layer (SR-1, SR-2, SR-3). Runs on masked user text before the LLM call."""
import re

CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end my life", "want to die", "self harm", "self-harm",
    "hurt myself", "no reason to live", "can't go on", "cant go on", "better off dead",
]

HARASSMENT_KEYWORDS = [
    "harass", "harassment", "bully", "bullying", "discriminat", "groped", "touched me",
    "unsafe", "assault", "threatened me", "sexual comment", "slur", "racist", "sexist",
    "retaliat", "hostile work environment",
]

INDIA_HELPLINES = [
    {"name": "Tele-MANAS (India, 24/7)", "contact": "14416 or 1-800-891-4416"},
    {"name": "KIRAN Mental Health Helpline (India, 24/7)", "contact": "1800-599-0019"},
    {"name": "iCall (India)", "contact": "9152987821"},
]


def _contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in keywords)


def check_crisis(masked_text: str) -> bool:
    return _contains_any(masked_text, CRISIS_KEYWORDS)


def check_harassment(masked_text: str) -> bool:
    return _contains_any(masked_text, HARASSMENT_KEYWORDS)


def crisis_response() -> str:
    lines = [
        "I'm really glad you told me. What you're feeling matters, and you don't have to face this alone right now.",
        "I'm not able to provide crisis support myself, but trained people are available right now who can help:",
    ]
    for h in INDIA_HELPLINES:
        lines.append(f"- {h['name']}: {h['contact']}")
    lines.append(
        "If you are outside India, please reach out to your local emergency or crisis helpline. "
        "If you are in immediate danger, please contact local emergency services."
    )
    return "\n".join(lines)


HARASSMENT_SYSTEM_NOTE = (
    "\n\nSafety note: the user's message may describe harassment, bullying, discrimination, "
    "or unsafe conditions. Do not frame this as a communication or confidence problem. "
    "Keep talking supportively, and naturally surface options such as documenting what happened, "
    "speaking with HR, talking to a trusted person, or seeking professional/legal advice, as appropriate."
)

TRIGGER_REGEN_NOTE = (
    "\n\nImportant: your previous reply used a word the user has asked you to avoid. "
    "Rewrite your reply without using any of the user's trigger words, keeping the same meaning."
)


def contains_trigger_words(text: str, triggers: list[str]) -> bool:
    if not triggers:
        return False
    lowered = text.lower()
    return any(t.lower() in lowered for t in triggers if t.strip())
