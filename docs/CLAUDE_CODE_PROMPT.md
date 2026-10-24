# OfficeMind — Build Prompt for Claude Code

> **How to use:** Create an empty project folder, put `OfficeMind_Requirements.md` inside `docs/`, open Claude Code in the folder root, and paste everything below the line as your first message.

---

You are building **OfficeMind**, an AI-powered workplace mental wellness companion, as a simple but fully working hackathon project.

## 0. Source of truth

Before writing any code, read `docs/OfficeMind_Requirements.md` from start to finish. It is the source of truth for product behaviour, screens, the branching question system, AI behaviour rules, the session context schema, safety/privacy rules, and acceptance criteria. Refer back to it by section number whenever you make a decision (for example "per FR-5.7" or "per SR-11").

If anything in this prompt conflicts with the requirements doc, this prompt wins on **technical choices** and the doc wins on **product behaviour**. If something is ambiguous, pick the simplest option that satisfies the doc, note the assumption in `docs/DECISIONS.md`, and keep going. Do not stop to ask me unless you are truly blocked.

After reading it, reply with a short build plan (stages below, plus anything you would adjust) and then start Stage 1.

## 1. Guiding principles

- **Simple, efficient, fully working.** A complete end-to-end flow beats extra features.
- **No extra frameworks.** Only what is listed in Section 2. No React, Vue, Tailwind, Bootstrap, Celery, Redis, Docker, LangChain, or frontend build tools.
- **Plain code over abstractions.** Fewer files, clear function names, short modules.
- **Privacy first.** No raw personal data ever reaches the LLM, the database, or the logs.
- **Phone-first UI.** Every screen is designed for a phone.

## 2. Tech stack (fixed)

| Area | Choice |
|---|---|
| Frontend | Flask + Jinja2 templates, one CSS file, small vanilla JS files |
| Backend | FastAPI + Uvicorn |
| DB | SQLite via SQLAlchemy 2.x ORM (declarative models). No Alembic yet, but structure models so it can be added later. |
| LLM | Gemini API via the `google-genai` Python SDK |
| Speech-to-text | Whisper, run locally with `faster-whisper` (audio never leaves the server) |
| Text-to-speech | Google/Gemini TTS via the Gemini API; browser `speechSynthesis` as fallback |
| PII masking | Microsoft Presidio (`presidio-analyzer`, `presidio-anonymizer`) with spaCy `en_core_web_lg` (allow `en_core_web_sm` via config for low-memory machines) |
| Auth | `bcrypt` for password hashing, `PyJWT` for tokens |
| HTTP between Flask and FastAPI | `requests` |
| Config | `python-dotenv` + one `config.py` |
| Python | 3.11 |

Check the current `google-genai` docs for the correct client usage and model names; never hard-code model names — read them from config.

## 3. Project structure

Use this layout (small deviations are fine if documented):

```
officemind/
├── README.md
├── .env.example
├── .gitignore                 # .env, *.db, __pycache__, venv, temp audio
├── requirements.txt
├── config.py                  # single config for both apps
├── docs/
│   ├── OfficeMind_Requirements.md
│   └── DECISIONS.md
├── scripts/
│   ├── init_db.py             # create fresh DB; --reset drops and recreates
│   └── test_masking.py        # prints raw vs masked for sample sentences
├── backend/                   # FastAPI
│   ├── main.py
│   ├── db.py                  # engine, SessionLocal, Base
│   ├── models.py              # User, UserPreference, Session, ActionPlan
│   ├── schemas.py             # Pydantic request/response models
│   ├── auth.py                # hash/verify, create/verify JWT, get_current_user
│   ├── routers/
│   │   ├── auth.py            # /auth/register, /auth/login, /auth/me, DELETE /auth/me
│   │   ├── preferences.py     # CRUD /preferences
│   │   ├── sessions.py        # start session, guided answers, end, action plan
│   │   └── chat.py            # /chat/text, /chat/voice, /chat/tts
│   ├── services/
│   │   ├── masking.py         # Presidio setup, custom recognizers, mask/unmask
│   │   ├── llm.py             # Gemini chat calls
│   │   ├── stt.py             # faster-whisper transcription
│   │   ├── tts.py             # Gemini/Google TTS
│   │   ├── safety.py          # crisis + harassment detection
│   │   └── context.py         # builds context object + system prompt
│   ├── data/
│   │   └── questions.json     # branching question tree for all 5 categories
│   └── prompts/
│       └── system_prompt.md   # master system prompt
└── frontend/                  # Flask
    ├── app.py
    ├── api_client.py          # thin requests wrapper to FastAPI
    ├── templates/
    │   ├── base.html          # phone frame shell
    │   ├── login.html  register.html
    │   ├── welcome.html  home.html  questions.html  checkin.html
    │   ├── companion.html     # voice + text chat
    │   ├── plan.html  profile.html  help.html
    └── static/
        ├── css/style.css
        └── js/  companion.js  questions.js
```

