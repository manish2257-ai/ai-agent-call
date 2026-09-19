"""
Comprehensive Tests for Free / Local STT & Provider Abstractions
Verifies:
1. Speech audio reaches STT and returns transcript
2. STT handles empty speech transcript (silence)
3. Empty / short audio validation
4. STT provider failure and automatic fallback behavior (e.g. OpenAI quota exhaustion -> local STT)
5. Provider switching via environment variables (STT_PROVIDER, LLM_PROVIDER, TTS_PROVIDER)
6. Safe logging compliance ([STT] provider=..., audio_bytes=..., transcript_length=..., success/failure)
7. LLM local heuristic provider works with 0 API credits
8. TTS local provider produces valid 8000Hz PCM with 0 API credits
9. Exotel WebSocket media stream remains unaffected
"""

import os
import json
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.testclient import TestClient

try:
    from app.main import app
    from app.services.stt_service import stt_service, STTService
    from app.services.local_stt_service import local_stt_service, LocalSTTService
    from app.services.llm_service import llm_service, LLMService
    from app.services.tts_service import tts_service, TTSService
    from app.services.openai_service import openai_service
except ImportError:
    from backend.app.main import app
    from backend.app.services.stt_service import stt_service, STTService
    from backend.app.services.local_stt_service import local_stt_service, LocalSTTService
    from backend.app.services.llm_service import llm_service, LLMService
    from backend.app.services.tts_service import tts_service, TTSService
    from backend.app.services.openai_service import openai_service

# Standard 160ms of 8000Hz 16-bit PCM audio (2560 bytes)
VALID_SPEECH_PCM = bytes([24, 0, 48, 0]) * 640


# 1. Speech Audio Reaches Local STT & Returns Transcript
@pytest.mark.asyncio
async def test_speech_audio_reaches_stt_and_returns_transcript(monkeypatch, caplog):
    monkeypatch.setenv("STT_PROVIDER", "local")

    # Mock local recognizer sync function to return a recognized phrase
    expected_transcript = "i am calling regarding a server outage"
    monkeypatch.setattr(
        local_stt_service,
        "_sync_transcribe",
        lambda model, pcm: expected_transcript
    )
    # Ensure model returns non-None
    monkeypatch.setattr(local_stt_service, "get_model", AsyncMock(return_value=MagicMock()))
    monkeypatch.setattr(local_stt_service, "is_available", lambda: True)

    with caplog.at_level(logging.INFO):
        result = await stt_service.transcribe_audio(VALID_SPEECH_PCM, sample_rate=8000)

    assert result["success"] is True
    assert result["text"] == expected_transcript
    assert result["status"] == "SUCCESS"
    assert result["provider"] == "local"

    # Verify safe required log messages
    log_text = caplog.text
    assert "[STT] provider=local" in log_text
    assert f"[STT] audio_bytes={len(VALID_SPEECH_PCM)}" in log_text
    assert f"[STT] transcript_length={len(expected_transcript)}" in log_text
    assert "[STT] success" in log_text

    # Strict Privacy: Transcript content must NOT be logged in STT logs
    assert expected_transcript not in log_text


# 2. Empty Transcript Handling
@pytest.mark.asyncio
async def test_stt_handles_empty_transcript(monkeypatch, caplog):
    monkeypatch.setenv("STT_PROVIDER", "local")

    # Recognizer returns empty string (silence / non-verbal sound)
    monkeypatch.setattr(local_stt_service, "_sync_transcribe", lambda model, pcm: "")
    monkeypatch.setattr(local_stt_service, "get_model", AsyncMock(return_value=MagicMock()))
    monkeypatch.setattr(local_stt_service, "is_available", lambda: True)

    with caplog.at_level(logging.INFO):
        result = await stt_service.transcribe_audio(VALID_SPEECH_PCM, sample_rate=8000)

    assert result["success"] is True
    assert result["text"] == ""
    assert result["status"] == "SUCCESS"

    log_text = caplog.text
    assert "[STT] transcript_length=0" in log_text
    assert "[STT] success" in log_text


# 3. Empty or Short Audio Validation
@pytest.mark.asyncio
async def test_stt_handles_empty_or_short_audio(monkeypatch, caplog):
    monkeypatch.setenv("STT_PROVIDER", "local")

    # A) Completely empty audio
    with caplog.at_level(logging.INFO):
        res_empty = await stt_service.transcribe_audio(b"", sample_rate=8000)
    assert res_empty["success"] is False
    assert res_empty["status"] == "EMPTY_AUDIO"
    assert "[STT] failure: EMPTY_AUDIO" in caplog.text

    # B) Audio shorter than 20ms frame (< 320 bytes)
    res_short = await local_stt_service.transcribe_audio(b"\x00" * 100, sample_rate=8000)
    assert res_short["success"] is False
    assert res_short["status"] == "INVALID_AUDIO"


