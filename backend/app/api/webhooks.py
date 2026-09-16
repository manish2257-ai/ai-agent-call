from typing import Dict, Any
from fastapi import APIRouter, Request, Response, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from ..core.config import settings
from ..services.call_manager import CallManager
from ..services.ai_agent import AIAgentService
from ..models.models import User, UserSettings, Call
from .deps import get_db
import logging

logger = logging.getLogger("Webhooks")

router = APIRouter(prefix="/webhooks/telephony", tags=["Telephony Webhooks"])

@router.post("/incoming")
async def handle_incoming_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_twilio_signature: str = Header(None)
):
    """
    Webhook triggered by Telephony provider (Twilio/Exotel/Plivo) when a caller dials the AI number.
    """
    body_form = await request.form()
    data = dict(body_form)
    logger.info(f"Incoming call webhook received. Caller: {data.get('From')}, CallSid: {data.get('CallSid')}")

    # Resolve Owner
    default_user = db.query(User).filter(User.email == "manish@aicallagent.com").first()
    if not default_user:
        default_user = db.query(User).first()
    
    user_id = default_user.id if default_user else 1

    user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    
    # If AI Agent is toggled OFF by owner:
    if user_settings and not user_settings.is_agent_enabled:
        twiml_off = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Response>\n'
            '    <Say>The AI call agent is currently inactive. Please call back later or leave a voicemail.</Say>\n'
            '    <Hangup/>\n'
            '</Response>'
        )
        return Response(content=twiml_off, media_type="application/xml")

    # Create new incoming call record
    caller_num = data.get("From", "+919876543210")
    call = CallManager.create_incoming_call(
        db=db,
        user_id=user_id,
        caller_number=caller_num,
        caller_name="Incoming Caller"
    )

    greeting_text = user_settings.greeting if user_settings else "Hello, you've reached Manish's AI assistant. How can I help?"

    twiml_response = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Response>\n'
        f'    <Say voice="Polly.Aditi">{greeting_text}</Say>\n'
        f'    <Gather input="speech" action="/webhooks/telephony/media?call_id={call.id}" timeout="5" speechTimeout="auto">\n'
        '    </Gather>\n'
        '</Response>'
    )
    return Response(content=twiml_response, media_type="application/xml")

@router.post("/media")
async def handle_media_webhook(
    request: Request,
    call_id: str = "default_call",
    db: Session = Depends(get_db)
):
    """
    Receives caller speech transcription or audio stream, generates AI response turn.
    """
    body_form = await request.form()
    data = dict(body_form)
    speech_result = data.get("SpeechResult", "Hello, I need help with something urgent.")

    logger.info(f"Speech received for call {call_id}: {speech_result}")

    # Generate AI answer
    ai_reply = await AIAgentService.generate_response(
        messages=[{"role": "user", "content": speech_result}]
    )

    twiml_continue = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Response>\n'
        f'    <Say voice="Polly.Aditi">{ai_reply}</Say>\n'
        f'    <Gather input="speech" action="/webhooks/telephony/media?call_id={call_id}" timeout="4" speechTimeout="auto">\n'
        '    </Gather>\n'
        '</Response>'
    )
    return Response(content=twiml_continue, media_type="application/xml")

@router.post("/status")
async def handle_status_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receives call terminal status (completed, busy, no-answer, failed).
    """
    body_form = await request.form()
    data = dict(body_form)
    call_status = data.get("CallStatus", "completed")
    call_sid = data.get("CallSid")
    logger.info(f"Call status callback: {call_sid} -> {call_status}")
    return {"status": "ok", "call_status": call_status}