## 4. Configuration (`config.py` + `.env`)

All keys and major settings live here. Commit `.env.example` with placeholder values; never commit `.env`.

```
GEMINI_API_KEY=
GEMINI_CHAT_MODEL=           # set to a current Gemini chat model
GEMINI_TTS_MODEL=            # set to a current Gemini TTS model
GEMINI_TTS_VOICE=            # a calm voice name
GOOGLE_APPLICATION_CREDENTIALS=   # only if using Google Cloud TTS instead
TTS_PROVIDER=gemini          # gemini | browser
WHISPER_MODEL_SIZE=base      # tiny | base | small
WHISPER_DEVICE=cpu
SPACY_MODEL=en_core_web_lg
DATABASE_URL=sqlite:///./officemind.db
JWT_SECRET=change-me
JWT_EXPIRE_MINUTES=720
FLASK_SECRET_KEY=change-me
BACKEND_URL=http://127.0.0.1:8000
FRONTEND_PORT=5000
BACKEND_PORT=8000
MAX_AUDIO_SECONDS=60
LOG_LEVEL=INFO
```

`config.py` should load these once, provide defaults where safe, and fail with a clear message if `GEMINI_API_KEY` or `JWT_SECRET` is missing.

## 5. Key implementation requirements

### 5.1 Privacy and PII masking (highest priority)

Build `services/masking.py` as a single choke point. **Every** piece of user text goes through it before any LLM call, DB write, or log line: typed messages, Whisper transcripts, free-text guided answers, and preference text.

- Use Presidio `AnalyzerEngine` with an explicit spaCy NLP config. Make sure the spaCy `ORG` label maps to Presidio `ORGANIZATION` and is **not** in the ignore list (it is ignored in some default configs).
- Built-in entities to mask: `PERSON`, `EMAIL_ADDRESS`, `PHONE_NUMBER`, `LOCATION`, `DATE_TIME`, `URL`, `IP_ADDRESS`, `CREDIT_CARD`, `IBAN_CODE`, `US_SSN`, `NRP`, plus `ORGANIZATION`. Add India-relevant regex recognizers too (Aadhaar-like 12-digit, PAN `[A-Z]{5}[0-9]{4}[A-Z]`), since the demo audience may be in India.
- Custom recognizers for **incident-identifying details** (per SR-11):
  - Ticket/case IDs: patterns like `[A-Z]{2,10}-\d+`, `INC\d{5,}`, `#\d{3,}`.
  - Money amounts: `₹`, `$`, `€`, `Rs`, `INR`, `lakh`, `crore` with numbers.
  - Project or product codenames: a configurable deny-list plus a heuristic for "Project X" / "the X project" phrasing.
  - Per-user "always mask" terms (SR-12): loaded from that user's preferences (`kind="mask_term"`) as a deny-list recognizer.
- Anonymise with **consistent numbered placeholders per session**: the same real value always becomes the same token (`<PERSON_1>`, `<ORG_1>`, `<TICKET_1>`). Keep the mapping in an in-memory dict keyed by session ID only. Never persist it, never log it, clear it when the session ends.
- `unmask_for_display(text, session_id)` restores real values for the on-screen transcript.
- `generic_for_speech(text)` replaces placeholders with neutral phrases ("your colleague", "the company", "the ticket") so TTS never receives real personal data.
- Instruct the LLM in the system prompt to keep placeholders exactly as written and never guess what they stand for.
- `scripts/test_masking.py` must run ~10 realistic sample sentences (e.g. "Priya from Infosys yelled at me about JIRA-4521 in the Bangalore office on Monday") and print raw → masked so I can verify masking quickly.
- Logging: log masked text only. Delete temp audio files immediately after transcription (use `try/finally`).

### 5.2 Voice and chat

