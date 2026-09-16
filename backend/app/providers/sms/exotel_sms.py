from typing import Dict, Any
from .base import SMSProvider
import logging
import httpx

logger = logging.getLogger("ExotelSMS")

class ExotelSMSProvider(SMSProvider):
    def __init__(self, account_sid: str, api_key: str, api_token: str, sender_id: str):
        self.account_sid = account_sid
        self.api_key = api_key
        self.api_token = api_token
        self.sender_id = sender_id

    def get_provider_name(self) -> str:
        return "Exotel SMS"

    async def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        url = f"https://api.exotel.com/v1/Accounts/{self.account_sid}/Sms/send.json"
        data = {
            "From": self.sender_id,
            "To": to_number,
            "Body": message
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(self.api_key, self.api_token)
                )
                if response.status_code in (200, 201):
                    return {"success": True, "message_id": "exo_msg_id", "status": "DELIVERED"}
                return {"success": False, "error": response.text, "status": "FAILED"}
        except Exception as e:
            logger.exception("Exotel SMS exception")
            return {"success": False, "error": str(e), "status": "FAILED"}
