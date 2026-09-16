"""
FastAPI Router for Twilio WhatsApp Messaging
Provides:
- POST /api/whatsapp/test: Sends a test message using Twilio Sandbox configuration
- GET /api/whatsapp/status: Safe status endpoint reporting configuration state
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from ..services.twilio_whatsapp_service import twilio_whatsapp_service

logger = logging.getLogger("whatsapp_api")

router = APIRouter(tags=["WhatsApp"])


class TestWhatsAppRequest(BaseModel):
    to: Optional[str] = Field(None, description="Optional target WhatsApp number, e.g. whatsapp:+917367966177")
    from_: Optional[str] = Field(None, alias="from", description="Optional sender WhatsApp number, e.g. whatsapp:+17372508034")
    content_sid: Optional[str] = Field(None, description="Twilio Content SID template, e.g. HXfe5ab5f00277942d4d4200328b4d403c")
    body: Optional[str] = Field(None, description="Optional custom message body (for non-template senders)")


@router.post("/api/whatsapp/test")
@router.post("/whatsapp/test")
async def test_whatsapp_message(payload: Optional[TestWhatsAppRequest] = None):
    """
    Sends a test WhatsApp message using the configured Twilio Sandbox template.
    Returns:
    {
      "success": true,
      "message": "WhatsApp message submitted successfully",
      "sid": "..."
    }
    Never returns credentials or secrets.
    """
    valid, err = twilio_whatsapp_service.validate_configuration()
    if not valid:
        logger.warning(f"Test WhatsApp requested but {err}")
        return {
            "success": False,
            "message": "Twilio WhatsApp configuration is incomplete.",
            "error": "Twilio WhatsApp configuration is incomplete."
        }

    to_target = payload.to if payload and payload.to else None
    from_target = payload.from_ if payload and payload.from_ else None
    content_sid = payload.content_sid if payload and payload.content_sid else None
    body_target = payload.body if payload and payload.body else None

    # Call service with bypass_cooldown=True for intentional testing
    result = twilio_whatsapp_service.send_whatsapp_message(
        to=to_target,
        from_=from_target,
        content_sid=content_sid,
        body=body_target,
        bypass_cooldown=True
    )

    if not result.get("success"):
        return {
            "success": False,
            "message": result.get("message", "Failed to send WhatsApp message via Twilio"),
            "error": result.get("error", "Twilio API error")
        }

    return {
        "success": True,
        "message": "WhatsApp message submitted successfully",
        "sid": result.get("sid"),
        "status": result.get("status", "queued")
    }


@router.get("/api/whatsapp/status")
@router.get("/whatsapp/status")
async def get_whatsapp_status():
    """
    Returns the current status of the Twilio WhatsApp service without revealing secrets.
    """
    valid, err = twilio_whatsapp_service.validate_configuration()
    
    # Mask numbers and account SID for safe inspection
    sid = twilio_whatsapp_service.account_sid
    masked_sid = (sid[:4] + "..." + sid[-4:]) if sid and len(sid) > 8 else None

    to_num = twilio_whatsapp_service.default_to
    masked_to = (to_num[:12] + "...") if len(to_num) > 12 else to_num

    return {
        "configured": valid,
        "status": "READY" if valid else "NOT_CONFIGURED",
        "account_sid_present": bool(sid),
        "auth_token_present": bool(twilio_whatsapp_service.auth_token),
        "account_sid_preview": masked_sid,
        "from": twilio_whatsapp_service.default_from,
        "to": masked_to,
        "content_sid": twilio_whatsapp_service.default_content_sid,
        "configuration_message": None if valid else err
    }
