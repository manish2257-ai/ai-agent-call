import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.session import Base
from backend.app.models.models import User, UserSettings, Call, Contact, UrgencyRuleModel
from backend.app.services.urgency_classifier import UrgencyClassifier
from backend.app.services.sms_service import SMSService
from backend.app.services.call_manager import CallManager
from backend.app.core.security import get_password_hash, verify_password, create_access_token, decode_token

# Test In-Memory SQLite DB
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)

# 1. Authentication & Security Tests
def test_password_hashing():
    pw = "secret_pass_123"
    hashed = get_password_hash(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_flow():
    user_id = 42
    token = create_access_token(subject=user_id)
    assert token is not None
    payload = decode_token(token)
    assert payload is not None
    assert payload.get("sub") == str(user_id)

# 2. Urgency Classification Tests
@pytest.mark.asyncio
async def test_urgency_classification_high():
    text = "Rahul: The website is down and customers cannot place orders immediately."
    res = await UrgencyClassifier.classify(transcript_text=text, caller_name="Rahul")
    assert res["urgency"] == "HIGH"
    assert "outage" in res["reason"].lower() or "disruption" in res["reason"].lower()
    assert res["callback_required"] is True

@pytest.mark.asyncio
async def test_urgency_classification_critical():
    text = "Caller: There is a serious fire in the server room and building emergency!"
    res = await UrgencyClassifier.classify(transcript_text=text)
    assert res["urgency"] == "CRITICAL"
    assert "emergency" in res["reason"].lower()

@pytest.mark.asyncio
async def test_urgency_classification_low():
    text = "Caller: Hello, I just wanted to ask what are your normal working hours next week?"
    res = await UrgencyClassifier.classify(transcript_text=text)
    assert res["urgency"] == "LOW"

# 3. SMS Alert Template & Cooldown Tests
def test_sms_formatting():
    msg = SMSService.format_alert_message(
        template=None,
        caller="Rahul",
        number="+919876543210",
        urgency="HIGH",
        reason="Website is down",
        summary="Users cannot checkout",
        time_str="10:45 AM"
    )
    assert "Rahul" in msg
    assert "+919876543210" in msg
    assert "HIGH" in msg
    assert "Website is down" in msg
    assert "10:45 AM" in msg

def test_sms_cooldown():
    caller_key = "+919999888877_HIGH"
    SMSService.record_alert_dispatched(caller_key)
    # Inside 5 min cooldown -> True
    assert SMSService.is_in_cooldown(caller_key, cooldown_minutes=5) is True
    # If cooldown is 0 min -> False
    assert SMSService.is_in_cooldown(caller_key, cooldown_minutes=0) is False

# 4. Call Creation & Database Operations Test
@pytest.mark.asyncio
async def test_call_lifecycle(db):
    user = User(
        email="test_owner@callagent.com",
        hashed_password=get_password_hash("pass"),
        full_name="Owner",
        phone_number="+19876543210"
    )
    db.add(user)
    db.commit()

    settings = UserSettings(user_id=user.id, owner_phone_number="+19876543210")
    db.add(settings)
    db.commit()

    # VIP Contact
    vip = Contact(
        user_id=user.id,
        name="Rahul Verma",
        phone_number="+919876543210",
        category="Client",
        always_alert=True
    )
    db.add(vip)
    db.commit()

    # Create call
    call = CallManager.create_incoming_call(
        db=db,
        user_id=user.id,
        caller_number="+919876543210"
    )
    assert call.id.startswith("call_")
    assert call.caller_name == "Rahul Verma"

    # Process call
    messages = [
        {"speaker": "AI", "content": "Hello, how can I help?"},
        {"speaker": "Caller", "content": "Our website crashed and orders failed."}
    ]
    res = await CallManager.process_completed_call(
        db=db,
        call_id=call.id,
        messages=messages,
        duration_seconds=30
    )
    assert res["urgency"] == "HIGH"
    assert res["sms_alert"] is not None

# 5. Production Health and WhatsApp Webhook Tests
def test_health_endpoint():
    from fastapi.testclient import TestClient
    try:
        from app.main import app
    except ImportError:
        from backend.app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_whatsapp_webhook_verification():
    from fastapi.testclient import TestClient
    try:
        from app.main import app
        from app.core.config import settings
    except ImportError:
        from backend.app.main import app
        from backend.app.core.config import settings
    client = TestClient(app)

    # Valid token verification
    response = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN,
            "hub.challenge": "1158201444"
        }
    )
    assert response.status_code == 200
    assert response.text == "1158201444"

    # Invalid token verification
    bad_response = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "1158201444"
        }
    )
    assert bad_response.status_code == 403

