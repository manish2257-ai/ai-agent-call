"""
Gemini Speech-To-Text (STT) Service Provider
Transcribes telephony audio using Google Gemini API (gemini-3.5-transcribe / Gemini Audio Understanding).
Features:
- Reads credentials strictly from environment variable GEMINI_API_KEY
- Uses zero-cost Gemini API endpoint (generateContent / audio understanding)
- Encapsulates 8kHz 16-bit linear PCM into standard WAV container
- Safe error classification (quota, authentication, rate limits, network)
- Masks API keys and authorization headers in all logs and outputs
- Zero external SDK bloat: uses lightweight, non-blocking httpx async client
"""

import os
import re
import io
import wave
import base64
import logging
from typing import Dict, Any, Optional, Tuple
import httpx

logger = logging.getLogger("GeminiSTTService")


class GeminiSTTService:
    def __init__(self):
        self.default_model = os.getenv("GEMINI_STT_MODEL", "gemini-3.5-transcribe")
        self.fallback_model = "gemini-2.5-flash"
        self.default_timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "15.0"))
        self.base_api_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def api_key(self) -> Optional[str]:
        """
        Retrieves the Gemini API key strictly from environment variables.
        Never returns placeholder or empty values.
        """
        key = os.getenv("GEMINI_API_KEY")
        if key and isinstance(key, str):
            cleaned = key.strip()
            if cleaned and not cleaned.startswith("your_new_") and len(cleaned) > 5:
                return cleaned
        return None

    @property
    def model(self) -> str:
        return os.getenv("GEMINI_STT_MODEL") or self.default_model

    @property
    def timeout_seconds(self) -> float:
        try:
            return float(os.getenv("GEMINI_TIMEOUT_SECONDS", str(self.default_timeout)))
        except (ValueError, TypeError):
            return self.default_timeout

    def validate_configuration(self) -> Tuple[bool, Optional[str]]:
        """
        Validates whether GEMINI_API_KEY is configured in the environment.
        Never prints or exposes secret values.
        """
        key = self.api_key
        if not key:
            return False, "GEMINI_API_KEY environment variable is not configured or is empty."
        return True, None

    def is_configured(self) -> bool:
        valid, _ = self.validate_configuration()
        return valid

    def _sanitize_error(self, error_str: str) -> str:
        """
        Sanitizes error messages to ensure Gemini API keys, tokens, and authorization
        headers are never logged, printed, or returned to clients.
        """
        if not error_str:
            return "Unknown error occurred"

        sanitized = str(error_str)
        key = self.api_key
        if key and key in sanitized:
            sanitized = sanitized.replace(key, "[REDACTED_GEMINI_KEY]")

        # Redact Google AI Studio API key patterns
        sanitized = re.sub(r"AIza[0-9A-Za-z\-_]{30,}", "[REDACTED_GEMINI_KEY]", sanitized)
        # Redact header parameters
        sanitized = re.sub(r"x-goog-api-key\s*[:=]\s*[^\s,;]+", "x-goog-api-key: [REDACTED]", sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r"key=[a-zA-Z0-9_\-]{10,}", "key=[REDACTED]", sanitized)
        # Redact Bearer authorization headers
        sanitized = re.sub(r"Bearer\s+[a-zA-Z0-9_\-\.]{10,}", "Bearer [REDACTED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    def classify_error(
        self,
        exc: Optional[Exception] = None,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Safely classifies Gemini API and network exceptions without exposing secrets.
        Distinguishes:
        - AUTHENTICATION_FAILED (HTTP 401 / 403 / API_KEY_INVALID / PERMISSION_DENIED)
        - INSUFFICIENT_QUOTA / RATE_LIMITED (HTTP 429 / RESOURCE_EXHAUSTED)
        - INVALID_AUDIO (HTTP 400 / INVALID_ARGUMENT)
        - TIMEOUT (httpx.TimeoutException)
        - CONNECTION_ERROR (httpx.NetworkError)
        - SERVER_ERROR (HTTP 500 / 503)
        Returns:
            Tuple[status_string, safe_error_message]
        """
        exc_str = (str(exc) if exc else "").lower()
        resp_str = (response_text or "").lower()
        combined = f"{exc_str} {resp_str}"

        # 1. Authentication failure (HTTP 401 or 403)
        if status_code in (401, 403) or "api_key_invalid" in combined or "permission_denied" in combined or "unauthenticated" in combined:
            return "AUTHENTICATION_FAILED", "Authentication failed: invalid or unauthorized Gemini API key."

        # 2. Rate limiting / Quota exhaustion (HTTP 429)
        if status_code == 429 or "resource_exhausted" in combined or "quota" in combined or "rate limit" in combined:
            return "INSUFFICIENT_QUOTA", "Gemini API rate limit or quota exceeded. Free Tier requests may be throttled."

        # 3. Invalid audio / Bad request (HTTP 400)
        if status_code == 400 or "invalid_argument" in combined or "audio" in combined:
            return "INVALID_AUDIO", "Gemini API rejected audio input as invalid or malformed."

        # 4. Timeout
        if exc and isinstance(exc, (httpx.TimeoutException, TimeoutError)) or "timeout" in combined or "timed out" in combined:
            return "TIMEOUT", "Gemini API request timed out."

        # 5. Connection error
        if exc and isinstance(exc, (httpx.NetworkError, ConnectionError)) or "connection" in combined:
            return "CONNECTION_ERROR", "Gemini API connection error."

        # 6. Server error (HTTP 500 / 503)
        if status_code and status_code >= 500:
            return "SERVER_ERROR", "Gemini API remote service error."

        return "UNKNOWN", self._sanitize_error(str(exc) if exc else "Transcription request failed")

    async def transcribe_audio(
        self,
        pcm_data: bytes,
        sample_rate: int = 8000
    ) -> Dict[str, Any]:
        """
        Transcribes 16-bit linear PCM audio using Gemini generateContent.
        Preserves caller utterance audio at 8000 Hz 16-bit mono PCM packaged in a WAV container.
        """
        if not pcm_data or len(pcm_data) == 0:
            return {"success": False, "text": "", "error": "Empty PCM audio buffer", "status": "EMPTY_AUDIO"}

        if len(pcm_data) < 320:  # Less than 20ms of 8kHz 16-bit mono audio
            return {"success": False, "text": "", "error": "Audio buffer too short to transcribe", "status": "INVALID_AUDIO"}

        is_valid, config_err = self.validate_configuration()
        if not is_valid:
            logger.warning("Gemini STT transcription skipped: %s", config_err)
            return {"success": False, "text": "", "error": config_err, "status": "NOT_CONFIGURED"}

        # Package raw 16-bit PCM into WAV container (preserving 8000 Hz mono)
        try:
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_data)
            wav_buffer.seek(0)
            wav_bytes = wav_buffer.read()
            b64_audio = base64.b64encode(wav_bytes).decode("ascii")
        except Exception as e:
            logger.error("Failed to construct WAV container from PCM: %s", self._sanitize_error(str(e)))
            return {"success": False, "text": "", "error": "Invalid PCM audio encoding", "status": "INVALID_AUDIO"}

        # Construct multimodal Gemini payload
        prompt_text = (
            "Transcribe this audio precisely. "
            "Output only the verbatim transcription text without any formatting, commentary, speaker tags, timestamps, or quotes."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": "audio/wav",
                                "data": b64_audio
                            }
                        },
                        {
                            "text": prompt_text
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0
            }
        }

        # Safe header with API key (never printed or logged)
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        target_model = self.model
        url = f"{self.base_api_url}/{target_model}:generateContent"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)

                # If primary model (e.g. gemini-3.5-transcribe) is not found, fallback to gemini-2.5-flash
                if response.status_code == 404 and target_model != self.fallback_model:
                    logger.info("Primary model '%s' returned 404; falling back to '%s'", target_model, self.fallback_model)
                    fallback_url = f"{self.base_api_url}/{self.fallback_model}:generateContent"
                    response = await client.post(fallback_url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates") or []
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        transcript_text = "".join(
                            part.get("text", "") for part in parts if isinstance(part, dict)
                        ).strip()
                        logger.info("Gemini STT transcription completed: %d bytes PCM -> transcript_length=%d", len(pcm_data), len(transcript_text))
                        return {"success": True, "text": transcript_text, "status": "SUCCESS"}
                    else:
                        logger.warning("Gemini STT returned empty candidates array")
                        return {"success": True, "text": "", "status": "SUCCESS"}
                else:
                    resp_text = response.text
                    status, safe_msg = self.classify_error(status_code=response.status_code, response_text=resp_text)
                    logger.warning("Gemini STT API error (HTTP %d, %s): %s", response.status_code, status, safe_msg)
                    return {"success": False, "text": "", "error": safe_msg, "status": status}

        except Exception as exc:
            status, safe_msg = self.classify_error(exc=exc)
            logger.error("Gemini STT exception (%s): %s", status, safe_msg)
            return {"success": False, "text": "", "error": safe_msg, "status": status}


# Global singleton instance
gemini_stt_service = GeminiSTTService()
