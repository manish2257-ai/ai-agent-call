"""
Application Configuration and System Status API Router
Provides safe, production-accurate status and non-secret configuration
for the Android and client applications.
"""

import os
import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..core.config import settings
from ..database.session import get_db
from ..models.models import UserSettings, Call, SmsAlert
from .exotel_voice import get_exotel_config_status, resolve_public_wss_url

router = APIRouter(tags=["App Configuration"])

@router.get("/api/app/config")
def get_app_config(request: Request, db: Session = Depends(get_db)):
    """
    Returns non-secret production configuration and live status.
    Serves as the source of truth for Android/mobile dashboards.
    """
    exotel_conf = get_exotel_config_status()
    telephony_ready = exotel_conf.get("is_ready", False)
    telephony_status = "READY" if telephony_ready else "NOT_CONFIGURED"

    virtual_num = exotel_conf.get("virtual_number")
    virtual_number_display = virtual_num if virtual_num else "Not configured"
    virtual_number_configured = exotel_conf.get("virtual_number_present", False)

    # SMS Gateway Provider (Exotel)
    sms_provider_name = os.getenv("SMS_PROVIDER", "Exotel").capitalize()
    sms_ready = bool(os.getenv("EXOTEL_ACCOUNT_SID") and os.getenv("EXOTEL_API_KEY"))
    sms_status = "READY" if sms_ready else "NOT_CONFIGURED"

    # OpenAI Service
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_configured = bool(openai_key)

    # Voicebot stream URL & status
    wss_url = resolve_public_wss_url(request)
    voicebot_status = "READY" if openai_configured else "NOT_CONFIGURED"
    websocket_status = "READY"

    # Settings from database
    user_settings = db.query(UserSettings).first()
    agent_enabled = user_settings.is_agent_enabled if user_settings else True

    owner_number = ""
    if user_settings and user_settings.owner_phone_number:
        owner_number = user_settings.owner_phone_number.strip()
    if not owner_number:
        owner_number = os.getenv("OWNER_PHONE_NUMBER", "").strip()
    owner_phone_display = owner_number if owner_number else "Not configured"

    ai_number = ""
    if user_settings and user_settings.ai_phone_number:
        ai_number = user_settings.ai_phone_number.strip()
    if not ai_number:
        ai_number = virtual_num or ""
    ai_phone_display = ai_number if ai_number else "Not configured"

    greeting = (user_settings.greeting if user_settings else None) or "Hello, you've reached Manish's AI assistant. Manish isn't available to take the call right now. How can I help?"
    urgency_threshold = (user_settings.urgency_threshold if user_settings else None) or "HIGH"

    # Real configured Webhook URLs
    forwarded_host = request.headers.get("x-forwarded-host", "").strip()
    host_hdr = request.headers.get("host", "").strip()
    app_url = os.getenv("APP_URL", "").strip()

    if forwarded_host and "localhost" not in forwarded_host:
        host = forwarded_host
    elif app_url:
        host = app_url.replace("https://", "").replace("http://", "").rstrip("/")
    elif host_hdr and "localhost" not in host_hdr:
        host = host_hdr
    else:
        host = "ais-dev-drq6zz2gzpkest44ecny22-192566711824.asia-east1.run.app"

    proto = "https" if ("run.app" in host or "https" in app_url) else "http"
    incoming_webhook_url = f"{proto}://{host}/webhooks/exotel/incoming"
    status_callback_url = f"{proto}://{host}/webhooks/exotel/status"

    # Metrics from real database records (never fake)
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    all_calls = db.query(Call).all()
    total_calls = len(all_calls)
    calls_today = len([c for c in all_calls if c.created_at and c.created_at >= today_start])
    urgent_escalations = len([c for c in all_calls if c.urgency in ("HIGH", "CRITICAL")])
    sms_alerts_sent = db.query(SmsAlert).count()
    avg_duration_seconds = 0
    if total_calls > 0:
        avg_duration_seconds = sum((c.duration_seconds or 0) for c in all_calls) // total_calls

    # Active status: strictly requires agent_enabled AND telephony_ready AND openai_configured
    is_active = bool(agent_enabled and telephony_ready and openai_configured)

    return {
        "telephony_provider": "Exotel",
        "telephony_status": telephony_status,
        "virtual_number_configured": virtual_number_configured,
        "virtual_number": virtual_number_display,
        "sms_provider": sms_provider_name,
        "sms_status": sms_status,
        "openai_configured": openai_configured,
        "voicebot_status": voicebot_status,
        "websocket_status": websocket_status,
        "voicebot_wss_url": wss_url,
        "incoming_webhook_url": incoming_webhook_url,
        "status_callback_url": status_callback_url,
        "agent_enabled": agent_enabled,
        "active": is_active,
        "owner_phone_number": owner_phone_display,
        "ai_phone_number": ai_phone_display,
        "greeting": greeting,
        "urgency_threshold": urgency_threshold,
        "metrics": {
            "calls_today": calls_today,
            "total_calls": total_calls,
            "urgent_escalations": urgent_escalations,
            "sms_alerts_sent": sms_alerts_sent,
            "avg_call_duration_seconds": avg_duration_seconds,
        }
    }
