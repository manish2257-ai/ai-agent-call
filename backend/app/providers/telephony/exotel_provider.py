from typing import Dict, Any, Optional
from .base import TelephonyProvider
import logging

logger = logging.getLogger("ExotelProvider")

class ExotelTelephonyProvider(TelephonyProvider):
    def __init__(self, account_sid: str, api_key: str, api_token: str, virtual_number: str):
        self.account_sid = account_sid
        self.api_key = api_key
        self.api_token = api_token
        self.virtual_number = virtual_number

    def get_provider_name(self) -> str:
        return "Exotel"

    async def handle_incoming_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        caller = payload.get("From", "Unknown")
        call_id = payload.get("CallSid", payload.get("CallUUID", "exo_mock"))
        logger.info(f"Exotel incoming call: {call_id} from {caller}")
        # Exotel uses Applet flows / JSON callback responses
        response_body = {
            "action": "play_and_record",
            "prompt_url": "https://api.yourdomain.com/static/greeting.mp3",
            "callback_url": "https://api.yourdomain.com/webhooks/telephony/media"
        }
        return {"content_type": "application/json", "body": response_body}

    async def transfer_call(self, call_id: str, forward_to_number: str) -> bool:
        logger.info(f"Exotel connecting caller {call_id} to owner {forward_to_number}")
        return True

    async def terminate_call(self, call_id: str) -> bool:
        logger.info(f"Exotel ending call {call_id}")
        return True

    def verify_webhook_signature(self, signature: Optional[str], url: str, params: Dict[str, Any]) -> bool:
        return True
