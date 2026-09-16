import datetime
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.models import SmsAlert, UserSettings
from ..core.config import settings
from ..providers.sms.base import SMSProvider
from ..providers.sms.twilio_sms import TwilioSMSProvider
from ..providers.sms.exotel_sms import ExotelSMSProvider
from ..providers.sms.mock_sms import MockSMSProvider

logger = logging.getLogger("SMSService")

class SMSService:
    _last_alert_times: Dict[str, datetime.datetime] = {}

    @classmethod
    def get_sms_provider(cls) -> SMSProvider:
        prov = settings.SMS_PROVIDER.lower()
        if prov == "twilio" and settings.SMS_ACCOUNT_ID and settings.SMS_AUTH_TOKEN:
            return TwilioSMSProvider(settings.SMS_ACCOUNT_ID, settings.SMS_AUTH_TOKEN, settings.SMS_FROM_NUMBER)
        elif prov == "exotel" and settings.SMS_ACCOUNT_ID and settings.SMS_AUTH_TOKEN:
            return ExotelSMSProvider(settings.SMS_ACCOUNT_ID, settings.SMS_ACCOUNT_ID, settings.SMS_AUTH_TOKEN, settings.SMS_FROM_NUMBER)
        return MockSMSProvider()

    @classmethod
    def is_in_cooldown(cls, caller_key: str, cooldown_minutes: int) -> bool:
        last_time = cls._last_alert_times.get(caller_key)
        if not last_time:
            return False
        elapsed = (datetime.datetime.now() - last_time).total_seconds() / 60.0
        return elapsed < cooldown_minutes

    @classmethod
    def record_alert_dispatched(cls, caller_key: str):
        cls._last_alert_times[caller_key] = datetime.datetime.now()

    @classmethod
    def format_alert_message(
        cls,
        template: Optional[str],
        caller: str,
        number: str,
        urgency: str,
        reason: str,
        summary: str,
        time_str: Optional[str] = None
    ) -> str:
        if not time_str:
            time_str = datetime.datetime.now().strftime("%I:%M %p")
        if not template:
            template = (
                "URGENT CALL ALERT\n\n"
                "Caller: {caller}\n"
                "Number: {number}\n"
                "Urgency: {urgency}\n\n"
                "Reason:\n{reason}\n\n"
                "Summary:\n{summary}\n\n"
                "Time:\n{time}\n\n"
                "Please review the call in the AI Call Agent app."
            )
        return (
            template.replace("{caller}", caller or "Unknown")
            .replace("{number}", number or "Unknown")
            .replace("{urgency}", urgency or "HIGH")
            .replace("{reason}", reason or "Urgent matter")
            .replace("{summary}", summary or "Needs immediate attention")
            .replace("{time}", time_str)
        )

    @classmethod
    async def dispatch_urgent_sms(
        cls,
        db: Session,
        call_id: Optional[str],
        to_number: str,
        caller: str,
        caller_number: str,
        urgency: str,
        reason: str,
        summary: str,
        user_settings: Optional[UserSettings] = None,
        bypass_cooldown: bool = False
    ) -> Dict[str, Any]:
        cooldown_mins = user_settings.sms_cooldown_minutes if user_settings else settings.ALERT_COOLDOWN_MINUTES
        caller_key = f"{caller_number}_{urgency}"

        if not bypass_cooldown and cls.is_in_cooldown(caller_key, cooldown_mins):
            logger.info(f"SMS alert suppressed by cooldown ({cooldown_mins} mins) for caller {caller_number}")
            return {
                "success": True,
                "status": "SUPPRESSED_BY_COOLDOWN",
                "message": f"Alert suppressed by cooldown ({cooldown_mins}m)"
            }

        template = user_settings.alert_template if user_settings else None
        msg_text = cls.format_alert_message(
            template=template,
            caller=caller,
            number=caller_number,
            urgency=urgency,
            reason=reason,
            summary=summary
        )

        provider = cls.get_sms_provider()
        res = await provider.send_sms(to_number=to_number, message=msg_text)

        # Record in database
        status_val = "DELIVERED" if res.get("success") else "FAILED"
        sms_record = SmsAlert(
            call_id=call_id,
            to_number=to_number,
            urgency=urgency,
            message_text=msg_text,
            status=status_val,
            provider=provider.get_provider_name(),
            retry_count=0
        )
        db.add(sms_record)
        db.commit()

        if res.get("success"):
            cls.record_alert_dispatched(caller_key)

        # Dispatch WhatsApp Notification via Twilio if configured
        whatsapp_res = None
        try:
            from .twilio_whatsapp_service import twilio_whatsapp_service
            whatsapp_res = await twilio_whatsapp_service.dispatch_urgent_alert(
                call_id=call_id,
                caller=caller,
                caller_number=caller_number,
                urgency=urgency,
                reason=reason,
                summary=summary,
                user_id=str(user_settings.user_id) if user_settings else None,
                bypass_cooldown=bypass_cooldown
            )
        except Exception as wa_err:
            logger.warning(f"Twilio WhatsApp alert dispatch encountered error: {wa_err}")

        return {
            "success": res.get("success", False),
            "status": status_val,
            "message_text": msg_text,
            "provider": provider.get_provider_name(),
            "whatsapp_alert": whatsapp_res
        }
