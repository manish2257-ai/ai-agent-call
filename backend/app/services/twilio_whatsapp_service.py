"""
Twilio WhatsApp Messaging Service
Handles sending template and freeform WhatsApp messages via the Twilio Python SDK.
Features:
- Secure credential reading from environment variables
- Twilio Client instantiation
- Template messaging via Content SID (Twilio WhatsApp Sandbox & Production approved templates)
- Fallback message body support for production senders
- Cooldown & duplicate prevention (no message loops)
- Safe error handling (never exposes TWILIO_AUTH_TOKEN)
- Firebase alert status logging (whatsapp_status, whatsapp_message_sid, whatsapp_sent_at, whatsapp_error)
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("twilio_whatsapp_service")

# Try importing Twilio SDK safely
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    HAS_TWILIO_SDK = True
except ImportError:
    HAS_TWILIO_SDK = False
    logger.warning("Twilio SDK is not installed or failed to import.")


class TwilioWhatsAppService:
    def __init__(self):
        # In-memory deduplication cache: key -> timestamp (epoch seconds)
        self._dispatch_timestamps: Dict[str, float] = {}

    @property
    def account_sid(self) -> Optional[str]:
        val = os.getenv("TWILIO_ACCOUNT_SID") or os.getenv("TELEPHONY_ACCOUNT_ID")
        if not val:
            try:
                from ..core.config import settings
                val = getattr(settings, "TWILIO_ACCOUNT_SID", None)
            except Exception:
                pass
        return val or None

    @property
    def auth_token(self) -> Optional[str]:
        val = os.getenv("TWILIO_AUTH_TOKEN") or os.getenv("TELEPHONY_AUTH_TOKEN")
        if not val:
            try:
                from ..core.config import settings
                val = getattr(settings, "TWILIO_AUTH_TOKEN", None)
            except Exception:
                pass
        return val or None

    @property
    def default_from(self) -> str:
        return os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+17372508034")

    @property
    def default_to(self) -> str:
        return os.getenv("TWILIO_WHATSAPP_TO", "whatsapp:+917367966177")

    @property
    def default_content_sid(self) -> str:
        return os.getenv("TWILIO_CONTENT_SID", "HXfe5ab5f00277942d4d4200328b4d403c")

    def validate_configuration(self) -> Tuple[bool, Optional[str]]:
        """
        Validates that required Twilio credentials are configured in the environment.
        Never reveals secret values.
        """
        if not self.account_sid or not self.auth_token:
            return False, "Twilio WhatsApp configuration is incomplete."
        if not HAS_TWILIO_SDK:
            return False, "Twilio Python SDK is not available."
        return True, None

    def is_configured(self) -> bool:
        valid, _ = self.validate_configuration()
        return valid

    def _sanitize_error(self, error_str: str) -> str:
        """
        Removes any sensitive token values or auth references from error output.
        """
        token = self.auth_token
        if token and token in error_str:
            error_str = error_str.replace(token, "[REDACTED]")
        sid = self.account_sid
        if sid and len(sid) > 8:
            # Mask middle of SID if exposed
            masked = sid[:4] + "..." + sid[-4:]
            error_str = error_str.replace(sid, masked)
        return error_str

    def _format_whatsapp_number(self, number: str) -> str:
        """
        Ensures the number has the 'whatsapp:' prefix required by Twilio.
        """
        cleaned = number.strip()
        if not cleaned.startswith("whatsapp:"):
            return f"whatsapp:{cleaned}"
        return cleaned

    def check_cooldown(self, deduplication_key: str, cooldown_seconds: int = 300) -> bool:
        """
        Prevents sending duplicate WhatsApp messages repeatedly in a loop.
        Returns True if in cooldown (should suppress), False otherwise.
        """
        now = time.time()
        last_time = self._dispatch_timestamps.get(deduplication_key)
        if last_time and (now - last_time) < cooldown_seconds:
            return True
        return False

    def record_dispatch(self, deduplication_key: str):
        self._dispatch_timestamps[deduplication_key] = time.time()

    def send_whatsapp_message(
        self,
        to: Optional[str] = None,
        from_: Optional[str] = None,
        content_sid: Optional[str] = None,
        content_variables: Optional[Dict[str, Any]] = None,
        body: Optional[str] = None,
        call_id: Optional[str] = None,
        bypass_cooldown: bool = False,
        cooldown_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Sends a WhatsApp message via Twilio.
        Defaults to configured Sandbox Content SID and numbers if not specified.
        """
        is_valid, config_err = self.validate_configuration()
        if not is_valid:
            logger.warning(f"WhatsApp dispatch skipped: {config_err}")
            return {
                "success": False,
                "message": config_err,
                "error": config_err,
                "status": "NOT_CONFIGURED"
            }

        target_to = self._format_whatsapp_number(to or self.default_to)
        target_from = self._format_whatsapp_number(from_ or self.default_from)
        target_content_sid = content_sid or self.default_content_sid

        # Cooldown & duplicate prevention
        dedup_key = f"{target_to}_{call_id or 'direct'}"
        if not bypass_cooldown and self.check_cooldown(dedup_key, cooldown_seconds):
            logger.info(f"WhatsApp message to {target_to} suppressed by cooldown.")
            return {
                "success": True,
                "message": "WhatsApp message suppressed by cooldown",
                "status": "SUPPRESSED_BY_COOLDOWN"
            }

        try:
            client = Client(self.account_sid, self.auth_token)

            message_args: Dict[str, Any] = {
                "to": target_to,
                "from_": target_from,
            }

            if target_content_sid:
                message_args["content_sid"] = target_content_sid
                if content_variables:
                    message_args["content_variables"] = json.dumps(content_variables)
            elif body:
                message_args["body"] = body
            else:
                message_args["content_sid"] = self.default_content_sid

            logger.info(f"Submitting Twilio WhatsApp message to {target_to} (from {target_from})")
            message = client.messages.create(**message_args)

            self.record_dispatch(dedup_key)

            return {
                "success": True,
                "message": "WhatsApp message submitted successfully",
                "sid": message.sid,
                "status": getattr(message, "status", "queued") or "queued",
                "to": target_to,
                "from": target_from
            }

        except Exception as e:
            safe_err = self._sanitize_error(str(e))
            logger.error(f"Error submitting Twilio WhatsApp message: {safe_err}")
            return {
                "success": False,
                "message": "Failed to send WhatsApp message via Twilio",
                "error": safe_err,
                "status": "FAILED"
            }

    async def dispatch_urgent_alert(
        self,
        call_id: Optional[str],
        caller: str,
        caller_number: str,
        urgency: str,
        reason: str,
        summary: str,
        user_id: Optional[str] = None,
        recipient_number: Optional[str] = None,
        bypass_cooldown: bool = False
    ) -> Dict[str, Any]:
        """
        Dispatches an urgent alert via Twilio WhatsApp and records notification status
        in Firebase Firestore if configured, safely handling any errors.
        """
        # Format variables if using a dynamic content template with parameters
        variables = {
            "1": caller or "Unknown Caller",
            "2": caller_number or "Unknown",
            "3": urgency or "HIGH",
            "4": reason or "Urgent inquiry"
        }

        # Send WhatsApp message
        result = self.send_whatsapp_message(
            to=recipient_number or self.default_to,
            content_sid=self.default_content_sid,
            content_variables=variables,
            call_id=call_id,
            bypass_cooldown=bypass_cooldown
        )

        # Update Firebase alert status if available
        try:
            from ..firebase.firebase_service import firebase_manager
            import datetime

            user_key = user_id or "default_owner"
            alert_payload = {
                "callId": call_id,
                "caller": caller,
                "callerNumber": caller_number,
                "urgency": urgency,
                "reason": reason,
                "summary": summary,
                "channel": "WHATSAPP_TWILIO",
                "whatsapp_status": result.get("status"),
                "whatsapp_message_sid": result.get("sid"),
                "whatsapp_sent_at": datetime.datetime.now(datetime.timezone.utc).isoformat() if result.get("success") else None,
                "whatsapp_error": result.get("error") if not result.get("success") else None
            }
            await firebase_manager.save_alert(user_id=str(user_key), alert_data=alert_payload)
            logger.info(f"Recorded WhatsApp alert status in Firebase for call {call_id}")
        except Exception as fb_err:
            logger.warning(f"Could not record WhatsApp status in Firebase: {fb_err}")

        return result


twilio_whatsapp_service = TwilioWhatsAppService()
