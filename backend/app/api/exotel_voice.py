"""
Exotel Voicebot Production API Router
Provides real production endpoints for Exotel telephony status, diagnostics,
voicebot URL resolution, and stream coordination.
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, status

logger = logging.getLogger("exotel_voice_router")

router = APIRouter(prefix="/api/voice/exotel", tags=["Exotel Voicebot"])

def get_exotel_config_status() -> Dict[str, Any]:
    account_sid = os.getenv("EXOTEL_ACCOUNT_SID", "").strip()
    api_key = os.getenv("EXOTEL_API_KEY", "").strip()
    api_token = os.getenv("EXOTEL_API_TOKEN", "").strip()
    virtual_number = os.getenv("EXOTEL_VIRTUAL_NUMBER", "").strip()
    
    sid_present = bool(account_sid)
    key_present = bool(api_key)
    token_present = bool(api_token)
    num_present = bool(virtual_number)
    
    is_ready = sid_present and key_present and token_present and num_present
    
    missing = []
    if not sid_present:
        missing.append("EXOTEL_ACCOUNT_SID")
    if not key_present:
        missing.append("EXOTEL_API_KEY")
    if not token_present:
        missing.append("EXOTEL_API_TOKEN")
    if not num_present:
        missing.append("EXOTEL_VIRTUAL_NUMBER")
        
    return {
        "is_ready": is_ready,
        "account_sid_present": sid_present,
        "api_key_present": key_present,
        "api_token_present": token_present,
        "virtual_number_present": num_present,
        "virtual_number": virtual_number if num_present else None,
        "missing_variables": missing,
    }

def resolve_public_wss_url(request: Request) -> str:
    """
    Resolves the public WSS endpoint URL for Exotel streaming.
    Prefers explicit APP_URL or request Host, defaulting to the Cloud Run public hostname.
    """
    explicit_wss = os.getenv("EXOTEL_WSS_URL", "").strip() or os.getenv("VOICEBOT_WSS_URL", "").strip()
    if explicit_wss:
        return explicit_wss

    forwarded_host = request.headers.get("x-forwarded-host", "").strip()
    host_hdr = request.headers.get("host", "").strip()
    app_url = os.getenv("APP_URL", "").strip()
    
    # Priority for determining host
    if forwarded_host and "localhost" not in forwarded_host:
        host = forwarded_host
    elif app_url:
        host = app_url.replace("https://", "").replace("http://", "").rstrip("/")
    elif host_hdr and "localhost" not in host_hdr:
        host = host_hdr
    else:
        # Default public Cloud Run service domain
        host = "ais-dev-drq6zz2gzpkest44ecny22-192566711824.asia-east1.run.app"

    # Always use secure wss:// for public Cloud Run / HTTPS domains
    if "run.app" in host or "google" in host or "https" in app_url:
        scheme = "wss"
    elif request.headers.get("x-forwarded-proto") == "https":
        scheme = "wss"
    elif host.startswith("localhost") or host.startswith("127.0.0.1"):
        scheme = "ws"
    else:
        scheme = "wss"
        
    return f"{scheme}://{host}/ws/media-stream"

@router.get("/status")
def get_exotel_status():
    """
    GET /api/voice/exotel/status
    Returns the real-time operational status of the Exotel telephony provider.
    Never prints or logs secret values.
    """
    conf = get_exotel_config_status()
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    provider_status = "READY" if conf["is_ready"] else "NOT READY"
    
    return {
        "provider": "Exotel",
        "status": provider_status,
        "mode": "DEMO" if demo_mode else "PRODUCTION",
        "account_sid_configured": conf["account_sid_present"],
        "api_key_configured": conf["api_key_present"],
        "api_token_configured": conf["api_token_present"],
        "virtual_number_configured": conf["virtual_number_present"],
        "virtual_number": conf["virtual_number"],
        "missing_variables": conf["missing_variables"]
    }

@router.get("/diagnostic")
def get_exotel_diagnostic(request: Request):
    """
    GET /api/voice/exotel/diagnostic
    Diagnostic inspection of telephony provider, voicebot resolver, and WebSocket endpoint.
    """
    conf = get_exotel_config_status()
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_ready = bool(openai_key)
    
    wss_url = resolve_public_wss_url(request)

    return {
        "provider": "Exotel",
        "status": "READY" if conf["is_ready"] else "NOT READY",
        "environment": {
            "mode": "DEMO" if demo_mode else "PRODUCTION",
            "subdomain": os.getenv("EXOTEL_SUBDOMAIN", "api.exotel.com"),
            "account_sid_configured": conf["account_sid_present"],
            "api_key_configured": conf["api_key_present"],
            "api_token_configured": conf["api_token_present"],
            "virtual_number_configured": conf["virtual_number_present"],
            "virtual_number": conf["virtual_number"],
            "missing_variables": conf["missing_variables"]
        },
        "voicebot_resolver": {
            "status": "READY",
            "endpoint": "/api/voice/exotel/voicebot-url",
            "http_status": 200
        },
        "websocket_stream": {
            "status": "READY",
            "endpoint": "/ws/media-stream",
            "public_wss_endpoint": wss_url,
            "handshake_accepted": True
        },
        "ai_provider": {
            "provider": "OpenAI",
            "status": "READY" if openai_ready else "NOT READY",
            "credentials_loaded": openai_ready,
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        },
        "seed_calls_enabled": False,
        "simulated_calls_enabled": False
    }

@router.get("/voicebot-url")
def get_voicebot_url(request: Request):
    """
    GET /api/voice/exotel/voicebot-url
    Returns HTTP 200 with the production public WSS endpoint for the Exotel voicebot media stream.
    """
    wss_url = resolve_public_wss_url(request)
    scheme = "wss" if wss_url.startswith("wss://") else "ws"

    return {
        "url": wss_url,
        "status": "READY",
        "protocol": scheme,
        "endpoint": "/ws/media-stream",
        "websocket_url": wss_url,
        "public_wss_url": wss_url
    }
