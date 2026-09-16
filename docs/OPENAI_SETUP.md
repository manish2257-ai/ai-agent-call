# OpenAI API Integration & Setup Guide

This guide explains how the OpenAI API integration works in the **AI Personal Call Agent** project, where to configure your API key, and how security is enforced.

---

## 🔒 Security Principles

1. **Strictly Server-Side**: All OpenAI API calls originate from the FastAPI backend. Neither the Android app nor the Flutter mobile client ever possesses or transmits the API key.
2. **Environment-Only Secrets**: The API key is loaded strictly from the `OPENAI_API_KEY` environment variable. It is never hardcoded in source code or commits.
3. **Protected `.env`**: `backend/.env` is excluded from Git via `.gitignore`.
4. **Redacted Error Logs**: Upstream API error messages are automatically sanitized by `OpenAIService._sanitize_error` to strip any Bearer tokens or `sk-...` strings before writing to logs.
5. **Safe Status Endpoints**: `/api/openai/status` and `/api/openai/health` report readiness (`READY` or `NOT_CONFIGURED`) without ever returning the actual key.

---

## 🛠️ Where to Add Your OpenAI API Key

### Local Development

Add your key to `backend/.env`:

```bash
# In backend/.env
OPENAI_API_KEY=your_new_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_VOICE=alloy
OPENAI_TIMEOUT_SECONDS=15.0
```

### Production / Deployment (e.g. Render, Railway, Cloud Run)

In your hosting platform's dashboard:
1. Navigate to **Environment Variables**.
2. Add a new variable:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: `sk-proj-...`
3. Optional configuration variables:
   - `OPENAI_MODEL`: `gpt-4o-mini` (default) or `gpt-4o`
   - `OPENAI_TIMEOUT_SECONDS`: `15.0` (default)
   - `OPENAI_VOICE`: `alloy` (default)

---

## 📡 API Endpoints

### 1. Check Configuration Status
```http
GET /api/openai/status
```
**Response (When Configured):**
```json
{
  "configured": true,
  "status": "READY",
  "model": "gpt-4o-mini",
  "timeout_seconds": 15.0,
  "message": "OpenAI API service is configured and ready."
}
```

**Response (When Missing Key):**
```json
{
  "configured": false,
  "status": "NOT_CONFIGURED",
  "model": "gpt-4o-mini",
  "timeout_seconds": 15.0,
  "message": "OPENAI_API_KEY environment variable is not configured."
}
```

### 2. Lightweight Health Check
```http
GET /api/openai/health
```
```json
{
  "configured": true,
  "status": "READY"
}
```

### 3. Server-Side Connectivity Test
```http
POST /api/openai/test
Content-Type: application/json

{
  "prompt": "Say hello in 5 words"
}
```
**Response:**
```json
{
  "success": true,
  "configured": true,
  "status": "READY",
  "model": "gpt-4o-mini",
  "response": "Hello! How can I help?"
}
```

---

## 🤖 How the AI Call Agent Uses OpenAI

1. **Conversational Turn Response (`AIAgentService.generate_response`)**:
   - Generates natural, context-aware call responses tailored to the owner's personality setting (e.g., Professional, Friendly, Direct).
   - Enforces the user's approved knowledge base rules.
   - Automatically supports English, Hindi, or natural Hinglish.
   - If OpenAI is unconfigured or unavailable, automatically falls back to the deterministic local conversation engine.

2. **Urgency Classification (`UrgencyClassifier.classify`)**:
   - Analyzes real-time or completed call transcripts.
   - Produces structured JSON containing `urgency` (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `SPAM`), `reason`, `action_required`, and `callback_required`.
   - Triggers automated Twilio WhatsApp and SMS alerts for urgent calls.

---

## 🧪 Running Tests

Run the backend test suite:
```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_openai.py
```
All tests verify safe redaction, unconfigured handling, and mock completions.