- `companion.html` shows a chat transcript, a large thumb-reachable mic button, a text input, and controls: mute mic, stop speaking, switch to text, end session (FR-5.3 to FR-5.5). Show a clear "listening" state when recording.
- Recording: browser `MediaRecorder` → upload the blob to Flask → Flask forwards to FastAPI `/chat/voice`. Use tap-to-start / tap-to-stop (simplest reliable approach on mobile). Enforce `MAX_AUDIO_SECONDS`.
- FastAPI voice pipeline: save temp file → `faster-whisper` transcribe → delete file → mask → safety check → LLM → unmask for display → generic text for TTS → TTS audio (base64) → return `{user_text_display, reply_display, reply_audio_b64}`.
- If transcription returns empty or low-confidence text, reply honestly ("I didn't quite catch that — could you say it again or type it?") rather than guessing (FR-5.7).
- If mic permission is denied, or STT/TTS fails, fall back to text automatically and show a small notice (FR-5.8). If `TTS_PROVIDER=browser` or Gemini TTS fails, use `speechSynthesis` in the browser.
- Load the Whisper model once at backend startup, not per request.
- Keep the conversation history (masked) in memory per session and send the last ~12 turns to Gemini.

### 5.3 LLM and system prompt

- Write `backend/prompts/system_prompt.md` as the master prompt, built directly from requirements **Section 6** (persona, 7-step sequence, must / must not lists, category-specific instructions, reference conversation) and **Section 9** (safety). Include: short spoken-style replies (2–4 sentences, one question max per turn), placeholder rules, and how to use the context object and user preferences.
- `services/context.py` builds the session context object (requirements **Section 7**) from guided answers and appends the user's likes, dislikes, triggers, and tone preference.
- Word triggers: tell the LLM to avoid those words, and also post-check the reply; if a trigger word appears, regenerate once with a stronger instruction.
- Action plan: at session end, make one Gemini call that returns **JSON only** (`summary`, `suggested_words`, `next_step`, optional `suggested_preference`). Strip code fences, parse safely, and fall back to a plain message if parsing fails.

### 5.4 Safety layer

- `services/safety.py` runs on masked user text before the LLM call: a keyword/phrase check for self-harm or crisis and for harassment, bullying, discrimination, or unsafe conditions, plus a short Gemini classification call when keywords are ambiguous.
- Crisis → skip the normal flow, return a calm supportive message, and show a crisis banner linking to `help.html`. Use India helplines by default (verify current numbers, e.g. Tele-MANAS 14416) with a note to use local services elsewhere. Don't make promises about how helplines handle confidentiality.
- Harassment / unsafe conditions → keep talking, but add the system instruction to surface documentation, HR, trusted people, and professional options (SR-2), and never frame it as the user's communication problem.

### 5.5 Auth (basic)

- Register: username, password (min 8 chars), optional display name. No email or real name required.
- Login returns a JWT; Flask stores it in its signed session cookie and sends it as a `Bearer` token to FastAPI. Flask decorator `login_required` redirects to login.
- `DELETE /auth/me` removes the user and all linked rows (cascade).

### 5.6 Preferences module ("character building")

