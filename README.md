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

## 8. Render Deployment

To deploy the FastAPI backend on [Render](https://render.com):

### Option A: Docker Runtime (Recommended if using Docker)
1. **Create a New Web Service** on Render and connect your GitHub repository (`ai-agent-call`).
2. **Configure Service Settings:**
   - **Name:** `ai-call-agent-backend`
   - **Root Directory:** `backend`
   - **Environment / Runtime:** `Docker`
   - **Plan:** `Free`
   *(Render automatically builds the `Dockerfile` in `backend/` and starts with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)*

### Option B: Native Python Runtime
1. **Configure Service Settings:**
   - **Root Directory:** `backend`
   - **Environment / Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`

3. **Configure Environment Variables (in Render Dashboard > Environment):**
   - `PORT`: (Managed automatically by Render, binds dynamically)
   - `ENVIRONMENT`: `production`
   - `DEBUG`: `false`
   - `WHATSAPP_ENABLED`: `true`
   - `WHATSAPP_WEBHOOK_VERIFY_TOKEN`: `<your-custom-verify-token>`
   - `WHATSAPP_ACCESS_TOKEN`: `<your-meta-cloud-api-token>`
   - `WHATSAPP_PHONE_NUMBER_ID`: `<your-meta-phone-number-id>`
   - `WHATSAPP_BUSINESS_ACCOUNT_ID`: `<your-waba-id>`
   - `WHATSAPP_RECIPIENT_PHONE_NUMBER`: `<owner-whatsapp-number-with-country-code>`
   - `JWT_SECRET`: `<secure-random-32-character-secret>`
   - `OPENAI_API_KEY`: `<your-openai-api-key>` (if using OpenAI voice/LLM features)
   - `DATABASE_URL`: `<render-postgres-internal-url>` (or external PostgreSQL / default SQLite)
   - `OWNER_PHONE_NUMBER`: `<owner-phone-number>`

4. **Health Check Endpoint:**
   - URL Path: `/health`
   - Expected Response: `{"status":"ok"}`

5. **Meta WhatsApp Webhook Configuration (in Meta Developer Portal):**
   - **Callback URL:** `https://<YOUR-RENDER-SERVICE-NAME>.onrender.com/webhooks/whatsapp`
   - **Verify Token:** Match the `WHATSAPP_WEBHOOK_VERIFY_TOKEN` configured in your Render environment variables.
   - **Webhook Subscriptions:** `messages`

---

## 10. Twilio WhatsApp Setup

### Overview
The backend integrates Twilio WhatsApp messaging to dispatch real-time alerts when urgent or critical calls are detected by the AI agent. It supports both the Twilio WhatsApp Sandbox (using template Content SIDs) and production WhatsApp Business Profiles.

### Required Environment Variables
Configure these in your backend `.env` file or cloud deployment dashboard (e.g., Render Environment Variables):

```bash
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token_here"
TWILIO_WHATSAPP_FROM="whatsapp:+17372508034"
TWILIO_WHATSAPP_TO="whatsapp:+917367966177"
TWILIO_CONTENT_SID="HXfe5ab5f00277942d4d4200328b4d403c"
```

> **Security Rule:** Never commit `TWILIO_AUTH_TOKEN` to version control or expose it to client applications.

### Where to Find Twilio Account SID and Configure Auth Token
1. Log into your [Twilio Console](https://console.twilio.com/).
2. On the **Dashboard**, under **Account Info**:
   - **Account SID:** Copy your `Account SID` (starts with `AC...`) and set it to `TWILIO_ACCOUNT_SID`.
   - **Auth Token:** Click "Show" next to `Auth Token`, copy it, and set it to `TWILIO_AUTH_TOKEN`.
3. In Twilio Console, navigate to **Messaging > Try it out > Send a WhatsApp message** to activate your Twilio WhatsApp Sandbox number (`whatsapp:+17372508034`).
4. Join the sandbox from your recipient phone by sending the join keyword (e.g. `join <sandbox-keyword>`) to `+1 737 250 8034`.

### How to Install Dependencies
From the `backend` directory:
```bash
cd backend
pip install -r requirements.txt
```
*(Dependencies include `twilio>=9.1.0` and `python-dotenv>=1.0.1`)*

### How to Start the Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

On Render (Docker runtime), the container automatically starts with:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### How to Test WhatsApp
You can verify the Twilio WhatsApp integration immediately using either curl or Swagger:

#### 1. Via curl:
```bash
curl -X POST "http://localhost:8000/api/whatsapp/test" \
     -H "Content-Type: application/json" \
     -d '{}'
```

Expected Response:
```json
{
  "success": true,
  "message": "WhatsApp message submitted successfully",
  "sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "status": "queued"
}
```

If credentials are not yet configured:
```json
{
  "success": false,
  "message": "Twilio WhatsApp configuration is incomplete.",
  "error": "Twilio WhatsApp configuration is incomplete."
}
```

#### 2. Via Swagger / OpenAPI UI:
1. Open your browser and navigate to:
   - Local: `http://localhost:8000/docs`
   - Render: `https://<YOUR-RENDER-SERVICE-NAME>.onrender.com/docs`
2. Scroll to the **WhatsApp** tag.
3. Open `POST /api/whatsapp/test`, click **Try it out**, and click **Execute**.
4. Check `GET /api/whatsapp/status` to safely verify configuration readiness without exposing your Auth Token.

### How the WhatsApp Notification Flow Works
```
Incoming Call / Simulation
           ↓
AI Urgency Classifier (Detects HIGH or CRITICAL)
           ↓
Alert System (SMSService & CallManager)
           ↓
Twilio WhatsApp Service (Deduplication / Cooldown Check)
           ↓
Twilio Python SDK (client.messages.create with Content SID)
           ↓
WhatsApp Message Delivered to Owner Device
           ↓
Firebase Firestore (Stores whatsapp_status, whatsapp_message_sid, whatsapp_sent_at)
```

- **Loop & Cooldown Prevention:** The service tracks recent dispatches per caller/call to ensure notifications are never fired in an uncontrolled loop.
- **Fault Tolerance:** If Twilio is temporarily unavailable or credentials expire, the error is safely caught and logged, preventing any disruption to ongoing calls, SMS, or app operations.
- **Firebase Status Sync:** Records `whatsapp_status`, `whatsapp_message_sid`, and `whatsapp_sent_at` in Firestore, without ever storing the Twilio Auth Token.

### Sandbox Limitations
- In the Twilio Sandbox, messages can only be sent to phone numbers that have explicitly opted in using the sandbox join code.
- Outbound messages from the Sandbox must use pre-approved sandbox Content Templates (such as `TWILIO_CONTENT_SID=HXfe5ab5f00277942d4d4200328b4d403c`).
- Session windows: Users must interact within 24 hours for open two-way text messages, or use Content Templates outside the 24-hour window.

### How to Switch to Production Later
To migrate from Twilio Sandbox to a production WhatsApp Business Profile:
1. In Twilio Console, go to **Messaging > Senders > WhatsApp senders** and register your WhatsApp Business Profile with your official phone number.
2. Update `TWILIO_WHATSAPP_FROM` to your approved production WhatsApp sender (e.g. `whatsapp:+1XXXXXXXXXX`).
3. Create your custom WhatsApp message templates in Twilio Content Editor, submit them to Meta for approval, and update `TWILIO_CONTENT_SID` with your approved production Content SID.
4. No application code changes are required—all configuration is managed via environment variables!


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
