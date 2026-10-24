"""Builds the session context object (requirements Section 7) and the full
system instruction sent to Gemini (system prompt + context + preferences)."""
from pathlib import Path

from backend.models import UserPreference

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.md"
_BASE_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")

CATEGORY_LABELS = {
    "behaviour_communication": "Behaviour & Communication",
    "belonging_relationships": "Belonging & Workplace Relationships",
    "workload_burnout": "Workload & Burnout",
    "anxiety_confidence": "Anxiety, Pressure & Confidence",
    "personal_other": "Personal & Other Work Concerns",
    "other": "Something else",
}


def context_summary(context: dict) -> str:
    lines = [f"Category: {CATEGORY_LABELS.get(context.get('category'), context.get('category'))}"]
    if context.get("specific_situation"):
        lines.append(f"Specific situation: {context['specific_situation']}")
    if context.get("situation_details"):
        lines.append(f"Situation details: {context['situation_details']}")
    if context.get("main_worry"):
        lines.append(f"Main worry: {context['main_worry']}")
    if context.get("desired_support"):
        lines.append(f"Desired support: {context['desired_support']}")
    if context.get("initial_stress_level"):
        lines.append(f"Initial stress level (1-10): {context['initial_stress_level']}")
    lines.append(f"Preferred interaction: {context.get('preferred_interaction', 'text')}")
    return "\n".join(lines)


def build_system_instruction(context: dict, preferences: list[UserPreference]) -> str:
    likes = [p.value for p in preferences if p.kind == "like"]
    dislikes = [p.value for p in preferences if p.kind == "dislike"]
    triggers = [p.value for p in preferences if p.kind == "trigger"]
    settings = {p.value.split(":")[0]: p.value.split(":", 1)[1] for p in preferences
                if p.kind == "setting" and ":" in p.value}

    parts = [_BASE_PROMPT, "\n## This session's context\n", context_summary(context)]

    if likes:
        parts.append(f"\nThe user likes: {', '.join(likes)}.")
    if dislikes:
        parts.append(f"\nThe user dislikes: {', '.join(dislikes)}. Avoid these.")
    if triggers:
        parts.append(
            f"\nWord triggers — never use these words or phrases, and handle the topic gently: {', '.join(triggers)}."
        )
    tone = settings.get("tone")
    if tone:
        parts.append(f"\nPreferred tone: {tone}.")
    length = settings.get("reply_length")
    if length == "short":
        parts.append("\nKeep replies especially brief: 1-2 short sentences.")

    if context.get("initial_stress_level") and context["initial_stress_level"] >= 7:
        parts.append(
            "\nThe user's stress level is high. Prioritise stabilising before clarifying or guiding."
        )

    return "\n".join(parts)


def opening_message_hint(context: dict) -> str:
    """A short instruction for the LLM's very first turn so it references the
    user's actual concern instead of asking 'what's wrong?' again."""
    situation = context.get("situation_details") or context.get("specific_situation") or "what they shared"
    worry = context.get("main_worry")
    hint = f"This is the start of the conversation. Open by acknowledging: {situation}."
    if worry:
        hint += f" Their main worry is: {worry}."
    hint += " Do not ask them to restate their situation. Follow the Acknowledge/Stabilise steps."
    return hint
