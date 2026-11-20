---
name: trading-bot-auditor
description: Audits the RegimeTrader bot for memory bloat, hallucinated tickers, and telemetry health.
---

# Trading Bot Auditor Playbook

This skill instructs you (the Antigravity AI) on how to safely and rapidly audit the RegimeTrader local bot's health, memory, and telemetry. When the user requests an audit, perform the following steps unconditionally.

## 1. Verify `monitoring/state.json` (Memory Bloat Check)
Run a Python script or read the file directly to check:
- `status`: Ensure it is 'RUNNING' or the expected active state.
- `timestamp`: Check if the last heartbeat is fresh.
- `alpaca_history_intraday`: This MUST be bounded to <= 288 records. If it is growing into the thousands, alert the user to a memory leak in the state telemetry.

## 2. Verify `monitoring/trade_ledger.json` (Context Integrity Check)
Run a script to analyze the ledger array:
- Count the total trades.
- Look for **duplicate sequential entries** of the same ticker/profit/outcome. If found, the ledger deduplication logic is failing.
- Look for **hallucinated tickers** (any ticker that violates the `[A-Z]{1,6}` or crypto/forex format).

## 3. Review API Keys and Configuration
Verify that the `.env` and `config/credentials.yaml` are loaded and contain necessary keys (Alpaca, Oanda). Remember that Oanda keys can be sourced safely from `.env` alone.

## 4. Run the Live Status Check
Execute the following script to provide a clean status readout:
```python
import json, os, glob
try:
    with open('monitoring/state.json', 'r') as f:
        state = json.load(f)
        print(f"Status: {state.get('status', 'UNKNOWN')} | Regime: {state.get('regime')} | Equity: ${state.get('equity', 0):,.2f}")
        for p in state.get('positions', []): print(f"  {p['ticker']}: {p['qty']} @ ${p['entry']:.2f}")
except Exception as e: print("State check error:", e)
```

## 5. Report Findings
Present the findings to the user using GitHub alerts for any critical memory leaks or hallucination violations.
