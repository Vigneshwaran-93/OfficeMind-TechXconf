from typing import Optional, Literal
from pydantic import BaseModel, Field


# --- Auth ---
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None


# --- Preferences ---
class PreferenceCreate(BaseModel):
    kind: Literal["like", "dislike", "trigger", "setting", "mask_term"]
    value: str


class PreferenceResponse(BaseModel):
    id: int
    kind: str
    value: str


# --- Sessions ---
class SessionContext(BaseModel):
    category: str
    specific_situation: Optional[str] = None
    situation_details: Optional[str] = None
    main_worry: Optional[str] = None
    desired_support: Optional[str] = None
    initial_stress_level: Optional[int] = None
    preferred_interaction: Literal["voice", "text"] = "text"
    conversation_stage: str = "acknowledge"


class SessionStartRequest(BaseModel):
    context: SessionContext


class SessionStartResponse(BaseModel):
    session_id: int
    opening_message: str


class SessionEndRequest(BaseModel):
    feeling_after: Optional[str] = None


class ActionPlanResponse(BaseModel):
    session_id: int
    summary: str
    suggested_words: str
    next_step: str
    suggested_preference: Optional[str] = None


class SavePlanRequest(BaseModel):
    session_id: int
    save: bool


# --- Chat ---
class ChatTextRequest(BaseModel):
    session_id: int
    message: str


class ChatResponse(BaseModel):
    user_text_display: str
    reply_display: str
    reply_audio_b64: Optional[str] = None
    crisis: bool = False
    harassment: bool = False


class TtsRequest(BaseModel):
    text: str
