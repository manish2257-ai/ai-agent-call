from abc import ABC, abstractmethod
from typing import Dict, Any

class SMSProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    async def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS alert to owner. Returns dict with status and message_id."""
        pass
