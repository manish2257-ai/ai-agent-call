"""
Local / Offline Speech-To-Text (STT) Provider using Vosk.
Features:
- 100% free and offline: requires zero OpenAI credits and zero cloud API keys
- Low memory footprint (~190MB RAM peak, fits within Render 512MB limit)
- CPU-only execution without PyTorch or CUDA dependencies
- Native ingestion of 8000 Hz 16-bit linear PCM from Exotel telephony
- Non-blocking async execution via asyncio.to_thread
- Strict privacy: transcripts and secrets are never logged
"""

import os
import io
import json
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("LocalSTTService")

# Global cached model reference
_vosk_model = None
_model_load_lock = asyncio.Lock()


class LocalSTTService:
    def __init__(self):
        self.model_path = os.getenv("VOSK_MODEL_PATH", "")
        self.lang = os.getenv("VOSK_MODEL_LANG", "en-us")

    def is_available(self) -> bool:
        """Checks if the vosk package is installed in the current environment."""
        try:
            import vosk  # noqa: F401
            return True
        except ImportError:
            return False

    def _load_model_sync(self):
        """Synchronously loads the Vosk model from cache, path, or download."""
        global _vosk_model
        if _vosk_model is not None:
            return _vosk_model

        try:
            import vosk
            vosk.SetLogLevel(-1)

            # 1. Custom model path specified by environment
            if self.model_path and os.path.exists(self.model_path):
                logger.info("Loading Vosk STT model from VOSK_MODEL_PATH: %s", self.model_path)
                _vosk_model = vosk.Model(self.model_path)
                return _vosk_model

            # 2. Known local locations
            candidates = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models", "vosk-model-small-en-us-0.15"),
                "/app/backend/models/vosk-model-small-en-us-0.15",
                "/app/models/vosk-model-small-en-us-0.15",
                os.path.expanduser("~/.cache/vosk/vosk-model-small-en-us-0.15"),
                os.path.abspath("backend/models/vosk-model-small-en-us-0.15"),
                os.path.abspath("models/vosk-model-small-en-us-0.15"),
                "/usr/share/vosk/models/vosk-model-small-en-us-0.15",
            ]
            for candidate in candidates:
                if os.path.isdir(candidate):
                    logger.info("Loading Vosk STT model from local directory: %s", candidate)
                    _vosk_model = vosk.Model(candidate)
                    return _vosk_model

            # 3. Automatic download/cache via language code
            logger.info("Loading Vosk STT model via lang='%s' (auto-caching)", self.lang)
            _vosk_model = vosk.Model(lang=self.lang)
            return _vosk_model
        except Exception as e:
            logger.error("Failed to load Vosk model: %s", str(e))
            return None

    async def get_model(self):
        """Asynchronously loads and caches the Vosk model."""
        global _vosk_model
        if _vosk_model is not None:
            return _vosk_model

        async with _model_load_lock:
            if _vosk_model is not None:
                return _vosk_model
            _vosk_model = await asyncio.to_thread(self._load_model_sync)
            return _vosk_model

    def _sync_transcribe(self, model, pcm_8k: bytes) -> str:
        """
        Synchronously feeds 8000 Hz 16-bit mono linear PCM to KaldiRecognizer.
        Upsamples from 8000 Hz to 16000 Hz for the vosk-model-small-en-us acoustic model.
        """
        import vosk
        # Upsample 8kHz mono 16-bit PCM to 16kHz mono 16-bit PCM by sample duplication
        pcm_16k = b"".join(pcm_8k[i:i + 2] * 2 for i in range(0, len(pcm_8k), 2))

        rec = vosk.KaldiRecognizer(model, 16000)
        rec.AcceptWaveform(pcm_16k)
        result_raw = rec.FinalResult()
        try:
            data = json.loads(result_raw)
            return (data.get("text") or "").strip()
        except Exception:
            return ""

    async def transcribe_audio(
        self,
        pcm_data: bytes,
        sample_rate: int = 8000
    ) -> Dict[str, Any]:
        """
        Transcribes 16-bit linear PCM audio using local offline Vosk engine.
        Returns:
            Dict with keys: success, text, status, error (if any)
        """
        if not pcm_data or len(pcm_data) == 0:
            return {"success": False, "text": "", "error": "Empty audio buffer", "status": "EMPTY_AUDIO"}

        if len(pcm_data) < 320:  # Less than 20ms of 8kHz audio
            return {"success": False, "text": "", "error": "Audio buffer too short", "status": "INVALID_AUDIO"}

        if not self.is_available():
            logger.warning("Vosk package is not installed; local offline STT unavailable")
            return {
                "success": False,
                "text": "",
                "error": "Vosk package not installed in environment",
                "status": "NOT_INSTALLED"
            }

        model = await self.get_model()
        if not model:
            return {
                "success": False,
                "text": "",
                "error": "Vosk acoustic model could not be loaded",
                "status": "MODEL_LOAD_FAILED"
            }

        try:
            transcript = await asyncio.to_thread(self._sync_transcribe, model, pcm_data)
            return {
                "success": True,
                "text": transcript,
                "status": "SUCCESS"
            }
        except Exception as e:
            logger.error("Local Vosk transcription exception: %s", str(e))
            return {
                "success": False,
                "text": "",
                "error": "Local transcription failed",
                "status": "FAILED"
            }


local_stt_service = LocalSTTService()
