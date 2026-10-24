# OfficeMind — Project Requirements Document

**AI-powered workplace mental wellness companion**

| Field | Value |
|---|---|
| Document type | Project Requirements Document (PRD) |
| Project stage | Hackathon MVP |
| Status | Draft v1.1 (technical requirements added) |
| Primary interaction | Voice-first, with text fallback |

---

## 1. Overview

### 1.1 Product summary

OfficeMind is a voice-first AI companion that helps employees handle the small, everyday workplace situations that create anxiety, stress, self-doubt, and loneliness — before they build up into something larger.

It is not a therapist, manager, productivity tracker, or "stay positive" chatbot. It is a calm, non-judgmental companion that helps users understand their situation, feel heard, and leave with one realistic next step.

### 1.2 Problem statement

Workplace mental stress rarely starts with a major crisis. It often begins with ordinary moments: not knowing how to tell a manager about a mistake, being afraid to ask a basic question, struggling with a new tool, feeling isolated after joining a company, or receiving too much work. Existing wellness tools tend to offer generic advice that does not address the specific situation the person is facing.

### 1.3 Core product principle

Every session follows this flow:

> **Understand the situation → Reduce immediate stress → Clarify the problem → Practise the response → Take one manageable next step**

### 1.4 Value pillars

| Pillar | Description |
|---|---|
| Emotional support | Users feel heard without being judged. |
| Behavioural guidance | Users understand how to handle difficult situations. |
| Voice-first interaction | Users speak naturally instead of typing everything. |
| Practical next steps | Users leave with one realistic action to take. |

---

## 2. Goals and Non-Goals

### 2.1 Goals

- **G1.** Help users move from an emotionally difficult workplace moment to a clearer, more manageable situation within a single session.
- **G2.** Personalise support using structured context gathered before the conversation, so users do not have to repeat themselves.
- **G3.** Produce a concrete outcome in every completed session: a summary, suggested words, and one next step.
- **G4.** Provide a natural, low-friction voice experience with a reliable text alternative.
- **G5.** Recognise situations that need more than conversational support (harassment, discrimination, unsafe conditions, crisis) and point users to appropriate help.

### 2.2 Non-Goals

- Diagnosing mental health or medical conditions.
- Recommending medical treatment or medication.
- Replacing therapy, HR, legal advice, or crisis services.
- Monitoring employee productivity or reporting to employers.
- Training custom speech or language models (existing services will be used).

---

## 3. Target Users

| Persona | Description | Typical need |
|---|---|---|
| New joiner | Recently joined, unfamiliar with people, tools, and norms | Belonging, asking basic questions without fear |
| Early-career employee | Low confidence, fears judgment from managers | Admitting mistakes, speaking to a manager |
| Overloaded contributor | Too many tasks, working late, struggling with boundaries | Prioritisation, workload conversations |
| Anxious performer | Overthinks, anticipates failure, panics before meetings | Grounding, meeting preparation |
| Employee with personal circumstances | Health, caregiving, or life events affecting work | Privacy, accommodation conversations |

---

## 4. User Journey

| Step | Screen | Purpose |
|---|---|---|
| 0 | Login / Register | Basic account so preferences and saved plans link to a user ID |
| 1 | Welcome | Create a safe, private-feeling space to talk about work |
| 2 | Home (category selection) | Choose one of five workplace concerns |
| 3 | Guided questions | Three adaptive steps: context, feelings, desired help |
| 4 | Emotional check-in | Optional stress rating and feeling selection |
| 5 | Voice companion | Listen, reassure, clarify, and practise |
| 6 | Action plan | Summary, suggested words, one next step |
| 7 | Follow-up | Save privately, revisit plan, optional check-in |
| 8 | Help & safety | Support resources, crisis guidance, privacy settings |

**MVP scope:** Login/Register and Screens 1–6 are core. Screens 7–8 may be simplified, but basic safety and privacy controls must exist from the start.

---

## 5. Functional Requirements

Priority key: **P0** = required for MVP · **P1** = should have · **P2** = nice to have

### 5.1 Welcome Screen

