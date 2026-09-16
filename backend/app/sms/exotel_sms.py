"""
Exotel SMS Gateway Integration Service
Features:
- Sends formatted urgent alert SMS to owner phone
- Duplicate SMS suppression (hash/cooldown cache)
- Strict privacy: redacts passwords, OTPs, PINs, and sensitive information
- Demo Mode simulation fallback
"""

import os
import re
import time
import hashlib
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("exotel_sms")

class ExotelSmsService:
    def __init__(self):
        self.api_key = os.getenv("EXOTEL_API_KEY", "")
        self.api_token = os.getenv("EXOTEL_API_TOKEN", "")
        self.account_sid = os.getenv("EXOTEL_ACCOUNT_SID", "")
        self.subdomain = os.getenv("EXOTEL_SUBDOMAIN", "api.exotel.com")
        self.sender_id = os.getenv("EXOTEL_SMS_SENDER_ID", "EXOTEL")
        self.cooldown_minutes = int(os.getenv("SMS_COOLDOWN_MINUTES", "15"))
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true" or not self.api_key

        # In-memory deduplication cache: hash -> timestamp
        self._sent_cache: Dict[str, float] = {}

    def sanitize_message_content(self, text: str) -> str:
        """Redacts any accidental passwords, OTPs, PINs, or card numbers."""
        # Redact 4-8 digit potential OTPs/PINs
        sanitized = re.sub(r'\b(otp|pin|password|passcode)[:=\s]+([0-9a-zA-Z]{4,8})\b', r'\1: [REDACTED]', text, flags=re.IGNORECASE)
        # Redact potential 16-digit credit cards
        sanitized = re.sub(r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[CARD REDACTED]', sanitized)
        return sanitized

    def format_urgent_sms(
        self,
        caller_name: str,
        caller_number: str,
        urgency: str,
        reason: str,
        summary: str,
        callback_required: bool
    ) -> str:
        """Builds concise compliant SMS alert body."""
        clean_reason = self.sanitize_message_content(reason)
        clean_summary = self.sanitize_message_content(summary)
        
        # Enforce brevity to prevent multi-part SMS leakage
        if len(clean_summary) > 160:
            clean_summary = clean_summary[:157] + "..."

        msg = (
            f"URGENT CALL ALERT\n\n"
            f"Caller: {caller_name}\n"
            f"Number: {caller_number}\n"
            f"Urgency: {urgency}\n\n"
            f"Reason:\n{clean_reason}\n\n"
            f"Summary:\n{clean_summary}\n\n"
            f"Callback required:\n{'YES' if callback_required else 'NO'}"
        )
        return msg

    def is_duplicate(self, caller_number: str, reason: str) -> bool:
        """Checks if a similar alert was dispatched within the cooldown window."""
        key = hashlib.sha256(f"{caller_number}:{reason[:30]}".encode()).hexdigest()
        now = time.time()
        
        if key in self._sent_cache:
            elapsed = now - self._sent_cache[key]
            if elapsed < (self.cooldown_minutes * 60):
                logger.info(f"Duplicate SMS suppressed for {caller_number} (elapsed: {int(elapsed)}s)")
                return True
        
        self._sent_cache[key] = now
        return False

    async def send_urgent_sms(
        self,
        destination_number: str,
        caller_name: str,
        caller_number: str,
        urgency: str,
        reason: str,
        summary: str,
        callback_required: bool = True
    ) -> Dict[str, Any]:
        """Dispatches an urgent alert SMS."""
        if self.is_duplicate(caller_number, reason):
            return {
                "success": False,
                "reason": "DUPLICATE_SUPPRESSED",
                "message": "Duplicate SMS alert suppressed by anti-spam cooldown."
            }

        body = self.format_urgent_sms(
            caller_name=caller_name,
            caller_number=caller_number,
            urgency=urgency,
            reason=reason,
            summary=summary,
            callback_required=callback_required
        )

        if self.demo_mode:
            logger.info(f"[DEMO SMS TO {destination_number}]\n{body}")
            return {
                "success": True,
                "provider": "Exotel (Simulated)",
                "sid": f"demo_sms_{int(time.time())}",
                "to": destination_number,
                "body": body,
                "status": "DELIVERED"
            }

        # Live Exotel API Call
        url = f"https://{self.api_key}:{self.api_token}@{self.subdomain}/v1/Accounts/{self.account_sid}/Sms/send.json"
        payload = {
            "From": self.sender_id,
            "To": destination_number,
            "Body": body,
            "Priority": "high"
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, data=payload, timeout=10.0)
                if res.status_code in (200, 201):
                    data = res.json()
                    return {
                        "success": True,
                        "provider": "Exotel",
                        "sid": data.get("SMSMessage", {}).get("Sid"),
                        "status": "SENT",
                        "body": body
                    }
                else:
                    logger.error(f"Exotel SMS error ({res.status_code}): {res.text}")
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": res.text
                    }
        except Exception as e:
            logger.error(f"Exotel SMS exception: {e}")
            return {"success": False, "error": str(e)}

exotel_sms_service = ExotelSmsService()
