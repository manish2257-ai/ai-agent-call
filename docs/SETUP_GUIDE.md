# 13-Step Owner Setup Guide

Follow this guide to take your AI Personal Call Agent from installation to live phone screening:

- [x] **Step 1: Account Creation**: Create your account in the AI Call Agent control app or web dashboard.
- [x] **Step 2: Enter Alert Phone Number**: Configure your mobile number (in international format, e.g. `+91XXXXXXXXXX`) where urgent SMS notifications must be delivered.
- [x] **Step 3: Configure AI Voice Provider**: Obtain your OpenAI API Key from `https://platform.openai.com/api-keys`. Add it to your `.env` or app Integration screen.
- [x] **Step 4: Configure Telephony Provider**: Choose Twilio (`twilio.com`), Exotel (`exotel.com`), or Plivo (`plivo.com`). Obtain your Account SID and Auth Token.
- [x] **Step 5: Configure SMS Gateway**: Select your SMS provider and specify the sender ID or virtual number.
- [x] **Step 6: Obtain AI Virtual Number**: Purchase or assign a phone number from your telephony console.
- [x] **Step 7: Configure Webhook URLs**:
  - In your provider's number settings, set the Voice Webhook URL to: `https://<YOUR_BACKEND_DOMAIN>/webhooks/telephony/incoming` (HTTP POST).
  - Set Status Callback to: `https://<YOUR_BACKEND_DOMAIN>/webhooks/telephony/status`.
- [x] **Step 8: Configure AI Greeting**: Customize the introductory greeting. Always keep the AI identification disclaimer.
- [x] **Step 9: Configure Urgency Rules**: Set your minimum SMS notification threshold (`HIGH` or `CRITICAL`) and customize keyword triggers.
- [x] **Step 10: Populate VIP Contacts & Knowledge Base**: Add frequent business clients, family, and office working hours.
- [x] **Step 11: Run Test Call Simulation**: Click "Simulate Call" in the app or dashboard to test speech turns.
- [x] **Step 12: Verify Urgent SMS Alert**: Click "Test Urgent Call" to receive a sample SMS alert on your phone.
- [x] **Step 13: Enable AI Agent & Carrier Forwarding**: Toggle the main AI Call Agent switch to **ON**. If desired, set up conditional call forwarding on your mobile SIM using the carrier codes in `docs/CARRIER_CALL_FORWARDING.md`.
