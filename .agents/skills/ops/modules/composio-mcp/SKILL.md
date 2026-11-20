---
name: composio-mcp
description: >-
  Connect to and execute tools via the Composio MCP Remote Server (https://connect.composio.dev/mcp).
  Provides integration with thousands of app toolkits (Slack, Gmail, GitHub, Jira, Notion, Trello, etc.)
  using standard MCP JSON-RPC 2.0 protocol and consumer API key authentication.
---

# Composio MCP Integration

## Overview
This skill provides complete integration with the Composio Remote Model Context Protocol (MCP) server.
It enables any Antigravity agent to discover, authenticate, and call thousands of third-party SaaS app tools directly via the Composio API gateway.

- **Server Endpoint:** `https://connect.composio.dev/mcp`
- **Consumer API Key:** `${COMPOSIO_API_KEY}` (stored in `~/.gemini/config/.env` mode `0600`)
- **Dashboard & Workspace:** `https://dashboard.composio.dev/fj906880l_workspace/~/connect/clients/antigravity`
- **Credentials File:** `/Users/malcolm/.gemini/config/composio.env`

## Core Composio MCP Tools
1. `COMPOSIO_SEARCH_TOOLS`: Search the Composio tool ecosystem by query or intent.
2. `COMPOSIO_GET_TOOL_SCHEMAS`: Retrieve exact parameter schemas for target tool slugs.
3. `COMPOSIO_MANAGE_CONNECTIONS`: Check or establish app OAuth connections for user toolkits.

## Quick Start
Add the server entry to your project or global `mcp_config.json`:

```json
{
  "mcpServers": {
    "composio": {
      "serverUrl": "https://connect.composio.dev/mcp",
      "headers": {
        "x-consumer-api-key": "${COMPOSIO_API_KEY}"
      }
    }
  }
}
```

Or invoke the helper CLI script:

```bash
uv run python /Users/malcolm/.gemini/config/skills/composio-mcp/scripts/composio_mcp_cli.py list-tools --output /path/to/tools.json
```

## Utility Scripts

The skill includes a standalone Python CLI script for interacting with the server:

### 1. Initialize Session
```bash
python3 /Users/malcolm/.gemini/config/skills/composio-mcp/scripts/composio_mcp_cli.py init --output init.json
```

### 2. List Remote Tools
```bash
python3 /Users/malcolm/.gemini/config/skills/composio-mcp/scripts/composio_mcp_cli.py list-tools --output tools.json
```

### 3. Get Tool Schemas
```bash
python3 /Users/malcolm/.gemini/config/skills/composio-mcp/scripts/composio_mcp_cli.py get-schemas --slugs "GMAIL_SEND_EMAIL,SLACK_SEND_MESSAGE" --output schemas.json
```

## Rate Limiting & SSL
- **Rate Limit:** Composio MCP endpoints permit standard burst usage; default backoff of 1 second applies for bulk queries.
- **SSL Context:** When executing via local Python scripts on macOS, pass an explicit SSL context (`ssl.create_default_context()`) to handle root CA bundles correctly.

## Common Mistakes
1. **Guessing Tool Slugs:** Never invent tool slugs. Always call `COMPOSIO_SEARCH_TOOLS` or `COMPOSIO_GET_TOOL_SCHEMAS` first to verify exact action names.
2. **Missing Session Header:** Remote MCP HTTP requests require passing the `mcp-session-id` header returned from the `initialize` endpoint on subsequent RPC calls.
3. **Unconnected Toolkits:** Ensure target user connections are active via `COMPOSIO_MANAGE_CONNECTIONS` before executing write/send actions.
