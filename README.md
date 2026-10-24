# OfficeMind

**An AI-powered workplace mental wellness companion** — voice-first, with text
fallback. OfficeMind helps employees work through the small, everyday moments
that create anxiety, stress, self-doubt, or loneliness at work: admitting a
mistake, asking a basic question, feeling overloaded, panicking before a
meeting, or just feeling unsure where they stand. It is not a therapist,
manager, or productivity tracker — it's a calm, non-judgmental companion that
helps you leave every session with one realistic next step.

> Screenshot: _add a screenshot of the Home screen or Companion chat here_
> (`docs/screenshot.png`).

Full product behaviour, screens, and acceptance criteria live in
[`docs/OfficeMind_Requirements.md`](docs/OfficeMind_Requirements.md).
Build decisions and assumptions are in [`docs/DECISIONS.md`](docs/DECISIONS.md).

## 1. Architecture

```
Browser (Flask page)
  │  text, or recorded audio (MediaRecorder → webm)
  ▼
Flask route  ──(server-to-server, bearer token)──▶  FastAPI
                                                      │
                                   audio? ──▶ Whisper STT (local, faster-whisper)
                                                      │ raw text
                                                      ▼
                                          Presidio masking layer
                                    (raw text → masked text + in-memory mapping)
                                                      │ masked text only
                                                      ▼
                                    Gemini LLM  (system prompt + context
                                    + preferences + masked history)
                                                      │ masked reply
                                                      ▼
                                 Re-identify for on-screen transcript only
                                 Generic phrasing ("your colleague") for TTS
                                                      │
                                                      ▼
                                          Gemini TTS → audio (base64)
  ◀───────────────────────── reply text + audio ──────┘
```

Flask (frontend, port 5000) renders the phone UI and proxies every API call to
FastAPI (backend, port 8000) with a bearer token, so the browser never talks
to FastAPI directly. The masking step is a single choke point: **every**
piece of user text — typed, transcribed, guided-question free text, or
preference text — passes through it before it reaches the database, a log
line, or Gemini.

## 2. Privacy model

- **What's masked:** names, emails, phone numbers, locations, dates, URLs, IP
  addresses, credit cards, government IDs (incl. Indian Aadhaar/PAN),
  organisations, ticket/case IDs (`JIRA-1234`, `INC00012345`, `#4521`), money
  amounts (`₹`, `$`, `Rs`, lakh/crore), and project codenames — replaced with
  consistent per-session placeholders (`<PERSON_1>`, `<ORG_1>`, ...).
- **What's never stored:** raw transcripts, the masking map (real value ↔
  placeholder — kept only in server memory for the life of a session, cleared
  when it ends), and raw audio (deleted immediately after transcription).
- **What's stored (masked only, opt-in):** a saved action plan — summary,
  suggested words, next step — only if you choose "Save this plan privately."
  Session context (category, situation, worry, etc.) is also stored masked.
- **Where audio goes:** nowhere outside this server. Speech-to-text runs
  locally via `faster-whisper`; only masked text ever reaches Gemini.
- OfficeMind is never shared with your employer.

Verify masking yourself any time with `python scripts/test_masking.py`.

## 3. Prerequisites

- Python 3.11 (this build was run against a pre-existing Python 3.14 venv —
  see `docs/DECISIONS.md` point 2)
