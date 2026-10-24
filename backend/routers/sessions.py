import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from backend.db import get_db
from backend.models import User, Session as SessionModel, ActionPlan, UserPreference
from backend.schemas import (
    SessionStartRequest, SessionStartResponse, SessionEndRequest,
    ActionPlanResponse, SavePlanRequest,
)
from backend.auth import get_current_user
from backend.services import session_store, llm, masking
from backend.services.context import build_system_instruction, opening_message_hint

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _mask_term_list(db: DbSession, user_id: int) -> list[str]:
    rows = db.query(UserPreference).filter(
        UserPreference.user_id == user_id, UserPreference.kind == "mask_term"
    ).all()
    return [r.value for r in rows]


@router.post("/start", response_model=SessionStartResponse)
def start_session(
    req: SessionStartRequest, user: User = Depends(get_current_user), db: DbSession = Depends(get_db)
):
    context = req.context.model_dump()
    db_session = SessionModel(user_id=user.id, category=context["category"], context_json=None)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    mask_terms = _mask_term_list(db, user.id)
    for field in ("specific_situation", "situation_details", "main_worry", "desired_support"):
        if context.get(field):
            context[field] = masking.mask_text(
                context[field], session_id=str(db_session.id), user_mask_terms=mask_terms
            ).masked_text

    db_session.context_json = json.dumps(context)
    db.commit()

    session_store.start(db_session.id, context, user.id)

    preferences = db.query(UserPreference).filter(UserPreference.user_id == user.id).all()
    system_instruction = build_system_instruction(context, preferences)
    hint = opening_message_hint(context)

    try:
        opening = llm.generate_reply(system_instruction, history=[], user_message=hint)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured yet.")
    except Exception:
        opening = "I'm here with you. Tell me a bit more about what's going on, whenever you're ready."

    session_store.append_turn(db_session.id, "model", opening, masking.unmask_for_display(opening, str(db_session.id)))

    return SessionStartResponse(
        session_id=db_session.id,
        opening_message=masking.unmask_for_display(opening, str(db_session.id)),
    )


@router.post("/{session_id}/end", response_model=ActionPlanResponse)
def end_session(
    session_id: int, req: SessionEndRequest,
    user: User = Depends(get_current_user), db: DbSession = Depends(get_db),
):
    db_session = db.get(SessionModel, session_id)
    if not db_session or db_session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    state = session_store.get(session_id)
    if state is None:
        raise HTTPException(status_code=400, detail="Session already ended or not started")

    preferences = db.query(UserPreference).filter(UserPreference.user_id == user.id).all()
    context = json.loads(db_session.context_json) if db_session.context_json else {}
    system_instruction = build_system_instruction(context, preferences)

    try:
        plan = llm.generate_action_plan(system_instruction, state["history"])
    except Exception:
        plan = {
            "summary": "We talked through your situation together.",
            "suggested_words": "",
            "next_step": "Take one small step when you're ready.",
            "suggested_preference": None,
        }

    sid = str(session_id)
    action_plan = ActionPlan(
        session_id=session_id,
        user_id=user.id,
        summary=plan["summary"],
        suggested_words=plan["suggested_words"],
        next_step=plan["next_step"],
        saved=False,
    )
    db.add(action_plan)

    import datetime
    db_session.ended_at = datetime.datetime.utcnow()
    db_session.feeling_after = req.feeling_after
    db.commit()
    db.refresh(action_plan)

    response = ActionPlanResponse(
        session_id=session_id,
        summary=masking.unmask_for_display(plan["summary"], sid),
        suggested_words=masking.unmask_for_display(plan["suggested_words"], sid),
        next_step=masking.unmask_for_display(plan["next_step"], sid),
        suggested_preference=plan.get("suggested_preference"),
    )

    session_store.end(session_id)
    masking.clear_session(sid)
    return response


@router.post("/{session_id}/feeling")
def set_feeling(session_id: int, req: SessionEndRequest, user: User = Depends(get_current_user), db: DbSession = Depends(get_db)):
    db_session = db.get(SessionModel, session_id)
    if not db_session or db_session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    db_session.feeling_after = req.feeling_after
    db.commit()
    return {"feeling_after": db_session.feeling_after}


@router.post("/plan/save")
def save_plan(req: SavePlanRequest, user: User = Depends(get_current_user), db: DbSession = Depends(get_db)):
    plan = db.query(ActionPlan).filter(ActionPlan.session_id == req.session_id).first()
    if not plan or plan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Action plan not found")
    plan.saved = req.save
    db.commit()
    return {"saved": plan.saved}


@router.get("/plans")
def list_saved_plans(user: User = Depends(get_current_user), db: DbSession = Depends(get_db)):
    plans = db.query(ActionPlan).filter(ActionPlan.user_id == user.id, ActionPlan.saved == True).all()  # noqa: E712
    return [
        {
            "session_id": p.session_id,
            "summary": p.summary,
            "suggested_words": p.suggested_words,
            "next_step": p.next_step,
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ]