def test_whatsapp_webhook_event_ingestion():
    from fastapi.testclient import TestClient
    try:
        from app.main import app
    except ImportError:
        from backend.app.main import app
    client = TestClient(app)

    payload = {
        "object": "whatsapp_business_account",
        "entry": [{"id": "12345", "changes": [{"value": {"messaging_product": "whatsapp"}}]}]
    }
    response = client.post("/webhooks/whatsapp", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# 6. Twilio WhatsApp Service & API Tests
def test_twilio_whatsapp_status_endpoint():
    from fastapi.testclient import TestClient
    try:
        from app.main import app
    except ImportError:
        from backend.app.main import app
    client = TestClient(app)
    response = client.get("/api/whatsapp/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "status" in data
    # Ensure auth token is NOT present in any response key or value
    assert "auth_token" not in data
    assert "TWILIO_AUTH_TOKEN" not in data

def test_twilio_whatsapp_test_unconfigured(monkeypatch):
    from fastapi.testclient import TestClient
    try:
        from app.main import app
    except ImportError:
        from backend.app.main import app
    
    # Ensure environment variables are clear
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TELEPHONY_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("TELEPHONY_AUTH_TOKEN", raising=False)

    client = TestClient(app)
    response = client.post("/api/whatsapp/test", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "incomplete" in data["message"].lower()

def test_twilio_whatsapp_send_with_mock_client(monkeypatch):
    import os
    from unittest.mock import MagicMock
    try:
        from app.services.twilio_whatsapp_service import twilio_whatsapp_service
    except ImportError:
        from backend.app.services.twilio_whatsapp_service import twilio_whatsapp_service

    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACtest1234567890abcdef1234567890ab")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "mock_auth_token_secret_value")

    # Mock Twilio Client
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.sid = "SM1234567890abcdef1234567890abcdef"
    mock_msg.status = "queued"
    mock_client.messages.create.return_value = mock_msg

    monkeypatch.setattr("twilio.rest.Client", lambda sid, token: mock_client)

    result = twilio_whatsapp_service.send_whatsapp_message(
        to="whatsapp:+917367966177",
        from_="whatsapp:+17372508034",
        content_sid="HXfe5ab5f00277942d4d4200328b4d403c",
        bypass_cooldown=True
    )

    assert result["success"] is True
    assert result["sid"] == "SM1234567890abcdef1234567890abcdef"
    assert result["status"] == "queued"
    # Never expose auth token
    assert "mock_auth_token_secret_value" not in str(result)

def test_twilio_whatsapp_cooldown_prevention(monkeypatch):
    from unittest.mock import MagicMock
    try:
        from app.services.twilio_whatsapp_service import twilio_whatsapp_service
    except ImportError:
        from backend.app.services.twilio_whatsapp_service import twilio_whatsapp_service

    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACtest1234567890abcdef1234567890ab")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "mock_auth_token_secret_value")

    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.sid = "SM1234567890abcdef1234567890abcdef"
    mock_msg.status = "queued"
    mock_client.messages.create.return_value = mock_msg
    monkeypatch.setattr("twilio.rest.Client", lambda sid, token: mock_client)

    # First send with call_id
    res1 = twilio_whatsapp_service.send_whatsapp_message(
        to="whatsapp:+917367966177",
        call_id="call_test_loop_123",
        bypass_cooldown=False
    )
    assert res1["success"] is True

    # Immediate second send for the same call should be suppressed by cooldown
    res2 = twilio_whatsapp_service.send_whatsapp_message(
        to="whatsapp:+917367966177",
        call_id="call_test_loop_123",
        bypass_cooldown=False
    )
    assert res2["success"] is True
    assert res2["status"] == "SUPPRESSED_BY_COOLDOWN"


