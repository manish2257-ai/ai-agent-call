import logging
from typing import List, Dict, Any, Optional
from ..core.config import settings

logger = logging.getLogger("AIAgent")

SYSTEM_PROMPTS = {
    "Professional": (
        "You are an AI personal call assistant for Manish.\n"
        "You are an AI assistant and must identify yourself honestly if asked.\n"
        "Your job is to:\n"
        "1. Understand why the caller is calling.\n"
        "2. Help with routine questions using approved knowledge.\n"
        "3. Collect important details (caller name, callback number, reason).\n"
        "4. Determine whether the matter requires immediate attention.\n"
        "5. Escalate urgent matters to the owner.\n"
        "6. Take a concise message when escalation is unnecessary.\n\n"
        "Never pretend to be the owner.\n"
        "Never fabricate facts.\n"
        "Never request passwords, OTPs, banking PINs, or sensitive credentials.\n"
        "If a caller reports an emergency involving immediate danger, advise them to call emergency services (911/112).\n"
        "Maintain a polished, polite, and professional tone."
    ),
    "Friendly": (
        "You are a friendly, helpful AI personal call assistant for Manish.\n"
        "Always identify yourself as an AI assistant if asked. Greet callers warmly, listen carefully,\n"
        "be empathetic and helpful, collect their details, and handle urgent matters promptly."
    ),
    "Concise": (
        "You are a concise, direct AI call assistant for Manish.\n"
        "Keep all responses strictly under 2 sentences. Quickly identify the caller's purpose,\n"
        "note urgent problems, collect contact details, and conclude without unnecessary fluff."
    ),
    "Business": (
        "You are an executive AI assistant representing Manish's business operations.\n"
        "Prioritize client inquiries, project deadlines, and operational issues. Maintain a sharp corporate tone."
    ),
    "Personal Assistant": (
        "You are Manish's personal AI secretary and call screener.\n"
        "Screen calls effectively, protect Manish's focus time, take detailed messages, and prioritize VIP contacts."
    )
}

FALLBACK_MESSAGE = "I'm having trouble processing your request right now. Please leave your name, callback number, and a short message."

class AIAgentService:
    @staticmethod
    def get_system_prompt(personality: str = "Professional", custom_prompt: Optional[str] = None, approved_knowledge: str = "") -> str:
        base = custom_prompt if custom_prompt else SYSTEM_PROMPTS.get(personality, SYSTEM_PROMPTS["Professional"])
        if approved_knowledge:
            base += f"\n\nApproved Knowledge Base:\n{approved_knowledge}\nAnswer questions using this approved information only. If information is not present, politely say you don't have that detail but can take a message for Manish."
        return base

    @staticmethod
    async def generate_response(
        messages: List[Dict[str, str]],
        personality: str = "Professional",
        custom_prompt: Optional[str] = None,
        approved_knowledge: str = "",
        language_mode: str = "English"
    ) -> str:
        # Check if OpenAI is configured via openai_service
        from .openai_service import openai_service
        if openai_service.is_configured():
            system_content = AIAgentService.get_system_prompt(personality, custom_prompt, approved_knowledge)
            if language_mode == "Hindi":
                system_content += "\nPlease respond in Hindi (Devanagari script or clean transliterated Roman script)."
            elif language_mode == "Hinglish":
                system_content += "\nPlease respond in natural Hinglish (conversational Hindi-English blend as spoken commonly)."

            full_messages = [{"role": "system", "content": system_content}] + messages
            res = await openai_service.chat_completion(
                messages=full_messages,
                temperature=0.3,
                max_tokens=150
            )
            if res.get("success") and res.get("content"):
                return res["content"]

        # High quality local conversation responder for Demo / Fallback
        last_caller_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_caller_msg = m.get("content", "").lower()
                break

        # Hinglish / Hindi detection
        if "baat karni hai" in last_caller_msg or "manish se" in last_caller_msg:
            return "Bilkul. Main Manish ka AI assistant bol raha hoon. Aap bataiye kis kaam ke liye baat karni hai?"
        
        # Outage / Urgent issue
        if "website is down" in last_caller_msg or "cannot place orders" in last_caller_msg or "outage" in last_caller_msg:
            return "I understand the urgency regarding the website outage and ordering issue. I am logging this as a HIGH priority alert and notifying Manish immediately via SMS."

        # Emergency
        if any(w in last_caller_msg for w in ["fire", "hospital", "police", "ambulance", "emergency"]):
            return "If this is an immediate safety emergency, please dial your local emergency services (such as 911 or 112) immediately. As an AI assistant I cannot dispatch first responders."

        # General enquiry
        if "working hours" in last_caller_msg or "timing" in last_caller_msg:
            return "Manish's office hours are Monday through Friday, 9:00 AM to 6:00 PM. May I have your name and email so Manish can follow up?"

        # Default polite response
        return "I've noted that. May I have your name and a preferred callback number so Manish can get back to you as soon as possible?"
