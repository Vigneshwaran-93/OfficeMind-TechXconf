"""Single choke point for PII / incident-identifying data masking (SR-9 to SR-14).

Every piece of user text (typed messages, Whisper transcripts, guided-question
free text, preference text) must go through mask_text() before it is sent to
the LLM, written to the database, or logged. The mapping from real value to
placeholder lives only in memory, keyed by session_id, and is never persisted.
"""
import re
import threading
from dataclasses import dataclass, field

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider

import config

_lock = threading.Lock()
_analyzer: AnalyzerEngine | None = None

# session_id -> { (entity_type, real_value_lower): (placeholder, original_text) }
_session_maps: dict[str, dict[tuple[str, str], tuple[str, str]]] = {}
# session_id -> { entity_type: next_index }
_session_counters: dict[str, dict[str, int]] = {}

PRIORITY_ENTITIES = {
    "TICKET", "MONEY_AMOUNT", "AADHAAR", "PAN", "CODENAME", "USER_TERM",
    "PHONE_NUMBER", "US_SSN",
}

BUILT_IN_ENTITIES = [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "DATE_TIME", "URL",
    "IP_ADDRESS", "CREDIT_CARD", "IBAN_CODE", "US_SSN", "NRP", "ORGANIZATION",
]

# Project/product codenames: configure deny-listed names here (per SR-11).
CODENAME_DENY_LIST = ["Project Phoenix", "Project Atlas", "Project Nova"]

GENERIC_PHRASES = {
    "PERSON": "your colleague",
    "ORGANIZATION": "the company",
    "TICKET": "the ticket",
    "LOCATION": "that place",
    "MONEY_AMOUNT": "a certain amount",
    "CODENAME": "the project",
    "DATE_TIME": "that time",
    "EMAIL_ADDRESS": "an email address",
    "PHONE_NUMBER": "a phone number",
    "URL": "a link",
    "IP_ADDRESS": "an IP address",
    "CREDIT_CARD": "a card number",
    "IBAN_CODE": "a bank account",
    "US_SSN": "an ID number",
    "NRP": "a group",
    "AADHAAR": "an ID number",
    "PAN": "an ID number",
}


def _build_analyzer() -> AnalyzerEngine:
    nlp_config = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": config.SPACY_MODEL}],
    }
    provider = NlpEngineProvider(nlp_configuration=nlp_config)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

    # Ensure spaCy ORG maps to Presidio ORGANIZATION and isn't ignored.
    registry = analyzer.registry
    ner_recognizer = next(
        (r for r in registry.recognizers if r.name == "SpacyRecognizer"), None
    )
    if ner_recognizer is not None:
        ner_recognizer.supported_entities = list(set(ner_recognizer.supported_entities) | {"ORGANIZATION"})
        if hasattr(ner_recognizer, "ner_strength"):
            pass

    # Ticket / case IDs: JIRA-1234, INC00012345, #1234
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="TICKET",
            name="ticket_id_recognizer",
            patterns=[
                Pattern("ticket_alpha_dash", r"\b[A-Z]{2,10}-\d+\b", 0.9),
                Pattern("ticket_inc", r"\bINC\d{5,}\b", 0.9),
                Pattern("ticket_hash", r"#\d{3,}\b", 0.6),
            ],
        )
    )

    # Money amounts: ₹, $, €, Rs, INR, lakh, crore
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="MONEY_AMOUNT",
            name="money_amount_recognizer",
            patterns=[
                Pattern("currency_symbol", r"[₹$€]\s?\d[\d,]*(\.\d+)?(\s?(lakh|crore|k|million))?", 0.85),
                Pattern("currency_word", r"\b(Rs\.?|INR)\s?\d[\d,]*(\.\d+)?(\s?(lakh|crore))?\b", 0.85),
                Pattern("lakh_crore", r"\b\d[\d,]*(\.\d+)?\s?(lakh|crore)s?\b", 0.7),
            ],
        )
    )

    # Bare Indian mobile numbers (Presidio's built-in phone recognizer often
    # misses 10-digit numbers with no country code or separators).
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            name="india_phone_recognizer",
            patterns=[Pattern("india_mobile", r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b", 0.85)],
        )
    )
    # Explicit US SSN backup pattern (in case the built-in recognizer's
    # context-boosting doesn't fire).
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="US_SSN",
            name="ssn_backup_recognizer",
            patterns=[Pattern("ssn_dashed", r"\b\d{3}-\d{2}-\d{4}\b", 0.85)],
        )
    )

    # India-relevant government IDs
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="AADHAAR",
            name="aadhaar_recognizer",
            patterns=[Pattern("aadhaar_12digit", r"\b\d{4}\s?\d{4}\s?\d{4}\b", 0.9)],
        )
    )
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="PAN",
            name="pan_recognizer",
            patterns=[Pattern("pan_format", r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", 0.9)],
        )
    )

    # Project/product codenames: deny-list plus "Project X" heuristic
    codename_patterns = [
        Pattern(f"codename_{i}", re.escape(name), 1.0) for i, name in enumerate(CODENAME_DENY_LIST)
    ]
    codename_patterns.append(Pattern("codename_project_x", r"\bProject [A-Z][a-zA-Z]+\b", 0.6))
    codename_patterns.append(Pattern("codename_the_x_project", r"\bthe [A-Z][a-zA-Z]+ project\b", 0.5))
    registry.add_recognizer(
        PatternRecognizer(supported_entity="CODENAME", name="codename_recognizer", patterns=codename_patterns)
    )

    return analyzer