| ID | Requirement | Priority |
|---|---|---|
| FR-1.1 | Display a friendly greeting and reassuring copy that sets a private, non-judgmental tone. | P0 |
| FR-1.2 | Provide a primary "Start talking" action that leads to the Home screen. | P0 |
| FR-1.3 | Display a brief privacy notice and link to Help & Safety. | P0 |

### 5.2 Home Screen — Category Selection

The home screen must show **exactly five category cards** plus an "Other concern" entry point. It must not become a crowded dashboard.

| ID | Requirement | Priority |
|---|---|---|
| FR-2.1 | Display five category cards with icon, title, and one-line description. | P0 |
| FR-2.2 | Each category exposes its list of related situations (see 5.2.1). | P0 |
| FR-2.3 | Provide a free-text / free-speech "Something else" option. | P0 |
| FR-2.4 | Selecting a category routes the user to its branching questions. | P0 |

#### 5.2.1 Category definitions

**1. Behaviour & Communication** — *Icon: speech bubbles*
Handle conversations, mistakes, uncertainty, and fear of judgment.
- How do I speak to my manager?
- I made a mistake. How do I admit it?
- I am new to Git or another tool. How do I tell my team?
- I am scared to ask a basic question.
- How do I handle a client meeting?
- How do I disagree respectfully or ask for feedback?

**2. Belonging & Workplace Relationships** — *Icon: users / heart-handshake*
Support people who feel alone, intimidated, excluded, or uncertain about relationships.
- I joined recently and feel lonely.
- Nobody talks to me after induction.
- I feel scared of my manager.
- I feel excluded from team conversations.
- I do not know how to approach colleagues.
- I am worried that my teammates judge me.

**3. Workload & Burnout** — *Icon: gauge / list-checks*
Manage overload, competing priorities, long hours, and boundaries.
- I have too many tickets to solve.
- I keep receiving extra work.
- I am working late every day.
- I cannot decide what to do first.
- I feel guilty taking a break.
- I cannot switch off after work.

**4. Anxiety, Pressure & Confidence** — *Icon: heart-pulse / cloud*
Help with overthinking, anticipating failure, and regaining composure.
- I have a client meeting and I am panicking.
- I keep thinking I will make a mistake.
- I feel anxious when my manager messages me.
- I am afraid of missing a deadline.
- I keep comparing myself with others.
- I cannot stop replaying a conversation in my head.

**5. Personal & Other Work Concerns** — *Icon: compass / life-buoy*
Flexible category, including personal circumstances affecting work.
- Personal health concerns affecting work.
- Difficulty balancing work and personal responsibilities.
- A concern about unfair treatment or workplace conflict.
- Returning to work after a difficult period.
- Feeling uncertain about career direction.
- Something else I cannot quite explain.

#### 5.2.2 Category design rules

- **Personal health concerns** (e.g. PCOS) belong under *Personal & Other Work Concerns*, with options to discuss workplace accommodations and privacy. The AI must not diagnose, recommend treatment, or assume the condition causes the user's feelings.
- **Bullying, harassment, discrimination, or unsafe conditions** must not be treated as anxiety or a communication problem. The app must help users recognise when documentation, HR, a trusted person, or a qualified professional may be appropriate.
- The category is a **starting point, not a permanent label**. If the conversation reveals a different issue, the AI responds to the actual issue.

### 5.3 Guided Questions — Three-Stage Branching System

The questions must feel like a gentle conversation, not a psychological assessment or survey.

| Stage | Goal | Example prompt |
|---|---|---|
| 1 · Context | What happened? | "What are you dealing with?" |
| 2 · Emotion | What is making it difficult? | "What is worrying you the most?" |
| 3 · Support | What help would be useful? | "What would help you most right now?" |

| ID | Requirement | Priority |
|---|---|---|
| FR-3.1 | Present three stages per session with a visible progress indicator. | P0 |
| FR-3.2 | Each answer determines the next question (branching, not fixed). | P0 |
| FR-3.3 | Each stage offers 4–5 tappable options including a "Something else" option. | P0 |
| FR-3.4 | Every stage can be skipped; users can describe their situation freely instead. | P0 |
| FR-3.5 | Answers are stored in the session context object (Section 7). | P0 |
| FR-3.6 | Final step offers "Continue to voice support" (and a text option). | P0 |

