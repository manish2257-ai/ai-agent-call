"""
LLM Provider Abstraction for Conversational Telephony Intelligence.
Routes conversational response generation to:
- LLM_PROVIDER=local / heuristic / free (Rule-based heuristics - 100% free, offline, zero API credits)
- LLM_PROVIDER=gemini                   (Google Gemini 2.5/1.5 Flash - Free Tier on AI Studio)
- LLM_PROVIDER=openai                   (OpenAI GPT-4o-mini - requires paid credits)

Provides:
- Seamless switching via LLM_PROVIDER environment variable
- Automatic fallback from paid OpenAI/Gemini to local heuristics if quota exhausted
- Safe diagnostic logging:
  [LLM] provider=...
  [LLM] success / failure
- Never logs API keys or user credentials
"""

import os
import logging
from typing import Dict, Any, List, Optional
import httpx
from .openai_service import openai_service

logger = logging.getLogger("LLMService")


class LLMService:
    def __init__(self):
        self.default_heuristic_fallback = "Thank you. I have recorded your message and will notify Manish right away."

    @property
    def provider_name(self) -> str:
        raw = os.getenv("LLM_PROVIDER", "").strip().lower()
        if raw == "gemini":
            return "gemini"
        if raw == "openai":
            return "openai"
        if raw in ("local", "heuristic", "free", "offline"):
            return "local"

        # Production default is 'local' (offline rule-based heuristics, 0 credit requirement)
        return "local"

    def _heuristic_reply(self, caller_text: str) -> str:
        """Rule-based responses for 100% free offline execution."""
        s = caller_text.lower()
        if any(w in s for w in ["are you a real person", "are you human", "are you ai"]):
            return "No. I am an AI assistant helping manage Manish's calls."
        if any(w in s for w in ["down", "outage", "crash", "broken", "offline", "failing"]):
            return "I understand the urgency regarding this outage. I am escalating this immediately and flagging it for urgent review."
        if any(w in s for w in ["contract", "deadline", "today", "urgent", "sign"]):
            return "Thank you. Since this involves a time-sensitive deadline today, I am flagging this as high priority and notifying Manish right away."
        if any(w in s for w in ["appointment", "consultation", "meeting", "schedule", "friday", "time"]):
            return "Manish takes consultation calls Monday to Friday. May I have your name and preferred time so I can pass this along to him?"
        if any(w in s for w in ["smoke", "fire", "emergency", "ambulance", "police"]):
            return "If there is immediate fire or safety danger, please hang up and call 112 or 911 immediately! As an AI I cannot dispatch emergency services."
        if any(w in s for w in ["loan", "credit card", "investment offer", "lottery"]):
            return "Manish does not accept promotional marketing calls. Thank you, goodbye."
        return self.default_heuristic_fallback

    async def _gemini_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calls Gemini generateContent for conversational AI."""
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return {"success": False, "content": None, "error": "GEMINI_API_KEY not configured"}

        gemini_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent"

        # Convert chat history to Gemini contents format
        contents = []
        for msg in messages:
            role = "model" if msg.get("role") in ("assistant", "system") else "user"
            content_text = msg.get("content", "")
            if content_text:
                contents.append({
                    "role": role,
                    "parts": [{"text": content_text}]
                })

        if not contents:
            return {"success": False, "content": None, "error": "Empty message list"}

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 150
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates") or []
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
                        return {"success": True, "content": text}
                return {"success": False, "content": None, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "content": None, "error": str(e)}

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        caller_speech: str = "",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates conversational assistant response through the active LLM provider.
        Safe logging:
        [LLM] provider=...
        [LLM] success / failure
        """
        provider = self.provider_name
        logger.info("[LLM] provider=%s", provider)

        result: Dict[str, Any] = {"success": False, "content": None, "provider": provider}

        # 1. Local heuristic provider (100% free)
        if provider == "local":
            reply = self._heuristic_reply(caller_speech)
            result = {"success": True, "content": reply, "provider": "local"}

        # 2. Gemini provider
        elif provider == "gemini":
            result = await self._gemini_chat_completion(messages, system_instruction=system_prompt)
            if not result.get("success") or not result.get("content"):
                logger.warning("Gemini LLM failed; falling back to local heuristics")
                result = {"success": True, "content": self._heuristic_reply(caller_speech), "provider": "local"}

        # 3. OpenAI provider
        elif provider == "openai":
            try:
                chat_res = await openai_service.chat_completion(
                    messages=messages,
                    max_tokens=150,
                    temperature=0.3
                )
                if chat_res.get("success") and chat_res.get("content"):
                    result = {"success": True, "content": chat_res["content"].strip(), "provider": "openai"}
                else:
                    logger.warning("OpenAI LLM failed or quota exhausted; falling back to local heuristics")
                    result = {"success": True, "content": self._heuristic_reply(caller_speech), "provider": "local"}
            except Exception as e:
                logger.warning("OpenAI LLM exception: %s; falling back to local heuristics", str(e))
                result = {"success": True, "content": self._heuristic_reply(caller_speech), "provider": "local"}

        if result.get("success") and result.get("content"):
            logger.info("[LLM] success")
        else:
            logger.warning("[LLM] failure")

        return result


llm_service = LLMService()
