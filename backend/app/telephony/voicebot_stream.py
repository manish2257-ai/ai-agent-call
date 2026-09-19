"""
Exotel Voicebot Bidirectional Audio Stream Handler
Manages real-time bi-directional audio streaming with Exotel Telephony over WebSocket.
Handles:
- Base64 8kHz 16-bit linear PCM audio streaming
- Voice Activity Detection (VAD) and silence detection
- Real-time Speech-To-Text (STT) via Whisper
- Contextual Conversational AI via OpenAI
- Low-latency Text-To-Speech (TTS) streaming in 20ms frames
- Safe diagnostic logging without exposing secrets
- Graceful error handling and local audio fallback
"""

import asyncio
import base64
import json
import logging
import math
import struct
from typing import Dict, Any, List, Optional
from ..services.openai_service import openai_service

logger = logging.getLogger("VoicebotStream")

# Audio frame specifications for telephony
SAMPLE_RATE = 8000
SAMPLE_WIDTH = 2  # 16-bit signed PCM
BYTES_PER_SAMPLE = 2
CHANNELS = 1
FRAME_DURATION_MS = 20  # standard 20ms frame
BYTES_PER_FRAME = int(SAMPLE_RATE * SAMPLE_WIDTH * (FRAME_DURATION_MS / 1000.0))  # 320 bytes
CHUNK_SIZE_BYTES = BYTES_PER_FRAME

# VAD thresholds
ENERGY_THRESHOLD = 300  # RMS threshold for voice presence
SILENCE_CONSECUTIVE_FRAMES = 25  # ~500ms of silence to mark utterance end
MIN_SPEECH_FRAMES = 4  # ~80ms minimum speech to avoid noise triggers


def calculate_rms(pcm_bytes: bytes) -> float:
    """Computes Root Mean Square (RMS) energy for 16-bit PCM samples."""
    if not pcm_bytes or len(pcm_bytes) < 2:
        return 0.0
    num_samples = len(pcm_bytes) // 2
    try:
        import audioop
        return float(audioop.rms(pcm_bytes, 2))
    except Exception:
        pass

    # Fallback calculation
    fmt = f"<{num_samples}h"
    try:
        samples = struct.unpack(fmt, pcm_bytes[:num_samples * 2])
        sum_squares = sum(s * s for s in samples)
        return math.sqrt(sum_squares / num_samples)
    except Exception:
        return 0.0


def calculate_peak_amplitude(pcm_bytes: bytes) -> int:
    """Computes peak absolute sample amplitude for 16-bit PCM samples."""
    if not pcm_bytes or len(pcm_bytes) < 2:
        return 0
    num_samples = len(pcm_bytes) // 2
    fmt = f"<{num_samples}h"
    try:
        samples = struct.unpack(fmt, pcm_bytes[:num_samples * 2])
        return max(abs(s) for s in samples)
    except Exception:
        return 0


# Alias for test suite compatibility
calculate_pcm_rms = calculate_rms