#### 5.3.1 Generic Stage 2 & 3 options (Behaviour & Communication)

*Stage 2 — What is worrying you most?*
I am afraid of being judged · I think I will disappoint someone · I do not know what to say · I am worried about the consequences · I cannot explain it, but I feel overwhelmed

*Stage 3 — What would help most right now?*
Help me calm down first · Tell me what I can do next · Help me find the right words · Practise the conversation with me · Let me talk and help me understand my feelings

#### 5.3.2 Example branch — "I made a mistake at work"

| Stage | Question | Options |
|---|---|---|
| 1 · Context | What happened? | I made a small error · I missed a deadline · I sent incorrect information · The impact is not clear yet |
| 2 · Emotion | What worries you most? | My manager will be angry · My team will lose trust in me · I do not know how to explain it · I feel panicked and cannot think clearly |
| 3 · Support | What would you like help with? | Calm down before I respond · Decide whether and how to report it · Draft a message to my manager · Practise what I should say |

### 5.4 Emotional Check-in

| ID | Requirement | Priority |
|---|---|---|
| FR-4.1 | Offer an optional stress rating (e.g. 1–10). | P1 |
| FR-4.2 | Offer optional feeling chips (e.g. anxious, overwhelmed, embarrassed, lonely). | P1 |
| FR-4.3 | Clearly label the check-in as self-reflection, not a clinical measurement. | P0 |
| FR-4.4 | A high stress rating should bias the AI toward stabilising first. | P1 |

### 5.5 Voice Companion

| ID | Requirement | Priority |
|---|---|---|
| FR-5.1 | Open the conversation by referencing the user's actual concern from context — no "tell me what's wrong" restart. | P0 |
| FR-5.2 | Support natural speech: pausing, interrupting, and changing subject. | P0 |
| FR-5.3 | Show a live transcript of both user and AI turns. | P0 |
| FR-5.4 | Clearly indicate when the microphone is active. | P0 |
| FR-5.5 | Provide controls: mute mic, stop AI speaking, end session, switch to text. | P0 |
| FR-5.6 | AI responses are short and conversational; no long paragraphs spoken to a distressed user. | P0 |
| FR-5.7 | If speech recognition fails, the AI says so rather than pretending to understand. | P0 |
| FR-5.8 | Fall back to text automatically if mic permission or speech services fail. | P0 |
| FR-5.9 | Session context (answers + conversation) persists throughout the session. | P0 |

### 5.6 Action Plan (Outcome Screen)

The session must never end with only "I hope you feel better."

| ID | Requirement | Priority |
|---|---|---|
| FR-6.1 | **What we understood** — a short, neutral summary of the situation. | P0 |
| FR-6.2 | **Words you can use** — a ready-to-use script or message draft. | P0 |
| FR-6.3 | **One manageable next step** — a single concrete action. | P0 |
| FR-6.4 | **How are you feeling now?** — optional: A little calmer / Clearer about what to do / I need more support. | P0 |
| FR-6.5 | Selecting "I need more support" surfaces Help & Safety resources and the option to continue talking. | P0 |
| FR-6.6 | Copy-to-clipboard for the suggested words. | P1 |

**Example outcome**

> **What we understood:** You are worried about how your manager will react to a mistake, but you have identified a way to correct it.
>
> **Words you can use:** "I noticed an error in the ticket and am correcting it. I'll verify the information and update you if anything else needs attention."
>
> **One manageable next step:** Check the ticket, correct the information if you can, and follow your team's reporting process if the error has wider consequences.

### 5.7 Follow-up

| ID | Requirement | Priority |
|---|---|---|
| FR-7.1 | Save action plan privately (opt-in). | P1 |
| FR-7.2 | Revisit saved plans. | P1 |
| FR-7.3 | Optional user-scheduled check-in reminder. | P2 |

### 5.8 Help & Safety

