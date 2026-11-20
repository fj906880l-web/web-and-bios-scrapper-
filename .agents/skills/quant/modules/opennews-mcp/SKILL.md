---
name: opennews-mcp
description: Open Financial News MCP Server and Real-time News Ingestion Protocol (6551team OpenNews-MCP). Use when fetching live macroeconomic news, sentiment streams, corporate earnings announcements, and market-moving headlines via standard MCP tool calls.
---

# OpenNews-MCP Server & Real-Time Financial Ingestion Protocol

OpenNews-MCP provides real-time financial news search, sentiment score streaming, and headline filtering via Model Context Protocol (MCP) tool integration.

## Core Features
1. **Live Headline Ingestion (`fetch_latest_news`)**: Scours major financial outlets (Bloomberg, Reuters, SEC EDGAR, Financial Times) for breaking news payloads.
2. **Sentiment Pre-Scoring**: Evaluates headline sentiment using ProsusAI/FinBERT before sending context to LLM agents.
3. **Structured Article Extraction**: Returns clean JSON schemas containing `ticker`, `headline`, `body`, `source_url`, and `published_timestamp`.

## Standard MCP Tools Exposed

```json
{
  "tools": [
    {
      "name": "search_financial_news",
      "description": "Searches real-time financial headlines for a specific ticker or keyword.",
      "parameters": {"ticker": "string", "limit": "integer"}
    },
    {
      "name": "get_macro_economic_stream",
      "description": "Fetches breaking Federal Reserve, CPI, employment, and yield curve news."
    }
  ]
}
```

## Python Integration Example

```python
import os
import requests

def query_opennews_mcp(ticker: str, limit: int = 5):
    api_url = os.getenv("OPENNEWS_MCP_URL", "http://localhost:8002/mcp/news")
    headers = {"X-API-Key": os.getenv("OPENNEWS_API_KEY", "")}
    try:
        res = requests.post(api_url, json={"ticker": ticker, "limit": limit}, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get("articles", [])
    except Exception as e:
        return []
    return []
```

## System Architecture Integration
- **Hybrid Rule Engine Note**: Included in Hybrid Hardcoded System Architecture (Fast-Path Deterministic Rules + LLM Subagent).
- **Zero Fake Data Enforcement**: Unreachable news feeds fail cleanly with `status: "offline"` and return empty lists without synthesizing mock headlines.
