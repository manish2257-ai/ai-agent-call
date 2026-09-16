import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.models import User, UserSettings, Call, SmsAlert
from ..schemas.schemas import DashboardStats
from .deps import get_db, get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardStats)
def get_dashboard_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)

    calls = db.query(Call).filter(Call.user_id == current_user.id).all()
    total_calls = len(calls)
    calls_today = len([c for c in calls if c.created_at and c.created_at >= today_start])
    urgent_calls = len([c for c in calls if c.urgency in ("HIGH", "CRITICAL")])
    missed_calls = len([c for c in calls if c.status in ("Missed", "Failed")])

    avg_duration = 0
    if total_calls > 0:
        avg_duration = sum(c.duration_seconds for c in calls) // total_calls

    last_call = db.query(Call).filter(Call.user_id == current_user.id).order_by(Call.created_at.desc()).first()
    last_urgent_alert = db.query(SmsAlert).order_by(SmsAlert.created_at.desc()).first()

    last_call_dict = None
    if last_call:
        last_call_dict = {
            "id": last_call.id,
            "caller_name": last_call.caller_name,
            "caller_number": last_call.caller_number,
            "urgency": last_call.urgency,
            "reason": last_call.reason or "Routine check",
            "time": last_call.created_at.strftime("%I:%M %p") if last_call.created_at else ""
        }

    last_alert_dict = None
    if last_urgent_alert:
        last_alert_dict = {
            "to_number": last_urgent_alert.to_number,
            "urgency": last_urgent_alert.urgency,
            "status": last_urgent_alert.status,
            "time": last_urgent_alert.created_at.strftime("%I:%M %p") if last_urgent_alert.created_at else ""
        }

    return {
        "is_agent_enabled": settings.is_agent_enabled,
        "ai_phone_number": settings.ai_phone_number or "+18005550199",
        "calls_today": calls_today,
        "total_calls": total_calls,
        "urgent_calls": urgent_calls,
        "missed_calls": missed_calls,
        "avg_duration_seconds": avg_duration,
        "last_call": last_call_dict,
        "last_urgent_alert": last_alert_dict
    }

@router.post("/toggle-agent")
def toggle_agent(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    settings.is_agent_enabled = not settings.is_agent_enabled
    db.commit()
    return {"is_agent_enabled": settings.is_agent_enabled}
