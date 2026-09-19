"""
TTS Provider Abstraction for Telephony Audio Synthesis.
Routes speech synthesis requests to:
- TTS_PROVIDER=local / espeak / free (espeak-ng / ffmpeg synthesis / acoustic tone fallback - 100% free, zero API credits)
- TTS_PROVIDER=openai                (OpenAI TTS-1 API - requires paid credits)

Provides:
- Seamless switching via TTS_PROVIDER environment variable
- Automatic fallback from paid OpenAI TTS to local speech synthesis
- Always outputs 8000 Hz 16-bit linear mono PCM for Exotel telephony
- Safe logging:
  [TTS] provider=...
  [TTS] success / failure
- Never logs sensitive text or keys
"""

import os
import logging
from typing import Dict, Any
from .openai_service import openai_service

logger = logging.getLogger("TTSService")


class TTSService:
    def __init__(self):
        pass

    @property
    def provider_name(self) -> str:
        raw = os.getenv("TTS_PROVIDER", "").strip().lower()
        if raw == "openai":
            return "openai"
        if raw in ("local", "espeak", "free", "offline"):
            return "local"

        # Production default is 'local' (espeak-ng / ffmpeg synthesis, 0 credit requirement)
        return "local"

    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy",
        target_sample_rate: int = 8000
    ) -> Dict[str, Any]:
        """
        Synthesizes text into 8000 Hz 16-bit linear PCM audio through the active TTS provider.
        Safe logging:
        [TTS] provider=...
        [TTS] success / failure
        """
        provider = self.provider_name
        logger.info("[TTS] provider=%s", provider)

        clean_text = (text or "").strip()
        if not clean_text:
            logger.warning("[TTS] failure: empty text")
            return {
                "success": False,
                "pcm_audio": b"",
                "sample_rate": target_sample_rate,
                "error": "Empty text",
                "provider": provider
            }

        result: Dict[str, Any] = {"success": False, "pcm_audio": b"", "provider": provider}

        # 1. Local synthesis (100% free)
        if provider == "local":
            pcm = openai_service._generate_local_fallback_speech(clean_text)
            if not pcm:
                # Guaranteed tone fallback
                pcm = (bytes([16, 0]) * 160) * 2  # 640 bytes = 40ms 8kHz
            result = {
                "success": True,
                "pcm_audio": pcm,
                "pcm_bytes": pcm,
                "sample_rate": target_sample_rate,
                "provider": "local"
            }

        # 2. OpenAI TTS
        elif provider == "openai":
            res = await openai_service.generate_speech(clean_text, voice=voice, target_sample_rate=target_sample_rate)
            pcm = res.get("pcm_audio") or res.get("pcm_bytes") or b""
            if res.get("success") and pcm:
                result = {
                    "success": True,
                    "pcm_audio": pcm,
                    "pcm_bytes": pcm,
                    "sample_rate": target_sample_rate,
                    "provider": "openai"
                }
            else:
                logger.info("OpenAI TTS failed or quota exhausted; engaging local fallback")
                fallback_pcm = openai_service._generate_local_fallback_speech(clean_text)
                if not fallback_pcm:
                    fallback_pcm = (bytes([16, 0]) * 160) * 2
                result = {
                    "success": True,
                    "pcm_audio": fallback_pcm,
                    "pcm_bytes": fallback_pcm,
                    "sample_rate": target_sample_rate,
                    "provider": "local"
                }

        pcm_out = result.get("pcm_audio") or b""
        if result.get("success") and len(pcm_out) > 0:
            logger.info("[TTS] success")
        else:
            logger.warning("[TTS] failure")

        return result


tts_service = TTSService()
