import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.models import User, Call, Contact
from .deps import get_db, get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
def get_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    calls = db.query(Call).filter(Call.user_id == current_user.id).all()
    total = len(calls)
    
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    week_start = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    
    calls_today = len([c for c in calls if c.created_at and c.created_at >= today_start])
    calls_this_week = len([c for c in calls if c.created_at and c.created_at >= week_start])
    
    urgency_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for c in calls:
        u = c.urgency if c.urgency in urgency_counts else "LOW"
        urgency_counts[u] += 1

    transferred = len([c for c in calls if c.status == "Transferred"])
    escalated = len([c for c in calls if c.status == "Escalated"])
    spam = len([c for c in calls if c.status == "Spam"])

    avg_duration = sum(c.duration_seconds for c in calls) // total if total > 0 else 0

    # Hourly distribution for today (mock/demo friendly)
    hourly = [
        {"hour": "9 AM", "count": 2},
        {"hour": "11 AM", "count": 4},
        {"hour": "1 PM", "count": 1},
        {"hour": "3 PM", "count": 5},
        {"hour": "5 PM", "count": 3}
    ]

    return {
        "total_calls": total,
        "calls_today": calls_today,
        "calls_this_week": calls_this_week,
        "average_duration_seconds": avg_duration,
        "urgency_distribution": urgency_counts,
        "transferred_calls": transferred,
        "escalated_calls": escalated,
        "spam_calls": spam,
        "hourly_breakdown": hourly
    }