# 4. STT Provider Failure and Fallback Behavior
@pytest.mark.asyncio
async def test_stt_provider_failure_and_fallback(monkeypatch, caplog):
    # Caller has STT_PROVIDER=openai, but OpenAI quota is exhausted (HTTP 429)
    monkeypatch.setenv("STT_PROVIDER", "openai")

    # Mock OpenAI to return INSUFFICIENT_QUOTA failure
    mock_openai_fail = {
        "success": False,
        "text": "",
        "status": "INSUFFICIENT_QUOTA",
        "error": "OpenAI API quota/credits exhausted."
    }
    monkeypatch.setattr(openai_service, "transcribe_audio", AsyncMock(return_value=mock_openai_fail))

    # Mock local STT service to succeed as fallback
    fallback_transcript = "emergency server is down"
    monkeypatch.setattr(local_stt_service, "is_available", lambda: True)
    monkeypatch.setattr(local_stt_service, "transcribe_audio", AsyncMock(return_value={
        "success": True,
        "text": fallback_transcript,
        "status": "SUCCESS",
        "provider": "local"
    }))

    with caplog.at_level(logging.INFO):
        result = await stt_service.transcribe_audio(VALID_SPEECH_PCM, sample_rate=8000)

    # Automatic fallback should have engaged and succeeded
    assert result["success"] is True
    assert result["text"] == fallback_transcript
    assert result["provider"] == "local"

    log_text = caplog.text
    assert "OpenAI STT encountered INSUFFICIENT_QUOTA; falling back to free/local STT" in log_text
    assert "[STT] fallback -> local" in log_text
    assert "[STT] success" in log_text


# 5. Provider Switching via Environment Variables
def test_provider_resolution_from_env(monkeypatch):
    mgr = STTService()

    monkeypatch.setenv("STT_PROVIDER", "local")
    assert mgr.provider_name == "local"

    monkeypatch.setenv("STT_PROVIDER", "free")
    assert mgr.provider_name == "local"

    monkeypatch.setenv("STT_PROVIDER", "vosk")
    assert mgr.provider_name == "local"

    monkeypatch.setenv("STT_PROVIDER", "gemini")
    assert mgr.provider_name == "gemini"

    monkeypatch.setenv("STT_PROVIDER", "openai")
    assert mgr.provider_name == "openai"


# 6. LLM Provider Local Heuristics
@pytest.mark.asyncio
async def test_llm_local_heuristics(monkeypatch, caplog):
    monkeypatch.setenv("LLM_PROVIDER", "local")

    with caplog.at_level(logging.INFO):
        res_outage = await llm_service.generate_response(
            messages=[{"role": "user", "content": "Our production database is down"}],
            caller_speech="Our production database is down"
        )
    assert res_outage["success"] is True
    assert "outage" in res_outage["content"].lower()
    assert "[LLM] provider=local" in caplog.text
    assert "[LLM] success" in caplog.text

    # Anti-impersonation test
    res_human = await llm_service.generate_response(
        messages=[],
        caller_speech="Are you a real person?"
    )
    assert "No. I am an AI assistant" in res_human["content"]


# 7. TTS Provider Local Synthesis
@pytest.mark.asyncio
async def test_tts_local_synthesis(monkeypatch, caplog):
    monkeypatch.setenv("TTS_PROVIDER", "local")

    with caplog.at_level(logging.INFO):
        res = await tts_service.generate_speech("Hello, thank you for calling.")

    assert res["success"] is True
    assert len(res["pcm_audio"]) > 0
    assert res["sample_rate"] == 8000
    assert res["provider"] == "local"

    log_text = caplog.text
    assert "[TTS] provider=local" in log_text
    assert "[TTS] success" in log_text


# 8. Exotel WebSocket Media Stream Remains Unaffected
def test_exotel_websocket_unaffected():
    client = TestClient(app)
    with client.websocket_connect("/ws/media-stream") as ws:
        # Exotel 'start' event with streamSid
        ws.send_text(json.dumps({
            "event": "start",
            "streamSid": "MZtest_stream_unaffected_1234",
            "mediaFormat": {"encoding": "audio/x-mulaw", "sampleRate": 8000}
        }))
        ack = json.loads(ws.receive_text())
        assert ack["event"] == "ack"
        assert ack["status"] == "connected"
        assert ack["streamSid"] == "MZtest_stream_unaffected_1234"

        # Exotel 'ping' event
        ws.send_text(json.dumps({"event": "ping"}))
        # Drain any greeting media packets that may arrive concurrently before pong
        while True:
            resp = json.loads(ws.receive_text())
            if resp.get("event") == "pong":
                break
        assert resp["event"] == "pong"

        # Exotel 'media' chunk
        ws.send_text(json.dumps({
            "event": "media",
            "media": {"payload": "AA=="}
        }))

        # Exotel 'stop' event
        ws.send_text(json.dumps({"event": "stop"}))
