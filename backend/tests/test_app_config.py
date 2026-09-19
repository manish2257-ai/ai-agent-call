import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_app_config():
    response = client.get("/api/app/config")
    assert response.status_code == 200
    data = response.json()

    # Core non-secret fields
    assert "telephony_provider" in data
    assert data["telephony_provider"] == "Exotel"
    assert "telephony_status" in data
    assert "virtual_number" in data
    assert "sms_provider" in data
    assert "sms_status" in data
    assert "openai_configured" in data
    assert "voicebot_status" in data
    assert "websocket_status" in data
    assert "voicebot_wss_url" in data
    assert "agent_enabled" in data
    assert "active" in data
    assert "metrics" in data

    # Verify NO secrets are leaked
    for key in ["api_key", "api_token", "password", "secret", "authorization"]:
        for k in data.keys():
            assert key not in k.lower(), f"Secret-like key {k} found in response"

    # Verify metrics structure
    metrics = data["metrics"]
    assert "calls_today" in metrics
    assert "total_calls" in metrics
    assert "urgent_escalations" in metrics
    assert "sms_alerts_sent" in metrics
    assert "avg_call_duration_seconds" in metrics
