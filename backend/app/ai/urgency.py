"""
Urgency Classification Engine
Evaluates contextual severity (LOW, MEDIUM, HIGH, CRITICAL).
HIGH and CRITICAL automatically trigger instant SMS and FCM alerts.
"""

import os
import json
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI

logger = logging.getLogger("urgency_engine")

class UrgencyLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class UrgencyClassifier:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true" or not self.api_key

    async def classify_urgency(
        self,
        caller_name: str,
        caller_number: str,
        reason: str,
        summary: str,
        messages: List[Dict[str, str]],
        is_vip: bool = False
    ) -> Dict[str, Any]:
        """
        Determines call urgency with contextual reasoning.
        Returns urgency level, rationale, and alertRequired boolean.
        """
        if is_vip:
            return {
                "urgency": UrgencyLevel.HIGH,
                "reason": "VIP Contact rule triggered (Priority escalation)",
                "alertRequired": True
            }

        full_text = f"Caller: {caller_name}\nReason: {reason}\nSummary: {summary}"

        if self.demo_mode or not self.client:
            return self._heuristic_urgency(full_text)

        prompt = f"""Assess the urgency of this telephone call for Manish.
Options:
- "LOW": Routine query, informational questions, non-urgent cold calls.
- "MEDIUM": Normal scheduling, non-blocking business inquiries, standard updates.
- "HIGH": Critical business blocker, production server outage, hard deadline today, urgent executive escalation.
- "CRITICAL": Life safety hazard, fire, smoke, medical emergency.

Call Details:
{full_text}

Respond in JSON format:
{{
  "urgency": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "reason": "Short explanation of urgency level",
  "alertRequired": true if urgency in ["HIGH", "CRITICAL"] else false
}}
"""
        try:
            res = await self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=100,
                temperature=0.0
            )
            data = json.loads(res.choices[0].message.content)
            urgency = data.get("urgency", UrgencyLevel.LOW).upper()
            if urgency not in [UrgencyLevel.LOW, UrgencyLevel.MEDIUM, UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]:
                urgency = UrgencyLevel.LOW
            return {
                "urgency": urgency,
                "reason": data.get("reason", "Contextual LLM urgency evaluation"),
                "alertRequired": urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
            }
        except Exception as e:
            logger.error(f"Urgency classification error: {e}")
            return self._heuristic_urgency(full_text)

    def _heuristic_urgency(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        if any(w in lower for w in ["smoke", "fire", "emergency", "ambulance", "hospital", "police"]):
            return {
                "urgency": UrgencyLevel.CRITICAL,
                "reason": "Immediate life safety hazard detected",
                "alertRequired": True
            }
        if any(w in lower for w in ["outage", "server down", "production crash", "website down", "deadline today", "critical bug"]):
            return {
                "urgency": UrgencyLevel.HIGH,
                "reason": "Time-sensitive operational disruption or hard deadline",
                "alertRequired": True
            }
        if any(w in lower for w in ["consulting", "reschedule", "meeting", "follow-up"]):
            return {
                "urgency": UrgencyLevel.MEDIUM,
                "reason": "Routine advisory and calendar scheduling enquiry",
                "alertRequired": False
            }
        return {
            "urgency": UrgencyLevel.LOW,
            "reason": "Standard non-urgent enquiry or informational message",
            "alertRequired": False
        }

urgency_classifier = UrgencyClassifier()
