import os
from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Personal Call Agent"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = "0.0.0.0"

    # AI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_VOICE: str = "alloy"

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
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-jwt-key-for-ai-call-agent-control-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY", "dev_encryption_key_32_bytes_len!")

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
        env_file = ".env"
        extra = "allow"

settings = Settings()
