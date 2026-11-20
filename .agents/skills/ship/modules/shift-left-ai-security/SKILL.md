---
name: shift-left-ai-security
description: Enforce the IBM 5 Principles of Shift-Left Security for AI-generated code, agent workflows, and autonomous trading systems. Governs fail-safe execution, pre-commit secrets scanning, supply-chain dependency auditing, business intent validation (50% capital cap), and agentic boundary enclosure.
trigger: /shift-left-security
---

# Shift-Left AI Security Skill (IBM 5 Principles)

## When to Activate
Activate this skill whenever:
1. Generating, refactoring, or reviewing code produced by AI models or autonomous subagents.
2. Building or deploying network servers, HTTP endpoints, or file-writing tools for agents.
3. Managing project dependencies, package manifests, or environment files.
4. Designing or executing quantitative trading strategies, financial allocation pipelines, or order routing.
5. Verifying system fail-safe behavior, state persistence, or error recovery loops.

---

## The 5 Core Invariants

### 1. Fail-Safe Outcome Verification (Principle 1)
- Never fail open. If a dependency, API call, account equity check, or auth token fails, abort execution cleanly.
- State file writes must be atomic: write to a temporary file (`.tmp.{pid}`) and use `os.replace` to prevent corrupted JSON files.
- Validate and sanitize all incoming payloads against malformed data.

### 2. Shift-Left Secrets & Ingestion Defense (Principle 2)
- All repositories must maintain strict `.gitignore` rules covering `.env*`, `*.pem`, `*.key`, `*secret*`, `*credentials*`, and `token.json`.
- Run automated secret scanning on pre-commit and pre-delivery. Zero plain-text credentials allowed in code.

### 3. Supply-Chain & Dependency Audit (Principle 3)
- Scrutinize external packages before installation. Check for package reputation, active maintenance, and known CVEs.
- Reject deprecated packages (e.g., legacy `alpaca-trade-api`). Use modern, maintained SDKs (`alpaca-py`).
- Keep core networking packages (`urllib3 >= 2.0.0`) patched against high-severity CVEs.

### 4. Intent & Assumption Alignment (Principle 4)
- Technical elegance does not equal policy compliance. Code must strictly enforce business rules.
- Quantitative Invariants:
  - **50% Capital Cap**: Cumulative risk/margin must never exceed 50% of account equity.
  - **No Fake Data**: Use only verified historical or live market telemetry.
  - **Self-Healing Re-Auditing**: Self-healed or LLM-modified signals must re-pass pre-trade risk audits before submission.

### 5. Continuous Agentic Guardrails (Principle 5)
- **Blast Radius Enclosure**: Any endpoint or tool allowing file modifications must validate paths with `is_safe_repo_path()`. Escaping repository root, modifying hidden files, or altering sensitive configurations is blocked.
- **Network Isolation**: Developer servers must bind to `127.0.0.1` by default with restricted CORS, avoiding unauthenticated access on `0.0.0.0`.
- **Structured Audit Trails**: Subagent actions must log timestamps, actor identities, parameters, and validation outcomes.

---

## Verification Command
```bash
python3 scripts/shift_left_security_guard.py --dir . --enforce
```
Score must be $\ge 80/100$ (target 100/100) to pass delivery gating.
