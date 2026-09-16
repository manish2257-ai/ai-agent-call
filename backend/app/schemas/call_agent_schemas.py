"""
Pydantic Schemas for AI Personal Call Agent
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SettingsModel(BaseModel):
    agentEnabled: bool = True
    ownerPhoneNumber: str = "+917367966177"
    aiPhoneNumber: str = "+918047100000"
    aiGreeting: str = "Hello, you've reached Manish's AI assistant. I'm an AI assistant helping manage his calls. How can I help?"
    aiPersonality: str = "Professional"
    urgencyThreshold: str = "HIGH"
    smsAlertsEnabled: bool = True
    whatsappAlertsEnabled: bool = True
    whatsappRecipientNumber: str = "+917367966177"
    pushNotificationsEnabled: bool = True
    maxCallDurationSeconds: int = 180
    recordingEnabled: bool = False
    persistentTranscriptionEnabled: bool = False
    consentMode: str = "DISABLE_RECORDING_AND_TRANSCRIPTION"
    callMetadataRetentionDays: int = 90
    transcriptRetentionDays: str = "DISABLED"
    recordingRetentionDays: str = "DISABLED"
    urgentAlertRetentionDays: int = 90
    smsProvider: str = "Exotel"
    telephonyProvider: str = "Exotel"

class TranscriptMessageModel(BaseModel):
    speaker: str
    content: str
    timestamp: str

class CallRecordModel(BaseModel):
    callId: str
    callerName: str
    callerNumber: str
    reason: str
    urgency: str
    summary: str
    callbackRequired: bool = False
    status: str = "COMPLETED"
    smsSent: bool = False
    whatsappSent: bool = False
    fcmSent: bool = False
    whatsappStatus: str = "NOT_CONFIGURED"
    whatsappMessageId: Optional[str] = None
    whatsappSentAt: Optional[str] = None
    startedAt: Optional[str] = None
    endedAt: Optional[str] = None
    duration: int = 0
    consentStatus: str = "NOT_REQUIRED"
    consentTimestamp: Optional[str] = None
    consentPolicyVersion: str = "1.0.0"
    recordingEnabled: bool = False
    transcriptionEnabled: bool = False
    messages: List[TranscriptMessageModel] = []
    createdAt: Optional[str] = None

class UrgentAlertModel(BaseModel):
    alertId: str
    callId: str
    callerName: str
    callerNumber: str
    urgency: str
    reason: str
    summary: str
    status: str = "DELIVERED"
    smsStatus: str = "SENT"
    whatsappStatus: str = "SENT"
    fcmStatus: str = "SENT"
    provider: str = "Exotel & WhatsApp Cloud"
    createdAt: Optional[str] = None

class TestWhatsAppRequest(BaseModel):
    recipientNumber: Optional[str] = None
    messageText: Optional[str] = "AI Call Agent test notification. WhatsApp integration is working."

class DemoSimulateCallRequest(BaseModel):
    scenario: str = "outage" # outage, enquiry, contract, family, spam, emergency
    callerName: Optional[str] = None
    callerNumber: Optional[str] = None
    speechInput: Optional[str] = None

class TestSmsRequest(BaseModel):
    destinationNumber: Optional[str] = None
    urgency: str = "HIGH"
    reason: str = "Manual test alert from Android control panel"
    summary: str = "Testing real-time SMS delivery to owner phone."

class TestNotificationRequest(BaseModel):
    title: str = "Urgent Call Alert (Test)"
    body: str = "Website outage reported by Rahul Verma. Urgent callback required."

class BulkPurgeRequest(BaseModel):
    confirmPhrase: str = Field(..., description="Must equal 'DELETE_ALL_DATA' to confirm")
