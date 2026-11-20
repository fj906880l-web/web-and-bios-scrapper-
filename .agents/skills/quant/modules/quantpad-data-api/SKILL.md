---
name: quantpad-data-api
description: QuantPad Market Data API, Streamable MCP Server, and Python SDK (quantpad-data) Cheatsheet for Bulk History, Streaming Ticks, and 10-Level L2 Order-Book Depth (mbp-10).
---

# QuantPad Market Data API & Python SDK Playbook

This skill defines the data interfaces, MCP discovery workflow, direct REST API endpoints, and `quantpad-data` Python SDK usage for QuantPad market data.

---

## 1. MCP Streamable Server (Discovery & Preview)

* **Endpoint**: `https://quantpad.ai/api/mcp`
* **Protocol**: Stateless Streamable HTTP, Clerk OAuth bearer token.
* **Purpose**: Read-only discovery and small previews (max 500 bars / 31-day window).
* **Recommended Tool Order**:
  1. `search_symbols` / `resolve_symbology` — find canonical QuantPad symbol from ticker or alias.
  2. `get_coverage` — check schemas & date ranges for that symbol.
  3. `describe_schema` — inspect exact fields returned by a schema.
  4. `preview_bars` — fetch small OHLCV sample for checking shape/data quality (do NOT loop for bulk datasets).
  5. `get_usage` — inspect recent request counts & quota.
  6. `get_api_usage_guide` — retrieve routing/install guide.

> **CRITICAL RULE**: MCP is intentionally read-only and preview-sized. Never infer that QuantPad lacks a dataset (like ticks or L2 order-book depth) merely because there is no MCP payload tool for it.

---

## 2. REST API & Python SDK (Bulk Data & L2 Depth)

* **Base URL**: `https://api.quantpad.ai`
* **Header**: `X-API-Key: <QUANTPAD_API_KEY>` (set in `.env`).
* **Endpoints**:
  * `GET /v1/bars` — OHLCV bulk data without per-request row cap (`format=arrow|csv`).
  * `GET /v1/ticks` — streaming ticks & 10-level L2 order-book depth (`schema=mbp-10`). Also supports `trades`, `mbp-1`, `cmbp-1`, `tcbbo`, `cbbo-1s`, `cbbo-1m`.
  * `GET /v1/universe` — symbol search.
  * `GET /v1/coverage` — per-schema coverage for a symbol.
  * `POST /v1/symbology/resolve` — resolve tickers/aliases to canonical symbols.

### Python SDK Usage (`quantpad-data`)

```bash
# Installation via uv or pip
uv add quantpad-data
# OR: python -m pip install quantpad-data
```

```python
import os
import quantpad_data as qpd

# Set API key from local environment
api_key = os.getenv("QUANTPAD_API_KEY")

# 1. Bulk OHLCV bars
bars = qpd.get_bars("AAPL", "1m", start_ms, end_ms)

# 2. Check coverage
coverage = qpd.get_coverage("AAPL")

# 3. 10-Level L2 Market-by-Price Order-Book Depth (mbp-10)
# Streams DataFrame chunks; project columns to optimize wide requests.
for chunk in qpd.get_mbp10(
    "ES.FUT",
    start_ms,
    end_ms,
    columns=["t", "bid_px_00", "ask_px_00", "bid_sz_00", "ask_sz_00"]
):
    print(chunk.head())
```

---

## 3. Workflow Routing Decision Tree

* **Quick Symbol / Coverage / Schema Sanity Check**: Use MCP tools (`search_symbols`, `get_coverage`).
* **Bulk History / Backtests / Ticks / L2 Depth (`mbp-10`)**: Use `quantpad-data` Python SDK or direct REST API (`https://api.quantpad.ai`).
* **Rate Limits & Failovers**: The SDK retries transient failures and rate limits automatically using `Retry-After` response headers.
