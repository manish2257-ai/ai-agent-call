from typing import Dict, Any, Optional
from .base import TelephonyProvider
import logging

logger = logging.getLogger("MockTelephony")

class MockTelephonyProvider(TelephonyProvider):
    def __init__(self, phone_number: str = "+18005550199"):
        self.phone_number = phone_number

    def get_provider_name(self) -> str:
        return "MockTelephony (Demo)"

    async def handle_incoming_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        caller = payload.get("From", "+919876543210")
        logger.info(f"[DEMO SIMULATION] Answered simulated call from {caller}")
        return {
            "status": "answered",
            "greeting": "Hello, you've reached Manish's AI assistant. Manish isn't available to take the call right now. How can I help you?",
            "call_sid": f"demo_call_{int(100000 + 50000)}"
        }

    async def transfer_call(self, call_id: str, forward_to_number: str) -> bool:
        logger.info(f"[DEMO SIMULATION] Forwarded call {call_id} to owner {forward_to_number}")
        return True

    async def terminate_call(self, call_id: str) -> bool:
        logger.info(f"[DEMO SIMULATION] Terminated call {call_id}")
        return True

    def verify_webhook_signature(self, signature: Optional[str], url: str, params: Dict[str, Any]) -> bool:
        return True