| ID | Requirement | Priority |
|---|---|---|
| FR-8.1 | Accessible from every screen. | P0 |
| FR-8.2 | List support resources and crisis guidance relevant to the user's region. | P0 |
| FR-8.3 | Privacy settings: view, export, and delete session data. | P0 |
| FR-8.4 | Explain when HR, documentation, a trusted person, or a professional may be appropriate. | P1 |

### 5.9 Authentication (Basic)

| ID | Requirement | Priority |
|---|---|---|
| FR-9.1 | Register with username (or email), password, and optional display name. Real names are not required. | P0 |
| FR-9.2 | Login and logout. Passwords stored only as salted hashes (bcrypt). | P0 |
| FR-9.3 | All app screens except Login/Register require an authenticated session. | P0 |
| FR-9.4 | Backend requests are authenticated with a signed token issued at login. | P0 |
| FR-9.5 | User can delete their account and all linked data. | P0 |

### 5.10 User Profile & Preference Module ("Character Building")

A small module that stores lightweight metadata about the user so the companion can adapt its tone and avoid upsetting language over time. All records link to the account by `user_id`.

| ID | Requirement | Priority |
|---|---|---|
| FR-10.1 | Store **likes** (e.g. "short answers", "practising out loud", "humour"). | P0 |
| FR-10.2 | Store **dislikes** (e.g. "breathing exercises", "long explanations"). | P0 |
| FR-10.3 | Store **word triggers**: words or phrases the AI must avoid or handle gently. | P0 |
| FR-10.4 | Store **preferences**: preferred tone (gentle / direct), response length, voice on/off by default. | P1 |
| FR-10.5 | User can view, add, edit, and delete every item from a simple Profile screen. | P0 |
| FR-10.6 | The AI may *suggest* a new like/dislike at the end of a session; it is saved only if the user confirms. | P1 |
| FR-10.7 | Preference text is passed through PII masking before it is saved. No personal identifiers are stored here. | P0 |
| FR-10.8 | Preferences are injected into the LLM system prompt for every session. | P0 |

---

## 6. AI Behaviour Requirements

### 6.1 Persona

Calm, warm, non-judgmental workplace companion. Grounded in facts, focused on the user's agency.

### 6.2 Conversation sequence

| Step | Behaviour |
|---|---|
| 1. Acknowledge | Recognise the user's actual concern without exaggerating it. |
| 2. Stabilise | If overwhelmed, offer a brief grounding exercise or slower pace. |
| 3. Clarify | Ask one useful question at a time, only when needed. |
| 4. Reframe | Separate what happened from what the user fears might happen. |
| 5. Guide | Offer practical, realistic options for the workplace situation. |
| 6. Practise | Draft a message, rehearse a conversation, or prepare for a meeting. |
| 7. Close | Ask what feels manageable and agree on one next step. |

### 6.3 The AI must

- Validate concerns proportionately.
- Stay grounded in facts the user has shared.
- Ask at most one question per turn.
- Respect the support type the user chose in Stage 3.
- Adapt if the real issue differs from the selected category.

### 6.4 The AI must not

- Say "everything will be fine" or offer false reassurance.
- Diagnose anxiety, depression, or any medical condition.
- Recommend treatment or medication.
- Criticise or speculate about the manager or colleagues.
- Lecture the user about confidence or positivity.
- Frame harassment, discrimination, or unsafe conditions as the user's communication problem.

### 6.5 Category-specific instructions

| Category | Special instruction | Expected output |
|---|---|---|
| Behaviour & Communication | Help the user communicate clearly without shame | Suggested words, message drafts, role-play |
| Belonging & Relationships | Explore loneliness and social uncertainty without assuming the user's interpretation is always correct | Low-pressure ways to connect, boundary-setting, support options |
| Workload & Burnout | Clarify capacity, priorities, dependencies, and boundaries | Prioritisation, manager scripts, workload discussion |
| Anxiety, Pressure & Confidence | Focus on immediate overwhelm, uncertainty, and realistic next steps | Grounding, thought clarification, meeting preparation |
| Personal & Other Concerns | Respect privacy; distinguish workplace guidance from medical/specialist advice | Practical options, accommodation conversations, referrals |

### 6.6 Reference conversation

