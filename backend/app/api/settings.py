from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.models import User, UserSettings
from ..schemas.schemas import UserSettingsSchema
from .deps import get_db, get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=UserSettingsSchema)
def get_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("", response_model=UserSettingsSchema)
def update_settings(settings_in: UserSettingsSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    for field, val in settings_in.dict().items():
        setattr(settings, field, val)

    db.commit()
    db.refresh(settings)
    return settings
