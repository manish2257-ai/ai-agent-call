import uuid
import datetime
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from ..models.models import (
    Call, CallSummary, CallTranscript, CallMessage,
    UrgencyEvent, Contact, UrgencyRuleModel, UserSettings
)
from .urgency_classifier import UrgencyClassifier
from .sms_service import SMSService
from .ai_agent import AIAgentService

logger = logging.getLogger("CallManager")

class CallManager:
    @staticmethod
    def create_incoming_call(db: Session, user_id: int, caller_number: str, caller_name: Optional[str] = None) -> Call:
        # Check if caller matches VIP contact
        contact = db.query(Contact).filter(Contact.user_id == user_id, Contact.phone_number == caller_number).first()
        resolved_name = contact.name if contact else (caller_name or "Unknown Caller")
        
        call_id = f"call_{uuid.uuid4().hex[:12]}"
        new_call = Call(
            id=call_id,
            user_id=user_id,
            caller_number=caller_number,
            caller_name=resolved_name,
            status="In Progress",
            urgency="LOW",
            duration_seconds=0,
            created_at=datetime.datetime.utcnow()
        )
        db.add(new_call)
        db.commit()
        db.refresh(new_call)
        return new_call

    @staticmethod
    async def process_completed_call(
        db: Session,
        call_id: str,
        messages: List[Dict[str, str]],
        duration_seconds: int = 45
    ) -> Dict[str, Any]:
        call = db.query(Call).filter(Call.id == call_id).first()
        if not call:
            raise ValueError("Call not found")

        user_settings = db.query(UserSettings).filter(UserSettings.user_id == call.user_id).first()

        # Build transcript text
        transcript_lines = []
        for m in messages:
            speaker = m.get("speaker", "Caller")
            content = m.get("content", "")
            ts = m.get("timestamp", datetime.datetime.now().strftime("%H:%M:%S"))
            transcript_lines.append(f"{speaker}: {content}")
            
            # Save message record
            msg_record = CallMessage(
                call_id=call_id,
                speaker=speaker,
                content=content,
                timestamp_str=ts
            )
            db.add(msg_record)

        raw_transcript = "\n".join(transcript_lines)

        # Store transcript if enabled
        if user_settings and user_settings.is_transcript_storage_enabled:
            transcript_record = CallTranscript(call_id=call_id, raw_text=raw_transcript)
            db.add(transcript_record)

        # Urgency Classification
        classification = await UrgencyClassifier.classify(
            transcript_text=raw_transcript,
            caller_name=call.caller_name,
            caller_number=call.caller_number
        )

        urgency_val = classification.get("urgency", "LOW")
        reason_val = classification.get("reason", "Routine enquiry")
        summary_val = classification.get("summary", "Caller spoke with AI assistant.")
        callback_req = classification.get("callback_required", False)

        # Save urgency event
        urgency_event = UrgencyEvent(
            call_id=call_id,
            urgency_level=urgency_val,
            reason=reason_val,
            raw_response_json=str(classification)
        )
        db.add(urgency_event)

        # Determine action item
        action_text = "No immediate action required"
        if urgency_val in ("HIGH", "CRITICAL"):
            action_text = f"Owner should review and follow up regarding: {reason_val}"
        elif callback_req:
            action_text = f"Callback requested by caller regarding: {reason_val}"

        # Save Summary
        summary_record = CallSummary(
            call_id=call_id,
            summary_text=summary_val,
            action_required=action_text,
            callback_required=callback_req,
            ai_outcome="Captured caller requirements and assessed urgency"
        )
        db.add(summary_record)

        # Update Call
        call.urgency = urgency_val
        call.reason = reason_val
        call.duration_seconds = duration_seconds
        call.status = "Escalated" if urgency_val in ("HIGH", "CRITICAL") else "Completed"
        
        # Check VIP Status
        vip = db.query(Contact).filter(Contact.user_id == call.user_id, Contact.phone_number == call.caller_number).first()
        is_vip = vip is not None and (vip.always_alert or vip.always_transfer)

        # Rule evaluation
        should_send_sms = False
        threshold = user_settings.urgency_threshold if user_settings else "HIGH"

        urgency_weights = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        if urgency_weights.get(urgency_val, 1) >= urgency_weights.get(threshold, 3):
            should_send_sms = True

        if is_vip:
            should_send_sms = True

        sms_result = None
        owner_number = user_settings.owner_phone_number if user_settings else "+19876543210"
        if should_send_sms:
            sms_result = await SMSService.dispatch_urgent_sms(
                db=db,
                call_id=call_id,
                to_number=owner_number,
                caller=call.caller_name,
                caller_number=call.caller_number,
                urgency=urgency_val,
                reason=reason_val,
                summary=summary_val,
                user_settings=user_settings
            )

        db.commit()

        return {
            "call_id": call_id,
            "urgency": urgency_val,
            "reason": reason_val,
            "summary": summary_val,
            "action_required": action_text,
            "sms_alert": sms_result
        }
