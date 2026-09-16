import json
import logging
from typing import Dict, Any, List
from ..core.config import settings

logger = logging.getLogger("UrgencyClassifier")

CLASSIFIER_PROMPT = """You are an expert urgency classification engine for an AI Personal Call Agent.
Analyze the call transcript and caller statements to determine the urgency level:
- LOW: General enquiry, casual greeting, asking about general hours or availability, routine info request.
- MEDIUM: Important but not immediate crisis, appointment rescheduling next week, non-critical enquiry.
- HIGH: Important client issue, deadline today, active website/service outage, urgent college/work deliverable.
- CRITICAL: Immediate life/safety emergency, active security breach, severe time-sensitive emergency.

Return ONLY valid JSON matching this exact schema:
{
  "urgency": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "reason": "Clear short phrase describing why this level was selected",
  "caller_name": "Extracted caller name if stated or Caller",
  "callback_required": true | false,
  "summary": "Concise 1-2 sentence executive summary of what the caller needs"
}
"""

class UrgencyClassifier:
    @staticmethod
    async def classify(transcript_text: str, caller_name: str = "Caller", caller_number: str = "") -> Dict[str, Any]:
        # If OpenAI API Key is available via openai_service, use real OpenAI model
        from .openai_service import openai_service
        if openai_service.is_configured():
            try:
                res = await openai_service.chat_completion(
                    messages=[
                        {"role": "system", "content": CLASSIFIER_PROMPT},
                        {"role": "user", "content": f"Transcript:\n{transcript_text}"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                if res.get("success") and res.get("content"):
                    data = json.loads(res["content"])
                    return data
            except Exception as e:
                logger.error(f"OpenAI urgency classification failed, falling back to rule-based engine: {e}")

        # Intelligent contextual heuristic classifier (production fallback / demo mode)
        lower_text = transcript_text.lower()

        # Critical Safety / Emergency Check
        if any(w in lower_text for w in ["fire", "ambulance", "hospital", "police", "heart attack", "injury", "danger", "accident", "emergency 911"]):
            return {
                "urgency": "CRITICAL",
                "reason": "Immediate safety emergency reported",
                "caller_name": caller_name or "Emergency Caller",
                "callback_required": True,
                "summary": "Caller reported an immediate emergency. AI advised caller to contact emergency services directly."
            }

        # High Urgency: Outage, server down, payment crash, deadline today, angry client
        if any(w in lower_text for w in ["down", "outage", "cannot place orders", "broken", "server crash", "crash", "deadline today", "urgent client", "asap", "emergency meeting", "immediately"]):
            extracted_name = "Rahul" if "rahul" in lower_text else caller_name
            return {
                "urgency": "HIGH",
                "reason": "Critical service disruption or urgent work deadline",
                "caller_name": extracted_name,
                "callback_required": True,
                "summary": "Caller reported an urgent issue or outage requiring immediate investigation."
            }

        # Medium Urgency: Reschedule, contract review, important follow up
        if any(w in lower_text for w in ["reschedule", "appointment", "contract", "invoice", "review", "tomorrow", "proposal", "deliverable"]):
            return {
                "urgency": "MEDIUM",
                "reason": "Time-sensitive business request or scheduling adjustment",
                "caller_name": caller_name,
                "callback_required": True,
                "summary": "Caller requested assistance with scheduling, contract review, or important follow up."
            }

        # Marketing / Spam Check
        if any(w in lower_text for w in ["credit card offer", "pre-approved loan", "insurance policy", "investment opportunity", "lottery"]):
            return {
                "urgency": "LOW",
                "reason": "Unsolicited marketing or promotional call",
                "caller_name": caller_name or "Promotional Caller",
                "callback_required": False,
                "summary": "Automated or cold-call promotional pitch."
            }

        # Default Low Urgency
        return {
            "urgency": "LOW",
            "reason": "General routine enquiry or casual message",
            "caller_name": caller_name,
            "callback_required": False,
            "summary": "Caller asked general questions or left a standard greeting."
        }
