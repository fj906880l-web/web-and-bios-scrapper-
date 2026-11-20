---
name: billing
description: >-
  Use when designing, integrating, reconciling, auditing, or upgrading Stripe Checkout/Payments, Stripe Connect (charge patterns, onboarding/KYC verification), Stripe Apps, Stripe Projects, Stripe Pay/Directory, or Metronome usage-based billing in one verified pass.
version: "2.0.0"
---

# /billing — Stripe Payments, Connect KYC, Apps, Projects & Metronome Usage Billing

Single-pass Category Master Skill. Invoking `/billing` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/billing`
- **Compatible Aliases:** `/billing`, `/stripe`, `/payments`, `/connect`, `/metronome`
- **Absorbed Legacy Skills (10):** `/stripe-best-practices`, `/stripe-docs`, `/stripe-apps`, `/stripe-directory`, `/stripe-pay`, `/stripe-projects`, `/upgrade-stripe`, `/connect-recommend`, `/connect-required-verification-information`, `/metronome`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `mode` | `enum(design|implement|connect|metronome|upgrade|reconcile|pay)` | `design` | Billing workflow mode |
| `livemode` | `bool` | `false` | Must stay false (sandbox/test mode) unless explicit AUTH: is supplied |
| `target` | `path` | `.` | Project workspace to inspect or update |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **Test/Sandbox First & `livemode:** false`: Default strictly to isolated Stripe sandboxes/test mode; any live money movement (`stripe-pay`, refunds, production key changes) requires explicit `AUTH:`.
- **Consulting Delivery Gate & Financial Circuit Breaker:** Require both signed agreement and confirmed payment before releasing final client deliverables; enforce `$100` or `15%` project reserve floor (preserve state without deletion on liquidity events).
- **Official Docs Grounding (`stripe-docs`):** Always verify API versions, Connect verification rules, and webhook signatures against official Stripe/Metronome docs rather than memory.
- **Idempotency & Webhook Integrity:** Enforce deterministic idempotency keys on all mutations/Metronome event ingestions, verify webhook HMAC signatures, and reconcile Monthly (`$10/mo`, `price_convergence_monthly_10`) / Yearly (`$80/yr`, `price_convergence_yearly_80`) tiers accurately.
- **Secret Isolation:** Never write `sk_live_`, `sk_test_`, or `rk_` keys into code or git; load strictly from `.env` (`0600`).

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Sandbox Isolation, Financial Guardrails & Mode Selection
- **Depends On:** None (Entry Gate)
- **Inputs:** target billing goal, `.env`/config `livemode` flag
- **Actions:** Confirm sandbox/test environment separation (`stripe-best-practices`), verify Delivery Gate & Financial Circuit Breaker rules, and route to Payments, Connect, Apps, Projects, Pay/Directory, Upgrade, or Metronome.
- **Gate Check:** Environment confirmed `livemode: false` (or explicit `AUTH:` recorded) with zero exposed keys.
- **Artifacts:** `billing_env_preflight`

### S2: Architecture, Connect Pattern & KYC/Rate-Card Design
- **Depends On:** `S1`
- **Inputs:** `connect-recommend` references, Metronome contract specs
- **Actions:** Select Checkout Sessions vs Payment Element, Connect charge pattern (`direct`/`destination`/`separate`), exact country/capability KYC requirements (`connect-required-verification-information`), or Metronome billable metrics + rate cards + idempotent ingestion schema; resolve counterparties via `stripe-directory`.
- **Gate Check:** Architecture matches Stripe/Metronome current patterns (no deprecated Charges/Sources APIs).
- **Artifacts:** `billing_architecture_spec`

### S3: Docs-Grounded Implementation, Upgrade & Security
- **Depends On:** `S2`
- **Inputs:** `stripe-docs` responses, SDK lockfiles, `stripe-apps` manifest
- **Actions:** Implement or upgrade SDKs/API versions/webhooks (`upgrade-stripe`), build Stripe Apps UI/script extensions (`stripe-apps`) or provision infra via `stripe-projects`, enforcing webhook signature verification and strict error handling.
- **Gate Check:** Webhook verification, idempotency keys, and pinned API version verified in code.
- **Artifacts:** `billing_code_changes`

### S4: Ledger & Stripe <-> Kit Subscription Reconciliation
- **Depends On:** `S3`
- **Inputs:** Stripe product catalog, Kit tags, invoice ledger
- **Actions:** Verify Monthly (`$10/mo`) and Yearly (`$80/yr`) tier mappings, Kit tag synchronization, and Base44/local invoice ledger consistency with zero mock transactions.
- **Gate Check:** Tier unit amounts, intervals, and subscriber tags match 1:1.
- **Artifacts:** `reconciliation_audit`

### S5: Strict `AUTH:` Gate for Live Funds & Payouts
- **Depends On:** `S4`
- **Inputs:** payment/transfer intent (`stripe-pay`), user words
- **Actions:** Verify recipient Stripe Profile/network ID via Directory and halt before any live fund transfer or production deploy unless `AUTH: user said "..."` is present.
- **Gate Check:** Zero unauthorized live transfers or production billing mutations.
- **Artifacts:** `billing_auth_gate`

### S6: Test-Mode E2E Verification & Outcome Report
- **Depends On:** `S5`
- **Inputs:** billing test suites
- **Actions:** Execute project billing tests (e.g., Stripe/Kit sync tests, checkout/webhook smoke tests) and report verified pass counts and any pending live authorizations.
- **Gate Check:** All test-mode verification suites observed green.
- **Artifacts:** `billing_verification_report`

## 4. Fallback & Escalation Rules

- **Missing `stripe-docs` MCP / Network Failure:** Inspect installed `stripe` SDK types/lockfiles directly and flag doc lookup gaps explicitly.
- **Missing KYC / Connect Verification Fields:** Enumerate exact missing requirements from `connect-required-verification-information` before generating onboarding links.
- **Unauthorized Live Action:** Block `stripe-pay` / live mode execution and emit `PENDING: <action> - awaiting your authorization`.

## 5. Single-Pass Completion Criteria

- [ ] Correct Stripe/Connect/Metronome pattern validated against current docs/SDK.
- [ ] Webhook verification, idempotency, and sandbox isolation confirmed.
- [ ] Billing/reconciliation tests observed passing with zero plaintext keys.
- [ ] Zero live charges or transfers executed without explicit `AUTH:`.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `stripe-best-practices` | Global | [`SKILL.md`](./modules/stripe-best-practices/SKILL.md) | Absorbed into `/billing` |
| `stripe-docs` | Global | [`SKILL.md`](./modules/stripe-docs/SKILL.md) | Absorbed into `/billing` |
| `stripe-apps` | Global | [`SKILL.md`](./modules/stripe-apps/SKILL.md) | Absorbed into `/billing` |
| `stripe-directory` | Global | [`SKILL.md`](./modules/stripe-directory/SKILL.md) | Absorbed into `/billing` |
| `stripe-pay` | Global | [`SKILL.md`](./modules/stripe-pay/SKILL.md) | Absorbed into `/billing` |
| `stripe-projects` | Global | [`SKILL.md`](./modules/stripe-projects/SKILL.md) | Absorbed into `/billing` |
| `upgrade-stripe` | Global | [`SKILL.md`](./modules/upgrade-stripe/SKILL.md) | Absorbed into `/billing` |
| `connect-recommend` | Global | [`SKILL.md`](./modules/connect-recommend/SKILL.md) | Absorbed into `/billing` |
| `connect-required-verification-information` | Global | [`SKILL.md`](./modules/connect-required-verification-information/SKILL.md) | Absorbed into `/billing` |
| `metronome` | Global | [`SKILL.md`](./modules/metronome/SKILL.md) | Absorbed into `/billing` |

- **Companion Plugins:** None
- **Companion MCP Servers:** `stripe-docs`, `kit-bridge`
