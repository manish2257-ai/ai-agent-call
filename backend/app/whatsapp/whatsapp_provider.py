"""
WhatsApp Urgent Alert Provider
Implements official WhatsApp Cloud API (Graph API) integration:
- Base WhatsAppProvider interface
- WhatsAppCloudProvider implementation
- Template message support (e.g. urgent_call_alert)
- Fallback text message support
- Idempotency & duplicate prevention (callId + notificationType)
- Strict privacy: data minimization, redacting OTPs/passwords
- Safe Mock / Demo mode fallback when credentials are not configured
"""

import os
import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("whatsapp_provider")

class WhatsAppProvider(ABC):
    @abstractmethod
    async def send_urgent_alert(
        self,
        call_id: str,
        caller_name: str,
        caller_number: str,
        urgency: str,
        reason: str,
        summary: str,
        callback_required: bool,
        call_time: str,
        recipient_number: Optional[str] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def send_test_message(self, recipient_number: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        pass


class WhatsAppCloudProvider(WhatsAppProvider):
    def __init__(self):
        self.enabled = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
        self.recipient_phone = os.getenv("WHATSAPP_RECIPIENT_PHONE_NUMBER", "")
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v20.0")
        self.template_name = os.getenv("WHATSAPP_TEMPLATE_NAME", "urgent_call_alert")
        self.template_lang = os.getenv("WHATSAPP_TEMPLATE_LANG", "en_US")
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true" or not self.access_token

        # Idempotency deduplication cache: key -> timestamp
        self._sent_idempotency_keys: Dict[str, float] = {}

    def is_configured(self) -> bool:
        return bool(self.access_token and self.phone_number_id)

    def get_status(self) -> Dict[str, Any]:
        configured = self.is_configured()
        if self.demo_mode and not configured:
            status = "SIMULATED"
        elif configured and self.enabled:
            status = "CONNECTED"
        elif configured and not self.enabled:
            status = "DISABLED"
        else:
            status = "NOT_CONFIGURED"

        return {
            "enabled": self.enabled,
            "configured": configured,
            "status": status,
            "phoneNumberIdConfigured": bool(self.phone_number_id),
            "recipientConfigured": bool(self.recipient_phone),
            "apiVersion": self.api_version,
            "templateName": self.template_name
        }

    def sanitize_content(self, text: str) -> str:
        """Redacts sensitive credentials, OTPs, or passwords."""
        # Redact OTP / Password / PIN indicators
        redacted = re.sub(r'(?i)\b(otp|password|pin|passcode|token|cvv)\s*[:=]?\s*([0-9a-zA-Z]{3,12})\b', r'\1: [REDACTED]', text)
        redacted = re.sub(r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[CARD NUMBER REDACTED]', redacted)
        return redacted

    def check_duplicate(self, call_id: str) -> bool:
        """Checks idempotency concept: callId + WHATSAPP within cooldown."""
        idempotency_key = f"{call_id}:WHATSAPP"
        now = time.time()
        if idempotency_key in self._sent_idempotency_keys:
            elapsed = now - self._sent_idempotency_keys[idempotency_key]
            if elapsed < 900:  # 15 minute cooldown per callId
                logger.info(f"Duplicate WhatsApp alert suppressed for call {call_id} (elapsed: {int(elapsed)}s)")
                return True
        self._sent_idempotency_keys[idempotency_key] = now
        return False

    async def send_urgent_alert(
        self,
        call_id: str,
        caller_name: str,
        caller_number: str,
        urgency: str,
        reason: str,
        summary: str,
        callback_required: bool,
        call_time: str,
        recipient_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatches an urgent alert via WhatsApp Cloud API."""
        dest = recipient_number or self.recipient_phone

        # 1. Idempotency Check
        if self.check_duplicate(call_id):
            return {
                "success": False,
                "status": "DUPLICATE_SUPPRESSED",
                "message": f"WhatsApp alert for call {call_id} already sent.",
                "callId": call_id
            }

        # 2. Sanitize content for privacy
        clean_reason = self.sanitize_content(reason)
        clean_summary = self.sanitize_content(summary)
        callback_str = "Yes" if callback_required else "No"

        # Format standardized message body
        msg_text = (
            f"🚨 URGENT CALL ALERT\n\n"
            f"Caller: {caller_name}\n"
            f"Number: {caller_number}\n\n"
            f"Urgency: {urgency}\n\n"
            f"Reason:\n{clean_reason}\n\n"
            f"Summary:\n{clean_summary}\n\n"
            f"Callback Required:\n{callback_str}\n\n"
            f"Time:\n{call_time}"
        )

        # 3. Handle Demo Mode or unconfigured credentials gracefully
        if self.demo_mode or not self.is_configured():
            logger.info(f"[DEMO WHATSAPP ALERT TO {dest}]\n{msg_text}")
            return {
                "success": True,
                "status": "SENT",
                "provider": "WhatsApp Cloud API (Simulated Demo)",
                "messageId": f"wamid.demo.{int(time.time())}",
                "to": dest,
                "body": msg_text,
                "isDemo": True
            }

        # 4. Live WhatsApp Cloud API Request
        url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Format clean recipient E.164 number without '+' for WhatsApp Cloud API
        clean_to = dest.replace("+", "").replace(" ", "").replace("-", "")

        # Use WhatsApp template if configured
        template_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {"code": self.template_lang},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": caller_name},
                            {"type": "text", "text": caller_number},
                            {"type": "text", "text": urgency},
                            {"type": "text", "text": clean_reason[:60]},
                            {"type": "text", "text": clean_summary[:120]},
                            {"type": "text", "text": callback_str},
                            {"type": "text", "text": call_time}
                        ]
                    }
                ]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(url, headers=headers, json=template_payload)
                if res.status_code in (200, 201):
                    data = res.json()
                    msg_id = data.get("messages", [{}])[0].get("id", "")
                    return {
                        "success": True,
                        "status": "SENT",
                        "provider": "WhatsApp Cloud API",
                        "messageId": msg_id,
                        "to": dest,
                        "isDemo": False
                    }
                else:
                    # Fallback to direct text payload if template is not yet approved or sandbox mode
                    logger.warning(f"WhatsApp template message failed ({res.status_code}): {res.text}. Trying text message fallback.")
                    text_payload = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": clean_to,
                        "type": "text",
                        "text": {"preview_url": False, "body": msg_text}
                    }
                    res_text = await client.post(url, headers=headers, json=text_payload)
                    if res_text.status_code in (200, 201):
                        data = res_text.json()
                        msg_id = data.get("messages", [{}])[0].get("id", "")
                        return {
                            "success": True,
                            "status": "SENT",
                            "provider": "WhatsApp Cloud API (Text Fallback)",
                            "messageId": msg_id,
                            "to": dest,
                            "isDemo": False
                        }
                    else:
                        logger.error(f"WhatsApp Cloud API error ({res_text.status_code}): {res_text.text}")
                        return {
                            "success": False,
                            "status": "FAILED",
                            "error": res_text.json().get("error", {}).get("message", res_text.text),
                            "statusCode": res_text.status_code
                        }
        except Exception as e:
            logger.error(f"WhatsApp request exception: {e}")
            return {
                "success": False,
                "status": "FAILED",
                "error": str(e)
            }

    async def send_test_message(self, recipient_number: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches a standalone test message."""
        dest = recipient_number or self.recipient_phone
        test_content = "AI Call Agent test notification. WhatsApp integration is working."

        if self.demo_mode or not self.is_configured():
            logger.info(f"[DEMO WHATSAPP TEST TO {dest}]: {test_content}")
            return {
                "success": True,
                "status": "SENT",
                "provider": "WhatsApp Cloud API (Simulated Demo)",
                "to": dest,
                "message": test_content,
                "isDemo": True
            }

        url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        clean_to = dest.replace("+", "").replace(" ", "").replace("-", "")
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_to,
            "type": "text",
            "text": {"preview_url": False, "body": test_content}
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code in (200, 201):
                    data = res.json()
                    return {
                        "success": True,
                        "status": "SENT",
                        "messageId": data.get("messages", [{}])[0].get("id", ""),
                        "to": dest
                    }
                else:
                    return {
                        "success": False,
                        "status": "FAILED",
                        "error": res.json().get("error", {}).get("message", res.text)
                    }
        except Exception as e:
            return {"success": False, "status": "FAILED", "error": str(e)}

whatsapp_service = WhatsAppCloudProvider()
