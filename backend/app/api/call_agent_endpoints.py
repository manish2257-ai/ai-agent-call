"""
Unified REST Endpoints for AI Personal Call Agent
Fulfills all requested routes:
- GET /health
- GET /health/integrations
- GET /dashboard
- GET /calls
- GET /calls/{callId}
- DELETE /calls/{callId}
- DELETE /calls/{callId}/transcript
- DELETE /calls/{callId}/recording
- POST /calls/purge
- GET /alerts
- DELETE /alerts/{alertId}
- GET /settings
- PUT /settings
- POST /alerts/test
- POST /notifications/test
- POST /demo/simulate-call
- POST /demo/simulate-urgent-call
- POST /demo/test-sms
- POST /webhooks/exotel/incoming
- POST /webhooks/exotel/status
- POST /webhooks/exotel/media
- GET /privacy/export
- GET /privacy/audit-logs
- POST /privacy/cleanup
"""

import os
import time
import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query, status
from typing import Dict, Any, List, Optional

logger = logging.getLogger("CallAgentEndpoints")

from app.firebase.firebase_service import firebase_manager
from app.telephony.exotel_telephony import exotel_service
from app.sms.exotel_sms import exotel_sms_service
from app.whatsapp.whatsapp_provider import whatsapp_service
from app.privacy.privacy_manager import privacy_manager, ConsentMode, ConsentStatus
from app.ai.voice_agent import ai_voice_agent
from app.ai.urgency import urgency_classifier, UrgencyLevel
from app.security.auth_middleware import get_current_user
from app.schemas.call_agent_schemas import (
    SettingsModel, CallRecordModel, UrgentAlertModel,
    DemoSimulateCallRequest, TestSmsRequest, TestNotificationRequest,
    TestWhatsAppRequest, BulkPurgeRequest
)

router = APIRouter(tags=["AI Call Agent API"])

# In-memory settings state for user
_user_settings_cache: Dict[str, Dict[str, Any]] = {
    "default": SettingsModel().model_dump()
}

def _get_user_settings(uid: str) -> Dict[str, Any]:
    if uid not in _user_settings_cache:
        _user_settings_cache[uid] = SettingsModel().model_dump()
    return _user_settings_cache[uid]

# --- HEALTH & INTEGRATIONS ---
@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "AI Personal Call Agent Backend",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/integrations")
def get_health_integrations():
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_exotel = bool(os.getenv("EXOTEL_API_KEY"))
    has_firebase = firebase_manager.is_initialized
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    whatsapp_info = whatsapp_service.get_status()

    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "demoMode": demo_mode,
        "whatsapp": {
            "enabled": whatsapp_info["enabled"],
            "configured": whatsapp_info["configured"],
            "status": whatsapp_info["status"]
        },
        "integrations": [
            {
                "name": "Firebase Auth & Firestore",
                "status": "CONNECTED" if has_firebase else ("SIMULATED" if demo_mode else "DISCONNECTED"),
                "details": "User authentication, call storage, and device tokens"
            },
            {
                "name": "OpenAI Voice API",
                "status": "CONNECTED" if has_openai else ("SIMULATED" if demo_mode else "DISCONNECTED"),
                "details": "Natural language call comprehension and urgency classification"
            },
            {
                "name": "Exotel Telephony",
                "status": "CONNECTED" if has_exotel else ("SIMULATED" if demo_mode else "DISCONNECTED"),
                "details": "Cloud virtual number and incoming voice webhooks"
            },
            {
                "name": "Exotel SMS",
                "status": "CONNECTED" if has_exotel else ("SIMULATED" if demo_mode else "DISCONNECTED"),
                "details": "Priority SMS dispatch for High & Critical calls"
            },
            {
                "name": "WhatsApp Cloud API",
                "status": whatsapp_info["status"],
                "details": "Official WhatsApp Business Platform urgent alert messaging"
            },
            {
                "name": "Firebase Cloud Messaging",
                "status": "CONNECTED" if has_firebase else ("SIMULATED" if demo_mode else "DISCONNECTED"),
                "details": "Real-time push alerts to Android APK"
            }
        ]
    }

