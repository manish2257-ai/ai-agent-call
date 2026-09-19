"""
OpenAI Voice & Conversational Intelligence Agent
Features:
- Enforces explicit AI identity disclosure and anti-impersonation rules
- Formulates helpful follow-up questions
- Contextual call summarization and reason extraction
- Safe fallback heuristics for local demo simulation without OpenAI keys
"""

import os
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

logger = logging.getLogger("ai_voice_agent")

SYSTEM_PROMPT = """You are Manish's AI telephone assistant.
Your job is to answer incoming phone calls on his behalf, understand why the caller is calling, ask helpful follow-up questions, collect their name and callback number if appropriate, determine urgency, and summarize the call.

CRITICAL OPERATIONAL RULES:
1. IDENTITY & HONESTY: Never impersonate Manish or claim to be human. You are strictly Manish's AI assistant. If asked "Are you a real person?", always answer: "No. I'm an AI assistant helping manage Manish's calls."
2. GREETING: Begin with: "Hello, you've reached Manish's AI assistant. I'm an AI assistant helping manage his calls. How can I help?"
3. DATA MINIMIZATION & SECURITY: NEVER ask callers for passwords, OTPs, PINs, bank details, card numbers, or sensitive credentials. If a caller voluntarily mentions a password or code, do not repeat it or include it in summaries.
4. EMERGENCY REDIRECTION: If caller describes an immediate life hazard (fire, smoke, medical emergency, physical crime), tell them to immediately hang up and call 112 or 911.
5. URGENCY: Identify whether the call is LOW (general query), MEDIUM (routine scheduling), HIGH (server outage, immediate contract deadline today, urgent client blocker), or CRITICAL (life safety hazard).
6. TONE: Professional, calm, concise, and helpful. Keep responses under 2-3 sentences suitable for spoken voice.
"""

class AIVoiceAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.llm_provider = os.getenv("LLM_PROVIDER", "").strip().lower()
        self.demo_mode = (
            os.getenv("DEMO_MODE", "true").lower() == "true"
            or not self.api_key
            or self.llm_provider in ("local", "heuristic", "free")
        )
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_response(
        self,
        conversation_history: List[Dict[str, str]],
        caller_speech: str,
        custom_instructions: Optional[str] = None
    ) -> str:
        """Generates the next conversational AI response."""
        # Check direct anti-impersonation questions
        lower_speech = caller_speech.lower().strip()
        if "are you a real person" in lower_speech or "are you human" in lower_speech:
            return "No. I'm an AI assistant helping manage Manish's calls."

        if self.demo_mode or not self.client:
            return self._heuristic_response(conversation_history, caller_speech)

        prompt = SYSTEM_PROMPT
        if custom_instructions:
            prompt += f"\nOwner Custom Guidance: {custom_instructions}"

        messages = [{"role": "system", "content": prompt}]
        for turn in conversation_history:
            role = "assistant" if turn.get("speaker") == "AI" else "user"
            messages.append({"role": role, "content": turn.get("content", "")})
        messages.append({"role": "user", "content": caller_speech})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI completion error: {e}. Falling back to heuristic response.")
            return self._heuristic_response(conversation_history, caller_speech)

    def _heuristic_response(self, conversation_history: List[Dict[str, str]], caller_speech: str) -> str:
        """Rule-based responses for seamless demo testing."""
        s = caller_speech.lower()
        if any(w in s for w in ["down", "outage", "crash", "broken", "offline", "failing"]):
            return "I understand the urgency regarding this outage. I am escalating this immediately and sending an urgent SMS alert to Manish."
        if any(w in s for w in ["contract", "deadline", "today", "urgent", "sign"]):
            return "Thank you. Since this involves a time-sensitive deadline today, I am flagging this as high priority and notifying Manish right away."
        if any(w in s for w in ["appointment", "consultation", "meeting", "schedule", "friday"]):
            return "Manish takes consultation calls Monday to Friday. May I have your name and preferred time so I can pass this along to him?"
        if any(w in s for w in ["smoke", "fire", "emergency", "ambulance", "police"]):
            return "If there is immediate fire or safety danger, please hang up and call 112 or 911 immediately! As an AI I cannot dispatch emergency services."
        if any(w in s for w in ["loan", "credit card", "investment offer", "lottery"]):
            return "Manish does not accept promotional marketing calls. I am ending this call."
        return "Thank you for the information. I have noted this down and will ensure Manish receives your message promptly."

    async def generate_call_summary(
        self,
        caller_name: str,
        caller_number: str,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Synthesizes structured call reason, summary, and action items."""
        full_transcript = "\n".join([f"{m.get('speaker', 'Caller')}: {m.get('content', '')}" for m in messages])
        
        if self.demo_mode or not self.client:
            return self._heuristic_summary(full_transcript, caller_name)

        summary_prompt = f"""Summarize this phone conversation between Manish's AI Assistant and caller {caller_name}.
Transcript:
{full_transcript}

Respond in JSON with:
"reason": "1-sentence why the caller called",
"summary": "2-3 sentence factual summary (do not include credentials/passwords/OTPs)",
"actionRequired": "Recommended action for owner",
"callbackRequired": true/false
"""
        try:
            res = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": summary_prompt}],
                response_format={"type": "json_object"},
                max_tokens=200,
                temperature=0.2
            )
            import json
            return json.loads(res.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI summary error: {e}")
            return self._heuristic_summary(full_transcript, caller_name)

    def _heuristic_summary(self, transcript: str, caller_name: str) -> Dict[str, Any]:
        t = transcript.lower()
        if "outage" in t or "down" in t:
            return {
                "reason": "Production website outage reported",
                "summary": f"{caller_name} reported that the website is down and customer checkout is failing.",
                "actionRequired": "Inspect production web servers and error logs immediately.",
                "callbackRequired": True
            }
        elif "contract" in t or "deadline" in t:
            return {
                "reason": "Contract deadline today before close of business",
                "summary": f"{caller_name} requested countersignature on contract before 5:00 PM.",
                "actionRequired": "Review and sign agreement document in email.",
                "callbackRequired": True
            }
        elif "smoke" in t or "fire" in t:
            return {
                "reason": "Urgent building safety notice - Electrical smoke",
                "summary": f"{caller_name} reported smoke hazard. AI provided emergency 112/911 redirection notice.",
                "actionRequired": "Verify safety status and emergency services dispatch.",
                "callbackRequired": True
            }
        return {
            "reason": "General enquiry or message left for owner",
            "summary": f"{caller_name} called to leave a message for Manish.",
            "actionRequired": "Review message and call back when convenient.",
            "callbackRequired": False
        }

ai_voice_agent = AIVoiceAgent()
