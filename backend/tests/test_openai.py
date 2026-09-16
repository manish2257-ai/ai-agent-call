import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

try:
    from app.main import app
    from app.services.openai_service import OpenAIService, openai_service
    from app.services.ai_agent import AIAgentService
except ImportError:
    from backend.app.main import app
    from backend.app.services.openai_service import OpenAIService, openai_service
    from backend.app.services.ai_agent import AIAgentService


client = TestClient(app)


def test_openai_unconfigured_safety(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    service = OpenAIService()

    is_valid, msg = service.validate_configuration()
    assert is_valid is False
    assert "OPENAI_API_KEY" in msg
    assert service.is_configured() is False


@pytest.mark.asyncio
async def test_openai_unconfigured_chat_completion(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    service = OpenAIService()

    res = await service.chat_completion(
        messages=[{"role": "user", "content": "Hello"}]
    )
    assert res["success"] is False
    assert res["status"] == "NOT_CONFIGURED"
    assert "OPENAI_API_KEY" in res["error"]


@pytest.mark.asyncio
async def test_openai_mock_completion_success(monkeypatch):
    mock_key = "sk-proj-test-mock-key-1234567890abcdef"
    monkeypatch.setenv("OPENAI_API_KEY", mock_key)

    service = OpenAIService()
    assert service.is_configured() is True

    # Mock AsyncOpenAI client
    mock_async_client = AsyncMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello! I am your AI call assistant."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.model = "gpt-4o-mini"
    mock_async_client.chat.completions.create = AsyncMock(return_value=mock_response)

    monkeypatch.setattr("openai.AsyncOpenAI", lambda **kwargs: mock_async_client)
    try:
        import app.services.openai_service as oai_module
    except ImportError:
        import backend.app.services.openai_service as oai_module
    monkeypatch.setattr(oai_module, "AsyncOpenAI", lambda **kwargs: mock_async_client)

    res = await service.chat_completion(
        messages=[{"role": "user", "content": "Hi"}],
        model="gpt-4o-mini"
    )

    assert res["success"] is True
    assert res["status"] == "READY"
    assert res["content"] == "Hello! I am your AI call assistant."
    assert res["model"] == "gpt-4o-mini"
    # Verify API key is NOT in the response dictionary
    assert mock_key not in str(res)


def test_openai_sanitizes_errors_and_never_exposes_key():
    mock_key = "sk-proj-12345678901234567890abcdef"
    service = OpenAIService()
    monkeypatch_env = {"OPENAI_API_KEY": mock_key}

    # Test custom sanitizer
    raw_error = f"Error communicating with upstream https://api.openai.com using Bearer {mock_key}"
    sanitized = service._sanitize_error(raw_error)
    assert mock_key not in sanitized
    assert "[REDACTED" in sanitized


def test_openai_status_endpoint_never_exposes_key(monkeypatch):
    mock_key = "sk-proj-super-secret-key-that-must-never-be-exposed-12345"
    monkeypatch.setenv("OPENAI_API_KEY", mock_key)

    response = client.get("/api/openai/status")
    assert response.status_code == 200
    data = response.json()

    assert "configured" in data
    assert data["status"] in ("READY", "NOT_CONFIGURED")
    # CRITICAL: Confirm the secret key is never in the response payload
    assert mock_key not in response.text
    assert "api_key" not in data
    assert "OPENAI_API_KEY" not in data or "not configured" in str(data.get("message", ""))


def test_openai_health_endpoint():
    response = client.get("/api/openai/health")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_ai_agent_graceful_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # When OpenAI is unconfigured or fails, AIAgentService still returns helpful safe response
    reply = await AIAgentService.generate_response(
        messages=[{"role": "user", "content": "My website is down and orders stopped!"}],
        personality="Professional"
    )
    assert reply is not None
    assert len(reply) > 10
    assert "outage" in reply.lower() or "urgent" in reply.lower() or "manish" in reply.lower()
