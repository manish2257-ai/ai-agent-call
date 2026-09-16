from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class TelephonyProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    async def handle_incoming_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming call webhook and generate TwiML / NCCO / Exotel response."""
        pass

    @abstractmethod
    async def transfer_call(self, call_id: str, forward_to_number: str) -> bool:
        """Transfer live active call to the owner's mobile number."""
        pass

    @abstractmethod
    async def terminate_call(self, call_id: str) -> bool:
        """Hang up the call."""
        pass

    @abstractmethod
    def verify_webhook_signature(self, signature: Optional[str], url: str, params: Dict[str, Any]) -> bool:
        """Validate carrier webhook cryptographic signature."""
        pass
