from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from backend.db import get_db
from backend.models import User, UserPreference
from backend.schemas import PreferenceCreate, PreferenceResponse
from backend.auth import get_current_user
from backend.services.masking import mask_text

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=list[PreferenceResponse])
def list_preferences(user: User = Depends(get_current_user), db: DbSession = Depends(get_db)):
    prefs = db.query(UserPreference).filter(UserPreference.user_id == user.id).all()
    return [PreferenceResponse(id=p.id, kind=p.kind, value=p.value) for p in prefs]


@router.post("", response_model=PreferenceResponse)
def create_preference(
    req: PreferenceCreate, user: User = Depends(get_current_user), db: DbSession = Depends(get_db)
):
    value = req.value
    if req.kind != "mask_term":
        value = mask_text(value, session_id=f"user-{user.id}-pref").masked_text
    pref = UserPreference(user_id=user.id, kind=req.kind, value=value)
    db.add(pref)
    db.commit()
    db.refresh(pref)
    return PreferenceResponse(id=pref.id, kind=pref.kind, value=pref.value)


@router.delete("/{pref_id}")
def delete_preference(pref_id: int, user: User = Depends(get_current_user), db: DbSession = Depends(get_db)):
    pref = db.get(UserPreference, pref_id)
    if not pref or pref.user_id != user.id:
        raise HTTPException(status_code=404, detail="Preference not found")
    db.delete(pref)
    db.commit()
    return {"deleted": True}
