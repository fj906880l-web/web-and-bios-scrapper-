---
name: static-code-analysis
description: >-
  Static code analysis and review loop for AI coding agents based on IBM Bob and Shift-Left SAST principles. Audits codebases and git diffs across 4 dimensions: Security (Data Flow), Reliability (Execution Path), Performance (N+1 Patterns), and Maintainability (Overengineering), generating grounded "Fix with Agent" prompts and enforcing delivery gating.
version: 2.0.0
triggers:
  - /review
  - /static-analysis
  - /code-analysis
---

# Static Code Analysis & Grounded Review Loop

## Overview

Static code analysis examines source code without executing it. While unit and integration tests verify what happens along the paths you explicitly execute, static code analysis helps AI coding agents reason about all the execution paths that were not tested.

This skill implements the **AI Coding Agent + Static Code Analysis Review Loop** demonstrated in the IBM engineering tutorial (by Sam Anthony), combining shift-left static analysis with autonomous agent remediation.

### The Grounded Review Loop
```
   ┌────────────────────────────────────────────────────────┐
   │ 1. Scan Commit / PR Diff (`security_scanner.py --diff`)│
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 2. Surface Grounded Findings (File, Line, Severity)   │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 3. Fix with Agent (Targeted Grounded AI Prompt)        │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │ 4. Human / Supervisor Approval & Re-Verification      │
   └────────────────────────────────────────────────────────┘
```

---

## The 4 Core Static Analysis Dimensions

### 1. Security Vulnerabilities (Data Flow Analysis)
Traces data from the entry point (API route, request body, query parameter) all the way into system sinks.
- **SQL Injection (`SEC-SQL-001`)**: Unparameterized SQL statements formatted with f-strings or string concatenation.
- **Exposed Credentials (`SEC-KEY-001`)**: Plaintext API keys, GitHub tokens, private keys in source code.
- **Sensitive Data Exposure (`SEC-EXP-001`)**: Endpoints returning raw database records or models that expose confidential attributes (passwords, hashes, tokens, internal IDs) without restrictive response serializers.
- **Command Injection (`SEC-CMD-001`)**: Unsanitized user inputs reaching `os.system` or `subprocess(shell=True)`.

### 2. Reliability & Resilience (Execution Path Analysis)
Evaluates execution paths for unhandled failures, crashes, and state corruption.
- **Unhandled Mutation Exceptions (`REL-EXC-001`)**: Database writes (`INSERT`, `UPDATE`, `DELETE`) or external API calls without enclosing `try...except` blocks and transaction rollbacks (`db.rollback()`), leading to 500 server crashes.
- **Missing Duplicate Safeguards (`REL-DUP-001`)**: Record creation endpoints lacking idempotency checks or duplicate conflict resolution.
- **Resource Leaks**: Database connections, cursors, or file descriptors opened without context managers (`with`) or explicit closure.

### 3. Performance & Scalability (Pattern Analysis)
Identifies architectural patterns that introduce scalability bottlenecks before they reach production.
- **N+1 Query Pattern (`PERF-N1-001`)**: Executing database queries inside iterative loops (`for` / `while`). For 100 entities, this generates 101 database queries ($O(N)$ linear degradation).
  - *Fix*: Batch-fetch records using SQL `JOIN` or `WHERE id IN (...)` prior to the loop.
- **Unbounded Queries (`PERF-UNBOUND-001`)**: Executing `SELECT *` without `LIMIT` or pagination in API routes, risking memory exhaustion when tables scale.

### 4. Maintainability & Code Quality (Complexity & Anti-Pattern Analysis)
Detects overengineering, unnecessary complexity, and reinventing existing standard library features.
- **Overengineered Validation (`MAINT-OVERENG-001`)**: Hand-rolled custom validation functions (e.g. 50-line email regex validator) when standard primitives exist (e.g. Pydantic `EmailStr` or standard validators).
- **Reinventing the Wheel**: Custom date formatters, UUID generators, or home-brewed JSON encoders instead of Python stdlib.

---

## Dependencies

- `agent-harness-v2`: Governs the 8-step lifecycle, confidence scoring, and delivery block gating (<80).
- `shift-left-ai-security`: Enforces the IBM 5 Shift-Left Security Principles (50% capital cap, zero leak, fail-safe).
- `harness-engineering`: Harness verification scripts and CodeGraph indexing.

---

## Quick Start

### 1. Review Modified Code in Git Diff (PR Review Loop)
```bash
python3 /Users/malcolm/.gemini/config/scripts/security_scanner.py --diff --review
```

### 2. Review a Specific File
```bash
python3 /Users/malcolm/.gemini/config/scripts/security_scanner.py --file app/routes/events.py --review
```

### 3. Audit Entire Directory with Delivery Gating
```bash
python3 /Users/malcolm/.gemini/config/scripts/security_scanner.py --dir . --enforce --threshold 80
```

---

## Configuring Exclusions

Not all findings are equally urgent; you can mark known acceptable trade-offs:

### Inline Comment Ignore
```python
# Ignore all rules on this line:
attendees = db.execute("SELECT * FROM attendees WHERE event_id = ?", (event["id"],)).fetchall()  # scanner:ignore

# Ignore a specific rule ID:
cursor.execute(f"SELECT * FROM {trusted_table}")  # scanner:ignore SEC-SQL-001
```

### Project-Level `.scannerignore`
Create a `.scannerignore` file in the project root:
```
# Ignore test files and legacy scripts
tests/*
migrations/*
legacy/report.py:PERF-N1-001
```

---

## Common Mistakes

1. **Relying Only on Green Tests**: Passing tests only prove code works under the specific inputs tested. They do not catch N+1 queries, unhandled mutation exceptions, or sensitive data leaks.
2. **Asking the Agent to "Guess What's Wrong"**: Don't prompt the agent with vague requests like "make this better." Pass the exact grounded finding from the scanner report (file, line number, issue description, matched code).
3. **Manual Validation Instead of Automated Gates**: Always run `--enforce` in CI/CD or pre-commit hooks to prevent merging vulnerable code.
