import os
import sys
from pathlib import Path

# Ensure backend and workspace directories are in sys.path for robust imports in all runtimes
_backend_dir = str(Path(__file__).resolve().parent.parent)
_workspace_dir = str(Path(__file__).resolve().parent.parent.parent)
for _p in [_backend_dir, _workspace_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import datetime
import logging
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .database.session import engine, Base, SessionLocal
from .models.models import User, UserSettings, Call, CallSummary, CallMessage, Contact, UrgencyRuleModel, KnowledgeBaseItem
from .core.security import get_password_hash
from .api import auth, dashboard, calls, contacts, settings as settings_api, urgency, knowledge_base, webhooks, analytics, alerts, call_agent_endpoints, whatsapp_api, openai_api, exotel_voice, app_config
from .services.twilio_whatsapp_service import twilio_whatsapp_service
from .services.openai_service import openai_service
from .telephony.voicebot_stream import VoicebotCallSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AppMain")

# DB table initialization
# Moved into startup_event for production resilience against connection delays

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Production-ready AI Personal Call Agent backend with Telephony Webhooks, Structured Urgency Engine, and SMS alerts."
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(calls.router)
app.include_router(contacts.router)
app.include_router(settings_api.router)
app.include_router(urgency.router)
app.include_router(knowledge_base.router)
app.include_router(webhooks.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(call_agent_endpoints.router)
app.include_router(whatsapp_api.router)
app.include_router(openai_api.router)
app.include_router(exotel_voice.router)
app.include_router(app_config.router)

@app.websocket("/ws/media-stream")
async def websocket_media_stream(websocket: WebSocket):
    """
    WebSocket endpoint for Exotel Voicebot real-time bi-directional audio stream.
    Mounts /ws/media-stream.
    """
    await websocket.accept()
    logger.info("WebSocket media stream connection accepted.")
    session = VoicebotCallSession(websocket)
    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                logger.info("WebSocket media stream client disconnected.")
                break
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    event = data.get("event")
                    if event == "connected":
                        await session.handle_connected(data)
                    elif event == "start":
                        await session.handle_start(data)
                    elif event == "media":
                        await session.handle_media(data)
                    elif event == "dtmf":
                        await session.handle_dtmf(data)
                    elif event == "mark":
                        await session.handle_mark(data)
                    elif event == "ping":
                        await session.send_json({"event": "pong"})
                    elif event == "stop":
                        await session.handle_stop(data)
                        break
                    else:
                        await session.send_json({"event": "ack", "status": "received"})
                except json.JSONDecodeError:
                    await session.send_json({"event": "ack", "raw": message["text"]})
            elif "bytes" in message:
                # Raw audio chunk if sent in binary mode
                raw_bytes = message["bytes"]
                await session.handle_media({"media": {"payload": base64.b64encode(raw_bytes).decode("ascii")}})
    except (WebSocketDisconnect, RuntimeError):
        logger.info("WebSocket media stream connection closed cleanly.")
    except Exception as e:
        logger.warning(f"WebSocket media stream handler: {e}")
    finally:
        session.cleanup()

@app.on_event("startup")
def startup_event():
    """Seed default owner, validate configurations, and initialize tables."""
    # Validate Twilio WhatsApp Configuration
    is_valid, config_msg = twilio_whatsapp_service.validate_configuration()
    if is_valid:
        logger.info("Twilio WhatsApp service configured successfully.")
    else:
        logger.info(f"Twilio WhatsApp configuration: {config_msg}")

    # Safe startup diagnostics for OpenAI (never logs secrets)
    openai_valid, openai_msg = openai_service.validate_configuration()
    logger.info("OpenAI Startup Diagnostics: configured=%s, model=%s", openai_valid, openai_service.model)

    # Safe startup diagnostics for STT Provider (never logs secrets)
    from .services.stt_service import stt_service
    from .services.gemini_stt_service import gemini_stt_service
    logger.info("STT Provider Startup Diagnostics: STT_PROVIDER=%s, GEMINI_CONFIGURED=%s", stt_service.provider_name, "true" if gemini_stt_service.is_configured() else "false")
    if openai_valid:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                async def _startup_diag():
                    diag = await openai_service.check_api_diagnostics()
                    if diag.get("quota_exhausted"):
                        logger.warning("OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits.")
                loop.create_task(_startup_diag())
        except Exception as e:
            logger.debug("OpenAI async startup check note: %s", e)
    else:
        logger.info("OpenAI service configuration note: %s", openai_msg)

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Database schema check or table creation warning: {e}")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "manish@aicallagent.com").first()
        if not user:
            logger.info("Initializing default owner account...")
            user = User(
                email="manish@aicallagent.com",
                hashed_password=get_password_hash("password123"),
                full_name="Manish Kumar",
                phone_number=os.getenv("OWNER_PHONE_NUMBER") or None
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # User Settings
            user_settings = UserSettings(
                user_id=user.id,
                ai_phone_number=os.getenv("EXOTEL_VIRTUAL_NUMBER") or None,
                owner_phone_number=os.getenv("OWNER_PHONE_NUMBER") or None,
                greeting="Hello, you've reached Manish's AI assistant. Manish isn't available to take the call right now. I can help you with your request and pass along an important message. How can I help?",
                personality="Professional",
                urgency_threshold="HIGH",
                sms_cooldown_minutes=5,
                is_transcript_storage_enabled=True,
                is_agent_enabled=True
            )
            db.add(user_settings)
            db.commit()
            logger.info("Database initialized without demo or placeholder data.")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs",
        "demo_mode": settings.DEMO_MODE
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
