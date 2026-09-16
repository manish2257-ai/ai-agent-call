# Carrier Call Forwarding Guide

## Overview

The **AI Personal Call Agent** operates via cloud telephony. Calls are received by the dedicated AI phone number assigned through your telephony provider (Twilio, Exotel, or Plivo).

To direct incoming calls from your existing cellular mobile SIM to your AI Call Agent, you can configure **Carrier-Level Conditional Call Forwarding**.

> ⚠️ **IMPORTANT NOTICE:** Carrier-level call forwarding availability, behavior, and charges depend entirely on your cellular carrier and subscription plan. Some prepaid or MVNO plans do not support call forwarding. Always verify with your telecom operator.

---

## Forwarding Modes

### 1. Conditional Call Forwarding (Recommended)
Only routes to AI when you cannot answer:
- When your line is **Busy** (on another call)
- When **Unanswered** (after 20 seconds of ringing)
- When **Unreachable** (phone switched off or out of cellular coverage)

This allows you to answer calls personally whenever available, while the AI screens missed, unanswered, or busy calls!

### 2. Unconditional Call Forwarding
Immediately forwards **ALL** incoming cellular calls to the AI number without your phone ringing.

---

## Carrier Dial Codes (USSD Codes)

Replace `<AI_NUMBER>` with your configured AI phone number in E.164 international format (e.g., `+918005550199` or `+18005550199`).

| Carrier | Conditional Forwarding (Busy / Unanswered / Unreachable) | Unconditional Forwarding (All Calls) | Deactivate All Forwarding |
| :--- | :--- | :--- | :--- |
| **Jio (India)** | `*404*<AI_NUMBER>#` (Unanswered)<br>`*402*<AI_NUMBER>#` (Busy)<br>`*406*<AI_NUMBER>#` (Unreachable) | `*401*<AI_NUMBER>#` | `*402` or `*413` |
| **Airtel (India)** | `*61*<AI_NUMBER>#` (Unanswered)<br>`*67*<AI_NUMBER>#` (Busy)<br>`*62*<AI_NUMBER>#` (Unreachable) | `*21*<AI_NUMBER>#` | `##002#` |
| **Vodafone Idea (Vi)** | `*61*<AI_NUMBER>#`<br>`*67*<AI_NUMBER>#`<br>`*62*<AI_NUMBER>#` | `*21*<AI_NUMBER>#` | `##002#` |
| **AT&T (USA)** | `*61*<AI_NUMBER>#`<br>`*67*<AI_NUMBER>#`<br>`*62*<AI_NUMBER>#` | `*21*<AI_NUMBER>#` | `##004#` or `##002#` |
| **T-Mobile (USA)** | `**004*<AI_NUMBER>#` | `**21*<AI_NUMBER>#` | `##004#` |
| **Verizon (USA)** | `*71<AI_NUMBER>` | `*72<AI_NUMBER>` | `*73` |

---

## Configuring via Android Settings

If dial codes are not preferred, configure call forwarding directly within Android OS:
1. Open the **Phone / Dialer** app on your Android device.
2. Tap the **Three Dots Menu** (⋮) at top right → **Settings**.
3. Tap **Calling Accounts** or **Supplementary Services**.
4. Select **Call Forwarding** → **Voice Calls**.
5. Choose **Forward when unanswered**, **Forward when busy**, or **Forward when unreachable**.
6. Enter your AI Phone Number and tap **Turn On**.

---

## Deactivation

To cancel all forwarding and revert back to normal phone behavior, dial:
`##002#`
or go to Android Phone Settings → Call Forwarding → Turn Off.
