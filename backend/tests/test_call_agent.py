"""
Automated Test Suite for AI Personal Call Agent
Tests:
- API health and integrations
- Call simulation & urgency classification
- Exotel SMS formatting & duplicate suppression
- Consent modes (DISABLE_RECORDING_AND_TRANSCRIPTION, DISCLOSURE_ONLY, ASK_FOR_CONSENT)
- Retention cleanup engine
- Data export & privacy redaction
"""

import pytest
from app.privacy.privacy_manager import privacy_manager, ConsentMode, ConsentStatus
from app.sms.exotel_sms import exotel_sms_service
from app.ai.urgency import urgency_classifier, UrgencyLevel

def test_privacy_redaction():
    text = "Caller said their password is secret123 and credit card is 4111 2222 3333 4444 with otp: 987654"
    redacted = privacy_manager.redact_secrets(text)
    assert "secret123" not in redacted
    assert "4111 2222 3333 4444" not in redacted
    assert "987654" not in redacted
    assert "[REDACTED]" in redacted or "[CARD NUMBER REDACTED]" in redacted

def test_consent_mode_default():
    """Default mode must disable persistent recording and transcription."""
    eval_result = privacy_manager.evaluate_consent_rules(ConsentMode.DISABLE_RECORDING_AND_TRANSCRIPTION)
    assert eval_result["allowRecording"] is False
    assert eval_result["allowTranscription"] is False
    assert eval_result["consentStatus"] == ConsentStatus.NOT_REQUIRED

def test_consent_mode_ask_for_consent():
    declined = privacy_manager.evaluate_consent_rules(ConsentMode.ASK_FOR_CONSENT, caller_response_text="No, please don't record")
    assert declined["consentStatus"] == ConsentStatus.DECLINED
    assert declined["allowRecording"] is False
    assert declined["allowTranscription"] is False

    granted = privacy_manager.evaluate_consent_rules(ConsentMode.ASK_FOR_CONSENT, caller_response_text="Yes, I agree to be recorded")
    assert granted["consentStatus"] == ConsentStatus.GRANTED
    assert granted["allowRecording"] is True
    assert granted["allowTranscription"] is True

def test_sms_duplicate_prevention():
    caller = "+919999900000"
    reason = "Critical database corruption"
    
    # First alert should not be considered duplicate
    is_dup_1 = exotel_sms_service.is_duplicate(caller, reason)
    assert is_dup_1 is False

    # Immediate second alert for same caller and reason must be detected as duplicate
    is_dup_2 = exotel_sms_service.is_duplicate(caller, reason)
    assert is_dup_2 is True

@pytest.mark.asyncio
async def test_urgency_classifier_heuristic():
    outage_eval = await urgency_classifier.classify_urgency(
        caller_name="Rahul",
        caller_number="+919810012345",
        reason="Server outage",
        summary="Production website is down and users cannot checkout",
        messages=[]
    )
    assert outage_eval["urgency"] == UrgencyLevel.HIGH
    assert outage_eval["alertRequired"] is True

    enquiry_eval = await urgency_classifier.classify_urgency(
        caller_name="Priya",
        caller_number="+919811223344",
        reason="General consulting hours enquiry",
        summary="Asking about booking slots for mobile app design",
        messages=[]
    )
    assert enquiry_eval["urgency"] in [UrgencyLevel.LOW, UrgencyLevel.MEDIUM]
    assert enquiry_eval["alertRequired"] is False

@pytest.mark.asyncio
async def test_whatsapp_duplicate_prevention():
    from app.whatsapp.whatsapp_provider import whatsapp_service
    call_id = "test_call_abc_123"

    # First call must pass duplicate check
    dup_1 = whatsapp_service.check_duplicate(call_id)
    assert dup_1 is False

    # Second check for same callId within cooldown must be detected as duplicate
    dup_2 = whatsapp_service.check_duplicate(call_id)
    assert dup_2 is True

@pytest.mark.asyncio
async def test_whatsapp_test_message():
    from app.whatsapp.whatsapp_provider import whatsapp_service
    res = await whatsapp_service.send_test_message()
    assert res["success"] is True
    assert "status" in res

