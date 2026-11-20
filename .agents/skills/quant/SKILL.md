---
name: quant
description: >-
  Use when auditing trading daemons, validating live/paper risk locks, running Qlib MTS/MTF pipelines, ingesting Alpaca/Robinhood/QuantPad/OpenNews/OnChain market data, sizing AI models, or fine-tuning and deploying local QLoRA/GGUF models via Soup, LUMINA Unsloth, and Ollama in one pass.
version: "2.0.0"
---

# /quant — Quantitative Trading, Risk Gating & Local Unsloth/Soup/Ollama Fine-Tuning

Single-pass Category Master Skill. Invoking `/quant` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/quant`
- **Compatible Aliases:** `/quant`, `/trade`, `/trading-bot`, `/soup`, `/unsloth`, `/finetune`
- **Absorbed Legacy Skills (8):** `/soup-finetuning-harness`, `/ai-algorithm-distillery`, `/active-trade-allocation`, `/qlib-mts-workflow`, `/quantpad-data-api`, `/opennews-mcp`, `/mcp-fd-and-bracket-audit`, `/trading-bot-auditor`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `mode` | `enum(audit|pipeline|finetune|telemetry|research)` | `audit` | Quant workflow lane |
| `target` | `path` | `/Users/malcolm/Downloads/trading-bot-` | Trading or fine-tuning workspace |
| `recipe` | `path` | `` | Optional Soup/Unsloth training recipe path |
| `live_exec` | `bool` | `false` | Must remain false; live orders blocked absent explicit AUTH: |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **50% Capital Cap & Reserve Floor:** Never allocate > 50% active equity/buying power; enforce FINRA/PDT checks, crypto floor-truncation (`math.floor(qty * 10000.0) / 10000.0`), and fail-closed zero equity guards.
- **Paper/Live Firewall & Test Lock Safety:** `alpaca_live` and `robinhood` must never receive unpromoted paper orders; NEVER run `pytest` inside a locked live runtime CWD (`tests/conftest.py` cleans CWD `system_lock.lock`)—test inside `/Users/malcolm/Downloads/trading-bot-` or isolated tempdirs.
- **Zero Mock/Fake Data & Manual Adoption:** Ban synthetic prices/mock broker order IDs (`is_valid_broker_order_id`); adopt manual broker holdings via `source: "manual"` with dynamic ATR SL <= 4.9% and atomic JSON writes (`tempfile` + `os.fsync` + `os.replace`).
- **MCP Singleton & FD-Leak Hygiene:** Enforce single `RobinhoodClient` subprocess (`PIPE` FDs < 20, `selectors.DefaultSelector` instead of `select.select`), guard null quotes on zero-qty/IPO assets, and prevent memory bloat or ticker hallucinations (`trading-bot-auditor`).
- **Model Asset & Resource Safety:** Treat `.pt`/`.pth`/`.joblib` as unsafe (prefer SafeTensors + SHA-256 verification + `weights_only=True`), enforce `stream_layers: true` (`<=4GB VRAM` / `<50%` Mac load), HTTPS-only model pulls, and Soup v0.75+ strict schema (`top-level base:`, `data.max_length`, `training.lr`).

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Firewall, Lock Isolation & Daemon FD Pre-Flight
- **Depends On:** None (Entry Gate)
- **Inputs:** `system_lock.lock`, `monitoring/{paper,live}_system_lock.lock`, `lsof`
- **Actions:** Inspect runtime locks read-only first; audit daemon FD/pipe counts (`<20` pipes, `<=1` `robinhood-for-agents` child) and open bracket SL coverage (`mcp-fd-and-bracket-audit`); verify `trading-bot-auditor` memory/ticker hygiene.
- **Gate Check:** Live/paper locks isolated, `PIPE` FDs < 20, zero phantom tickers.
- **Artifacts:** `lock_and_fd_audit`

### S2: Live Multi-Source Market & News Telemetry Ingestion
- **Depends On:** `S1`
- **Inputs:** Alpaca/Robinhood/QuantPad/QuiverQuant/AlphaVantage/OpenNews/OnChain MCPs
- **Actions:** Fetch real market bars, L2 quotes, options chains, congressional/insider flows, or OpenNews macro feeds; reject any mock/fallback fabricated pricing.
- **Gate Check:** All series timestamped, real-source backed, and free of NaN/stale gaps.
- **Artifacts:** `live_market_telemetry`

### S3: Algorithm Sizing & Local Fine-Tuning (Soup / Unsloth / Ollama)
- **Depends On:** `S2`
- **Inputs:** `ai_algorithm_distillery.py`, `soup_tool_runner.py`, LUMINA Unsloth API
- **Actions:** Compute MoE/RAG/quantization/compression budgets (`ai_algorithm_distillery.py`); in `finetune` mode, generate/validate Soup v0.75+ recipe (`init` / `validate-recipe` / `doctor` / `matrix-verify` with `stream_layers: true` or LUMINA `/api/unsloth/job/start`), verify checkpoint SHA-256, and export GGUF `q4_k_m` to local Ollama.
- **Gate Check:** Doctor/schema checks exit `0`; host load stays `<50%`; GGUF registered in Ollama cleanly.
- **Artifacts:** `distillery_and_model_artifact`

### S4: Qlib MTS/MTF Walk-Forward & DSR Evaluation
- **Depends On:** `S2`
- **Inputs:** point-in-time factor expressions, HMM regime states
- **Actions:** Run Qlib MTF/MTS factor evaluation (`qlib-mts-workflow`), calculate Deflated Sharpe Ratio (DSR) to reject overfit backtests, and compute allocation caps (`active-trade-allocation`).
- **Gate Check:** Walk-forward and DSR gates satisfied within <=50% buying-power cap.
- **Artifacts:** `qlib_mts_evaluation`

### S5: Paper Execution, Manual Adoption & Hard `AUTH:` Live Gate
- **Depends On:** `S4`
- **Inputs:** validated signal, broker order state
- **Actions:** Adopt any manual entries safely (`source: "manual"`, ATR SL <= 4.9%); permit paper/dry-run validation inside isolated test dir (`Downloads/trading-bot-`); unconditionally block any live order submission absent explicit `AUTH:`.
- **Gate Check:** Zero unapproved live orders; atomic persistence verified (`orders.json` / `risk_state.json`).
- **Artifacts:** `execution_gate_verdict`

### S6: Verification, Security Scan & Post-Mortem Memory Sync
- **Depends On:** `S5`
- **Inputs:** isolated test suite (`Downloads/trading-bot-`), `daily_security_workflow.py`
- **Actions:** Run quant tests in safe directory (`Downloads/trading-bot-`), run security scan (`>=80`, `os.replace` preserved in `risk_manager.py`), and log lessons to memory.
- **Gate Check:** All tests and security scans pass without touching live runtime locks.
- **Artifacts:** `quant_verification_summary`

## 4. Fallback & Escalation Rules

- **3-Strike Self-Correction & Fail-Closed Equity:** On missing broker balance, API timeout, or NaN telemetry, fail closed (halt new entries) and retry read-only telemetry up to 3 times.
- **Locked Runtime CWD Detected:** Refuse running `pytest` directly inside `/Users/malcolm/trading-bot-` when `system_lock.lock` exists; redirect verification to `/Users/malcolm/Downloads/trading-bot-`.
- **OOM / VRAM Guardrail:** Force `stream_layers: true`, `batch_size: 1`, `gradient_accumulation_steps >= 4`, or pause local training if Mac load approaches 50%.

## 5. Single-Pass Completion Criteria

- [ ] 50% buying-power cap, paper/live firewall, and zero-mock-data invariants verified.
- [ ] Daemon FD/pipe count < 20 and open-order stop-loss bracket coverage audited.
- [ ] Tests executed safely outside locked live CWD and observed green.
- [ ] Any Soup/Unsloth fine-tune recipe validated via `doctor`/`validate-recipe` before run.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `soup-finetuning-harness` | Global | [`SKILL.md`](./modules/soup-finetuning-harness/SKILL.md) | Absorbed into `/quant` |
| `ai-algorithm-distillery` | Global | [`SKILL.md`](./modules/ai-algorithm-distillery/SKILL.md) | Absorbed into `/quant` |
| `active-trade-allocation` | Local-Merged | [`SKILL.md`](./modules/active-trade-allocation/SKILL.md) | Absorbed into `/quant` |
| `qlib-mts-workflow` | Local-Merged | [`SKILL.md`](./modules/qlib-mts-workflow/SKILL.md) | Absorbed into `/quant` |
| `quantpad-data-api` | Local-Merged | [`SKILL.md`](./modules/quantpad-data-api/SKILL.md) | Absorbed into `/quant` |
| `opennews-mcp` | Local-Merged | [`SKILL.md`](./modules/opennews-mcp/SKILL.md) | Absorbed into `/quant` |
| `mcp-fd-and-bracket-audit` | Local-Merged | [`SKILL.md`](./modules/mcp-fd-and-bracket-audit/SKILL.md) | Absorbed into `/quant` |
| `trading-bot-auditor` | Local-Merged | [`SKILL.md`](./modules/trading-bot-auditor/SKILL.md) | Absorbed into `/quant` |

- **Companion Plugins:** None
- **Companion MCP Servers:** `alpaca`, `robinhood-for-agents`, `QuiverQuant_MCP`, `alphavantage`, `quantpad`, `onchain-market-mcp`
