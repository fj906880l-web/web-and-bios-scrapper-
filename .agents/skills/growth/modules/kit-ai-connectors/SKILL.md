---
name: kit-ai-connectors
description: Connect, operate, and troubleshoot Kit AI Connectors (https://app.kit.com/mcp) and Kit Developer Docs MCP (https://developers.kit.com/mcp) across Claude, ChatGPT, Cursor, Gemini/Antigravity, and multi-account creator setups.
version: 2.0.0
---

# Kit AI Connectors (`kit` & `kit-docs`) Operational Skill

## 1. Dual MCP Server Architecture (Avoid Label Clashes)
Always configure the two official Kit MCP servers under distinct keys:
- **`kit` (`https://app.kit.com/mcp`)**: Read and act on the creator's Kit account (65+ tools across Subscribers, Broadcasts, Sequences, Tags, Segments, Forms, Landing Pages, Webhooks, Custom Fields).
- **`kit-docs` (`https://developers.kit.com/mcp`)**: Search Kit's developer documentation.

```json
{
  "mcpServers": {
    "kit": {
      "serverUrl": "https://app.kit.com/mcp",
      "url": "https://app.kit.com/mcp"
    },
    "kit-docs": {
      "serverUrl": "https://developers.kit.com/mcp",
      "url": "https://developers.kit.com/mcp"
    }
  }
}
```

## 2. Multi-Account Connector Routing (`?account1`, `?account2`)
When managing multiple newsletters or agency client accounts, append a unique query identifier to `https://app.kit.com/mcp`:
- **Account 1**: Name `Kit (Account1)` → URL `https://app.kit.com/mcp?account1`
- **Account 2**: Name `Kit (Account2)` → URL `https://app.kit.com/mcp?account2`

## 3. 3-Layer Safety & Permission Guardrails
1. **Risk Tags (`read`, `write`, `destructive`)**:
   - `read`: Account stats, subscribers (`~100`/page), tags, sequences, broadcasts, forms, custom fields.
   - `write`: Creating tags, tagging subscribers, creating broadcast drafts, editing landing pages.
   - `destructive`: Sending a Broadcast, deleting an Email Sequence, unsubscribing a subscriber, firing a webhook.
2. **In-App Confirmation Deep Links**:
   - Destructive/open-world actions **never** fire directly from the MCP tool; they return a deep link to `https://app.kit.com/...` requiring the creator to click **Confirm** inside Kit.
3. **Rate Limits & Pagination**:
   - **Rate limit**: `120 requests / minute` per AI client connection.
   - **Pagination**: Subscribers are fetched `~100` per page to protect context windows; each page is a separate tool call.

## 4. Client Setup & Troubleshooting Playbook
- **Why an app appears under `https://app.kit.com/account_settings/kit_mcp` ("Connections")**:
  - Only clients that complete the interactive browser **OAuth Allow** flow against `https://app.kit.com/mcp` register in the Connections list.
- **Fixing Failing Tools in ChatGPT (Stale Tool Cache)**:
  1. Open the Kit app's plugin details page in ChatGPT and **Delete** the app (disconnecting alone leaves the cached tool list).
  2. Revoke access on `https://app.kit.com/account_settings/kit_mcp`.
  3. Recreate the app in ChatGPT (Settings → Developer Mode → `+` Create App → URL `https://app.kit.com/mcp` → OAuth) using a **brand-new name** (e.g., `Kit AI` instead of `Kit`).