> **User:** I made a mistake in a ticket. My manager might think I am incompetent. I am really scared.
>
> **OfficeMind:** That sounds stressful, especially when you are worried about how your manager will see you. Let's take this one step at a time. You don't have to figure out the entire conversation right now. Can we first separate two things: what actually happened with the ticket, and what you are afraid your manager might think?
>
> **User:** I entered the wrong information, but I think I can correct it.
>
> **OfficeMind:** Okay. So there is a specific error, and you already have a possible correction. That gives us somewhere to start. We don't know yet how your manager will react, so let's focus on what you can control. You could say: "I noticed that I entered incorrect information in the ticket. I'm correcting it now and will verify the details before closing it." Would you like to practise saying that, or is there something about the mistake we should understand first?

---

## 7. Session Context Schema

Before voice chat begins, the app builds a structured context object and passes it to the LLM.

```json
{
  "category": "behaviour_communication",
  "specific_situation": "mistake_at_work",
  "situation_details": "Entered incorrect information in a ticket",
  "main_worry": "Manager may think I am incompetent",
  "desired_support": "Help me prepare what to say",
  "initial_stress_level": 8,
  "preferred_interaction": "voice",
  "conversation_stage": "support"
}
```

*Values are illustrative.*

| Field | Type | Required | Notes |
|---|---|---|---|
| `category` | enum | Yes | One of five categories or `other` |
| `specific_situation` | string | No | From Stage 1 |
| `situation_details` | string | No | Free text if provided |
| `main_worry` | string | No | From Stage 2 |
| `desired_support` | string | No | From Stage 3 |
| `initial_stress_level` | integer 1–10 | No | From check-in |
| `preferred_interaction` | enum `voice`/`text` | Yes | |
| `conversation_stage` | enum | Yes | Tracks position in the 7-step sequence |

**Rules:** Context is guidance, not diagnosis or a rigid script. Missing fields are acceptable; the AI asks a follow-up only when an important detail is missing.

---

## 8. System Architecture

### 8.1 Layers

```
┌───────────────────────────────────────────────────────────┐
│ Frontend: Welcome · Categories · Questions · Voice · Plan │
└───────────────────────────┬───────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│ Conversation Orchestrator                                 │
│ (category + answers + emotional context + session state)  │
└──────────────┬──────────────────────────────┬─────────────┘
               │                              │
┌──────────────▼──────────────┐ ┌─────────────▼─────────────┐
│ LLM Engine                  │ │ Voice Engine              │
│ dialogue, guidance, scripts │ │ STT · TTS · realtime      │
└──────────────┬──────────────┘ └─────────────┬─────────────┘
               │                              │
┌──────────────▼──────────────────────────────▼─────────────┐
│ Safety, Privacy & Session Management                      │
│ sensitive content · consent · data controls · escalation  │
└───────────────────────────────────────────────────────────┘
```

### 8.2 Modules

| Module | Responsibility |
|---|---|
| Category selector | Routes the user into the right topic |
| Question engine | Serves the three stages and adapts follow-ups |
| Context builder | Assembles the session context object |
| Conversation engine | Generates empathetic, practical responses |
| Voice adapter | Microphone input and spoken output |
| Guidance engine | Generates scripts, options, and action plans |
| Safety layer | Detects urgent safety concerns and harmful advice |
| Session manager | Maintains conversation context and preferences |
| Privacy controls | Consent, deletion, and optional saving |

| PII masking layer | Masks personal and incident-identifying data before any LLM call |
| Auth module | Register, login, token issue/verify |
| Preference module | Likes, dislikes, triggers, tone; linked to `user_id` |

For the hackathon, these may be logical modules within a single application rather than separate services.

### 8.3 Technology Stack

Keep the stack minimal. No additional frameworks beyond those listed.

