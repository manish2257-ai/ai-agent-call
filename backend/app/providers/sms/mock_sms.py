from typing import Dict, Any
import datetime
from .base import SMSProvider
import logging

logger = logging.getLogger("MockSMS")

class MockSMSProvider(SMSProvider):
    def get_provider_name(self) -> str:
        return "Mock SMS (Demo Simulator)"

    async def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        msg_id = f"mock_sms_{int(datetime.datetime.now().timestamp())}"
        logger.info(f"[DEMO SMS SENT] To: {to_number}\nMessage:\n{message}")
        return {
            "success": True,
            "message_id": msg_id,
            "status": "DELIVERED",
            "to": to_number,
            "preview": message
        }
