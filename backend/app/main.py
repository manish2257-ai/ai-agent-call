import datetime
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .database.session import engine, Base, SessionLocal
from .models.models import User, UserSettings, Call, CallSummary, CallMessage, Contact, UrgencyRuleModel, KnowledgeBaseItem
from .core.security import get_password_hash
from .api import auth, dashboard, calls, contacts, settings as settings_api, urgency, knowledge_base, webhooks, analytics, alerts, call_agent_endpoints, whatsapp_api
from .services.twilio_whatsapp_service import twilio_whatsapp_service

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

@app.on_event("startup")
def startup_event():
    """Seed default owner, validate configurations, and initialize tables."""
    # Validate Twilio WhatsApp Configuration
    is_valid, config_msg = twilio_whatsapp_service.validate_configuration()
    if is_valid:
        logger.info("Twilio WhatsApp service configured successfully.")
    else:
        logger.info(f"Twilio WhatsApp configuration: {config_msg}")

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Database schema check or table creation warning: {e}")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "manish@aicallagent.com").first()
        if not user:
            logger.info("Seeding default owner user and demo data...")
            user = User(
                email="manish@aicallagent.com",
                hashed_password=get_password_hash("password123"),
                full_name="Manish Kumar",
                phone_number="+19876543210"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # User Settings
            user_settings = UserSettings(
                user_id=user.id,
                ai_phone_number="+18005550199",
                owner_phone_number="+19876543210",
                greeting="Hello, you've reached Manish's AI assistant. Manish isn't available to take the call right now. I can help you with your request and pass along an important message. How can I help?",
                personality="Professional",
                urgency_threshold="HIGH",
                sms_cooldown_minutes=5,
                is_transcript_storage_enabled=True,
                is_agent_enabled=True
            )
            db.add(user_settings)

            # Seed Demo Calls
            demo_call_1 = Call(
                id="call_demo_outage",
                user_id=user.id,
                caller_number="+919876543210",
                caller_name="Rahul Verma",
                status="Escalated",
                urgency="HIGH",
                duration_seconds=54,
                reason="Website outage and checkout blockage",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=35)
            )
            db.add(demo_call_1)

            demo_call_2 = Call(
                id="call_demo_enquiry",
                user_id=user.id,
                caller_number="+919811223344",
                caller_name="Priya Sharma",
                status="Completed",
                urgency="LOW",
                duration_seconds=38,
                reason="General inquiry about consulting slots",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            )
            db.add(demo_call_2)

            demo_call_3 = Call(
                id="call_demo_contract",
                user_id=user.id,
                caller_number="+919844556677",
                caller_name="Vikram Sethi",
                status="Escalated",
                urgency="HIGH",
                duration_seconds=42,
                reason="Client project contract deadline today",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5)
            )
            db.add(demo_call_3)

            db.commit()

            # Add summaries and messages
            s1 = CallSummary(
                call_id="call_demo_outage",
                summary_text="Rahul reported that the website is unavailable and customers cannot place orders.",
                action_required="Owner should investigate the website and check payment gateway.",
                callback_required=True,
                ai_outcome="Dispatched urgent SMS alert to owner."
            )
            m1 = CallMessage(call_id="call_demo_outage", speaker="AI", content="Hello, you've reached Manish's AI assistant. How can I help?", timestamp_str="10:41 AM")
            m2 = CallMessage(call_id="call_demo_outage", speaker="Caller", content="The website is down and users cannot check out.", timestamp_str="10:41 AM")
            m3 = CallMessage(call_id="call_demo_outage", speaker="AI", content="I understand. I am dispatching a HIGH priority alert to Manish immediately.", timestamp_str="10:42 AM")
            db.add_all([s1, m1, m2, m3])

            s2 = CallSummary(
                call_id="call_demo_enquiry",
                summary_text="Priya asked about business hours and consulting booking policy.",
                action_required="Sent routine info. No immediate callback needed.",
                callback_required=False,
                ai_outcome="Handled routine enquiry with approved knowledge."
            )
            db.add(s2)

            db.commit()
            logger.info("Database initialized with demo data.")
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