| Layer | Choice | Notes |
|---|---|---|
| Frontend | **Flask** + Jinja templates, plain HTML/CSS/vanilla JS | Server-rendered pages; JS only for recording audio and chat. No React/Vue/Tailwind build steps. |
| Backend | **FastAPI** | REST API for auth, sessions, chat, voice, preferences |
| Database | **SQLite** via **SQLAlchemy** ORM | Fresh DB created by an init script; ORM chosen so a future move to Postgres/Alembic is straightforward |
| LLM | **Gemini API** (`google-genai` SDK) | Model names set in config, not hard-coded |
| Speech-to-text | **Whisper** (local, `faster-whisper`) | Raw voice stays on the server and never goes to a third party |
| Text-to-speech | **Google / Gemini TTS** | Browser `speechSynthesis` as a fallback |
| PII masking | **Microsoft Presidio** (analyzer + anonymizer, spaCy model) | Runs on all user text before the LLM |
| Config | Single `config` module reading a `.env` file | All API keys, model names, feature flags, paths |
| Version control | Git, local commits per build stage | No remote push required |

### 8.4 Request Flow (Voice and Text)

```
Browser (Flask page)
  │  text, or recorded audio (MediaRecorder → webm/ogg)
  ▼
Flask route  ──(server-to-server, bearer token)──▶  FastAPI
                                                      │
                                   audio? ──▶ Whisper STT (local)
                                                      │ raw text
                                                      ▼
                                          Presidio masking layer
                                    (raw text → masked text + mapping)
                                                      │ masked text only
                                                      ▼
                                    Gemini LLM  (system prompt + context
                                    + preferences + masked history)
                                                      │ masked reply
                                                      ▼
                                 Re-identify for on-screen transcript only
                                 Generic phrasing ("your manager") for TTS
                                                      │
                                                      ▼
                                          Google/Gemini TTS → audio
  ◀───────────────────────── reply text + audio ──────┘
```

The masking mapping lives **in server memory for the session only** and is never written to the database or sent to any external service.

### 8.5 Data Model (minimum)

| Table | Key fields |
|---|---|
| `users` | `id`, `username`, `password_hash`, `display_name`, `created_at` |
| `user_preferences` | `id`, `user_id` (FK), `kind` (`like` / `dislike` / `trigger` / `setting`), `value`, `created_at` |
| `sessions` | `id`, `user_id` (FK), `category`, `context_json` (masked), `started_at`, `ended_at`, `feeling_after` |
| `action_plans` | `id`, `session_id` (FK), `user_id` (FK), `summary`, `suggested_words`, `next_step` (all masked), `saved` |

Raw transcripts are **not stored** by default. Only masked action plans are stored, and only when the user chooses to save.

---

## 9. Safety and Privacy Requirements

| ID | Requirement | Priority |
|---|---|---|
| SR-1 | Detect signals of self-harm, crisis, or immediate danger and switch to crisis guidance with region-appropriate resources. | P0 |
| SR-2 | Detect harassment, bullying, discrimination, or unsafe conditions and surface documentation, HR, trusted-person, and professional options. | P0 |
| SR-3 | Filter AI output for diagnosis, treatment advice, or harmful guidance. | P0 |
| SR-4 | Obtain explicit consent before saving any session data. Default is not to save. | P0 |
| SR-5 | Allow users to delete all stored data at any time. | P0 |
| SR-6 | Never share data with employers. State this clearly in the UI. | P0 |
| SR-7 | Do not make categorical promises about confidentiality of third-party crisis services. | P0 |
| SR-8 | Encrypt stored data at rest and in transit. | P1 |
| SR-9 | All user text (typed, transcribed, guided-question free text, preference text) passes through Presidio **before** any LLM call or database write. | P0 |
| SR-10 | Mask standard PII: names, emails, phone numbers, locations, dates, IDs, URLs, IP addresses, credit card and government ID numbers. | P0 |
| SR-11 | Mask **incident-identifying details** that could tie a story to a specific person or company: organisation and client names, project/product codenames, ticket or case IDs (e.g. `JIRA-1234`, `INC0012345`), job titles combined with names, specific monetary figures, and exact dates/times. Implemented with custom Presidio recognizers (regex + deny-lists). | P0 |
| SR-12 | Each user may add private "always mask" terms (e.g. their company or team name), applied via a per-user deny-list recognizer. | P1 |
| SR-13 | Use consistent placeholders within a session (`<PERSON_1>`, `<ORG_1>`) so the LLM can still reason about who is who. | P0 |
| SR-14 | Never log raw user text or audio. Logs contain masked text only. Temporary audio files are deleted immediately after transcription. | P0 |
| SR-15 | API keys live only in `.env`, which is git-ignored; a `.env.example` is committed instead. | P0 |

