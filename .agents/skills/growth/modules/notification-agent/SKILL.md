---
name: notification-agent
description: Monitors Market Haven campaign telemetry, synthesizes milestone updates with Gemini/Google Antigravity SDK, and dispatches email and SSE notifications.
---

# Notification Agent Skill

## Capabilities
1. **Telemetry Inspection**: Reads GoFundMe drive totals, Stripe transactions, and Gumroad sales from local SQLite database and `data/income_telemetry.json`.
2. **AI Digest Generation**: Synthesizes updates into motivating email newsletters and donor impact notifications using `google.antigravity`.
3. **Notification Dispatch**: Sends outbound emails via Resend API or logs events to internal API webhooks.
