import pytest
import asyncio
import base64
import json
from unittest.mock import AsyncMock, MagicMock, patch
from backend.app.telephony.voicebot_stream import (
    VoicebotCallSession,
    calculate_rms,
    BYTES_PER_FRAME,
    SAMPLE_RATE
)

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []

    async def send_text(self, text: str):
        self.sent_messages.append(text)

@pytest.mark.asyncio
async def test_calculate_rms():
    # Test silence
    silence = b"\x00" * 320
    assert calculate_rms(silence) == 0.0

    # Test sine tone / high energy
    tone = b"\x7f\x00" * 160
    assert calculate_rms(tone) > 0.0

@pytest.mark.asyncio
async def test_voicebot_session_start():
    ws = MockWebSocket()
    session = VoicebotCallSession(ws)

    start_event = {
        "event": "start",
        "streamSid": "stream_test_12345",
        "callSid": "call_test_67890"
    }

    with patch("backend.app.telephony.voicebot_stream.openai_service.generate_speech", new_callable=AsyncMock) as mock_tts:
        # Mock 8kHz PCM speech (e.g. 640 bytes = 2 frames of 20ms)
        mock_tts.return_value = {
            "success": True,
            "pcm_audio": b"\x10\x00" * 320
        }

        await session.handle_start(start_event)
        # Yield to event loop to allow the background play_text_to_caller task to stream
        await asyncio.sleep(0.05)

        assert session.stream_sid == "stream_test_12345"
        assert len(ws.sent_messages) >= 2

        # Verify first message is ack
        first_msg = json.loads(ws.sent_messages[0])
        assert first_msg.get("event") == "ack"
        assert first_msg.get("status") == "connected"
        assert first_msg.get("streamSid") == "stream_test_12345"

        # Verify subsequent message is outgoing media frame
        media_msg = json.loads(ws.sent_messages[1])
        assert media_msg.get("event") == "media"
        assert media_msg.get("streamSid") == "stream_test_12345"
        assert "payload" in media_msg.get("media", {})

        # Verify decoded payload has correct frame size
        payload_bytes = base64.b64decode(media_msg["media"]["payload"])
        assert len(payload_bytes) == BYTES_PER_FRAME

@pytest.mark.asyncio
async def test_voicebot_session_media_vad_trigger():
    ws = MockWebSocket()
    session = VoicebotCallSession(ws)
    session.stream_sid = "stream_test_999"

    speech_chunk = b"\x50\x20" * 160
    silence_chunk = b"\x00" * 320

    with patch.object(session, "process_caller_utterance", new_callable=AsyncMock) as mock_process:
        # Feed speech frames
        for _ in range(6):
            await session.handle_media({
                "event": "media",
                "media": {"payload": base64.b64encode(speech_chunk).decode("ascii")}
            })

        assert session.speech_frames >= 4

        # Feed silence frames to trigger end of utterance
        for _ in range(26):
            await session.handle_media({
                "event": "media",
                "media": {"payload": base64.b64encode(silence_chunk).decode("ascii")}
            })

        # Yield to let async task start
        await asyncio.sleep(0.02)
        assert mock_process.called

@pytest.mark.asyncio
async def test_voicebot_session_stop():
    ws = MockWebSocket()
    session = VoicebotCallSession(ws)
    session.stream_sid = "stream_stop_test"

    stop_event = {"event": "stop", "streamSid": "stream_stop_test"}
    await session.handle_stop(stop_event)
    assert not session.is_connected
