---
name: daily-security-workflow
description: >-
  Autonomous daily security workflow combining the IBM 5 Shift-Left Security Principles
  with the LUMINA Zero-Trust Operational Protocol (SEC-PROTO-2026-05). Runs automated
  SAST checks, dependency audits, broker order authentication, egress boundary gating,
  and records tamper-evident SHA-256 hash-chained consequential audit ledgers.
---

# Daily Security Workflow (IBM 5 & LUMINA Zero-Trust)

## Overview
An autonomous, recurring daily security audit and verification protocol. Unifies IBM's 5 Shift-Left Security Principles (Fail-Safe Outcomes, Shift-Left Ingestion/SAST, Supply-Chain Scrutiny, Intent/Capital Alignment, Continuous Agentic Boundaries) with the LUMINA Zero-Trust Operational Protocol (`SEC-PROTO-2026-05`). It executes a 6-stage verification gate, generates a security health scorecard, and signs every audit into a tamper-evident, SHA-256 hash-chained consequential audit ledger (`monitoring/consequential_audit_ledger.jsonl`).

## Dependencies
- `shift-left-ai-security`: Core principles for AI-generated code, prompt injection defense, and 50% capital cap enforcement.
- `agent-harness-v2`: Harness runtime governing continuous confidence, memory hub, and Supervisor CEO gating (<80 security block).
- `composio-mcp`: Authenticated GitHub MCP tools for verifying remote repository status.

## Quick Start
Run the daily security audit directly from the workspace:

```bash
# Run full audit and write report to file
python scripts/daily_security_workflow.py scan --output monitoring/daily_security_report.json

# Verify cryptographic continuity of the consequential audit ledger
python scripts/daily_security_workflow.py audit-ledger

# Verify egress boundary permissions for alert channels
python scripts/daily_security_workflow.py verify-egress --classification CONFIDENTIAL --destination discord_private_webhook

# Display formatted daily security health scorecard
python scripts/daily_security_workflow.py report
```

## Utility Scripts (CLI-Based)

The primary runner is `scripts/daily_security_workflow.py`. It follows the multi-command CLI pattern with explicit subcommands and required `--output` options for file writing:

### 1. `scan`
Executes all 6 security checks:
- **P1: Fail-Safe Verification**: Confirms account equity is verified before trading and file operations use atomic `os.replace`.
- **P2: Shift-Left SAST**: Scans files for exposed API keys/tokens and verifies root `.gitignore` excludes secrets (`.env*`, `*.key`, `*.pem`, `*secret*`).
- **P3: Supply Chain Scrutiny**: Validates package requirements, checking for deprecated/unpinned dependencies.
- **P4: Intent & Capital Alignment**: Confirms authentic broker order ID verification (`is_valid_broker_order_id`) to prevent phantom live alerts and enforces capital cap <= 50%.
- **P5: Agentic Boundaries**: Ensures servers bind to `127.0.0.1` (never `0.0.0.0`) and employ canonical path traversal validation (`is_safe_repo_path`).
- **P6: LUMINA Egress Controls**: Enforces `SEC-PROTO-2026-05` data classification rules (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`) across all egress destinations.

```bash
python scripts/daily_security_workflow.py scan --output monitoring/daily_security_report.json
```

### 2. `audit-ledger`
Verifies the cryptographic continuity and SHA-256 hash chaining of all historical audit records:

```bash
python scripts/daily_security_workflow.py audit-ledger
```

### 3. `verify-egress`
Tests if a given data classification is authorized to egress to a specific channel:

```bash
python scripts/daily_security_workflow.py verify-egress --classification RESTRICTED --destination local
python scripts/daily_security_workflow.py verify-egress --classification CONFIDENTIAL --destination onedrive  # Rejects (exit 1)
```

### 4. `report`
Outputs an executive terminal summary of the system security posture and check results.

## Workflow

### 1. Daily Autonomous Schedule Slot (07:30 AM ET)
The daily security scan executes automatically at 07:30 AM ET across all operational environments:
- Wired into `core/social_scheduler_service.py` (`Slot 0: 07:30 AM ET daily`).
- Integrated into `scripts/start_quiet_services.sh` upon background service launch.
- Triggered in CI/CD via `.github/workflows/daily_security_audit.yml` daily at 06:00 UTC.

### 2. Multi-Agent Orchestration & Role Boundaries
When multi-agent tasks execute:
1. **Orchestrator-Worker Pattern**: The Security Scanner subagent audits diffs and code artifacts in isolation before any code reaches staging or production.
2. **Role Isolation**: Only agents signed with `role="ADMIN"` can modify the security rules or resolve approval gates.
3. **Circuit Breakers**: If any security scan scores < 80, the deployment gate freezes execution immediately (Fail-Closed).
4. **Context Compaction**: All scanner findings are written to structured JSON files (`monitoring/daily_security_report.json`) to prevent context window saturation.

## Rate Limiting
- External notification webhooks (Discord, Slack, Email) are limited to a maximum of **1 dispatch per second** with exponential backoff and jitter.
- Local hash calculations and file system scans operate locally with zero network I/O and zero rate limits.

## Common Mistakes
1. **Binding to `0.0.0.0`**: Exposing local dashboards or coworkers to the local area network. Always enforce `127.0.0.1` binding.
2. **Mock/Synthetic Order IDs in Live Alerts**: Emitting trade signals or webhooks with dummy order IDs ("mock", "sim", "submitted"). Always filter via `is_valid_broker_order_id()`.
3. **Broken Hash Chains**: Manually editing `monitoring/consequential_audit_ledger.jsonl`. This will trigger immediate tamper detection in `audit-ledger`.
4. **Failing Open on Missing Balances**: Defaulting account equity to a hardcoded non-zero amount when the broker API returns None. Always fail-closed and block order submission.
