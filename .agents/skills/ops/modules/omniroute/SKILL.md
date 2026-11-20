---
name: omniroute
description: Self-hosted AI gateway, model router, and token-compression proxy (OmniRoute) for multi-provider fallback, rate limit management, and local/remote LLM routing.
---

# OmniRoute AI Gateway & LLM Router Protocol

OmniRoute is an open-source, self-hosted AI gateway running at `http://localhost:20128/v1` that provides a unified OpenAI-compatible proxy interface for multi-provider LLM routing, automatic rate-limit failover, and prompt token compression.

## Key Features & Protocol Standards

1. **Intelligent Model Fallback**:
   - Acts as a local proxy (`http://localhost:20128/v1`) in front of OpenAI, Anthropic, OpenRouter, DeepSeek, Ollama, and local models.
   - Reroutes requests to backup models automatically when rate limits (429) or timeouts occur.

2. **RTK Token Compression Engine**:
   - Strips redundant tool outputs and prompt boilerplate.
   - Reduces token usage by 15% to 95% on long context queries.

3. **Status Check & CLI**:
   - Health Endpoint: `http://localhost:20128/health`
   - Start Server: `omniroute start` or `npx omniroute`

4. **Agent Integration**:
   - Standard OpenAI SDK base URL: `http://localhost:20128/v1`
   - Works with Claude Code, Cursor, Google Antigravity SDK, and background subagents.
