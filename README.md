# AI Personal Call Agent (Production-Ready MVP)

An autonomous AI telephony receptionist system that answers incoming phone calls, identifies itself, determines caller intent, evaluates urgency with natural language understanding, notifies the owner via SMS and push notifications for urgent matters, and provides a control panel for call history, privacy, and retention management.

> **CRITICAL LEGAL & JURISDICTION NOTICE:**
> Call recording, live AI speech processing, transcription, caller disclosure, biometric data collection, and retention laws vary by jurisdiction (e.g., one-party vs. all-party consent in the US, GDPR in the EU, and DPDP in India). 
> 
> The system owner is solely responsible for consulting legal counsel and configuring the appropriate consent mode (`DISABLE_RECORDING_AND_TRANSCRIPTION`, `DISCLOSURE_ONLY`, or `ASK_FOR_CONSENT`) and disclosure language prior to production deployment. This software does not provide legal advice.

---

## 1. System Architecture

```
Caller
  │ (PSTN / Mobile Network)
  ▼
Exotel Cloud Virtual Number
  │ (Inbound Voice Webhook / Passthru Flow)
  ▼
FastAPI Backend (/webhooks/exotel/incoming)
  │
  ├──► OpenAI Voice AI (GPT-4o-mini / Whisper)
  │      └── Anti-Impersonation & Contextual Urgency Reasoning
  │
  ├──► Firebase Cloud Firestore (Tenant-Isolated Call Logs)
  │
  ├──► Exotel SMS API (Urgent Alert Dispatch to Owner Mobile)
  │      └── Duplicate Suppression & Credential Redaction
  │
  ├──► WhatsApp Cloud API (Official WhatsApp Business Platform Urgent Alert)
  │      └── Template Messaging, Idempotency & Cooldown
  │
  └──► Firebase Cloud Messaging (Push Alert to Android App)
         ▼
Android Control Panel APK (Flutter / Jetpack Compose)
```

---

## 2. Technology Stack

- **Mobile Control Panel:** Flutter / Dart / Material 3 & Native Android APK
- **Backend Service:** Python 3.12+, FastAPI, Pydantic, Uvicorn, HTTPX
- **Cloud Telephony & SMS:** Exotel Voice & SMS APIs
- **Instant Messaging Alerts:** WhatsApp Business Platform / WhatsApp Cloud API
- **Artificial Intelligence:** OpenAI API (GPT-4o / GPT-4o-mini)
- **Database & Auth:** Firebase Cloud Firestore & Firebase Authentication
- **Push Notifications:** Firebase Cloud Messaging (FCM)

---

## 3. Privacy, Consent & Retention Controls

### Consent Modes
1. `DISABLE_RECORDING_AND_TRANSCRIPTION` (**Default MVP setting**): Live conversation is processed transiently in memory to handle the call and formulate the summary. No audio files or turn-by-turn transcripts are persisted.
2. `DISCLOSURE_ONLY`: Caller is notified prior to conversation.
3. `ASK_FOR_CONSENT`: Prompts caller for affirmative consent ("Do you want to continue?"). If declined, persistent storage is deactivated immediately.

### Retention Defaults
- **Call Metadata & Summaries:** 90 days (configurable: 7, 30, 90, 180, 365 days).
- **Transcripts:** Disabled by default.
- **Audio Recordings:** Disabled by default.
- **Urgent Alerts:** 90 days.
- **Automatic Cleanup:** Backend maintenance task scans and deletes expired records.
- **Manual Control:** Individual call/transcript deletion and bulk data purge with confirmation.

---

## 4. Environment Variables (`.env`)

Create a `.env` file in the root or `backend/` directory:

```bash
# Server Configuration
PORT=8000
HOST=0.0.0.0
DEMO_MODE=true

# Firebase Service Account
FIREBASE_CREDENTIALS_PATH=./firebase/service-account.json

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Exotel Telephony & SMS Credentials
EXOTEL_API_KEY=your_exotel_api_key_here
EXOTEL_API_TOKEN=your_exotel_api_token_here
EXOTEL_ACCOUNT_SID=your_exotel_account_sid_here
EXOTEL_SUBDOMAIN=api.exotel.com
EXOTEL_VIRTUAL_NUMBER=+918047100000
EXOTEL_SMS_SENDER_ID=EXOTEL

# Owner Configuration
OWNER_PHONE_NUMBER=+919876543210
SMS_COOLDOWN_MINUTES=15
```

---

## 5. API Credential Setup Guide

### 1. OpenAI
- **Required Credential:** `OPENAI_API_KEY`
- **Where to Get It:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Where to Put It:** In `.env` under `OPENAI_API_KEY`.

