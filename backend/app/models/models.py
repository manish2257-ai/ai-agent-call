import enum
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Float, Enum, Index
)
from sqlalchemy.orm import relationship
from ..database.session import Base

class UrgencyLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CallStatus(str, enum.Enum):
    COMPLETED = "Completed"
    ESCALATED = "Escalated"
    TRANSFERRED = "Transferred"
    FAILED = "Failed"
    MISSED = "Missed"
    SPAM = "Spam"

class ContactCategory(str, enum.Enum):
    FAMILY = "Family"
    FRIEND = "Friend"
    CLIENT = "Client"
    COLLEGE = "College"
    BUSINESS = "Business"
    OTHER = "Other"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    calls = relationship("Call", back_populates="user", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")
    rules = relationship("UrgencyRuleModel", back_populates="user", cascade="all, delete-orphan")
    knowledge_items = relationship("KnowledgeBaseItem", back_populates="user", cascade="all, delete-orphan")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True, nullable=False)
    is_agent_enabled = Column(Boolean, default=True)
    ai_phone_number = Column(String(50), default="+18005550199")
    owner_phone_number = Column(String(50), default="+19876543210")
    greeting = Column(Text, default="Hello, you've reached Manish's AI assistant. Manish isn't available to take the call right now. I can help you with your request and pass along an important message. How can I help?")
    personality = Column(String(50), default="Professional")  # Professional, Friendly, Concise, Business, Personal Assistant
    system_prompt = Column(Text, nullable=True)
    language_mode = Column(String(50), default="English")  # English, Hindi, Hinglish, Auto
    max_call_duration_seconds = Column(Integer, default=300)
    urgency_threshold = Column(String(50), default="HIGH")  # Threshold to trigger SMS: HIGH / CRITICAL
    alert_template = Column(Text, default="URGENT CALL ALERT\nCaller: {caller}\nNumber: {number}\nUrgency: {urgency}\nReason: {reason}\nSummary: {summary}\nTime: {time}\nPlease review in AI Call Agent app.")
    sms_cooldown_minutes = Column(Integer, default=5)
    is_transcript_storage_enabled = Column(Boolean, default=True)
    is_audio_recording_enabled = Column(Boolean, default=False)
    retention_days = Column(Integer, default=90)
    transfer_enabled = Column(Boolean, default=True)
    transfer_number = Column(String(50), nullable=True)

    user = relationship("User", back_populates="settings")

class Call(Base):
    __tablename__ = "calls"

    id = Column(String(100), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    caller_number = Column(String(50), index=True, nullable=False)
    caller_name = Column(String(255), default="Unknown Caller")
    status = Column(String(50), default=CallStatus.COMPLETED.value, index=True)
    urgency = Column(String(50), default=UrgencyLevel.LOW.value, index=True)
    duration_seconds = Column(Integer, default=0)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="calls")
    summary = relationship("CallSummary", back_populates="call", uselist=False, cascade="all, delete-orphan")
    transcript = relationship("CallTranscript", back_populates="call", uselist=False, cascade="all, delete-orphan")
    messages = relationship("CallMessage", back_populates="call", cascade="all, delete-orphan")
    urgency_events = relationship("UrgencyEvent", back_populates="call", cascade="all, delete-orphan")
    sms_alerts = relationship("SmsAlert", back_populates="call", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_calls_user_caller", "user_id", "caller_number"),
        Index("idx_calls_user_created", "user_id", "created_at"),
        Index("idx_calls_user_urgency", "user_id", "urgency"),
    )

class CallSummary(Base):
    __tablename__ = "call_summaries"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(100), ForeignKey("calls.id"), unique=True, index=True, nullable=False)
    summary_text = Column(Text, nullable=False)
    action_required = Column(Text, nullable=True)
    callback_required = Column(Boolean, default=False)
    ai_outcome = Column(String(255), default="Handled routine enquiry")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    call = relationship("Call", back_populates="summary")

class CallTranscript(Base):
    __tablename__ = "call_transcripts"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(100), ForeignKey("calls.id"), unique=True, index=True, nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    call = relationship("Call", back_populates="transcript")

class CallMessage(Base):
    __tablename__ = "call_messages"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(100), ForeignKey("calls.id"), index=True, nullable=False)
    speaker = Column(String(50), nullable=False)  # "AI" or "Caller"
    content = Column(Text, nullable=False)
    timestamp_str = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    call = relationship("Call", back_populates="messages")

class UrgencyEvent(Base):
    __tablename__ = "urgency_events"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(100), ForeignKey("calls.id"), index=True, nullable=False)
    urgency_level = Column(String(50), index=True, nullable=False)
    reason = Column(Text, nullable=False)
    confidence_score = Column(Float, default=1.0)
    raw_response_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    call = relationship("Call", back_populates="urgency_events")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(50), index=True, nullable=False)
    category = Column(String(50), default=ContactCategory.FRIEND.value)
    notes = Column(Text, nullable=True)
    always_alert = Column(Boolean, default=False)
    always_transfer = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="contacts")

class BlockedNumber(Base):
    __tablename__ = "blocked_numbers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    phone_number = Column(String(50), index=True, nullable=False)
    reason = Column(String(255), default="Spam")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class UrgencyRuleModel(Base):
    __tablename__ = "urgency_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    condition_type = Column(String(50), nullable=False)  # URGENCY_LEVEL, VIP_CALLER, KEYWORD, MARKETING_SPAM
    condition_value = Column(String(255), nullable=False)
    action = Column(String(50), nullable=False)  # SMS, CALL_TRANSFER, NO_ALERT
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="rules")

class KnowledgeBaseItem(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="FAQ")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="knowledge_items")

class SmsAlert(Base):
    __tablename__ = "sms_alerts"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(100), ForeignKey("calls.id"), index=True, nullable=True)
    to_number = Column(String(50), nullable=False)
    urgency = Column(String(50), default="HIGH")
    message_text = Column(Text, nullable=False)
    status = Column(String(50), default="DELIVERED")  # DELIVERED, PENDING, FAILED
    provider = Column(String(50), default="twilio")
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    call = relationship("Call", back_populates="sms_alerts")

class TelephonyConfig(Base):
    __tablename__ = "telephony_config"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    provider_name = Column(String(50), default="twilio")
    account_id = Column(String(255), nullable=True)
    encrypted_auth_token = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    webhook_status = Column(String(50), default="CONFIGURED")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
