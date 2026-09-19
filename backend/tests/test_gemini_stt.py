"""
Unit Tests for Gemini Speech-To-Text (STT) and Provider Abstraction
Tests:
1. Gemini STT success
2. Gemini authentication failure
3. Gemini quota/rate-limit failure
4. Empty and short audio handling
5. Provider selection and diagnostic logging (verifying transcript is never logged)
6. OpenAI provider remains fully functional
"""

import pytest
import logging
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

try:
    from app.services.gemini_stt_service import GeminiSTTService, gemini_stt_service
    from app.services.stt_service import STTService, stt_service
    from app.services.openai_service import OpenAIService, openai_service
except ImportError:
    from backend.app.services.gemini_stt_service import GeminiSTTService, gemini_stt_service
    from backend.app.services.stt_service import STTService, stt_service
    from backend.app.services.openai_service import OpenAIService, openai_service


# Standard 40ms of 8kHz 16-bit PCM (640 bytes)
SAMPLE_PCM = bytes([16, 0]) * 320


# 1. Gemini STT Success
@pytest.mark.asyncio
async def test_gemini_stt_success(monkeypatch):
    mock_key = "AIzaSyTestValidGeminiApiKey1234567890"
    monkeypatch.setenv("GEMINI_API_KEY", mock_key)

    service = GeminiSTTService()
    assert service.is_configured() is True

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Hello, I am calling about scheduling an appointment."}
                    ],
                    "role": "model"
                },
                "finishReason": "STOP"
            }
        ]
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: mock_client)

    result = await service.transcribe_audio(SAMPLE_PCM)

    assert result["success"] is True
    assert result["status"] == "SUCCESS"
    assert result["text"] == "Hello, I am calling about scheduling an appointment."
    # Strict secrecy: ensure key is NEVER in result dictionary
    assert mock_key not in str(result)


# 2. Gemini Authentication Failure
@pytest.mark.asyncio
async def test_gemini_stt_authentication_failure(monkeypatch):
    mock_key = "AIzaSyInvalidKeyForTest987654321"
    monkeypatch.setenv("GEMINI_API_KEY", mock_key)

    service = GeminiSTTService()

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = '{"error": {"code": 401, "message": "API_KEY_INVALID", "status": "UNAUTHENTICATED"}}'
    mock_response.json.return_value = {"error": {"code": 401, "message": "API_KEY_INVALID"}}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: mock_client)

    result = await service.transcribe_audio(SAMPLE_PCM)

    assert result["success"] is False
    assert result["status"] == "AUTHENTICATION_FAILED"
    assert "authentication failed" in result["error"].lower()
    # Key must not be leaked
    assert mock_key not in str(result)


# 3. Gemini Quota / Rate-Limit Failure
@pytest.mark.asyncio
async def test_gemini_stt_quota_rate_limit_failure(monkeypatch):
    mock_key = "AIzaSyQuotaExhaustedKey123456789"
    monkeypatch.setenv("GEMINI_API_KEY", mock_key)

    service = GeminiSTTService()

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = '{"error": {"code": 429, "message": "Resource has been exhausted (check quota).", "status": "RESOURCE_EXHAUSTED"}}'
    mock_response.json.return_value = {"error": {"code": 429, "message": "RESOURCE_EXHAUSTED"}}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: mock_client)

    result = await service.transcribe_audio(SAMPLE_PCM)

    assert result["success"] is False
    assert result["status"] == "INSUFFICIENT_QUOTA"
    assert "rate limit or quota exceeded" in result["error"].lower()
    assert mock_key not in str(result)


# 4. Empty and Short Audio Handling
@pytest.mark.asyncio
async def test_gemini_stt_empty_and_short_audio(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyDummyKeyForAudioTest123")
    service = GeminiSTTService()

    # Empty audio
    empty_result = await service.transcribe_audio(b"")
    assert empty_result["success"] is False
    assert empty_result["status"] == "EMPTY_AUDIO"

    # Too short audio (< 320 bytes)
    short_result = await service.transcribe_audio(b"\x00" * 100)
    assert short_result["success"] is False
    assert short_result["status"] == "INVALID_AUDIO"


# 5. Provider Selection and Safe Diagnostics
@pytest.mark.asyncio
async def test_stt_provider_selection_and_diagnostics(monkeypatch, caplog):
    mock_key = "AIzaSyDiagnosticsTestKey123456"
    monkeypatch.setenv("GEMINI_API_KEY", mock_key)

    # A) Test STT_PROVIDER=gemini selection
    monkeypatch.setenv("STT_PROVIDER", "gemini")
    stt_mgr = STTService()
    assert stt_mgr.provider_name == "gemini"

    # B) Test STT_PROVIDER=openai selection
    monkeypatch.setenv("STT_PROVIDER", "openai")
    assert stt_mgr.provider_name == "openai"

    # C) Verify Safe Diagnostics Emission and Zero Transcript Logging
    monkeypatch.setenv("STT_PROVIDER", "gemini")
    mock_response = MagicMock()
    mock_response.status_code = 200
    sensitive_transcript = "Secret caller text that should never be logged directly"
    mock_response.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": sensitive_transcript}]}}
        ]
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: mock_client)

    with caplog.at_level(logging.INFO):
        res = await stt_mgr.transcribe_audio(SAMPLE_PCM)

    assert res["success"] is True
    assert res["text"] == sensitive_transcript

    # Verify required diagnostic messages appear in logs
    log_text = caplog.text
    assert "STT_PROVIDER = gemini" in log_text
    assert "GEMINI_CONFIGURED = true" in log_text
    assert "STT_REQUEST = sent" in log_text
    assert "STT_RESULT = success" in log_text

    # CRITICAL: Confirm sensitive transcript was NOT logged
    assert sensitive_transcript not in log_text
    # Confirm secret API key was NOT logged
    assert mock_key not in log_text


# 6. OpenAI Provider Remains Functional
@pytest.mark.asyncio
async def test_openai_provider_remains_functional(monkeypatch):
    mock_key = "sk-proj-test-openai-key-1234567890"
    monkeypatch.setenv("OPENAI_API_KEY", mock_key)
    monkeypatch.setenv("STT_PROVIDER", "openai")

    # Verify OpenAI service still transcribes directly
    mock_client = AsyncMock()
    mock_transcript = MagicMock()
    mock_transcript.text = "Hello from OpenAI Whisper"
    mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_transcript)

    monkeypatch.setattr("openai.AsyncOpenAI", lambda **kwargs: mock_client)
    try:
        import app.services.openai_service as oai_module
    except ImportError:
        import backend.app.services.openai_service as oai_module
    monkeypatch.setattr(oai_module, "AsyncOpenAI", lambda **kwargs: mock_client)

    # 1. Direct OpenAI service call
    openai_res = await openai_service.transcribe_audio(SAMPLE_PCM)
    assert openai_res["success"] is True
    assert openai_res["status"] == "SUCCESS"
    assert openai_res["text"] == "Hello from OpenAI Whisper"

    # 2. STT Service delegation when STT_PROVIDER=openai
    stt_mgr = STTService()
    assert stt_mgr.provider_name == "openai"
    routed_res = await stt_mgr.transcribe_audio(SAMPLE_PCM)
    assert routed_res["success"] is True
    assert routed_res["text"] == "Hello from OpenAI Whisper"