- One table `user_preferences(id, user_id FK, kind, value, created_at)` where `kind` ∈ `like | dislike | trigger | setting | mask_term`.
- `profile.html`: simple lists per kind with add / delete, plus tone (gentle / direct), reply length (short / normal), and voice default (on / off).
- Mask preference text before saving (except `mask_term`, which is the user's own deny-list; store it, but never send it to the LLM).
- At the end of a session, if the action-plan call returns `suggested_preference`, show it on the plan screen with "Save" / "No thanks" — save only on confirmation.

### 5.7 Guided questions

- `backend/data/questions.json` holds the full branching tree for all five categories from requirements **Section 5.2–5.3**: Stage 1 options per category, Stage 2 and Stage 3 options that can depend on the previous answer, plus a "Something else" free-text option at every stage. Include at least one full specific branch per category (like the "I made a mistake" example).
- Every stage has a Skip button and a progress indicator (1 of 3, 2 of 3, 3 of 3). Then show the optional emotional check-in (stress 1–10 slider + feeling chips).

### 5.8 Phone-friendly UI

- Mobile-first CSS. In `base.html`, wrap everything in `.phone` container:
  - On screens under ~500 px: full width and full height (`100dvh`), no frame — feels like a native app. Respect safe-area insets.
  - On wider screens: centred device frame about 400 × 860 px, rounded corners, subtle shadow, on a soft neutral background; content scrolls inside the frame.
- Calm palette (soft blues/greens, warm neutrals), system font stack, tap targets ≥ 44 px, bottom-anchored mic/send bar, large readable text. Support `prefers-color-scheme: dark`.
- Use one CSS file and a small set of inline SVG icons; no icon libraries.
- Five category cards on Home, each with an icon, title, and one-line description, plus a "Something else" card.

## 6. Build stages — commit locally after each

Run `git init` first. At the end of **every** stage: run the app (or the relevant script), confirm the stage's check passes, then `git add -A && git commit -m "stage N: <summary>"`. Do not push anywhere. Make a separate commit if you fix a bug from a previous stage.

| Stage | Build | Check before committing |
|---|---|---|
| 1 | Skeleton: folders, `requirements.txt`, `config.py`, `.env.example`, `.gitignore`, empty Flask and FastAPI apps with health routes | Both servers start; `/health` returns OK; Flask page loads |
| 2 | DB: SQLAlchemy models, `db.py`, `scripts/init_db.py` (fresh + `--reset`) | Script creates `officemind.db` with all four tables |
| 3 | Auth: register/login/me/delete in FastAPI; Flask login, register, logout pages and `login_required` | Can register, log in, see a protected page, log out |
| 4 | Phone UI shell: `base.html`, `style.css`, Welcome and Home with five category cards | Looks native in mobile dev-tools view and framed on desktop |
| 5 | Guided questions: `questions.json`, branching flow, skip, progress, check-in; session start stores masked context | Can complete or skip all 3 stages for each category |
| 6 | PII masking service + `scripts/test_masking.py` | Script output shows all names, orgs, ticket IDs, amounts, dates masked consistently |
| 7 | Text chat: context builder, system prompt, Gemini call, safety layer, unmask for display | A text conversation follows the 7-step behaviour; crisis text triggers banner |
| 8 | Voice: Whisper STT, Gemini TTS, browser fallback, mic UI states, text fallback | Spoken message is transcribed, answered, and spoken back; denying mic falls back to text |
| 9 | Action plan screen + save + feeling-after + suggested preference | Ending a session shows summary, words, next step; save works |
| 10 | Profile / preferences module wired into prompts; Help & Safety page; delete account | Adding a trigger word changes AI behaviour; delete removes all data |
| 11 | README, `docs/DECISIONS.md`, cleanup, final end-to-end run against requirements **Section 13** | Every acceptance criterion passes or is documented as a known gap |

## 7. README requirements

`README.md` must include:

1. What OfficeMind is (short) and a screenshot placeholder.
2. Architecture overview (Flask → FastAPI → Presidio → Gemini; Whisper local) with the ASCII flow from requirements **Section 8.4**.
3. Privacy model: what is masked, what is never stored, where audio goes.
4. Prerequisites: Python 3.11, `ffmpeg` (needed by Whisper), git, a Gemini API key.
5. Setup step by step: clone, venv, `pip install -r requirements.txt`, `python -m spacy download en_core_web_lg`, copy `.env.example` to `.env` and fill keys, `python scripts/init_db.py`.
6. How to run: two terminals (`uvicorn backend.main:app --port 8000 --reload` and `python frontend/app.py`), then open `http://127.0.0.1:5000`. Note that browsers only allow microphone access on `localhost`/`127.0.0.1` or HTTPS, and explain how to test on a real phone (e.g. a tunnel with HTTPS).
7. How to verify masking (`python scripts/test_masking.py`).
8. How to reset the database.
9. Configuration reference table for every `.env` key.
10. Troubleshooting: missing ffmpeg, spaCy model not found, Gemini model name errors, mic permission blocked, slow Whisper on CPU (use `tiny`/`base`).
11. Project structure tree and known limitations.

## 8. Things not to do

- Do not send raw (unmasked) user text or audio to Gemini or any external service.
- Do not store raw transcripts or the masking map in the database or logs.
- Do not add frameworks, CSS libraries, JS bundlers, or Docker.
- Do not hard-code API keys or model names.
- Do not build features outside the requirements doc and this prompt.
- Do not leave stages half-finished before committing; each commit should run.

Start by reading `docs/OfficeMind_Requirements.md`, then share your plan and begin Stage 1.
