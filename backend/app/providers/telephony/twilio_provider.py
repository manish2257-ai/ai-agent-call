from typing import Dict, Any, Optional
from .base import TelephonyProvider
import logging

logger = logging.getLogger("TwilioProvider")

class TwilioTelephonyProvider(TelephonyProvider):
    def __init__(self, account_sid: str, auth_token: str, phone_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number

    def get_provider_name(self) -> str:
        return "Twilio"

    async def handle_incoming_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        caller = payload.get("From", "Unknown")
        call_sid = payload.get("CallSid", "CA_mock")
        logger.info(f"Twilio incoming call: {call_sid} from {caller}")
        
        # Generates standard TwiML with Stream / Gather
        twiml_response = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>\n"
            '    <Say voice="Polly.Aditi">Hello, you have reached Manish\'s AI assistant. How can I help you today?</Say>\n'
            '    <Gather input="speech" action="/webhooks/telephony/media" speechTimeout="auto" language="en-IN">\n'
            "    </Gather>\n"
            "</Response>"
        )
        return {"content_type": "application/xml", "body": twiml_response}

    async def transfer_call(self, call_id: str, forward_to_number: str) -> bool:
        logger.info(f"Twilio transferring call {call_id} to {forward_to_number}")
        # In live production with twilio-python:
        # client = Client(self.account_sid, self.auth_token)
        # client.calls(call_id).update(twiml=f'<Response><Dial>{forward_to_number}</Dial></Response>')
        return True

    async def terminate_call(self, call_id: str) -> bool:
        logger.info(f"Twilio terminating call {call_id}")
        return True

    def verify_webhook_signature(self, signature: Optional[str], url: str, params: Dict[str, Any]) -> bool:
        if not signature:
            return False
        # Production validates via RequestValidator(self.auth_token).validate(...)
        return True
