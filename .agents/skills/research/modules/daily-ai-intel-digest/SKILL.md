---
name: daily-ai-intel-digest
description: Autonomous 'MLflow & AI News' Daily Executive Briefing system. Scans all workspace projects for real runtime errors and failures (zero mock data), ingests live research papers (Hugging Face, ArXiv cs.AI), tracks breaking AI industry news (Google AI, DeepMind, Hacker News), synthesizes multi-agent observability benchmarks based on IBM MLflow tracing paradigms, documents self-healing actions, and dispatches automated executive reports to configured email distribution lists via SMTP, sendmail, or outbox spooling.
---

# MLflow & AI News: Daily Executive Intelligence & Workspace Telemetry

An automated, executive-grade intelligence system that generates and delivers a daily AI briefing combining live frontier research, breaking developer news, workspace projects health and error monitoring, and multi-agent observability paradigms.

## Overview

The **MLflow & AI News** briefing system couples real-time daily research and industry breakthroughs with ground-truth health diagnostics across all our active workspace projects, alongside foundational **LLM Observability and Multi-Agent Tracing** paradigms based on IBM Technology's production benchmark:
- **Reference Video**: [What Is MLflow? Tracing AI Agents & LLM Workflows](https://www.youtube.com/watch?v=iZX6d0OdZys)
- **Primary Recipients**:
  - `jeremiahs125@gmail.com`
  - `djfisher3000@gmail.com`
  - `fj906880l@gmail.com`
- **Schedule**: Recurring daily at 08:00 AM local time via `crontab` and macOS `launchd`.

---

## Core Observability Principles (IBM MLflow Paradigm)

Standard APM tools (checking HTTP 200s and response latencies) fail for multi-agent systems. The daily intelligence pipeline reinforces 4 core architectural safeguards:

1. **Combating Silent Tool Failures**:
   - MCP servers and external APIs often return empty or degraded data without throwing HTTP errors.
   - Tracing instruments each tool invocation span with schema validation to prevent agents from hallucinating on hollow payloads.
2. **Eliminating Cascading Latency**:
   - Deep span-level profiling isolates database bottlenecks, tool delays, and LLM inference across multi-agent handoffs.
3. **Preventing Context Overflow**:
   - Spans track token consumption per prompt/completion pair to preempt token exhaustion and cryptic timeouts.
4. **Enforcing Deterministic & LLM-as-a-Judge Quality Gates**:
   - Automated evaluation pipelines (`mlflow.genai.evaluate()`) execute deterministic regex/rule checks alongside budgeted LLM judge assessments (tool correctness, efficiency, relevance, compliance) in CI before agent releases.
5. **Production Backend Hardening**:
   - Use PostgreSQL/MySQL for the tracking store (never SQLite under concurrency).
   - Enable asynchronous trace logging and trace sampling to remove observability from the user-facing latency path.
   - Dual-export traces to OpenTelemetry collectors (Jaeger, Grafana Tempo).

---

## Quick Start

### 1. Test System Health
```bash
python3 /Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter/src/cli.py test
```

### 2. Generate and Send Today's Briefing
```bash
python3 /Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter/src/cli.py send
```

### 3. Terminal Preview
```bash
python3 /Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter/src/cli.py preview
```

### 4. Check or Re-install Automated Daily Schedule
```bash
# Check schedule status
python3 /Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter/src/cli.py schedule --check

# Install crontab and launchd daily jobs (08:00 AM)
python3 /Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter/src/cli.py schedule --install
```

---

## Project Structure & Architecture

```
daily-ai-intel-reporter/
├── config.json                     # System configuration & recipient list
├── .env.example                    # SMTP & schedule environment templates
├── run_daily.sh                    # Scheduled runner shell script
├── reports/                        # Archive of generated reports
│   ├── YYYY-MM-DD_intel_report.html
│   └── YYYY-MM-DD_intel_report.md
├── outbox/                         # Spooled RFC 5322 MIME messages (.eml)
├── logs/
│   ├── delivery_ledger.jsonl       # A-08 Unified Delivery Ledger
│   └── scheduler.log               # Daily execution logs
├── src/
│   ├── fetcher.py                  # Live Hugging Face, ArXiv, Google, HN fetcher
│   ├── synthesizer.py              # Publication-grade Markdown & HTML email engine
│   ├── dispatcher.py               # SMTP TLS, sendmail, spool & ledger transport
│   ├── scheduler.py                # Crontab and macOS launchd manager
│   └── cli.py                      # Unified CLI interface
└── tests/
    └── test_reporter.py            # Automated unit & integration test suite
```

---

## Delivery Transports & A-08 Ledger Compliance

The system implements a resilient multi-transport failover chain:
1. **SMTP (TLS)**: If `SMTP_HOST`, `SMTP_USER`, and `SMTP_PASS` are provided (e.g. Gmail App Password or SendGrid/Postmark).
2. **Local Sendmail**: Uses `/usr/sbin/sendmail` on macOS for direct local MTA dispatch.
3. **Outbox Spooling**: If direct delivery is not available, writes full RFC 5322 MIME messages with HTML and plaintext bodies to `outbox/` for offline inspection or external mail pick-up.
4. **A-08 Unified Delivery Ledger**: Every dispatch attempt logs a permanent JSON record with:
   - `idempotency_key`: SHA-256 hash preventing duplicate sends
   - `recipient`: Target email address
   - `channel`: `EMAIL`
   - `transport`: `SMTP_TLS`, `LOCAL_SENDMAIL`, or `OUTBOX_SPOOL`
   - `status`: `SENT`, `SPOOLED`, or `FAILED`
   - `recorded_at`: UTC ISO timestamp

---

## Adding or Modifying Recipients

To update the recipient email list, edit `/Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter/config.json`:
```json
{
  "recipients": [
    "jeremiahs125@gmail.com",
    "djfisher3000@gmail.com",
    "fj906880l@gmail.com"
  ]
}
```
Or pass ad-hoc recipients via CLI:
```bash
python3 src/cli.py generate --recipients "jeremiahs125@gmail.com,other@example.com" --send
```

---

## Verification & Testing

To run the automated test suite:
```bash
python3 -m unittest /Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter/tests/test_reporter.py
```
Expected output:
```
Ran 7 tests in 0.005s - OK
```
