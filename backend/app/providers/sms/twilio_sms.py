from typing import Dict, Any
from .base import SMSProvider
import logging
import httpx

logger = logging.getLogger("TwilioSMS")

class TwilioSMSProvider(SMSProvider):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    def get_provider_name(self) -> str:
        return "Twilio SMS"

    async def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        data = {
            "From": self.from_number,
            "To": to_number,
            "Body": message
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(self.account_sid, self.auth_token)
                )
                if response.status_code in (200, 201):
                    res_json = response.json()
                    logger.info(f"Twilio SMS dispatched: SID={res_json.get('sid')}")
                    return {"success": True, "message_id": res_json.get("sid"), "status": "DELIVERED"}
                else:
                    logger.error(f"Twilio SMS failed with status {response.status_code}: {response.text}")
                    return {"success": False, "error": response.text, "status": "FAILED"}
        except Exception as e:
            logger.exception("Twilio SMS request exception")
            return {"success": False, "error": str(e), "status": "FAILED"}
