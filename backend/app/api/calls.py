import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..models.models import User, Call, CallSummary, CallTranscript, CallMessage, Contact, UserSettings
from ..schemas.schemas import CallSchema, SimulatedCallRequest
from ..services.call_manager import CallManager
from .deps import get_db, get_current_user

router = APIRouter(prefix="/calls", tags=["Calls"])

@router.get("", response_model=List[CallSchema])
def list_calls(
    filter_timeframe: Optional[str] = Query(None, description="today, yesterday, week, month"),
    urgency: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Call).filter(Call.user_id == current_user.id)

    if urgency:
        query = query.filter(Call.urgency == urgency.upper())

    if search:
        s = f"%{search}%"
        query = query.filter((Call.caller_name.ilike(s)) | (Call.caller_number.ilike(s)) | (Call.reason.ilike(s)))

    if filter_timeframe == "today":
        start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        query = query.filter(Call.created_at >= start)
    elif filter_timeframe == "yesterday":
        yest = datetime.date.today() - datetime.timedelta(days=1)
        start = datetime.datetime.combine(yest, datetime.time.min)
        end = datetime.datetime.combine(yest, datetime.time.max)
        query = query.filter(Call.created_at >= start, Call.created_at <= end)
    elif filter_timeframe == "week":
        week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        query = query.filter(Call.created_at >= week_ago)

    calls = query.order_by(Call.created_at.desc()).all()
    return calls

@router.get("/{call_id}", response_model=CallSchema)
def get_call_details(call_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.id == call_id, Call.user_id == current_user.id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    return call

@router.post("/{call_id}/transfer")
def transfer_call(call_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.id == call_id, Call.user_id == current_user.id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    call.status = "Transferred"
    db.commit()
    return {"status": "success", "message": f"Call {call_id} successfully transferred to owner phone."}

@router.post("/{call_id}/mark-urgent")
def mark_call_urgent(call_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.id == call_id, Call.user_id == current_user.id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    call.urgency = "HIGH"
    call.status = "Escalated"
    db.commit()
    return {"status": "success", "message": f"Call {call_id} marked as HIGH urgency."}

@router.delete("/{call_id}")
def delete_call(call_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    call = db.query(Call).filter(Call.id == call_id, Call.user_id == current_user.id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    db.delete(call)
    db.commit()
    return {"status": "success", "message": "Call deleted."}

@router.delete("")
def delete_all_calls(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Call).filter(Call.user_id == current_user.id).delete()
    db.commit()
    return {"status": "success", "message": "All call history purged successfully."}

@router.post("/simulate")
async def simulate_call(
    payload: SimulatedCallRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scenarios = {
        "website_outage": {
            "name": "Rahul",
            "number": "+919876543210",
            "messages": [
                {"speaker": "AI", "content": "Hello, you've reached Manish's AI assistant. Manish isn't available right now. How can I help you?"},
                {"speaker": "Caller", "content": "Hello, this is Rahul. The website is down and customers can't place orders! We need this fixed immediately."},
                {"speaker": "AI", "content": "I understand the urgency regarding the website outage and ordering failure. I am flagging this as HIGH priority and immediately notifying Manish via SMS alert."},
                {"speaker": "Caller", "content": "Thank you, please make sure he calls me back as soon as he sees it."},
                {"speaker": "AI", "content": "Will do Rahul. I have dispatched the alert. Have a good day."}
            ]
        },
        "general_enquiry": {
            "name": "Priya Sharma",
            "number": "+919811223344",
            "messages": [
                {"speaker": "AI", "content": "Hello, you've reached Manish's AI assistant. How can I help?"},
                {"speaker": "Caller", "content": "Hi! I wanted to check what Manish's working hours are and if he is available for a design consultation next week."},
                {"speaker": "AI", "content": "Manish's office hours are Monday to Friday 9:00 AM to 6:00 PM. I can take a message and pass along your consultation request."},
                {"speaker": "Caller", "content": "That would be great, my name is Priya. Thanks!"}
            ]
        },
        "client_contract": {
            "name": "Vikram Sethi",
            "number": "+919844556677",
            "messages": [
                {"speaker": "AI", "content": "Hello, you've reached Manish's AI assistant. How can I help?"},
                {"speaker": "Caller", "content": "Hi, Vikram here from Acme Corp. We have our contract deadline today and need Manish's sign-off before 4 PM."},
                {"speaker": "AI", "content": "Understood Vikram. Since the contract deadline is today, I'm escalating this to Manish right away."},
                {"speaker": "Caller", "content": "Perfect, please do."}
            ]
        },
        "vip_family": {
            "name": "Ananya (Family)",
            "number": "+919877665544",
            "messages": [
                {"speaker": "AI", "content": "Hello! You have reached Manish's AI assistant."},
                {"speaker": "Caller", "content": "Hey, it's Ananya. Manish isn't picking up his direct line. Can you please connect me or send him an urgent ping?"},
                {"speaker": "AI", "content": "Hi Ananya! I recognize you from the VIP list. I am alerting Manish right now on his priority phone."}
            ]
        },
        "spam_marketing": {
            "name": "QuickLoan Services",
            "number": "+919800000001",
            "messages": [
                {"speaker": "AI", "content": "Hello, you've reached Manish's AI assistant. How can I help?"},
                {"speaker": "Caller", "content": "Congratulations Sir! You are pre-approved for a personal loan of 10 Lakhs at 8% interest. Would you like to apply?"},
                {"speaker": "AI", "content": "Manish does not accept unsolicited loan promotions. Thank you and goodbye."}
            ]
        },
        "emergency": {
            "name": "Neighbor Alert",
            "number": "+919899887766",
            "messages": [
                {"speaker": "AI", "content": "Hello, you've reached Manish's AI assistant. How can I help?"},
                {"speaker": "Caller", "content": "There is smoke coming out of the apartment hallway downstairs, need to check if everyone is okay!"},
                {"speaker": "AI", "content": "If there is fire or smoke, please call 112 / 911 emergency services immediately! I am also alerting Manish right away."}
            ]
        }
    }

    sc = scenarios.get(payload.scenario_id, scenarios["website_outage"])
    caller_name = payload.caller_name or sc["name"]
    caller_number = payload.caller_number or sc["number"]
    messages = sc["messages"]

    # Create Call
    call = CallManager.create_incoming_call(
        db=db,
        user_id=current_user.id,
        caller_number=caller_number,
        caller_name=caller_name
    )

    # Process completion
    res = await CallManager.process_completed_call(
        db=db,
        call_id=call.id,
        messages=messages,
        duration_seconds=52
    )

    return {
        "call_id": call.id,
        "scenario": payload.scenario_id,
        "caller_name": caller_name,
        "caller_number": caller_number,
        "messages": messages,
        "result": res
    }