# --- DASHBOARD ---
@router.get("/dashboard")
async def get_dashboard(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    calls = await firebase_manager.get_all_calls(uid)
    alerts = await firebase_manager.get_alerts(uid)
    settings = _get_user_settings(uid)

    today_str = datetime.date.today().isoformat()
    today_calls = [c for c in calls if (c.get("createdAt") or "").startswith(today_str)]
    urgent_calls = [c for c in calls if c.get("urgency") in ["HIGH", "CRITICAL"]]

    latest_call = calls[0] if calls else None

    return {
        "agentStatus": "ONLINE" if settings.get("agentEnabled", True) else "OFFLINE",
        "totalCallsToday": len(today_calls) if today_calls else len(calls),
        "totalUrgentCalls": len(urgent_calls),
        "aiPhoneNumber": settings.get("aiPhoneNumber", "+918047100000"),
        "ownerPhoneNumber": settings.get("ownerPhoneNumber", "+917367966177"),
        "latestCall": latest_call,
        "latestAlerts": alerts[:3],
        "connectionStatus": {
            "firebase": "CONNECTED" if firebase_manager.is_initialized else "SIMULATED",
            "openAI": "CONNECTED" if os.getenv("OPENAI_API_KEY") else "SIMULATED",
            "exotel": "CONNECTED" if os.getenv("EXOTEL_API_KEY") else "SIMULATED",
            "sms": "CONNECTED" if os.getenv("EXOTEL_API_KEY") else "SIMULATED",
            "whatsapp": whatsapp_service.get_status()["status"]
        }
    }

# --- CALLS ---
@router.get("/calls")
async def get_calls(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    calls = await firebase_manager.get_all_calls(uid)
    return calls

@router.get("/calls/{call_id}")
async def get_call_by_id(call_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    call = await firebase_manager.get_call(uid, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call record not found")
    return call

@router.delete("/calls/{call_id}")
async def delete_call_by_id(call_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    success = await firebase_manager.delete_call(uid, call_id)
    if not success:
        raise HTTPException(status_code=404, detail="Call not found")
    privacy_manager.log_audit_event("DELETE_CALL", uid, {"callId": call_id})
    return {"success": True, "message": f"Call {call_id} deleted"}

@router.delete("/calls/{call_id}/transcript")
async def delete_call_transcript_by_id(call_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    success = await firebase_manager.delete_call_transcript(uid, call_id)
    if not success:
        raise HTTPException(status_code=404, detail="Call not found")
    privacy_manager.log_audit_event("DELETE_TRANSCRIPT", uid, {"callId": call_id})
    return {"success": True, "message": f"Transcript for call {call_id} deleted"}

@router.delete("/calls/{call_id}/recording")
async def delete_call_recording_by_id(call_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    # Recordings are disabled by default; acknowledge and audit deletion
    privacy_manager.log_audit_event("DELETE_RECORDING", uid, {"callId": call_id})
    return {"success": True, "message": f"Recording for call {call_id} removed"}

@router.post("/calls/purge")
async def purge_all_data(req: BulkPurgeRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    if req.confirmPhrase != "DELETE_ALL_DATA":
        raise HTTPException(status_code=400, detail="Invalid confirmation phrase. Must provide 'DELETE_ALL_DATA'")
    count = await firebase_manager.delete_all_calls(uid)
    privacy_manager.log_audit_event("BULK_DATA_PURGE", uid, {"deletedCallsCount": count})
    return {"success": True, "deletedRecords": count, "message": "All stored call history successfully purged."}

# --- ALERTS ---
@router.get("/alerts")
async def get_alerts(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    alerts = await firebase_manager.get_alerts(uid)
    return alerts

@router.delete("/alerts/{alert_id}")
async def delete_alert_by_id(alert_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    success = await firebase_manager.delete_alert(uid, alert_id)
    privacy_manager.log_audit_event("DELETE_ALERT", uid, {"alertId": alert_id})
    return {"success": success, "message": f"Alert {alert_id} deleted"}

# --- SETTINGS ---
@router.get("/settings")
async def get_settings(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    return _get_user_settings(uid)

@router.put("/settings")
async def update_settings(new_settings: SettingsModel, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    _user_settings_cache[uid] = new_settings.model_dump()
    privacy_manager.log_audit_event("UPDATE_SETTINGS", uid, {
        "consentMode": new_settings.consentMode,
        "recordingEnabled": new_settings.recordingEnabled,
        "transcriptionEnabled": new_settings.persistentTranscriptionEnabled,
        "retentionDays": new_settings.callMetadataRetentionDays
    })
    return {"success": True, "settings": _user_settings_cache[uid]}

# --- DEMO & TESTING SIMULATION ---
@router.post("/alerts/test")
@router.post("/demo/test-sms")
async def test_sms_alert(req: TestSmsRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    settings = _get_user_settings(uid)
    dest = req.destinationNumber or settings.get("ownerPhoneNumber") or os.getenv("OWNER_PHONE_NUMBER", "").strip()
    if not dest:
        raise HTTPException(status_code=400, detail="Destination phone number is not configured.")

    result = await exotel_sms_service.send_urgent_sms(
        destination_number=dest,
        caller_name="Caller (Test Alert)",
        caller_number="+919810012345",
        urgency=req.urgency,
        reason=req.reason,
        summary=req.summary,
        callback_required=True
    )
    return result

@router.post("/notifications/test")
async def test_push_notification(req: TestNotificationRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    sent = await firebase_manager.send_fcm_notification(
        user_id=uid,
        title=req.title,
        body=req.body,
        data={"type": "URGENT_CALL_ALERT", "urgency": "HIGH"}
    )
    return {"success": sent, "message": "Test push notification dispatched"}

@router.post("/demo/simulate-call")
@router.post("/demo/simulate-urgent-call")
async def simulate_call(req: DemoSimulateCallRequest, user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    settings = _get_user_settings(uid)
    now_time = datetime.datetime.now().strftime("%I:%M %p")
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    scenario = req.scenario.lower()

    if scenario == "outage" or req.speechInput and "down" in req.speechInput.lower():
        caller_name = req.callerName or "Rahul Verma"
        caller_number = req.callerNumber or "+91 98765 43210"
        urgency = UrgencyLevel.HIGH
        reason = "Website outage - Customers cannot place orders"
        summary = "Production website is down and customer checkout is failing."
        action = "Investigate production servers immediately."
        messages = [
            {"speaker": "AI", "content": settings.get("aiGreeting"), "timestamp": now_time},
            {"speaker": "Caller", "content": "This is Rahul. The website is down and customers cannot place orders. We need this fixed immediately.", "timestamp": now_time},
            {"speaker": "AI", "content": "I understand the urgency. I am marking this as HIGH priority and sending an immediate SMS alert to Manish.", "timestamp": now_time}
        ]
    elif scenario == "contract":
        caller_name = req.callerName or "Vikram Sethi"
        caller_number = req.callerNumber or "+91 98445 56677"
        urgency = UrgencyLevel.HIGH
        reason = "Contract deadline today before 5:00 PM"
        summary = "Acme Corp requires countersignature on enterprise agreement before 5 PM."
        action = "Sign contract document in email."
        messages = [
            {"speaker": "AI", "content": settings.get("aiGreeting"), "timestamp": now_time},
            {"speaker": "Caller", "content": "Vikram here from Acme Corp. Hard deadline today at 5 PM for contract signature.", "timestamp": now_time},
            {"speaker": "AI", "content": "Understood Vikram. I am alerting Manish right away.", "timestamp": now_time}
        ]
    elif scenario == "emergency":
        caller_name = req.callerName or "Building Management"
        caller_number = req.callerNumber or "+91 98998 87766"
        urgency = UrgencyLevel.CRITICAL
        reason = "Immediate safety hazard - Electrical smoke"
        summary = "Caller reported smoke in building hallway. AI provided emergency 112/911 notice.",
        action = "Verify safety status and emergency dispatch."
        messages = [
            {"speaker": "AI", "content": settings.get("aiGreeting"), "timestamp": now_time},
            {"speaker": "Caller", "content": "There is smoke coming from the electrical box!", "timestamp": now_time},
            {"speaker": "AI", "content": "If there is fire or smoke, please call 112 or 911 immediately! As an AI I cannot dispatch emergency services.", "timestamp": now_time}
        ]
    else:
        caller_name = req.callerName or "Priya Sharma"
        caller_number = req.callerNumber or "+91 98112 23344"
        urgency = UrgencyLevel.LOW
        reason = "Consulting slot enquiry for Friday"
        summary = "Priya asked about advisory availability for mobile application development."
        action = "Send calendar booking link when convenient."
        messages = [
            {"speaker": "AI", "content": settings.get("aiGreeting"), "timestamp": now_time},
            {"speaker": "Caller", "content": "Hi, I wanted to inquire if Manish is available for a consultation this Friday?", "timestamp": now_time},
            {"speaker": "AI", "content": "Manish's consultation hours are Monday to Friday. I've noted your request and will forward it to him.", "timestamp": now_time}
        ]

    # Evaluate consent and privacy rules
    consent_eval = privacy_manager.evaluate_consent_rules(settings.get("consentMode", ConsentMode.DISABLE_RECORDING_AND_TRANSCRIPTION))
    
    # Filter messages if persistent transcription is disabled
    stored_messages = messages if (settings.get("persistentTranscriptionEnabled") and consent_eval["allowTranscription"]) else []

    call_id = f"call_{int(time.time())}"
    call_record = {
        "callId": call_id,
        "callerName": caller_name,
        "callerNumber": caller_number,
        "reason": privacy_manager.redact_secrets(reason),
        "urgency": urgency,
        "summary": privacy_manager.redact_secrets(summary),
        "callbackRequired": urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL],
        "status": "ESCALATED" if urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL] else "COMPLETED",
        "smsSent": False,
        "whatsappSent": False,
        "fcmSent": False,
        "whatsappStatus": "PENDING" if urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL] else "NOT_CONFIGURED",
        "whatsappMessageId": None,
        "whatsappSentAt": None,
        "startedAt": now_iso,
        "duration": 48,
        "consentStatus": consent_eval["consentStatus"],
        "consentPolicyVersion": consent_eval["policyVersion"],
        "recordingEnabled": False,
        "transcriptionEnabled": bool(stored_messages),
        "messages": stored_messages,
        "createdAt": now_iso
    }

    # If Urgent (HIGH or CRITICAL), trigger SMS, WhatsApp, and FCM independently
    if urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]:
        owner_phone = settings.get("ownerPhoneNumber", "+917367966177")
        wa_phone = settings.get("whatsappRecipientNumber", owner_phone)

        # 1. SMS Alert via Exotel (Attempted independently)
        sms_sent = False
        if settings.get("smsAlertsEnabled", True):
            try:
                sms_res = await exotel_sms_service.send_urgent_sms(
                    destination_number=owner_phone,
                    caller_name=caller_name,
                    caller_number=caller_number,
                    urgency=urgency,
                    reason=reason,
                    summary=summary,
                    callback_required=True
                )
                sms_sent = sms_res.get("success", False)
            except Exception as e:
                logger.error(f"SMS notification error: {e}")
        call_record["smsSent"] = sms_sent

        # 2. WhatsApp Alert via WhatsApp Cloud API (Attempted independently)
        wa_sent = False
        wa_status = "NOT_CONFIGURED"
        wa_msg_id = None
        if settings.get("whatsappAlertsEnabled", True):
            try:
                wa_res = await whatsapp_service.send_urgent_alert(
                    call_id=call_id,
                    caller_name=caller_name,
                    caller_number=caller_number,
                    urgency=urgency,
                    reason=reason,
                    summary=summary,
                    callback_required=True,
                    call_time=now_time,
                    recipient_number=wa_phone
                )
                wa_sent = wa_res.get("success", False)
                wa_status = wa_res.get("status", "SENT" if wa_sent else "FAILED")
                wa_msg_id = wa_res.get("messageId")
            except Exception as e:
                logger.error(f"WhatsApp notification error: {e}")
                wa_status = "FAILED"
        call_record["whatsappSent"] = wa_sent
        call_record["whatsappStatus"] = wa_status
        call_record["whatsappMessageId"] = wa_msg_id
        call_record["whatsappSentAt"] = now_iso if wa_sent else None

        # 3. Push Notification via FCM (Attempted independently)
        fcm_sent = False
        if settings.get("pushNotificationsEnabled", True):
            try:
                fcm_sent = await firebase_manager.send_fcm_notification(
                    user_id=uid,
                    title=f"URGENT CALL: {caller_name}",
                    body=f"{urgency}: {reason}",
                    data={"callId": call_id, "urgency": urgency}
                )
            except Exception as e:
                logger.error(f"FCM notification error: {e}")
        call_record["fcmSent"] = fcm_sent

        # 4. Store in alerts collection
        alert_record = {
            "alertId": f"alert_{int(time.time())}",
            "callId": call_id,
            "callerName": caller_name,
            "callerNumber": caller_number,
            "urgency": urgency,
            "reason": reason,
            "summary": summary,
            "status": "DELIVERED",
            "smsStatus": "SENT" if sms_sent else "FAILED",
            "whatsappStatus": wa_status,
            "fcmStatus": "SENT" if fcm_sent else "FAILED",
            "provider": "Exotel & WhatsApp Cloud",
            "createdAt": now_iso
        }
        await firebase_manager.save_alert(uid, alert_record)

    await firebase_manager.save_call(uid, call_record)
    return {"success": True, "call": call_record}

# --- WHATSAPP TESTING & RETRY ENDPOINTS ---
@router.post("/notifications/test-whatsapp")
@router.post("/demo/test-whatsapp")
async def test_whatsapp_notification(req: TestWhatsAppRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Sends a test WhatsApp notification to the recipient without creating a call."""
    uid = user.get("uid", "user_demo_manish_123")
    settings = _get_user_settings(uid)
    dest = req.recipientNumber or settings.get("whatsappRecipientNumber", "+917367966177")

    result = await whatsapp_service.send_test_message(recipient_number=dest)
    return result

@router.post("/demo/simulate-whatsapp-alert")
async def simulate_whatsapp_alert(user: Dict[str, Any] = Depends(get_current_user)):
    """Simulates a HIGH urgency call with explicit WhatsApp alert dispatch."""
    req = DemoSimulateCallRequest(
        scenario="outage",
        callerName="Rahul",
        callerNumber="+91 98765 43210"
    )
    return await simulate_call(req, user)

@router.post("/alerts/{alert_id}/retry-whatsapp")
async def retry_whatsapp_alert(alert_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Retries sending WhatsApp notification for an existing alert, respecting idempotency and cooldown."""
    uid = user.get("uid", "user_demo_manish_123")
    alerts = await firebase_manager.get_alerts(uid)
    target = next((a for a in alerts if a.get("alertId") == alert_id or a.get("id") == alert_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Alert record not found")

    settings = _get_user_settings(uid)
    dest = settings.get("whatsappRecipientNumber") or os.getenv("WHATSAPP_RECIPIENT_PHONE_NUMBER") or target.get("callerNumber") or ""
    now_time = datetime.datetime.now().strftime("%I:%M %p")

    result = await whatsapp_service.send_urgent_alert(
        call_id=target.get("callId", alert_id),
        caller_name=target.get("callerName", "Caller"),
        caller_number=target.get("callerNumber", ""),
        urgency=target.get("urgency", "HIGH"),
        reason=target.get("reason", "Urgent reason"),
        summary=target.get("summary", "Urgent summary"),
        callback_required=True,
        call_time=now_time,
        recipient_number=dest
    )
    return result

# --- WHATSAPP CLOUD API WEBHOOKS ---
@router.get("/webhooks/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
):
    """
    Verification challenge handshake for Meta WhatsApp Cloud API.
    Meta makes a GET request with hub.mode=subscribe, hub.challenge, and hub.verify_token.
    Accepts GET requests without authentication.
    """
    expected_verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN") or os.getenv("WHATSAPP_VERIFY_TOKEN", "ai_call_agent_verify_token_2026")
    
    if not expected_verify_token:
        logger.error("WhatsApp Webhook verification rejected: WHATSAPP_WEBHOOK_VERIFY_TOKEN is not configured in server environment.")
        raise HTTPException(status_code=403, detail="Webhook verify token not configured")

    if hub_mode == "subscribe" and hub_verify_token == expected_verify_token:
        logger.info("WhatsApp Webhook verification handshake successful.")
        # Return hub.challenge as plain-text HTTP 200 response
        return Response(content=hub_challenge or "", media_type="text/plain", status_code=200)
    else:
        logger.warning(
            f"WhatsApp Webhook verification failed: hub.mode='{hub_mode}', "
            f"token_provided={'<non-empty>' if hub_verify_token else '<empty>'}, "
            f"token_matched={hub_verify_token == expected_verify_token}"
        )
        raise HTTPException(status_code=403, detail="Verification token or mode mismatch")

@router.post("/webhooks/whatsapp")
async def whatsapp_incoming_webhook(request: Request):
    """
    Receives WhatsApp message delivery status updates (sent, delivered, read) and incoming user replies.
    Returns HTTP 200 immediately to prevent Meta webhook delivery retries.
    """
    try:
        data = await request.json()
        logger.info("Received WhatsApp webhook event payload successfully.")
        return Response(content='{"status": "SUCCESS"}', media_type="application/json", status_code=200)
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook payload: {str(e)}")
        return Response(content='{"status": "ACKNOWLEDGED"}', media_type="application/json", status_code=200)

# --- EXOTEL TELEPHONY WEBHOOKS ---
@router.post("/webhooks/exotel/incoming")
async def exotel_incoming_webhook(request: Request):
    """
    Exotel voice webhook triggered when a caller dials the AI virtual number.
    Returns Passthru/Gather XML for interactive conversational greeting.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid") or f"exotel_{int(time.time())}"
    caller = form_data.get("From", "Unknown Caller")
    dialed_number = form_data.get("To", "+918047100000")

    settings = _get_user_settings("default")
    greeting = settings.get("aiGreeting", "Hello, you've reached Manish's AI assistant. How can I help?")

    # Enforce AI identity disclosure
    response_xml = exotel_service.build_voice_response(
        spoken_text=greeting,
        gather_action_url="/webhooks/exotel/media"
    )
    return Response(content=response_xml, media_type="application/xml")

@router.post("/webhooks/exotel/status")
async def exotel_status_webhook(request: Request):
    """Exotel status callback receiving duration, status, and termination events."""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    status = form_data.get("Status")
    duration = form_data.get("RecordingDuration") or form_data.get("Legs", {}).get("Duration", "0")
    return {"status": "ACKNOWLEDGED", "callSid": call_sid, "callStatus": status}

@router.post("/webhooks/exotel/media")
async def exotel_media_webhook(request: Request):
    """Exotel conversational turn callback."""
    form_data = await request.form()
    speech_result = form_data.get("SpeechResult") or form_data.get("Digits", "")
    
    # Generate conversational AI response
    reply_text = await ai_voice_agent.generate_response([], speech_result)
    xml = exotel_service.build_voice_response(spoken_text=reply_text)
    return Response(content=xml, media_type="application/xml")

# --- PRIVACY, RETENTION & EXPORT ---
@router.get("/privacy/export")
async def export_data(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    calls = await firebase_manager.get_all_calls(uid)
    alerts = await firebase_manager.get_alerts(uid)
    settings = _get_user_settings(uid)
    exported_json = privacy_manager.export_user_data(calls, alerts, settings)
    privacy_manager.log_audit_event("EXPORT_DATA", uid, {"recordsExported": len(calls)})
    return Response(
        content=exported_json,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=call_agent_export_{int(time.time())}.json"}
    )

@router.get("/privacy/audit-logs")
async def get_audit_logs(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    return privacy_manager.get_audit_logs(uid)

@router.post("/privacy/cleanup")
async def trigger_retention_cleanup(user: Dict[str, Any] = Depends(get_current_user)):
    uid = user.get("uid", "user_demo_manish_123")
    calls = await firebase_manager.get_all_calls(uid)
    alerts = await firebase_manager.get_alerts(uid)
    settings = _get_user_settings(uid)
    
    cleanup_plan = privacy_manager.cleanup_expired_records(calls, alerts, settings)
    for c_id in cleanup_plan["callsToDelete"]:
        await firebase_manager.delete_call(uid, c_id)
    for c_id in cleanup_plan["transcriptsToClear"]:
        await firebase_manager.delete_call_transcript(uid, c_id)
    for a_id in cleanup_plan["alertsToDelete"]:
        await firebase_manager.delete_alert(uid, a_id)

    privacy_manager.log_audit_event("AUTOMATIC_CLEANUP", uid, cleanup_plan)
    return {
        "success": True,
        "deletedCalls": len(cleanup_plan["callsToDelete"]),
        "clearedTranscripts": len(cleanup_plan["transcriptsToClear"]),
        "deletedAlerts": len(cleanup_plan["alertsToDelete"]),
        "timestamp": cleanup_plan["timestamp"]
    }