- [`ffmpeg`](https://ffmpeg.org/) on your `PATH` (required by Whisper for audio decoding)
- Git
- A [Gemini API key](https://ai.google.dev/) (for chat + TTS)

## 4. Setup

```bash
git clone <this repo>
cd techxconf

# Create and activate a virtualenv (skip if one already exists, e.g. ./venv)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_lg

cp .env.example .env           # then fill in GEMINI_API_KEY (see table below)
python scripts/init_db.py      # creates officemind.db
```

## 5. Running it

Two terminals, from the project root, with the venv active in both:

```bash
# Terminal 1 — backend
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000 --reload

# Terminal 2 — frontend
venv\Scripts\python.exe frontend\app.py
```

Then open **http://127.0.0.1:5000**.

> Browsers only allow microphone access on `localhost` / `127.0.0.1` or over
> HTTPS. To test voice on a real phone, run the frontend behind an HTTPS
> tunnel (e.g. `ngrok http 5000` or `cloudflared tunnel --url http://localhost:5000`)
> and open the tunnel's HTTPS URL on your phone.

## 6. Verifying PII masking

```bash
venv\Scripts\python.exe scripts\test_masking.py
```

Prints ~10 realistic sample sentences with names, companies, ticket IDs,
amounts, and dates, showing raw → masked → unmasked-for-display →
generic-for-speech for each.

## 7. Resetting the database

```bash
venv\Scripts\python.exe scripts\init_db.py --reset
```

Drops and recreates all four tables (`users`, `user_preferences`, `sessions`,
`action_plans`) from the current SQLAlchemy models.

## 8. Configuration reference (`.env`)

| Key | Meaning |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API key. Required for chat and Gemini TTS; the rest of the app works without it. |
| `GEMINI_CHAT_MODEL` | Gemini model used for conversation + action plans. |
| `GEMINI_TTS_MODEL` | Gemini model used for text-to-speech. |
| `GEMINI_TTS_VOICE` | Prebuilt Gemini TTS voice name (a calm one recommended). |
| `GOOGLE_APPLICATION_CREDENTIALS` | Unused in this build (Gemini TTS only — see `docs/DECISIONS.md`). |
| `TTS_PROVIDER` | `gemini` or `browser`. `browser` skips server-side TTS entirely. |
| `WHISPER_MODEL_SIZE` | `tiny` \| `base` \| `small`. Smaller = faster, less accurate. |
| `WHISPER_DEVICE` | `cpu` (or `cuda` if you have a GPU build of ctranslate2). |
| `SPACY_MODEL` | `en_core_web_lg` (default) or `en_core_web_sm` for low-memory machines. |
| `DATABASE_URL` | SQLAlchemy URL, default `sqlite:///./officemind.db`. |
| `JWT_SECRET` | Random secret for signing auth tokens. The app refuses to start without one. |
| `JWT_EXPIRE_MINUTES` | Access token lifetime. |
| `FLASK_SECRET_KEY` | Random secret for Flask's signed session cookie. |
| `BACKEND_URL` | Where Flask reaches FastAPI, default `http://127.0.0.1:8000`. |
| `FRONTEND_PORT` / `BACKEND_PORT` | Ports for each server. |
| `MAX_AUDIO_SECONDS` | Hard cap on a single voice recording. |
| `LOG_LEVEL` | Standard Python logging level. |

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| `faster-whisper` errors about missing codecs | Install `ffmpeg` and ensure it's on your `PATH`. |
| `OSError: [E050] Can't find model 'en_core_web_lg'` | Run `python -m spacy download en_core_web_lg`, or set `SPACY_MODEL=en_core_web_sm` in `.env` and download that instead. |
| Gemini call fails with a model-not-found error | Check `GEMINI_CHAT_MODEL` / `GEMINI_TTS_MODEL` in `.env` against the [current Gemini model list](https://ai.google.dev/gemini-api/docs/models) — model names aren't hard-coded. |
| Microphone button does nothing / permission blocked | The app falls back to text automatically with a notice. Make sure you're on `localhost`/`127.0.0.1` or HTTPS — browsers block mic access otherwise. |
| Whisper is slow on CPU | Set `WHISPER_MODEL_SIZE=tiny` or `base` in `.env`. |
| `GEMINI_API_KEY is not configured yet` (503) | Add your key to `.env` and restart the backend — every other screen still works without it. |

## 10. Project structure

```
techxconf/
├── README.md
├── .env.example / .env (gitignored)
├── .gitignore
├── requirements.txt
├── config.py
├── docs/
│   ├── OfficeMind_Requirements.md
│   ├── CLAUDE_CODE_PROMPT.md
│   └── DECISIONS.md
├── scripts/
│   ├── init_db.py
│   └── test_masking.py
├── backend/                   # FastAPI
│   ├── main.py
│   ├── db.py / models.py / schemas.py / auth.py
│   ├── routers/ (auth, preferences, sessions, chat)
│   ├── services/ (masking, llm, stt, tts, safety, context, session_store)
│   ├── data/questions.json
│   └── prompts/system_prompt.md
└── frontend/                  # Flask
    ├── app.py / api_client.py
    ├── templates/ (base, login, register, welcome, home, questions,
    │               companion, plan, profile, help, _icons)
    └── static/css/style.css, static/js/(questions.js, companion.js)
```

## 11. Known limitations

- Designed and tested as a single-process hackathon build — per-session
  conversation state lives in backend memory, so it doesn't survive a backend
  restart (saved action plans do, since those are in the database).
- See `docs/DECISIONS.md` for the full list of assumptions and the Presidio
  over-masking note.
- No automated test suite; correctness was verified by running each flow
  manually and with `scripts/test_masking.py`.
