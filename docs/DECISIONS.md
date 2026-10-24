# Build Decisions & Assumptions

Notes on ambiguous points in the requirements doc, resolved with the simplest
option that satisfies it, per `docs/CLAUDE_CODE_PROMPT.md` Section 0.

1. **Project root, not a nested `officemind/` folder.** The build prompt's
   example layout nests everything under `officemind/`. This folder already
   contained the venv and both doc files at its root, so the whole app (backend/,
   frontend/, scripts/, docs/) was built directly at the repo root instead.
   Structure otherwise matches Section 3 exactly.

2. **Python 3.14 venv, not 3.11.** The provided venv is Python 3.14. Per the
   user's instruction, we used it as-is rather than creating a new 3.11 venv.
   All pinned dependencies (FastAPI, Flask, SQLAlchemy, google-genai,
   faster-whisper, presidio-analyzer/anonymizer, spaCy + en_core_web_lg)
   installed and ran cleanly with no compatibility issues encountered.

3. **`GEMINI_API_KEY` is checked lazily, not at startup.** `config.py` fails
   fast on a missing `JWT_SECRET` (a one-time setup value), but
   `GEMINI_API_KEY` is checked only when a Gemini call is actually about to be
   made (`config.require_llm_config()`, raising `RuntimeError`, caught by the
   relevant routes as a 503). This lets the rest of the app — auth, DB, phone
   UI, guided questions, masking — run and be demoed before a key is added,
   per the user's request to add the key later.

4. **Guided questions + emotional check-in are one client-side flow.**
   `questions.html` / `questions.js` drive stages 1–3 and the check-in as a
   single state machine instead of a separate `checkin.html` page, so
   branching, skip, and progress logic live in one place. Functionally
   equivalent to Screens 3–4 in the requirements doc.

5. **Preference "settings" (tone / reply length / voice default) accumulate
   as new rows** rather than being upserted in place (kept as a single
   `user_preferences` table per the fixed schema). `context.py`'s dict
   comprehension takes the most recently added value per setting key, so
   behaviour is correct, but old rows aren't pruned. Acceptable for hackathon
   scope; a unique constraint + upsert would be the production fix.

6. **"Export data" (part of FR-8.3)** is satisfied by viewing saved action
   plans on the Help & Safety page rather than a separate export file —
   raw transcripts are never stored by design (SR-14), so there is nothing
   else to export beyond plans the user already chose to save.

7. **Google Cloud TTS (`GOOGLE_APPLICATION_CREDENTIALS`) is not implemented**
   as a third TTS path. Only Gemini TTS and the browser `speechSynthesis`
   fallback are wired up, matching the two providers in `TTS_PROVIDER`.

8. **Scheduled check-in reminders (FR-7.3)** are out of scope, per the
   requirements doc's own "Out of scope (post-hackathon)" list.

## Known gaps / follow-ups

- Presidio's NLP-based NER occasionally over-masks acronyms that look like
  names or orgs (e.g. "PAN", "SSN" literal words get flagged as ORGANIZATION
  alongside the correctly-masked ID itself). This is over-masking, not
  under-masking, so it errs on the safe side for privacy but is cosmetically
  imperfect. Verified against `scripts/test_masking.py`.
- `faster-whisper` downloads its model from Hugging Face on first run;
  subsequent backend starts are faster once cached.
