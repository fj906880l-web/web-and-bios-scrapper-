---
name: mcp-fd-and-bracket-audit
description: >-
  Audits trading-bot daemon file descriptor/pipe leaks, Robinhood MCP subprocess
  counts, live vs. paper lock isolation, and open-order stop-loss bracket coverage.
  Use when diagnosing `filedescriptor out of range in select()`, missing broker
  exits, stalled portfolios, or verifying daemon health after code syncs.
---

# MCP FD-Leak & Bracket Coverage Audit Skill

## Steps
1. **Verify Runtime Locks (Read-Only First):**
   - Check `system_lock.lock`, `monitoring/paper_system_lock.lock`, and `monitoring/live_system_lock.lock` before any test or daemon restart.
2. **Audit Daemon File Descriptors & MCP Child Processes:**
   - Locate PID via `launchctl list | awk '/com\.tradingbot\.regime-trader/ {print $1}'`.
   - Inspect pipe/FD counts: `lsof -p <PID> | awk '{print $5}' | sort | uniq -c | sort -rn`.
   - Confirm `PIPE` FDs `< 20` and `robinhood-for-agents` child processes `<= 1` (`ps -ef | grep robinhood-for-agents`).
3. **Audit Live Bracket & Exit Coverage:**
   - Verify `monitoring/orders.json` (`robinhood_live_brackets` and `active_brackets`) against `RobinhoodBracketMonitor` status and open Alpaca sell orders (`stop` vs. `limit`-only coverage).
   - Verify no crypto fractional rounding exceeds available quantity (`math.floor(qty * 10000) / 10000`).
4. **Verify Isolation & Security Gate:**
   - Run targeted tests inside `/Users/malcolm/Downloads/trading-bot-` (`tests/conftest.py` preserves any pre-existing root `system_lock.lock`), then sync and run `/Users/malcolm/trading-bot-/.venv/bin/python scripts/daily_security_workflow.py scan` (`Score 100/100 [PASS]`).
