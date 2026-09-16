import os
from typing import Optional, List
from pydantic_settings import BaseSettings

try:
    from dotenv import load_dotenv
    # Load .env from current directory or backend directory
    load_dotenv()
    backend_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    if os.path.exists(backend_env):
        load_dotenv(backend_env)
except ImportError:
    pass

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Personal Call Agent"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = "0.0.0.0"

    # AI / OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_VOICE: str = os.getenv("OPENAI_VOICE", "alloy")
    OPENAI_TIMEOUT_SECONDS: float = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "15.0"))

    # Telephony
    TELEPHONY_PROVIDER: str = "mock"  # "twilio", "exotel", "plivo", "mock"
    TELEPHONY_ACCOUNT_ID: Optional[str] = os.getenv("TELEPHONY_ACCOUNT_ID", "")
    TELEPHONY_AUTH_TOKEN: Optional[str] = os.getenv("TELEPHONY_AUTH_TOKEN", "")
    TELEPHONY_PHONE_NUMBER: str = os.getenv("TELEPHONY_PHONE_NUMBER", "+18005550199")
    TELEPHONY_WEBHOOK_URL: str = os.getenv("TELEPHONY_WEBHOOK_URL", "http://localhost:8000/webhooks/telephony/incoming")

    # SMS
    SMS_PROVIDER: str = "mock"  # "twilio", "exotel", "mock"
    SMS_ACCOUNT_ID: Optional[str] = os.getenv("SMS_ACCOUNT_ID", "")
    SMS_AUTH_TOKEN: Optional[str] = os.getenv("SMS_AUTH_TOKEN", "")
    SMS_FROM_NUMBER: str = os.getenv("SMS_FROM_NUMBER", "+18005550199")
    OWNER_PHONE_NUMBER: str = os.getenv("OWNER_PHONE_NUMBER", "+19876543210")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./call_agent.db")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY") or "session_jwt_key_unset_configured_via_env"
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY", None)

    # WhatsApp (Meta Cloud API)
    WHATSAPP_ENABLED: bool = True
    WHATSAPP_ACCESS_TOKEN: Optional[str] = os.getenv("WHATSAPP_ACCESS_TOKEN", None)
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID", None)
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", None)
    WHATSAPP_RECIPIENT_PHONE_NUMBER: Optional[str] = os.getenv("WHATSAPP_RECIPIENT_PHONE_NUMBER", None)
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: Optional[str] = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "ai_call_agent_verify_token_2026")
    WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v20.0")

    # Twilio WhatsApp Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID", None)
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN", None)
    TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+17372508034")
    TWILIO_WHATSAPP_TO: str = os.getenv("TWILIO_WHATSAPP_TO", "whatsapp:+917367966177")
    TWILIO_CONTENT_SID: str = os.getenv("TWILIO_CONTENT_SID", "HXfe5ab5f00277942d4d4200328b4d403c")

    # Rules
    ALERT_COOLDOWN_MINUTES: int = 5
    MAX_CALL_DURATION_SECONDS: int = 300
    DEMO_MODE: bool = True

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        extra = "allow"

settings = Settings()
