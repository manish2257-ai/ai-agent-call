from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.models import User, UserSettings
from ..schemas.schemas import TestAlertRequest
from ..services.sms_service import SMSService
from .deps import get_db, get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("/test")
async def send_test_alert(
    req: TestAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    owner_number = settings.owner_phone_number if settings else "+19876543210"

    result = await SMSService.dispatch_urgent_sms(
        db=db,
        call_id=None,
        to_number=owner_number,
        caller=req.caller_name,
        caller_number=req.caller_number,
        urgency=req.urgency,
        reason=req.reason,
        summary=req.summary,
        user_settings=settings,
        bypass_cooldown=True  # manual test bypasses cooldown
    )

    return {
        "status": "success",
        "to_number": owner_number,
        "details": result
    }
