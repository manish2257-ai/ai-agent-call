"""
Speech-To-Text (STT) Provider Abstraction
Routes telephony voice transcription requests to:
- STT_PROVIDER=local / free / vosk  (Offline Vosk speech recognition - 100% free, runs in ~190MB RAM)
- STT_PROVIDER=gemini               (Google Gemini multimodal audio understanding - Free Tier on AI Studio)
- STT_PROVIDER=openai               (OpenAI Whisper-1 API - requires paid account credits)

Provides:
- Seamless provider switching via STT_PROVIDER environment variable
- Automatic fallback from paid/cloud providers to local offline STT on failure or quota exhaustion
- Safe logging matching the exact pattern:
  [STT] provider=...
  [STT] audio_bytes=...
  [STT] transcript_length=...
  [STT] success / failure
- Strict privacy: NEVER logs API keys, tokens, or transcript text
"""

import os
import logging
from typing import Dict, Any
from .local_stt_service import local_stt_service
from .gemini_stt_service import gemini_stt_service
from .openai_service import openai_service

logger = logging.getLogger("STTService")


class STTService:
    def __init__(self):
        pass

    @property
    def provider_name(self) -> str:
        """
        Resolves active STT provider ('local', 'gemini', or 'openai').
        Defaults strictly to 'local' (free offline Vosk).
        """
        raw = os.getenv("STT_PROVIDER", "").strip().lower()
        if raw == "openai":
            return "openai"
        if raw == "gemini":
            return "gemini"
        if raw in ("local", "free", "vosk", "offline"):
            return "local"

        # Production default is strictly 'local'
        return "local"

    def _sanitize_error(self, error_str: str) -> str:
        """Sanitizes errors against both OpenAI and Gemini credential patterns."""
        sanitized = gemini_stt_service._sanitize_error(error_str)
        return openai_service._sanitize_error(sanitized)

    async def transcribe_audio(
        self,
        pcm_data: bytes,
        sample_rate: int = 8000
    ) -> Dict[str, Any]:
        """
        Transcribes 16-bit linear PCM audio through the active STT provider with automatic fallback.
        Emits safe diagnostic logging and strictly avoids logging the actual transcript.
        """
        provider = self.provider_name
        audio_len = len(pcm_data) if pcm_data else 0

        # Diagnostic logging (both standard and bracketed formats)
        logger.info("STT_PROVIDER = %s", provider)
        logger.info("GEMINI_CONFIGURED = %s", "true" if gemini_stt_service.is_configured() else "false")
        logger.info("STT_REQUEST = sent")
        logger.info("[STT] provider=%s", provider)
        logger.info("[STT] audio_bytes=%d", audio_len)

        if not pcm_data or audio_len == 0:
            logger.info("[STT] transcript_length=0")
            logger.warning("[STT] failure: EMPTY_AUDIO")
            return {"success": False, "text": "", "error": "Empty PCM audio buffer", "status": "EMPTY_AUDIO", "provider": provider}

        result: Dict[str, Any] = {}

        # 1. Primary dispatch
        if provider == "local":
            result = await local_stt_service.transcribe_audio(pcm_data, sample_rate=sample_rate)
            # If local model failed or not installed, fallback to gemini or openai if configured
            if not result.get("success"):
                logger.warning("Local STT returned %s; attempting cloud fallback", result.get("status"))
                if gemini_stt_service.is_configured():
                    logger.info("[STT] fallback -> gemini")
                    result = await gemini_stt_service.transcribe_audio(pcm_data, sample_rate=sample_rate)
                elif openai_service.is_configured():
                    logger.info("[STT] fallback -> openai")
                    result = await openai_service.transcribe_audio(pcm_data, sample_rate=sample_rate)

        elif provider == "gemini":
            result = await gemini_stt_service.transcribe_audio(pcm_data, sample_rate=sample_rate)
            # If Gemini is unconfigured or exhausts quota (HTTP 429), fallback to local STT
            if not result.get("success") and result.get("status") in ("NOT_CONFIGURED", "INSUFFICIENT_QUOTA", "AUTHENTICATION_FAILED", "TIMEOUT", "CONNECTION_ERROR"):
                logger.info("Gemini STT encountered %s; falling back to local STT", result.get("status"))
                if local_stt_service.is_available():
                    logger.info("[STT] fallback -> local")
                    local_res = await local_stt_service.transcribe_audio(pcm_data, sample_rate=sample_rate)
                    if local_res.get("success"):
                        result = local_res

        elif provider == "openai":
            result = await openai_service.transcribe_audio(pcm_data, sample_rate=sample_rate)
            # If OpenAI fails (e.g. HTTP 429 quota exhaustion or invalid key), fallback to local STT or gemini
            if not result.get("success") and result.get("status") in ("INSUFFICIENT_QUOTA", "AUTHENTICATION_FAILED", "TIMEOUT", "CONNECTION_ERROR"):
                logger.info("OpenAI STT encountered %s; falling back to free/local STT", result.get("status"))
                if local_stt_service.is_available():
                    logger.info("[STT] fallback -> local")
                    local_res = await local_stt_service.transcribe_audio(pcm_data, sample_rate=sample_rate)
                    if local_res.get("success"):
                        result = local_res
                elif gemini_stt_service.is_configured():
                    logger.info("[STT] fallback -> gemini")
                    gem_res = await gemini_stt_service.transcribe_audio(pcm_data, sample_rate=sample_rate)
                    if gem_res.get("success"):
                        result = gem_res

        # Tag resulting provider
        result["provider"] = result.get("provider") or provider

        # Safe result logs matching requested format:
        # [STT] transcript_length=...
        # [STT] success / failure
        text = result.get("text") or ""
        transcript_len = len(text)
        logger.info("[STT] transcript_length=%d", transcript_len)

        if result.get("success"):
            logger.info("STT_RESULT = success")
            logger.info("[STT] success")
        else:
            status = result.get("status", "FAILED")
            logger.info("STT_RESULT = failure")
            logger.warning("[STT] failure: %s", status)

        return result


# Global singleton instance
stt_service = STTService()
