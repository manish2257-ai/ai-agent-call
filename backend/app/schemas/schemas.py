from typing import Optional, List, Dict, Any
import datetime
from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = "Manish"
    phone_number: Optional[str] = "+19876543210"

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    phone_number: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class UserSettingsSchema(BaseModel):
    is_agent_enabled: bool = True
    ai_phone_number: str = "+18005550199"
    owner_phone_number: str = "+19876543210"
    greeting: str
    personality: str = "Professional"
    system_prompt: Optional[str] = None
    language_mode: str = "English"
    max_call_duration_seconds: int = 300
    urgency_threshold: str = "HIGH"
    alert_template: str
    sms_cooldown_minutes: int = 5
    is_transcript_storage_enabled: bool = True
    is_audio_recording_enabled: bool = False
    retention_days: int = 90
    transfer_enabled: bool = True
    transfer_number: Optional[str] = None

    class Config:
        from_attributes = True

class CallMessageSchema(BaseModel):
    speaker: str
    content: str
    timestamp_str: Optional[str] = None

    class Config:
        from_attributes = True

class CallSummarySchema(BaseModel):
    summary_text: str
    action_required: Optional[str] = None
    callback_required: bool = False
    ai_outcome: Optional[str] = None

    class Config:
        from_attributes = True

class CallSchema(BaseModel):
    id: str
    caller_number: str
    caller_name: str
    status: str
    urgency: str
    duration_seconds: int
    reason: Optional[str]
    created_at: datetime.datetime
    summary: Optional[CallSummarySchema] = None
    messages: List[CallMessageSchema] = []

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    name: str
    phone_number: str
    category: str = "Friend"
    notes: Optional[str] = None
    always_alert: bool = False
    always_transfer: bool = False
    is_blocked: bool = False

class ContactResponse(ContactCreate):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class UrgencyRuleCreate(BaseModel):
    title: str
    condition_type: str
    condition_value: str
    action: str
    is_enabled: bool = True

class UrgencyRuleResponse(UrgencyRuleCreate):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class KnowledgeItemCreate(BaseModel):
    title: str
    category: str = "FAQ"
    content: str

class KnowledgeItemResponse(KnowledgeItemCreate):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class UrgencyClassificationResult(BaseModel):
    urgency: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    reason: str
    caller_name: Optional[str] = "Caller"
    callback_required: bool = False
    summary: str

class DashboardStats(BaseModel):
    is_agent_enabled: bool
    ai_phone_number: str
    calls_today: int
    total_calls: int
    urgent_calls: int
    missed_calls: int
    avg_duration_seconds: int
    last_call: Optional[Dict[str, Any]] = None
    last_urgent_alert: Optional[Dict[str, Any]] = None

class TestAlertRequest(BaseModel):
    caller_name: str = "Rahul"
    caller_number: str = "+919876543210"
    urgency: str = "HIGH"
    reason: str = "Website is currently unavailable"
    summary: str = "Customer reports that users cannot place orders."

class SimulatedCallRequest(BaseModel):
    scenario_id: str  # "website_outage", "general_enquiry", "client_contract", "vip_family", "spam_marketing", "emergency"
    caller_name: Optional[str] = None
    caller_number: Optional[str] = None
    caller_speech: Optional[str] = None
