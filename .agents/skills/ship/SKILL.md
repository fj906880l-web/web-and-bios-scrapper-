---
name: ship
description: >-
  Use when hardening code, auditing security/UI quality, running adversarial verification, or sealing release artifacts end-to-end. Synthesizes TruffleHog v3+, Cloudflare 6-phase audit, IBM 5 Shift-Left principles, Vanta scaling guardrails, container blast-radius isolation, SAST (>=80), Fable Judge, Try-Harder PoC validation, and tactile anti-slop UI checks in one pass.
version: "2.0.0"
---

# /ship — Verified Security Hardening, Adversarial QA & Release Sealing

Single-pass Category Master Skill. Invoking `/ship` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/ship`
- **Compatible Aliases:** `/ship`, `/release`, `/audit`, `/verify-release`
- **Absorbed Legacy Skills (8):** `/verified-release-and-ui-craft`, `/shift-left-ai-security`, `/daily-security-workflow`, `/vanta-security-scaling-guardrails`, `/developer-isolation-blast-radius`, `/static-code-analysis`, `/fable-judge`, `/try-harder-poc-validation`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `target` | `path` | `.` | Repository, directory, or build dir to audit/seal |
| `mode` | `enum(full|diff|ui|release|daily)` | `full` | Execution focus while preserving mandatory gates |
| `dist_dir` | `path` | `./dist` | Release artifact directory for SHA-256 sealing |
| `threshold` | `int` | `80` | Minimum SAST security score required to unblock delivery |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **Delivery Block (< 80):** Never approve or ship any artifact scoring below 80/100 on `security_scanner.py` or failing `scan_mind_virus.py`.
- **Secret Isolation & TruffleHog:** Enforce `0600` permissions on `~/.gemini/config/.env`; zero plaintext keys, private keys, or credentials in code, logs, or git history.
- **Cryptographic Separation:** Confidentiality requires `AES-256-GCM` or `ChaCha20-Poly1305` (unique nonce); integrity requires `SHA-256`/`SHA-512`/`BLAKE2b` (ban MD5/SHA-1/ECB); passwords require salted `Argon2id`/`bcrypt`.
- **Client-Side Hardening Realism (BLA):** Treat obfuscation/entanglement strictly as cost-amplification; never place proprietary secrets or security boundaries in client bundles.
- **Blast-Radius & Network Containment (`SEC-PROTO-2026-04/05`):** Bind local services to `127.0.0.1` (never `0.0.0.0`), ban `$HOME`/`/` mounts and privileged-mode containers (enforce `--cap-drop=ALL` + `no-new-privileges`), and enforce `PUBLIC/INTERNAL/CONFIDENTIAL/RESTRICTED` egress gates.
- **Zero Weakened Tests & Adversarial Independence:** Never relax assertions or fabricate mock passes; validate bugs with `TWINS:` whole-repo searches and live PoC reproduction.

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Pre-Flight, Secret Hygiene & DLP Intake
- **Depends On:** None (Entry Gate)
- **Inputs:** target path, git diff, `.env` permissions
- **Actions:** Verify `trufflehog`/`git`/`python3` via `verified_release_craft.py check-tools`, confirm `~/.gemini/config/.env` is `0600`, run secret/history scan (`trufflehog ... --results=verified --fail` or static secret scan), and sanitize any untrusted prompts via `security_scaling_guardrails.py sanitize-prompt`.
- **Gate Check:** Zero verified live secrets exposed; `.env` mode == `600`.
- **Artifacts:** `pre_flight_secrets_report`

### S2: Blast-Radius, Vanta Guardrails & Crypto Separation
- **Depends On:** `S1`
- **Inputs:** source dir, container/MCP configs, payload schemas
- **Actions:** Run `verified_release_craft.py check-crypto-patterns`, enforce `vanta` query cost/schema/LRU/air-gap checks (`security_scaling_guardrails.py`), verify devcontainer least-privilege isolation, and confirm `127.0.0.1` binding + `is_safe_repo_path` containment.
- **Gate Check:** Zero prohibited crypto primitives (`MD5`, `SHA-1`, `ECB`, raw SHA password hashes); zero container host-root escapes.
- **Artifacts:** `guardrails_crypto_audit.json`

### S3: Static Analysis (SAST), Mind-Virus & Audit Ledger
- **Depends On:** `S2`
- **Inputs:** workspace files or `--diff`
- **Actions:** Execute `python3 /Users/malcolm/.gemini/config/scripts/security_scanner.py --dir <target> --enforce --threshold 80` and `python3 /Users/malcolm/.gemini/config/scripts/scan_mind_virus.py --dir <target>`; verify daily security ledger chain if present.
- **Gate Check:** SAST score >= 80/100 and Mind-Virus verdict == `CLEAN`.
- **Artifacts:** `sast_mind_virus_gate`

### S4: Cloudflare 6-Phase Hunt, Fable Judge & Try-Harder PoC
- **Depends On:** `S3`
- **Inputs:** recon architecture, coverage ledger, claimed fixes/diffs
- **Actions:** Execute reconnaissance & coverage-led audit across trust boundaries, run `fable-judge` adversarial verification (re-run claimed checks, hunt the 6 frauds, run `TWINS:` search across whole repo), and execute `try-harder-poc-validation` end-to-end PoC reproduction.
- **Gate Check:** Every finding backed by observed execution/counter-evidence; zero unverified completeness claims.
- **Artifacts:** `adversarial_judge_verdict`

### S5: Tactile Anti-Slop UI, Accessibility & Runtime QA
- **Depends On:** `S3`
- **Inputs:** frontend `src/` or live localhost UI
- **Actions:** Run `verified_release_craft.py audit-ui-slop --dir <src>`, enforce Oil UI 3-direction craft & spring physics without generic AI chrome, and run `chrome-devtools-mcp` / `a11y-debugging` / `debug-optimize-lcp` / `memory-leak-debugging` / `cookie-debugging` when web UI is touched.
- **Gate Check:** Zero AI slop boilerplate phrases/chrome; zero blocking console/a11y errors.
- **Artifacts:** `ui_quality_audit`

### S6: Release Artifact Sealing & Integrity Manifest
- **Depends On:** `S4`, `S5`
- **Inputs:** release/build directory (`dist_dir`)
- **Actions:** Generate deterministic `SHA256SUMS.json` via `verified_release_craft.py sha256-manifest` and independently verify with `verify-manifest` (rejecting any path traversal).
- **Gate Check:** `verify-manifest` exits `0` with `mismatches == []` and `missing == []`.
- **Artifacts:** `SHA256SUMS.json`

### S7: Release Verdict & Outcome-First Report
- **Depends On:** `S6`
- **Inputs:** all stage outputs
- **Actions:** Emit clean verdict (`SHIP` vs `BLOCK`), `INTENT:` / `TWINS:` / `PENDING:` lines, and exact file:line citations.
- **Gate Check:** All 6 earlier stages green or blocker explicitly surfaced with remediation diff.
- **Artifacts:** `release_verdict_summary`

## 4. Fallback & Escalation Rules

- **3-Strike Self-Correction:** Fix mechanical/code failures up to 3 consecutive times while preserving security thresholds; on the 3rd failure, emit a Diagnostic Report and halt.
- **Missing Optional Binary (`trufflehog` or `bla`):** Fall back to `verified_release_craft.py` + `security_scanner.py` regex/AST secret checks and clearly disclose `trufflehog` binary absence as a caveat.
- **Hard Delivery Block:** If score < 80, verified secret found, or Mind-Virus threat detected, block release unconditionally and surface exact remediation diffs.
- **Try-Harder Escalation:** If a primary verification tool fails or lacks coverage, pivot to direct code inspection + live PoC script execution without guessing.

## 5. Single-Pass Completion Criteria

- [ ] SAST score >= 80/100 and Mind-Virus scan `CLEAN`.
- [ ] Zero exposed secrets, weak crypto patterns, or AI-slop chrome.
- [ ] All existing and added unit/integration tests observed passing post-edit.
- [ ] SHA-256 manifest generated and verified cleanly when releasing build outputs.
- [ ] `TWINS:` line emitted whenever a defect was fixed.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `verified-release-and-ui-craft` | Global | [`SKILL.md`](./modules/verified-release-and-ui-craft/SKILL.md) | Absorbed into `/ship` |
| `shift-left-ai-security` | Global | [`SKILL.md`](./modules/shift-left-ai-security/SKILL.md) | Absorbed into `/ship` |
| `daily-security-workflow` | Global | [`SKILL.md`](./modules/daily-security-workflow/SKILL.md) | Absorbed into `/ship` |
| `vanta-security-scaling-guardrails` | Global | [`SKILL.md`](./modules/vanta-security-scaling-guardrails/SKILL.md) | Absorbed into `/ship` |
| `developer-isolation-blast-radius` | Global | [`SKILL.md`](./modules/developer-isolation-blast-radius/SKILL.md) | Absorbed into `/ship` |
| `static-code-analysis` | Global | [`SKILL.md`](./modules/static-code-analysis/SKILL.md) | Absorbed into `/ship` |
| `fable-judge` | Global | [`SKILL.md`](./modules/fable-judge/SKILL.md) | Absorbed into `/ship` |
| `try-harder-poc-validation` | Global | [`SKILL.md`](./modules/try-harder-poc-validation/SKILL.md) | Absorbed into `/ship` |

- **Companion Plugins:** `expert-testing-debugging`, `a11y-debugging`, `cookie-debugging`, `debug-optimize-lcp`, `memory-leak-debugging`, `firebase-security-rules-auditor`, `accidental-data-loss-prevention`
- **Companion MCP Servers:** `chrome-devtools-mcp`, `github-mcp-server`, `firebase-mcp-server`
