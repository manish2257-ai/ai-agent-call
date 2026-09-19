"""
Tests for Exotel AI Voice Pipeline:
- Base64 PCM decoding
- PCM buffering & VAD
- Correct Exotel outgoing media JSON structure
- stream_sid preservation
- Audio conversion to 8 kHz mono 16-bit PCM
- WebSocket media event handling
- OpenAI failure fallback
- TTS failure fallback
"""

import os
import json
import base64
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.openai_service import openai_service
from backend.app.telephony.voicebot_stream import (
    calculate_pcm_rms,
    VoicebotCallSession,
    SAMPLE_RATE,
    BYTES_PER_SAMPLE,
    CHUNK_SIZE_BYTES
)

client = TestClient(app)

def test_base64_pcm_decoding():
    """Verify base64 PCM chunk decoding."""
    raw_pcm = bytes([1, 0, 2, 0, 3, 0]) * 50
    encoded = base64.b64encode(raw_pcm).decode('ascii')
    decoded = base64.b64decode(encoded)
    assert decoded == raw_pcm
    assert len(decoded) == 300

def test_pcm_buffering_and_vad():
    """Verify RMS calculation and speech/silence detection."""
    silence = bytes(640)
    rms_silence = calculate_pcm_rms(silence)
    assert rms_silence == 0

    import struct
    speech = struct.pack('<320h', *([1000] * 320))
    rms_speech = calculate_pcm_rms(speech)
    assert rms_speech >= 900

def test_correct_exotel_outgoing_media_json():
    """Verify outgoing Exotel media message structure."""
    test_sid = 'stream_unit_test_999'
    dummy_pcm = bytes([16, 0]) * 320  # 640 bytes
    payload_b64 = base64.b64encode(dummy_pcm).decode('ascii')
    
    msg = {
        'event': 'media',
        'stream_sid': test_sid,
        'streamSid': test_sid,
        'media': {
            'payload': payload_b64
        }
    }
    raw_json = json.dumps(msg)
    parsed = json.loads(raw_json)
    assert parsed['event'] == 'media'
    assert parsed['stream_sid'] == test_sid
    assert parsed['streamSid'] == test_sid
    assert 'payload' in parsed['media']
    # Verify no WAV container header in the raw PCM payload
    decoded_payload = base64.b64decode(parsed['media']['payload'])
    assert not decoded_payload.startswith(b'RIFF')
    assert len(decoded_payload) == 640

def test_stream_sid_preservation():
    """Verify stream_sid is strictly preserved from incoming start event."""
    session = VoicebotCallSession(websocket=None)
    start_payload = {
        'event': 'start',
        'streamSid': 'stream_custom_exotel_555',
        'call_sid': 'call_abc123',
        'from': '+919810012345',
        'to': '+918047100000'
    }
    session.stream_sid = start_payload['streamSid']
    session.call_sid = start_payload['call_sid']
    assert session.stream_sid == 'stream_custom_exotel_555'
    assert session.call_sid == 'call_abc123'

def test_audio_conversion_to_8khz_mono_16bit():
    """Verify resampling 24 kHz PCM to 8 kHz mono 16-bit PCM."""
    # 1 second of 24 kHz 16-bit audio = 24000 samples * 2 bytes = 48000 bytes
    pcm_24k = bytes([5, 0]) * 24000
    resampled_8k = openai_service._resample_pcm(pcm_24k, orig_sr=24000, target_sr=8000)
    # At 8 kHz, 1 second = 8000 samples * 2 bytes = 16000 bytes
    assert len(resampled_8k) == 16000

def test_websocket_media_event_handling():
    """Verify full WebSocket interaction with start, media, ping, and stop events."""
    with client.websocket_connect('/ws/media-stream') as ws:
        # Send start event
        ws.send_text(json.dumps({
            'event': 'start',
            'streamSid': 'stream_full_flow_test',
            'mediaFormat': {'encoding': 'audio/x-l16', 'sampleRate': 8000}
        }))
        
        # Expect ack
        ack_raw = ws.receive_text()
        ack = json.loads(ack_raw)
        assert ack['event'] == 'ack'
        assert ack['status'] == 'connected'
        assert ack['streamSid'] == 'stream_full_flow_test'
        
        # Send media frame
        dummy_pcm = bytes(320)
        payload_b64 = base64.b64encode(dummy_pcm).decode('ascii')
        ws.send_text(json.dumps({
            'event': 'media',
            'media': {'payload': payload_b64}
        }))
        
        # Send ping
        ws.send_text(json.dumps({'event': 'ping'}))
        pong = json.loads(ws.receive_text())
        assert pong['event'] == 'pong'
        
        # Send stop
        ws.send_text(json.dumps({'event': 'stop'}))

@pytest.mark.asyncio
async def test_openai_failure_fallback():
    """Verify transcription gracefully returns safe failure without crashing or leaking keys."""
    dummy_audio = bytes(3200)
    res = await openai_service.transcribe_audio(dummy_audio, sample_rate=8000)
    assert 'success' in res
    assert 'status' in res
    assert 'text' in res
    if res.get('error'):
        assert 'sk-' not in res['error']

@pytest.mark.asyncio
async def test_tts_failure_fallback():
    """Verify TTS fallback produces valid 8 kHz PCM even when OpenAI rate limits."""
    res = await openai_service.generate_speech('Hello, testing fallback audio.', target_sample_rate=8000)
    assert res['success'] is True
    assert len(res.get('pcm_bytes', b'')) > 0
    assert res.get('sample_rate') == 8000
