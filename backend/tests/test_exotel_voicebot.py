"""
Comprehensive Test Suite for Exotel Production Voicebot Endpoints
Tests:
- GET /health
- GET /api/voice/exotel/status
- GET /api/voice/exotel/diagnostic
- GET /api/voice/exotel/voicebot-url
- WebSocket /ws/media-stream handshake & message protocol
- Credentials detection without secret leakage
- Ready state validation
- Exotel XML generation & telephony response builders
- Webhook signature verification
"""

import os
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.telephony.exotel_telephony import exotel_service

client = TestClient(app)

def test_health_endpoint():
    """Verify health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") in ["ok", "healthy"]

def test_exotel_status_endpoint():
    """Verify GET /api/voice/exotel/status schema and fields."""
    response = client.get("/api/voice/exotel/status")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "Exotel"
    assert "status" in data
    assert data["mode"] in ["PRODUCTION", "DEMO"]
    assert "account_sid_configured" in data
    assert "api_key_configured" in data
    assert "api_token_configured" in data
    assert "virtual_number_configured" in data
    # Verify no secret values are exposed
    for key in ["api_key", "api_token", "account_sid"]:
        assert key not in data

def test_exotel_diagnostic_endpoint():
    """Verify GET /api/voice/exotel/diagnostic report."""
    response = client.get("/api/voice/exotel/diagnostic")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "Exotel"
    assert "environment" in data
    assert data["voicebot_resolver"]["status"] == "READY"
    assert data["voicebot_resolver"]["http_status"] == 200
    assert data["websocket_stream"]["status"] == "READY"
    assert data["websocket_stream"]["endpoint"] == "/ws/media-stream"
    assert data["websocket_stream"]["public_wss_endpoint"].startswith("wss://") or data["websocket_stream"]["public_wss_endpoint"].startswith("ws://")
    assert "ai_provider" in data
    assert data["seed_calls_enabled"] is False
    assert data["simulated_calls_enabled"] is False

def test_exotel_voicebot_url_resolver():
    """Verify GET /api/voice/exotel/voicebot-url returns 200 and public WSS endpoint."""
    headers = {
        "x-forwarded-host": "ais-dev-drq6zz2gzpkest44ecny22-192566711824.asia-east1.run.app",
        "x-forwarded-proto": "https"
    }
    response = client.get("/api/voice/exotel/voicebot-url", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "wss://ais-dev-drq6zz2gzpkest44ecny22-192566711824.asia-east1.run.app/ws/media-stream"
    assert data["url"].startswith("wss://")
    assert data["status"] == "READY"
    assert data["protocol"] == "wss"
    assert data["endpoint"] == "/ws/media-stream"
    assert data["websocket_url"] == data["url"]
    assert data["public_wss_url"] == data["url"]

def test_websocket_media_stream_handshake():
    """Verify WebSocket /ws/media-stream accepts connections and handles telephony events."""
    with client.websocket_connect("/ws/media-stream") as ws:
        # 1. Send start event
        ws.send_text(json.dumps({
            "event": "start",
            "streamSid": "stream_test_abc123",
            "mediaFormat": {"encoding": "audio/x-mulaw", "sampleRate": 8000}
        }))
        ack = json.loads(ws.receive_text())
        assert ack["event"] == "ack"
        assert ack["status"] == "connected"
        assert ack["streamSid"] == "stream_test_abc123"

        # 2. Send ping event
        ws.send_text(json.dumps({"event": "ping"}))
        pong = json.loads(ws.receive_text())
        assert pong["event"] == "pong"

        # 3. Send audio media packet (should not error)
        ws.send_text(json.dumps({
            "event": "media",
            "media": {"payload": "base64audiochunk=="}
        }))

        # 4. Send stop event
        ws.send_text(json.dumps({"event": "stop"}))

def test_exotel_ready_when_credentials_present(monkeypatch):
    """Verify provider status becomes READY when valid env vars are present."""
    monkeypatch.setenv("EXOTEL_ACCOUNT_SID", "ACtest123456789")
    monkeypatch.setenv("EXOTEL_API_KEY", "key_test_abcdef")
    monkeypatch.setenv("EXOTEL_API_TOKEN", "token_test_xyz789")
    monkeypatch.setenv("EXOTEL_VIRTUAL_NUMBER", "+918047100000")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-test1234567890")

    response = client.get("/api/voice/exotel/status")
    data = response.json()
    assert data["status"] == "READY"
    assert data["account_sid_configured"] is True
    assert data["api_key_configured"] is True
    assert data["api_token_configured"] is True
    assert data["virtual_number_configured"] is True

    diag = client.get("/api/voice/exotel/diagnostic")
    diag_data = diag.json()
    assert diag_data["status"] == "READY"
    assert diag_data["ai_provider"]["credentials_loaded"] is True
    assert diag_data["ai_provider"]["status"] == "READY"

def test_exotel_voice_xml_generation():
    """Verify Exotel Voice XML generation with proper escaping."""
    xml = exotel_service.build_voice_response("Hello & Welcome to the Voicebot <Assistant>")
    assert "<Response>" in xml
    assert "<Say" in xml
    assert "Hello &amp; Welcome to the Voicebot &lt;Assistant&gt;" in xml
    assert "<Hangup/>" in xml

def test_exotel_voice_xml_gather_flow():
    """Verify Exotel Voice XML with Gather action URL."""
    action_url = "https://example.com/gather-callback"
    xml = exotel_service.build_voice_response("Please enter your pin", gather_action_url=action_url)
    assert f'<Gather action="{action_url}"' in xml
    assert "Please enter your pin" in xml

def test_exotel_transfer_xml_generation():
    """Verify Exotel transfer XML response structure."""
    target = "+919810012345"
    xml = exotel_service.build_call_transfer_response(destination_phone=target, whisper_message="Transferring call")
    assert "<Dial" in xml
    assert target in xml
    assert "Transferring call" in xml

def test_exotel_webhook_verification():
    """Verify webhook verification logic."""
    assert exotel_service.verify_webhook({}, {}) is True

def test_exotel_voicebot_url_default_fallback():
    """Verify voicebot-url resolver falls back safely when no special headers are sent."""
    response = client.get("/api/voice/exotel/voicebot-url")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert "ws" in data["protocol"]
    assert "/ws/media-stream" in data["websocket_url"]

def test_websocket_unknown_event():
    """Verify websocket gracefully acks unknown JSON events."""
    with client.websocket_connect("/ws/media-stream") as ws:
        ws.send_text(json.dumps({"event": "custom_telephony_event", "param": "val"}))
        ack = json.loads(ws.receive_text())
        assert ack["event"] == "ack"
        assert ack["status"] == "received"

def test_websocket_raw_text_handling():
    """Verify websocket handles raw non-JSON text gracefully without disconnecting."""
    with client.websocket_connect("/ws/media-stream") as ws:
        ws.send_text("RAW_TELEPHONY_HEARTBEAT")
        ack = json.loads(ws.receive_text())
        assert ack["event"] == "ack"
        assert ack["raw"] == "RAW_TELEPHONY_HEARTBEAT"
