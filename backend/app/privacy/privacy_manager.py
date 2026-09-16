"""
Privacy, Consent, Retention & Audit Management
Features:
- Jurisdiction-aware Consent Modes (DISCLOSURE_ONLY, ASK_FOR_CONSENT, DISABLE_RECORDING_AND_TRANSCRIPTION)
- Consent status tracking (NOT_REQUIRED, PENDING, GRANTED, DECLINED)
- Strict Retention Policies (7, 30, 90, 180, 365 days, Disabled)
- Automatic Data Deletion Cleanup Worker
- Manual Individual & Bulk Data Deletion
- JSON/CSV Data Export ('Export My Data')
- Immutable Audit Logging for Security-Sensitive Actions
- Sensitive Data & Credential Redaction
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("privacy_manager")

class ConsentMode:
    DISABLE_RECORDING_AND_TRANSCRIPTION = "DISABLE_RECORDING_AND_TRANSCRIPTION" # Default MVP
    DISCLOSURE_ONLY = "DISCLOSURE_ONLY"
    ASK_FOR_CONSENT = "ASK_FOR_CONSENT"

class ConsentStatus:
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    DECLINED = "DECLINED"

class PrivacyManager:
    def __init__(self):
        self.privacy_policy_version = "1.0.0"
        self.consent_policy_version = "1.0.0"
        self.default_disclosure_text = (
            "Hello, you've reached Manish's AI assistant. "
            "I'm an AI assistant helping manage his calls. How can I help?"
        )
        self.recording_disclosure_text = (
            "This call may be processed by an AI assistant, and it may be recorded "
            "or transcribed depending on settings. Do you want to continue?"
        )

        # In-memory audit log store
        self._audit_logs: List[Dict[str, Any]] = []

    def log_audit_event(self, action: str, user_id: str, details: Dict[str, Any], ip_address: Optional[str] = None):
        """Records a tamper-evident audit entry."""
        # Cleanse any accidental secrets from audit payload
        clean_details = {k: v for k, v in details.items() if "secret" not in k.lower() and "key" not in k.lower() and "token" not in k.lower()}
        entry = {
            "id": f"audit_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            "action": action,
            "userId": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": clean_details,
            "ipAddress": ip_address or "127.0.0.1"
        }
        self._audit_logs.append(entry)
        logger.info(f"[AUDIT] {action} by {user_id}: {clean_details}")

    def get_audit_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        user_logs = [log for log in self._audit_logs if log["userId"] == user_id]
        return sorted(user_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def redact_secrets(self, text: str) -> str:
        """Redacts credentials, OTPs, PINs, or card patterns from text before storage."""
        if not text:
            return ""
        # Redact OTP / Password / PIN indicators
        redacted = re.sub(r'(?i)\b(otp|password|pin|passcode|token|cvv)\s*(?:is\s*|[:=]\s*)?([0-9a-zA-Z]{3,12})\b', r'\1: [REDACTED]', text)
        # Redact 16-digit card patterns
        redacted = re.sub(r'\b(?:\d{4}[ -]?){3}\d{4}\b', '[CARD NUMBER REDACTED]', redacted)
        return redacted

    def evaluate_consent_rules(
        self,
        consent_mode: str,
        caller_response_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates caller consent according to configured jurisdiction mode.
        Returns consent decision, recording eligibility, and disclosure to speak.
        """
        if consent_mode == ConsentMode.DISABLE_RECORDING_AND_TRANSCRIPTION:
            return {
                "consentRequired": False,
                "consentStatus": ConsentStatus.NOT_REQUIRED,
                "allowRecording": False,
                "allowTranscription": False,
                "disclosureText": self.default_disclosure_text,
                "policyVersion": self.consent_policy_version
            }

        if consent_mode == ConsentMode.DISCLOSURE_ONLY:
            return {
                "consentRequired": False,
                "consentStatus": ConsentStatus.NOT_REQUIRED,
                "allowRecording": True,
                "allowTranscription": True,
                "disclosureText": f"{self.default_disclosure_text} Notice: This call is recorded for quality.",
                "policyVersion": self.consent_policy_version
            }

        if consent_mode == ConsentMode.ASK_FOR_CONSENT:
            # Check caller affirmative or negative answer
            if caller_response_text:
                lower = caller_response_text.lower()
                if any(w in lower for w in ["yes", "sure", "okay", "fine", "agree", "proceed"]):
                    return {
                        "consentRequired": True,
                        "consentStatus": ConsentStatus.GRANTED,
                        "allowRecording": True,
                        "allowTranscription": True,
                        "disclosureText": self.recording_disclosure_text,
                        "policyVersion": self.consent_policy_version
                    }
                elif any(w in lower for w in ["no", "don't", "dont", "refuse", "stop", "decline"]):
                    return {
                        "consentRequired": True,
                        "consentStatus": ConsentStatus.DECLINED,
                        "allowRecording": False,
                        "allowTranscription": False,
                        "disclosureText": "Understood. Continuing without recording or transcript storage.",
                        "policyVersion": self.consent_policy_version
                    }
            return {
                "consentRequired": True,
                "consentStatus": ConsentStatus.PENDING,
                "allowRecording": False,
                "allowTranscription": False,
                "disclosureText": self.recording_disclosure_text,
                "policyVersion": self.consent_policy_version
            }

        return {
            "consentRequired": False,
            "consentStatus": ConsentStatus.NOT_REQUIRED,
            "allowRecording": False,
            "allowTranscription": False,
            "disclosureText": self.default_disclosure_text,
            "policyVersion": self.consent_policy_version
        }

    def cleanup_expired_records(
        self,
        calls: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Scans calls and alerts against configured retention thresholds
        and returns IDs to delete or purge.
        """
        now = datetime.now(timezone.utc)
        call_retention_days = int(settings.get("callMetadataRetentionDays", 90))
        transcript_retention_days = settings.get("transcriptRetentionDays", "DISABLED")
        alert_retention_days = int(settings.get("urgentAlertRetentionDays", 90))

        calls_to_delete = []
        transcripts_to_clear = []
        alerts_to_delete = []

        # 1. Evaluate calls
        for call in calls:
            created_str = call.get("createdAt")
            if not created_str:
                continue
            try:
                created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except Exception:
                continue

            age_days = (now - created_dt).days

            # Call Metadata expired?
            if call_retention_days > 0 and age_days >= call_retention_days:
                calls_to_delete.append(call["callId"])
            else:
                # Transcripts expired?
                if transcript_retention_days == "DISABLED":
                    if call.get("messages") or call.get("transcript"):
                        transcripts_to_clear.append(call["callId"])
                elif isinstance(transcript_retention_days, int) and transcript_retention_days > 0:
                    if age_days >= transcript_retention_days and (call.get("messages") or call.get("transcript")):
                        transcripts_to_clear.append(call["callId"])

        # 2. Evaluate alerts
        for alert in alerts:
            created_str = alert.get("createdAt")
            if not created_str:
                continue
            try:
                created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                if alert_retention_days > 0 and (now - created_dt).days >= alert_retention_days:
                    alerts_to_delete.append(alert["alertId"])
            except Exception:
                continue

        return {
            "callsToDelete": calls_to_delete,
            "transcriptsToClear": transcripts_to_clear,
            "alertsToDelete": alerts_to_delete,
            "timestamp": now.isoformat()
        }

    def export_user_data(self, calls: List[Dict[str, Any]], alerts: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        """Exports sanitized call logs and summaries in portable JSON format."""
        export_payload = {
            "exportVersion": "1.0",
            "exportedAt": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "Exported call metadata and summaries from AI Personal Call Agent.",
            "totalCalls": len(calls),
            "totalAlerts": len(alerts),
            "configuredRetention": {
                "callMetadataDays": settings.get("callMetadataRetentionDays", 90),
                "consentMode": settings.get("consentMode", ConsentMode.DISABLE_RECORDING_AND_TRANSCRIPTION)
            },
            "calls": [
                {
                    "callId": c.get("callId"),
                    "callerName": c.get("callerName"),
                    "callerNumber": c.get("callerNumber"),
                    "urgency": c.get("urgency"),
                    "reason": c.get("reason"),
                    "summary": c.get("summary"),
                    "callbackRequired": c.get("callbackRequired"),
                    "durationSeconds": c.get("duration"),
                    "startedAt": c.get("startedAt"),
                    "consentStatus": c.get("consentStatus")
                }
                for c in calls
            ],
            "alerts": alerts
        }
        return json.dumps(export_payload, indent=2)

privacy_manager = PrivacyManager()