def _get_analyzer() -> AnalyzerEngine:
    global _analyzer
    if _analyzer is None:
        with _lock:
            if _analyzer is None:
                _analyzer = _build_analyzer()
    return _analyzer


def _entities_for(user_mask_terms: list[str] | None) -> list:
    entities = list(BUILT_IN_ENTITIES) + ["TICKET", "MONEY_AMOUNT", "AADHAAR", "PAN", "CODENAME"]
    if user_mask_terms:
        entities.append("USER_TERM")
    return entities


def _user_term_recognizer(terms: list[str]) -> PatternRecognizer:
    patterns = [Pattern(f"user_term_{i}", re.escape(t), 1.0) for i, t in enumerate(terms) if t.strip()]
    if not patterns:
        patterns = [Pattern("user_term_none", r"(?!x)x", 0.0)]  # never matches
    return PatternRecognizer(supported_entity="USER_TERM", name="user_term_recognizer", patterns=patterns)


@dataclass
class MaskResult:
    masked_text: str
    entities_found: list[str] = field(default_factory=list)


def _placeholder_for(session_id: str, entity_type: str, real_value: str) -> str:
    key = (entity_type, real_value.lower())
    session_map = _session_maps.setdefault(session_id, {})
    if key in session_map:
        return session_map[key][0]
    counters = _session_counters.setdefault(session_id, {})
    counters[entity_type] = counters.get(entity_type, 0) + 1
    placeholder = f"<{entity_type}_{counters[entity_type]}>"
    session_map[key] = (placeholder, real_value)
    return placeholder


def mask_text(text: str, session_id: str, user_mask_terms: list[str] | None = None) -> MaskResult:
    """Mask PII and incident-identifying details in `text`, using consistent
    numbered placeholders for the given session_id."""
    if not text or not text.strip():
        return MaskResult(masked_text=text or "")

    analyzer = _get_analyzer()
    registry = analyzer.registry
    if user_mask_terms:
        registry.add_recognizer(_user_term_recognizer(user_mask_terms))

    try:
        results = analyzer.analyze(
            text=text,
            language="en",
            entities=_entities_for(user_mask_terms),
        )
    finally:
        if user_mask_terms:
            registry.recognizers = [
                r for r in registry.recognizers if r.name != "user_term_recognizer"
            ]

    # Resolve overlaps: custom incident-identifying recognizers take priority
    # over generic NLP-derived entities (e.g. a 12-digit Aadhaar number should
    # win over a DATE_TIME false positive), then higher score, then longer match.
    results = sorted(
        results,
        key=lambda r: (
            r.start,
            0 if r.entity_type in PRIORITY_ENTITIES else 1,
            -r.score,
            -(r.end - r.start),
        ),
    )
    filtered = []
    last_end = -1
    for r in results:
        if r.start >= last_end:
            filtered.append(r)
            last_end = r.end

    filtered.sort(key=lambda r: r.start, reverse=True)
    masked = text
    entities_found = []
    for r in filtered:
        real_value = text[r.start:r.end]
        entity_type = "ORGANIZATION" if r.entity_type == "ORG" else r.entity_type
        placeholder = _placeholder_for(session_id, entity_type, real_value)
        masked = masked[:r.start] + placeholder + masked[r.end:]
        entities_found.append(entity_type)

    return MaskResult(masked_text=masked, entities_found=entities_found)


def unmask_for_display(text: str, session_id: str) -> str:
    """Restore real values for the on-screen transcript only."""
    session_map = _session_maps.get(session_id, {})
    if not session_map:
        return text
    reverse = {placeholder: original for placeholder, original in session_map.values()}
    # Replace longest placeholders first to avoid partial overlap issues.
    for placeholder in sorted(reverse, key=len, reverse=True):
        text = text.replace(placeholder, reverse[placeholder])
    return text


_PLACEHOLDER_RE = re.compile(r"<([A-Z_]+?)_(\d+)>")


def generic_for_speech(text: str) -> str:
    """Replace placeholders with neutral spoken phrases so TTS never receives
    real personal data (and never reads out a literal placeholder token)."""
    def _replace(match: re.Match) -> str:
        entity_type = match.group(1)
        return GENERIC_PHRASES.get(entity_type, "that detail")

    return _PLACEHOLDER_RE.sub(_replace, text)


def clear_session(session_id: str) -> None:
    _session_maps.pop(session_id, None)
    _session_counters.pop(session_id, None)