### 2. Exotel (Telephony & SMS)
- **Required Credentials:** `EXOTEL_API_KEY`, `EXOTEL_API_TOKEN`, `EXOTEL_ACCOUNT_SID`, `EXOTEL_VIRTUAL_NUMBER`
- **Where to Get It:** Exotel Dashboard -> API Settings & Virtual Numbers
- **Where to Put It:** In `.env`.

### 3. Firebase
- **Required Credential:** Service Account JSON file
- **Where to Get It:** Firebase Console -> Project Settings -> Service Accounts -> Generate New Private Key.
- **Where to Put It:** Save to `backend/service-account.json` and set `FIREBASE_CREDENTIALS_PATH`.

### 4. WhatsApp Business Platform / WhatsApp Cloud API
- **Required Credentials:**
  - `WHATSAPP_ENABLED=true`
  - `WHATSAPP_ACCESS_TOKEN`: Meta System User Permanent Access Token (never store in APK)
  - `WHATSAPP_PHONE_NUMBER_ID`: WhatsApp Business Phone Number ID from Meta Developer Dashboard
  - `WHATSAPP_BUSINESS_ACCOUNT_ID`: WhatsApp Business Account (WABA) ID
  - `WHATSAPP_RECIPIENT_PHONE_NUMBER`: Destination personal phone number in E.164 format (e.g. `+919876543210`)
  - `WHATSAPP_API_VERSION`: Graph API version (default: `v20.0`)
- **Setup Steps:**
  1. Register at [developers.facebook.com](https://developers.facebook.com) and create a Business App with "WhatsApp" product added.
  2. Navigate to **WhatsApp > API Setup** to copy your test or production Phone Number ID and WABA ID.
  3. Under **Business Settings > Users > System Users**, generate a permanent System User Access Token with `whatsapp_business_messaging` and `whatsapp_business_management` permissions.
  4. Optionally submit and approve the `urgent_call_alert` utility message template in Meta WhatsApp Manager (or use session text fallback).
  5. Place all credentials in `backend/.env`. **Never** expose or bundle WhatsApp tokens inside the mobile app.

*Note: If credentials are not supplied, the system automatically runs in **Demo Mode**, enabling all testing workflows.*

---

## 6. Local Development & Testing

### Running the FastAPI Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation: `http://localhost:8000/docs`

### Running Backend Tests
```bash
cd backend
pytest tests/
```

### Running the Flutter Mobile App
```bash
cd mobile
flutter pub get
flutter test
flutter run
```

---

## 7. Optional Carrier Call Forwarding (Unanswered / Busy Calls)

To have your AI receptionist answer calls when your personal mobile is unanswered or busy:
- **Jio / Airtel / Vi (When Unanswered):** Dial `*61*<EXOTEL_VIRTUAL_NUMBER>#`
- **Jio / Airtel / Vi (When Busy):** Dial `*67*<EXOTEL_VIRTUAL_NUMBER>#`
- **US Carriers (AT&T / T-Mobile / Verizon):** Dial `*71<EXOTEL_VIRTUAL_NUMBER>`
- **Deactivate All Call Forwarding:** Dial `##002#`

---

## 8. Final Acceptance Test Verification

1. **AI Answering:** Exotel inbound webhook triggers automated greeting.
2. **AI Identity Disclosure:** AI assistant explicitly identifies itself as an AI.
3. **Conversational Turn Taking:** Analyzes caller purpose and gathers details naturally.
4. **Urgency Classification:** Accurately identifies outages/emergencies as HIGH/CRITICAL.
5. **SMS Alert Triggering:** Dispatches sanitized SMS to owner phone and prevents duplicate alerts.
6. **WhatsApp Urgent Alerts:** Dispatches official WhatsApp Business Platform / Cloud API message for HIGH/CRITICAL calls.
7. **Multi-Channel Resilience:** WhatsApp failure does not interrupt SMS or push notification delivery.
8. **Idempotency & Cooldown:** Uses `callId + WHATSAPP` concept to suppress duplicate messaging within cooldown.
9. **WhatsApp Alert Retry:** Allows on-demand retry of WhatsApp notification from the Android alerts screen.
10. **Privacy Sanitization:** Strips OTPs, passwords, and sensitive credentials prior to formatting WhatsApp templates.
11. **Server-Side Token Isolation:** WhatsApp tokens are never sent to or stored on the mobile client.
12. **Push Notifications:** Delivers FCM alerts to the Android device.
13. **Privacy & Retention:** Respects default zero-persistence policy for audio and transcripts.
14. **Manual Deletion:** Allows single call and bulk history purge.
15. **Channel Status Transparency:** Shows connection state and per-channel delivery badges in the UI.
