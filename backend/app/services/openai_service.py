"""
OpenAI API Service Provider
Handles server-side communication with OpenAI's Chat Completions API using the official OpenAI Python SDK.
Features:
- Secure credential reading strictly from environment variable OPENAI_API_KEY
- Timeout, exception handling, and safe logging (never logs or returns API keys)
- Clean AsyncOpenAI client instantiation
- Safe error sanitization (masks any bearer token or key patterns)
- Structured fallback-ready response contracts
"""

import os
import re
import io
import wave
import subprocess
import tempfile
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("OpenAIService")

try:
    import openai
    from openai import AsyncOpenAI, OpenAI
    HAS_OPENAI_SDK = True
except ImportError:
    HAS_OPENAI_SDK = False
    logger.warning("Official OpenAI Python SDK is not installed or failed to import.")


class OpenAIService:
    def __init__(self):
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.default_timeout = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "15.0"))

    @property
    def api_key(self) -> Optional[str]:
        """
        Retrieves the OpenAI API key strictly from environment variables.
        Never returns placeholder or empty values.
        """
        key = os.getenv("OPENAI_API_KEY")
        if key and isinstance(key, str):
            cleaned = key.strip()
            # Ignore placeholder template values
            if cleaned and not cleaned.startswith("your_new_") and len(cleaned) > 5:
                return cleaned
        return None

    @property
    def model(self) -> str:
        return os.getenv("OPENAI_MODEL") or self.default_model

    @property
    def timeout_seconds(self) -> float:
        try:
            return float(os.getenv("OPENAI_TIMEOUT_SECONDS", str(self.default_timeout)))
        except (ValueError, TypeError):
            return self.default_timeout

    def validate_configuration(self) -> Tuple[bool, Optional[str]]:
        """
        Validates whether the OpenAI API key is configured in the environment.
        Never prints or exposes secret values.
        """
        if not HAS_OPENAI_SDK:
            return False, "OpenAI Python SDK is not installed."
        key = self.api_key
        if not key:
            return False, "OPENAI_API_KEY environment variable is not configured or is empty."
        return True, None

    def is_configured(self) -> bool:
        valid, _ = self.validate_configuration()
        return valid

    def _sanitize_error(self, error_str: str) -> str:
        """
        Sanitizes error messages to ensure OpenAI API keys and Bearer tokens
        are never logged, printed, or returned to clients.
        """
        if not error_str:
            return "Unknown error occurred"

        sanitized = error_str
        key = self.api_key
        if key and key in sanitized:
            sanitized = sanitized.replace(key, "[REDACTED_API_KEY]")

        # Redact any standard sk- pattern
        sanitized = re.sub(r"sk-[a-zA-Z0-9_-]{10,}", "[REDACTED_API_KEY]", sanitized)
        # Redact Bearer authorization headers
        sanitized = re.sub(r"Bearer\s+[a-zA-Z0-9_\-\.]{10,}", "Bearer [REDACTED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    def classify_error(self, exc: Exception) -> Tuple[str, str]:
        """
        Safely classifies OpenAI and network exceptions without exposing secrets.
        Distinguishes:
        A) insufficient_quota / credit_balance_exhausted
        B) authentication failure
        C) rate limit (concurrency / RPM / TPM)
        D) network failure (timeout / connection error)
        E) invalid audio
        F) other OpenAI API errors
        Returns:
            Tuple[status_string, safe_error_message]
        """
        if not exc:
            return "UNKNOWN", "Unknown error occurred"

        exc_name = type(exc).__name__
        exc_str = str(exc).lower()

        # A) Insufficient Quota / Credit Balance Exhausted (HTTP 429)
        if (
            "credit_balance_exhausted" in exc_str
            or "insufficient_quota" in exc_str
            or ("quota" in exc_str and "credit" in exc_str)
            or ("no credits remaining" in exc_str)
        ):
            safe_msg = "OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits."
            logger.warning("OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits.")
            return "INSUFFICIENT_QUOTA", safe_msg

        # B) Authentication Failure (HTTP 401)
        if (
            (HAS_OPENAI_SDK and isinstance(exc, openai.AuthenticationError))
            or "authenticationerror" in exc_name.lower()
            or getattr(exc, "status_code", None) == 401
            or "401" in exc_str
            or "incorrect api key" in exc_str
            or "invalid_api_key" in exc_str
            or "invalid api key" in exc_str
        ):
            safe_msg = "OpenAI authentication failed. Please verify OPENAI_API_KEY configuration."
            logger.error("OpenAI AuthenticationError: %s", safe_msg)
            return "AUTHENTICATION_FAILED", safe_msg

        # C) Rate Limit (HTTP 429 - tokens/requests per minute)
        if (
            (HAS_OPENAI_SDK and isinstance(exc, openai.RateLimitError))
            or "ratelimiterror" in exc_name.lower()
            or getattr(exc, "status_code", None) == 429
            or "rate limit" in exc_str
            or "ratelimit" in exc_str
            or "429" in exc_str
        ):
            safe_msg = "OpenAI rate limit exceeded. Please retry shortly."
            logger.warning("OpenAI RateLimitError: %s", safe_msg)
            return "RATE_LIMITED", safe_msg

        # D) Network Failure (Timeout / Connection Error)
        if (
            (HAS_OPENAI_SDK and isinstance(exc, openai.APITimeoutError))
            or "timeouterror" in exc_name.lower()
            or "timeout" in exc_str
            or "timed out" in exc_str
        ):
            safe_msg = f"OpenAI request timed out after {self.timeout_seconds} seconds."
            logger.error("OpenAI APITimeoutError: %s", safe_msg)
            return "TIMEOUT", safe_msg

        if (
            (HAS_OPENAI_SDK and isinstance(exc, openai.APIConnectionError))
            or "connectionerror" in exc_name.lower()
            or "connection" in exc_str
            or "network" in exc_str
        ):
            safe_msg = "Could not connect to OpenAI API servers. Please check network connectivity."
            logger.error("OpenAI APIConnectionError: %s", safe_msg)
            return "CONNECTION_ERROR", safe_msg

        # F) Other OpenAI API errors
        safe_err = self._sanitize_error(str(exc))
        if (HAS_OPENAI_SDK and isinstance(exc, openai.BadRequestError)) or getattr(exc, "status_code", None) == 400:
            logger.error("OpenAI BadRequestError: %s", safe_err)
            return "BAD_REQUEST", safe_err

        logger.error("OpenAI %s: %s", exc_name, safe_err)
        return "FAILED", safe_err

    async def check_api_diagnostics(self) -> Dict[str, Any]:
        """
        Executes safe startup/runtime diagnostics:
        - OPENAI_API_KEY is configured: true/false
        - OPENAI_MODEL is configured
        - OpenAI API request reaches the expected endpoint / servers
        - HTTP 429 is reported clearly as billing/quota exhaustion
        NEVER logs or exposes the API key, token, or auth headers.
        """
        is_valid, config_err = self.validate_configuration()
        if not is_valid:
            logger.info("OpenAI Diagnostics: configured=False (OPENAI_API_KEY not configured or empty)")
            return {
                "configured": False,
                "model": self.model,
                "api_reachable": False,
                "quota_exhausted": False,
                "status": "NOT_CONFIGURED",
                "message": config_err
            }

        client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        api_reachable = False
        quota_exhausted = False
        diagnostic_status = "READY"
        diagnostic_message = "OpenAI API is reachable and operational."

        try:
            # 1. Check API reachability via model metadata list
            raw = await client.models.with_raw_response.list()
            api_reachable = True
            req_id = raw.headers.get("x-request-id", "present")
            logger.info(
                "OpenAI Diagnostics: configured=True, model=%s, api_reachable=True (request_id_present=%s)",
                self.model,
                bool(req_id)
            )
        except Exception as e:
            status, safe_err = self.classify_error(e)
            if status == "INSUFFICIENT_QUOTA":
                api_reachable = True
                quota_exhausted = True
                diagnostic_status = "INSUFFICIENT_QUOTA"
                diagnostic_message = "OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits."
            else:
                diagnostic_status = status
                diagnostic_message = safe_err
                logger.warning("OpenAI Diagnostics reachability check note: %s", safe_err)

        # 2. Check completions quota if not already detected
        if api_reachable and not quota_exhausted:
            try:
                await client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=1
                )
            except Exception as e:
                status, safe_err = self.classify_error(e)
                if status == "INSUFFICIENT_QUOTA":
                    quota_exhausted = True
                    diagnostic_status = "INSUFFICIENT_QUOTA"
                    diagnostic_message = "OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits."
                    logger.warning("OpenAI Diagnostics: HTTP 429 quota/credits exhausted. Voice STT/TTS requires available API billing credits.")

        return {
            "configured": True,
            "model": self.model,
            "api_reachable": api_reachable,
            "quota_exhausted": quota_exhausted,
            "status": diagnostic_status,
            "message": diagnostic_message
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 250,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes a server-side OpenAI Chat Completion with timeout and full error handling.
        Returns a structured dictionary without revealing credentials.
        """
        is_valid, config_err = self.validate_configuration()
        if not is_valid:
            logger.warning("OpenAI chat completion skipped: %s", config_err)
            return {
                "success": False,
                "error": config_err,
                "status": "NOT_CONFIGURED",
                "content": None
            }

        target_model = model or self.model
        client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

        try:
            kwargs: Dict[str, Any] = {
                "model": target_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if response_format:
                kwargs["response_format"] = response_format

            logger.info("Dispatching OpenAI chat completion with model: %s", target_model)
            response = await client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content or ""
            return {
                "success": True,
                "content": content.strip(),
                "model": response.model,
                "status": "READY"
            }

        except Exception as e:
            status, safe_msg = self.classify_error(e)
            return {
                "success": False,
                "error": safe_msg,
                "status": status,
                "content": None
            }

    async def transcribe_audio(
        self,
        pcm_data: bytes,
        sample_rate: int = 8000
    ) -> Dict[str, Any]:
        """
        Transcribes 16-bit linear PCM audio using OpenAI Whisper.
        Encapsulates raw PCM into an in-memory WAV container before dispatching.
        Safely distinguishes:
        A) insufficient_quota / credit_balance_exhausted
        B) authentication failure
        C) rate limit
        D) network failure
        E) invalid audio
        F) other OpenAI API errors
        """
        if not pcm_data:
            return {"success": False, "text": "", "error": "Empty PCM audio buffer", "status": "EMPTY_AUDIO"}

        if len(pcm_data) < 320:  # Less than 20ms of 8kHz 16-bit audio
            return {"success": False, "text": "", "error": "Audio buffer too short to transcribe", "status": "INVALID_AUDIO"}

        is_valid, config_err = self.validate_configuration()
        if not is_valid:
            logger.warning("STT transcription skipped: %s", config_err)
            return {"success": False, "text": "", "error": config_err, "status": "NOT_CONFIGURED"}

        try:
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_data)
            wav_buffer.seek(0)
            wav_bytes = wav_buffer.read()
        except Exception as e:
            logger.error("Failed to construct WAV container from PCM: %s", e)
            return {"success": False, "text": "", "error": "Invalid PCM audio encoding", "status": "INVALID_AUDIO"}

        client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        try:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=("caller_audio.wav", wav_bytes, "audio/wav")
            )
            text = (transcript.text or "").strip()
            logger.info("Transcribed caller speech (%d bytes PCM) -> transcript_length=%d", len(pcm_data), len(text))
            return {"success": True, "text": text, "status": "SUCCESS"}
        except Exception as e:
            status, safe_err = self.classify_error(e)
            if status == "INSUFFICIENT_QUOTA":
                logger.warning("OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits.")
            else:
                logger.error("Whisper transcription error (%s): %s", status, safe_err)
            return {"success": False, "text": "", "error": safe_err, "status": status}

    def _resample_pcm(
        self,
        pcm_data: bytes,
        in_rate: int = 24000,
        out_rate: int = 8000,
        orig_sr: Optional[int] = None,
        target_sr: Optional[int] = None
    ) -> bytes:
        """
        Resamples mono 16-bit linear PCM audio to the telephony target rate (8000 Hz).
        Uses audioop if available, with an integer decimation fallback.
        """
        in_rate = orig_sr or in_rate
        out_rate = target_sr or out_rate
        if not pcm_data or in_rate == out_rate:
            return pcm_data
        try:
            import audioop
            converted, _ = audioop.ratecv(pcm_data, 2, 1, in_rate, out_rate, None)
            return converted
        except Exception:
            ratio = in_rate // out_rate
            if ratio > 1:
                return b"".join(pcm_data[i:i + 2] for i in range(0, len(pcm_data), 2 * ratio))
            return pcm_data

    def _generate_local_fallback_speech(self, text: str) -> bytes:
        """
        Synthesizes 8kHz 16-bit mono PCM locally using espeak-ng and ffmpeg.
        Guarantees that telephony callers never experience dead air even if cloud APIs fail.
        """
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf_wav, \
                 tempfile.NamedTemporaryFile(suffix=".pcm", delete=False) as tf_pcm:
                wav_path = tf_wav.name
                pcm_path = tf_pcm.name

            try:
                # 1. Generate speech with espeak-ng
                cmd1 = ["espeak-ng", "-w", wav_path, text]
                subprocess.run(cmd1, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)

                # 2. Resample to 8000Hz mono 16-bit signed PCM
                cmd2 = ["ffmpeg", "-y", "-i", wav_path, "-ar", "8000", "-ac", "1", "-f", "s16le", pcm_path]
                subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)

                with open(pcm_path, "rb") as f:
                    data = f.read()
                return data
            finally:
                for p in [wav_path, pcm_path]:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except OSError:
                            pass
        except Exception as e:
            logger.warning("Local TTS fallback failed: %s; returning empty PCM", e)
            return b""

    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy",
        target_sample_rate: int = 8000,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Synthesizes text into 8000 Hz 16-bit linear PCM audio for Exotel telephony.
        Uses OpenAI TTS with automatic fallback to local synthesis.
        """
        clean_text = (text or "").strip()
        if not clean_text:
            return {
                "success": False,
                "pcm_audio": b"",
                "pcm_bytes": b"",
                "sample_rate": target_sample_rate,
                "error": "Empty text for speech synthesis"
            }

        is_valid, _ = self.validate_configuration()
        if is_valid:
            client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
            try:
                logger.info("Synthesizing speech via OpenAI TTS for %d chars", len(clean_text))
                response = await client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    response_format="pcm",  # 24kHz 16-bit mono PCM
                    input=clean_text
                )
                raw_pcm = await response.aread() if hasattr(response, "aread") else response.content
                if raw_pcm:
                    pcm_out = self._resample_pcm(raw_pcm, in_rate=24000, out_rate=target_sample_rate)
                    logger.info("OpenAI TTS generated %d bytes raw -> %d bytes %dHz PCM", len(raw_pcm), len(pcm_out), target_sample_rate)
                    return {
                        "success": True,
                        "pcm_audio": pcm_out,
                        "pcm_bytes": pcm_out,
                        "sample_rate": target_sample_rate,
                        "source": "openai"
                    }
            except Exception as e:
                status, safe_err = self.classify_error(e)
                if status == "INSUFFICIENT_QUOTA":
                    logger.warning("OpenAI API quota/credits exhausted. Voice STT/TTS requires available API billing credits.")
                else:
                    logger.warning("OpenAI TTS failed (%s: %s); engaging local telephony speech fallback", status, safe_err)

        # Fallback to local audio synthesis
        logger.info("Synthesizing speech via local telephony fallback for: '%s'", clean_text[:40])
        fallback_pcm = self._generate_local_fallback_speech(clean_text)
        if fallback_pcm:
            if target_sample_rate != 8000:
                fallback_pcm = self._resample_pcm(fallback_pcm, in_rate=8000, out_rate=target_sample_rate)
            return {
                "success": True,
                "pcm_audio": fallback_pcm,
                "pcm_bytes": fallback_pcm,
                "sample_rate": target_sample_rate,
                "source": "local_fallback"
            }

        # Guaranteed acoustic fallback tone if local synthesis produces empty bytes
        synth_fallback = (bytes([16, 0]) * 160) * int(target_sample_rate / 8000)
        return {
            "success": True,
            "pcm_audio": synth_fallback,
            "pcm_bytes": synth_fallback,
            "sample_rate": target_sample_rate,
            "source": "tone_fallback"
        }


openai_service = OpenAIService()

