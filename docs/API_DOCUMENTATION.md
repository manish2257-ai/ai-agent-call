# AI Personal Call Agent - REST API Specification

The FastAPI backend exposes interactive OpenAPI docs at `http://localhost:8000/docs`.

## Base URL
`http://localhost:8000` or production domain.

## Authentication
Uses standard JWT Bearer tokens:
Header: `Authorization: Bearer <token>`

---

## 1. Authentication Endpoints
- `POST /auth/register`: Create owner account.
- `POST /auth/login`: Authenticate and obtain JWT access token.
- `GET /auth/me`: Retrieve current profile.

## 2. Dashboard Endpoints
- `GET /dashboard`: Overview metrics, AI status, last call, and last urgent SMS alert.
- `POST /dashboard/toggle-agent`: Turn the AI agent ON/OFF.

## 3. Call Lifecycle & Management
- `GET /calls`: Retrieve call history with query filters:
  - `filter_timeframe`: `today`, `yesterday`, `week`
  - `urgency`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
  - `search`: Keyword or caller name search
- `GET /calls/{id}`: Detailed call record with full transcript and summary.
- `POST /calls/{id}/transfer`: Route active call to owner.
- `POST /calls/{id}/mark-urgent`: Manually upgrade urgency to HIGH.
- `DELETE /calls/{id}`: Delete single call record.
- `DELETE /calls`: Purge all call history.
- `POST /calls/simulate`: Run real-time interactive demo simulation.

## 4. VIP Contacts
- `GET /contacts`: List VIP contacts.
- `POST /contacts`: Add new VIP contact.
- `PUT /contacts/{id}`: Update contact.
- `DELETE /contacts/{id}`: Delete contact.

## 5. Urgency Rules
- `GET /urgency-rules`: Get user rules.
- `POST /urgency-rules`: Add custom urgency trigger.
- `PUT /urgency-rules/{id}`: Edit rule.
- `DELETE /urgency-rules/{id}`: Remove rule.

## 6. Knowledge Base
- `GET /knowledge-base`: List approved FAQs and business facts.
- `POST /knowledge-base`: Add knowledge item.
- `DELETE /knowledge-base/{id}`: Remove knowledge item.

## 7. Webhooks
- `POST /webhooks/telephony/incoming`: Carrier incoming call webhook.
- `POST /webhooks/telephony/media`: Streaming speech transcription turn.
- `POST /webhooks/telephony/status`: Call status lifecycle event.

## 8. Alerts
- `POST /alerts/test`: Send manual test SMS to verify SMS gateway and template.

## 9. Analytics
- `GET /analytics`: Detailed aggregate statistics, hourly call distribution, urgency breakdown.