class VoicebotCallSession:
    """
    Manages state, audio buffers, VAD, and bidirectional streaming for a single Exotel voice call.
    """

    def __init__(self, websocket):
        self.websocket = websocket
        self.stream_sid: Optional[str] = None
        self.call_sid: Optional[str] = None
        self.caller_from: str = ""
        self.call_to: str = ""
        self.media_format: Dict[str, Any] = {}
        self.is_connected: bool = True
        self.is_speaking: bool = False
        self.lock = asyncio.Lock()

        # Audio buffering & VAD
        self.pcm_buffer = bytearray()
        self.speech_frames: int = 0
        self.silence_frames: int = 0

        # Diagnostics & metrics (safe numbers only, never secrets)
        self.total_media_packets: int = 0
        self.total_bytes_received: int = 0
        self.total_bytes_sent: int = 0
        self.mark_counter: int = 0
        self.dtmf_history: List[str] = []

        # Conversation history & persona
        self.system_prompt = (
            "You are Manish's AI personal call assistant answering an incoming phone call. "
            "You speak concisely, politely, and warmly in 1 to 2 short conversational sentences. "
            "Understand why the caller is calling, ask helpful follow-up questions, collect their name and callback number, "
            "and inform them you will relay their message to Manish immediately. "
            "Never ask for passwords, OTPs, PINs, or sensitive financial information."
        )
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    async def handle_connected(self, data: Dict[str, Any]) -> None:
        """Handles Exotel 'connected' event."""
        logger.info("Exotel voicebot connected event received.")
        self.is_connected = True
        await self.send_json({
            "event": "ack",
            "status": "connected"
        })

    async def handle_start(self, data: Dict[str, Any]) -> None:
        """Processes Exotel 'start' event, saves streamSid, metadata, and initiates welcome greeting."""
        start_data = data.get("start") if isinstance(data.get("start"), dict) else {}
        self.stream_sid = (
            data.get("stream_sid")
            or data.get("streamSid")
            or start_data.get("stream_sid")
            or start_data.get("streamSid")
            or "stream_production"
        )
        self.call_sid = (
            data.get("call_sid")
            or data.get("callSid")
            or start_data.get("call_sid")
            or start_data.get("callSid")
            or "call_exotel"
        )
        self.caller_from = (
            data.get("from")
            or data.get("From")
            or start_data.get("from")
            or start_data.get("From")
            or ""
        )
        self.call_to = (
            data.get("to")
            or data.get("To")
            or start_data.get("to")
            or start_data.get("To")
            or ""
        )
        self.media_format = (
            data.get("media_format")
            or data.get("mediaFormat")
            or start_data.get("media_format")
            or start_data.get("mediaFormat")
            or {"encoding": "audio/x-l16", "sampleRate": 8000}
        )

        logger.info(
            "Voicebot session started: stream_sid=%s, call_sid=%s, from=%s, to=%s",
            self.stream_sid,
            self.call_sid,
            self.caller_from,
            self.call_to,
        )

        # Reset audio buffers and state
        self.pcm_buffer.clear()
        self.speech_frames = 0
        self.silence_frames = 0
        self.total_media_packets = 0
        self.total_bytes_received = 0
        self.total_bytes_sent = 0

        # Send acknowledgment event back to Exotel (both stream_sid and streamSid preserved)
        await self.send_json({
            "event": "ack",
            "status": "connected",
            "stream_sid": self.stream_sid,
            "streamSid": self.stream_sid,
        })

        # Initial greeting
        initial_greeting = (
            "Hello, this is your AI assistant. How can I help you today?"
        )
        self.history.append({"role": "assistant", "content": initial_greeting})

        # Synthesize and stream greeting in the background
        asyncio.create_task(self.play_text_to_caller(initial_greeting))

    async def handle_media(self, data: Dict[str, Any]) -> None:
        """Processes incoming Exotel 'media' audio packet."""
        self.total_media_packets += 1
        payload = (
            data.get("media", {}).get("payload")
            if isinstance(data.get("media"), dict)
            else data.get("payload", "")
        )
        if not payload:
            return

        try:
            raw_pcm = base64.b64decode(payload)
        except Exception as e:
            logger.warning("Failed to decode incoming base64 media: %s", e)
            return

        self.total_bytes_received += len(raw_pcm)

        # If bot is actively speaking, skip processing to avoid feedback loops
        if self.is_speaking:
            return

        rms = calculate_rms(raw_pcm)
        peak = calculate_peak_amplitude(raw_pcm)

        if self.total_media_packets % 100 == 1 or rms > ENERGY_THRESHOLD:
            logger.info(
                "Inbound media diag: packet=%d, bytes=%d, rms=%.1f, peak=%d, vad_speech_frames=%d, vad_silence_frames=%d, threshold=%d",
                self.total_media_packets,
                len(raw_pcm),
                rms,
                peak,
                self.speech_frames,
                self.silence_frames,
                ENERGY_THRESHOLD,
            )

        if rms > ENERGY_THRESHOLD:
            self.speech_frames += 1
            self.silence_frames = 0
            self.pcm_buffer.extend(raw_pcm)

            # Cap buffer at 15 seconds to prevent unbounded memory growth
            if len(self.pcm_buffer) > (SAMPLE_RATE * SAMPLE_WIDTH * 15):
                utterance_pcm = bytes(self.pcm_buffer)
                self.pcm_buffer.clear()
                self.speech_frames = 0
                self.silence_frames = 0
                asyncio.create_task(self.process_caller_utterance(utterance_pcm))
        else:
            if self.speech_frames >= MIN_SPEECH_FRAMES:
                self.silence_frames += 1
                self.pcm_buffer.extend(raw_pcm)

                # End of utterance detected after consecutive silence frames
                if self.silence_frames >= SILENCE_CONSECUTIVE_FRAMES:
                    utterance_pcm = bytes(self.pcm_buffer)
                    self.pcm_buffer.clear()
                    self.speech_frames = 0
                    self.silence_frames = 0

                    # Dispatch turn processing asynchronously without blocking WS loop
                    asyncio.create_task(self.process_caller_utterance(utterance_pcm))

    async def process_caller_utterance(self, pcm_audio: bytes) -> None:
        """Runs STT, chat completion, and TTS response for an utterance without blocking WS loop."""
        async with self.lock:
            if not pcm_audio or len(pcm_audio) < BYTES_PER_FRAME * MIN_SPEECH_FRAMES:
                return

            duration_sec = len(pcm_audio) / (SAMPLE_RATE * SAMPLE_WIDTH)
            logger.info(
                "Utterance buffer submitted: stream_sid=%s, bytes=%d, duration=%.2fs, min_speech_ms=%d, silence_ms=%d",
                self.stream_sid,
                len(pcm_audio),
                duration_sec,
                MIN_SPEECH_FRAMES * FRAME_DURATION_MS,
                SILENCE_CONSECUTIVE_FRAMES * FRAME_DURATION_MS,
            )

            # 1. Speech to text via Whisper
            logger.info("STT request dispatched: stream_sid=%s, bytes=%d, duration=%.2fs, sample_rate=%d", self.stream_sid, len(pcm_audio), duration_sec, SAMPLE_RATE)
            try:
                stt_result = await openai_service.transcribe_audio(pcm_audio, sample_rate=SAMPLE_RATE)
            except Exception as e:
                logger.warning("Transcription exception: %s", openai_service._sanitize_error(str(e)))
                stt_result = {"success": False, "text": "", "error": "Transcription failed"}

            caller_text = (stt_result.get("text") or "").strip()
            stt_status = stt_result.get("status", "UNKNOWN")
            logger.info(
                "STT result received: stream_sid=%s, success=%s, transcript_length=%d, status=%s",
                self.stream_sid,
                stt_result.get("success"),
                len(caller_text),
                stt_status,
            )
            if not stt_result.get("success") or not caller_text:
                if stt_status == "INSUFFICIENT_QUOTA":
                    logger.warning(
                        "OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits. (stream_sid=%s)",
                        self.stream_sid,
                    )
                elif not stt_result.get("success"):
                    logger.warning("Transcription failed: stream_sid=%s, status=%s", self.stream_sid, stt_status)
                else:
                    logger.info("Transcription succeeded with empty speech: stream_sid=%s", self.stream_sid)
                fallback_prompt = "I'm sorry, I had trouble hearing that. Could you please repeat?"
                await self.play_text_to_caller(fallback_prompt)
                return

            logger.info("Transcription succeeded: stream_sid=%s, transcript_length=%d", self.stream_sid, len(caller_text))
            self.history.append({"role": "user", "content": caller_text})

            # 2. Chat completion
            logger.info("AI response started: stream_sid=%s", self.stream_sid)
            try:
                chat_result = await openai_service.chat_completion(
                    messages=self.history,
                    max_tokens=150,
                    temperature=0.3,
                )
            except Exception as e:
                logger.warning("AI response exception: %s", openai_service._sanitize_error(str(e)))
                chat_result = {"success": False, "content": None}

            if chat_result.get("success") and chat_result.get("content"):
                ai_reply = chat_result["content"].strip()
                logger.info("AI response succeeded: stream_sid=%s", self.stream_sid)
            else:
                logger.warning("AI response failed: stream_sid=%s; using fallback reply", self.stream_sid)
                ai_reply = "Thank you. I have recorded your message and will notify Manish right away."

            self.history.append({"role": "assistant", "content": ai_reply})

            # 3. Text to speech and streaming
            await self.play_text_to_caller(ai_reply)

    async def play_text_to_caller(self, text: str) -> None:
        """Synthesizes text and streams 20ms audio frames to Exotel."""
        logger.info("TTS started: stream_sid=%s, chars=%d", self.stream_sid, len(text))
        try:
            tts_result = await openai_service.generate_speech(text, target_sample_rate=SAMPLE_RATE)
        except Exception as e:
            logger.warning("TTS exception: %s", openai_service._sanitize_error(str(e)))
            tts_result = {"success": False, "pcm_audio": b""}

        pcm_audio = tts_result.get("pcm_audio") or tts_result.get("pcm_bytes") or b""
        if not pcm_audio:
            logger.warning("TTS failed: stream_sid=%s; falling back to tone", self.stream_sid)
            pcm_audio = (bytes([16, 0]) * 160) * 2  # 640 bytes = 40ms audio
        else:
            logger.info("TTS succeeded: stream_sid=%s, bytes=%d", self.stream_sid, len(pcm_audio))

        await self.stream_pcm_to_exotel(pcm_audio)

    async def stream_pcm_to_exotel(self, pcm_audio: bytes) -> None:
        """Paces and transmits 20ms PCM frames over WebSocket to Exotel telephony."""
        if not self.is_connected or not self.stream_sid:
            return

        # Strip WAV container header if present
        if pcm_audio.startswith(b"RIFF") and len(pcm_audio) > 44:
            pcm_audio = pcm_audio[44:]

        self.is_speaking = True
        try:
            total_bytes = len(pcm_audio)
            frame_size = BYTES_PER_FRAME  # 320 bytes = 20ms at 8kHz 16-bit mono

            for i in range(0, total_bytes, frame_size):
                if not self.is_connected:
                    break
                chunk = pcm_audio[i:i + frame_size]
                # Pad final partial frame with silence if needed
                if len(chunk) < frame_size:
                    chunk = chunk + b"\x00" * (frame_size - len(chunk))

                b64_payload = base64.b64encode(chunk).decode("ascii")
                message = {
                    "event": "media",
                    "stream_sid": self.stream_sid,
                    "streamSid": self.stream_sid,
                    "media": {
                        "payload": b64_payload,
                    },
                }
                await self.send_json(message)
                self.total_bytes_sent += len(chunk)

                # Sleep ~18ms to pace outgoing telephony stream in real time
                await asyncio.sleep(0.018)

            # Send optional mark event to track playback completion
            self.mark_counter += 1
            await self.send_json({
                "event": "mark",
                "stream_sid": self.stream_sid,
                "streamSid": self.stream_sid,
                "mark": {
                    "name": f"speech_mark_{self.mark_counter}"
                }
            })

            logger.info(
                "Streaming finished: stream_sid=%s, bytes_sent=%d",
                self.stream_sid,
                self.total_bytes_sent,
            )
        except Exception as e:
            logger.warning("Error while streaming PCM audio frames: %s", e)
        finally:
            self.is_speaking = False

    async def handle_dtmf(self, data: Dict[str, Any]) -> None:
        """Preserves and processes DTMF keypress events from caller."""
        dtmf_obj = data.get("dtmf") if isinstance(data.get("dtmf"), dict) else {}
        digit = str(dtmf_obj.get("digit") or data.get("digit") or "")
        self.dtmf_history.append(digit)
        logger.info("DTMF event received: stream_sid=%s, digit=%s", self.stream_sid, digit)

    async def handle_mark(self, data: Dict[str, Any]) -> None:
        """Handles incoming Exotel mark events."""
        mark_obj = data.get("mark") if isinstance(data.get("mark"), dict) else {}
        mark_name = mark_obj.get("name") or data.get("name") or "unknown"
        logger.info("Exotel mark event acknowledged: stream_sid=%s, mark=%s", self.stream_sid, mark_name)

    async def handle_stop(self, data: Dict[str, Any]) -> None:
        """Handles Exotel 'stop' event."""
        logger.info(
            "Voicebot session stopped: stream_sid=%s, packets_received=%d, bytes_received=%d, bytes_sent=%d",
            self.stream_sid,
            self.total_media_packets,
            self.total_bytes_received,
            self.total_bytes_sent,
        )
        self.is_connected = False
        self.pcm_buffer.clear()

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Safely transmits a JSON message over the active WebSocket."""
        if not self.is_connected or not self.websocket:
            return
        try:
            await self.websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.warning("WebSocket send_text failed: %s", e)
            self.is_connected = False

    def cleanup(self) -> None:
        """Cleans up session resources on disconnect."""
        self.is_connected = False
        self.pcm_buffer.clear()
        logger.info(
            "Voicebot session cleaned up: stream_sid=%s, total_packets=%d, bytes_received=%d, bytes_sent=%d",
            self.stream_sid,
            self.total_media_packets,
            self.total_bytes_received,
            self.total_bytes_sent,
        )