---

## 10. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Latency | Voice response begins within ~1.5 seconds of the user finishing speaking (target). |
| NFR-2 | Reliability | Text fallback available whenever voice fails. |
| NFR-3 | Accessibility | Transcript always visible; keyboard and screen-reader support; adjustable speech rate. |
| NFR-4 | Tone | All UI copy reviewed for calm, non-clinical, non-judgmental language. |
| NFR-5 | Devices | Mobile-first. On a phone the app fills the screen like a native app. On a desktop browser the app renders inside a centred phone-sized frame (≈ 390–430 px wide, ≈ 844–900 px tall, rounded corners) rather than stretching. |
| NFR-7 | Touch | Tap targets ≥ 44 px; bottom-anchored mic and send controls reachable by thumb. |
| NFR-8 | Simplicity | No frontend build tooling; no extra frameworks beyond the stack in 8.3. |
| NFR-6 | Simplicity | Guided questions take under one minute to complete. |

---

## 11. MVP Scope

### In scope

- Welcome, Home, Guided Questions, Emotional Check-in, Voice Companion, Action Plan (Screens 1–6)
- Branching questions for all five categories (at least one full branch per category)
- Existing STT/TTS or realtime voice API
- Text fallback
- Basic Help & Safety screen and crisis detection
- Consent-based saving and delete-all control
- Basic login/register and the Preferences ("character building") module
- Presidio masking with custom incident-identifying recognizers
- Phone-framed layout on desktop, full-screen on mobile
- README with setup instructions

### Out of scope (post-hackathon)

- Scheduled check-in reminders
- Multi-language support
- Employer/organisation dashboards
- Long-term mood tracking or analytics
- Custom-trained speech models

---

## 12. Success Metrics

| Metric | Target (MVP demo) |
|---|---|
| Sessions reaching the Action Plan screen | ≥ 70% |
| Users selecting "A little calmer" or "Clearer about what to do" | ≥ 60% |
| Time from Welcome to voice conversation | < 90 seconds |
| AI responses violating "must not" rules in test set | 0 |
| Crisis-scenario test cases routed to safety guidance | 100% |

---

## 13. Acceptance Criteria (Demo)

1. A user can pick a category, answer or skip three adaptive questions, and start a voice conversation in under 90 seconds.
2. The AI's first turn references the user's selected concern without asking them to repeat it.
3. The AI follows the 7-step sequence and asks no more than one question per turn.
4. Every completed session produces a summary, suggested words, and one next step.
5. Denying mic permission results in a working text conversation.
6. A message describing harassment is not treated as a confidence issue and surfaces appropriate support options.
7. A message indicating crisis triggers safety guidance immediately.
8. Users can delete their data from the privacy settings.

---

## 14. Open Questions

- Which Gemini model versions to pin for chat and TTS at build time?
- Whisper model size (`base` vs `small`) — trade-off between speed and accuracy on the demo machine.
- Which regions' crisis resources should be included in the MVP?
- How will the safety layer be evaluated before the demo (test prompt set, manual review)?
- Should users be able to change category mid-conversation explicitly, or only implicitly via the AI?

---

## 15. Development Process

| ID | Requirement |
|---|---|
| DP-1 | One `config.py` reads all keys, model names, paths, and feature flags from `.env`. No secrets in code. |
| DP-2 | `scripts/init_db.py` creates a fresh SQLite database from the SQLAlchemy models (and can reset it). |
| DP-3 | Make a local Git commit at the end of each build stage with a clear message (e.g. `stage 3: presidio masking layer`). |
| DP-4 | `README.md` covers: overview, architecture, prerequisites, setup, `.env` keys, DB init, running both servers, testing masking, and troubleshooting. |
| DP-5 | Keep it simple and fully working: prefer fewer files and plain code over abstractions. |
