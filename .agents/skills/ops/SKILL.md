---
name: ops
description: >-
  Use when orchestrating multi-agent swarms, routing MCP/API models (OmniRoute, Composio, Nod, LUMINA, Antigravity), managing meetings and 48-hour follow-up loops, triaging work by energy tier, or aligning human writing style and RBAC safety in one end-to-end pass.
version: "2.0.0"
---

# /ops — Agent Orchestration, MCP Routing, Meetings, Energy Tasking & Style Sync

Single-pass Category Master Skill. Invoking `/ops` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/ops`
- **Compatible Aliases:** `/ops`, `/sync`, `/orchestrate`, `/nod`, `/harness`, `/meetings`, `/energy`
- **Absorbed Legacy Skills (16):** `/agent-harness-v2`, `/agent-systems-unified-skill`, `/autonomous-architect-protocol`, `/delegation-diligence-loop`, `/unified-ai-architecture-and-standards`, `/icm-architect`, `/tri-perspective-collaboration`, `/nod-bridge-ops`, `/omniroute`, `/composio-mcp`, `/unigent`, `/typesafe-ai`, `/skillopt`, `/nod-human-ops`, `/mas_orchestrator`, `/ego-lite`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `objective` | `string` | `` | Orchestration task, meeting/inbox triage, or bridge sync request |
| `energy` | `enum(auto|peak|steady|recovery)` | `auto` | Operator energy tier for task batching and routing |
| `channel` | `enum(internal|group|direct|bridge)` | `internal` | Target communication/alignment channel |
| `entity` | `enum(all|charity|lumina|consulting)` | `all` | Organizational lane & RBAC scope |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **4-Asset Memory & Harness First:** Load Chat Memory (`L0->L3`), Skills, Wiki, and CodeGraph (`memory_hub/`) before planning or delegating; keep ISTL confidence strictly in `[0.00, 0.99]` (never `1.0`).
- **Supervisor CEO & Security Gates:** Intervene when confidence < 0.30, repeated failures > 2, or security score < 50; block delivery below 80 and scan all inter-agent payloads via `scan_mind_virus.py`.
- **Nod Bridge & Auth Boundaries:** Use ONLY non-hidden `~/nod_antigravity_bridge/{inbox_for_nod,outbox_from_nod}/`; never bypass Nod Desktop `401` (`x-nod-desktop-token`) or `403` action-review guards; Bearer HTTP (`127.0.0.1:58408`) requires `>=43`-char `NOD_AUTH_TOKEN`.
- **WhatsApp Single-Socket & Multi-Window Reload Rule:** Never launch duplicate Baileys sockets against `~/.nod_whatsapp_auth`; use shared loopback hub `127.0.0.1:58409` (`--daemon`/`embedded_hub`/`proxy_to_hub`), reload primary `embedded_hub` window before secondary windows in host UI, and keep Nod Docker containers on `--restart unless-stopped`.
- **Zero-Fabrication & RBAC Alignment (`nod-human-ops`):** Never claim a script ran, file saved, or reply sent without verified tool output/ID; enforce `~/.nod_whatsapp_auth/rbac_policy.json`, 50% trading cap, Charity zero-paid-ads invariant, and `<50%` local CPU/RAM cap (`qwen3.5:2b`, `OLLAMA_KEEP_ALIVE=2m`).
- **A-01..A-08 Ecosystem Standards:** Enforce explicit task state machines (`pending->running->succeeded/failed`), exponential backoff retries, outreach delivery acks, idempotency keys, and unified delivery ledger.

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Harness Sync & 4-Asset Memory Hydration
- **Depends On:** None (Entry Gate)
- **Inputs:** `memory_hub/`, active workspace `GEMINI.md` & `state.json`
- **Actions:** Load role loadout via `harness_runtime.py`, verify active Master Skills parity, check Nod/WhatsApp/OmniRoute health (`nod_get_status`, `wa_get_status`), and initialize ISTL confidence.
- **Gate Check:** Memory hub hydrated and live bridge/service status observed.
- **Artifacts:** `harness_state_snapshot`

### S2: Energy-Based Tasking & Meeting Triage
- **Depends On:** `S1`
- **Inputs:** incoming tasks, calendar events, Base44 `IntakeSubmission`, 48h reminder queue
- **Actions:** Classify queued work by Energy Tier (`Peak`: deep architecture/debugging/quant math -> batch uninterrupted; `Steady`: PR reviews/workflows/deployments -> run structured pipelines; `Recovery`: inbox triage, 48h reminders `assigned->reminded->done->verified`, calendar free-slot checks & Base44 Google Meet Auto-Booking -> route to fast lane). Enforce Global-Impact Bar to eliminate paperweight work.
- **Gate Check:** Every task tagged with energy tier, owner entity (`Jeremiah`/`Fernando`/`DJ`), and next verified action.
- **Artifacts:** `energy_task_and_meeting_plan`

### S3: Concurrency, Model & MCP/API Routing
- **Depends On:** `S2`
- **Inputs:** task SLA, context size, available local/remote providers
- **Actions:** Select concurrency model (`asyncio` I/O vs threads vs processes per `agent-systems-unified-skill`), route local inference via OmniRoute / Ollama (`qwen3.5:2b` fast lane or `antigravity-master` / `qwen3.5:9b` deep lane keeping host load <50%), and resolve dynamic MCP toolkits via `composio_mcp_cli.py` or TypeSafe `typesafe_judge.py`.
- **Gate Check:** Zero unbounded worker pools or rate-limit loops; model & MCP route verified.
- **Artifacts:** `routing_decision_manifest`

### S4: Bounded Delegation, Bridge Dispatch & Durable Execution
- **Depends On:** `S3`
- **Inputs:** scoped briefs, ICM folder structure, `~/nod_antigravity_bridge/`
- **Actions:** Organize multi-step specs as ICM folder trees (`icm-architect`), dispatch Nod deep tasks via `nod_dispatch_task` / `POST 127.0.0.1:58408/api/messages` or file bridge, enforce Tri-Perspective SpacetimeDB reducers + blue/green expand-contract DB migrations when modifying shared schemas, and run `agent-harness-v2` / `delegation-diligence-loop` verification.
- **Gate Check:** Every delegated step verified by exit code / endpoint proof (`Diligence` pass).
- **Artifacts:** `delegation_execution_log`

### S5: Writing-Style, Tone & RBAC Alignment Gate
- **Depends On:** `S4`
- **Inputs:** draft reply/debrief, speaker role, learned writing-style profile
- **Actions:** Apply Nod's learned email/conversation writing style + natural human teammate voice + ~80% ASDSTE 100 clarity; run `alignAndTailorResponse` rules to redact secrets, cross-sender JIDs, or out-of-lane disclosures (`group` vs `direct`, Charity vs Lumina vs Consulting).
- **Gate Check:** Message matches user's natural writing style with zero secret/PII leakage or bot filler.
- **Artifacts:** `aligned_outbound_payload`

### S6: Supervisor Gate, SkillOpt Reflection & EOD Debrief
- **Depends On:** `S5`
- **Inputs:** run telemetry, ISTL scores, security/mind-virus scans
- **Actions:** Verify `security_scanner.py >= 80` and `scan_mind_virus.py CLEAN`, adjust ISTL confidence (`+0.08` success / `-0.18` failure), run bounded SkillOpt reflection (`skillopt`) if recurring bottleneck detected, and format on-demand `"text us last"` debriefs with verified wins/blockers/Global-Impact move/team prompt.
- **Gate Check:** Supervisor cleared (`confidence >= 0.30`, `security >= 80`); zero unverified claims.
- **Artifacts:** `supervisor_and_debrief_report`

### S7: Atomic State Persistence & Unified Delivery Ledger
- **Depends On:** `S6`
- **Inputs:** updated task statuses, memory atoms, bridge snapshots
- **Actions:** Persist state atomically via `tempfile` + `os.fsync` + `os.replace` (`state.json`, `memory_hub/`, `~/.nod_whatsapp_auth/` snapshots), record A-08 delivery acks, and return concise outcome summary.
- **Gate Check:** All state files saved atomically with zero partial writes.
- **Artifacts:** `delivery_ledger_entry`

### Energy-Based Tasking Matrix
| Energy Tier | Best Work Types | Execution / Routing Rule | Local Resource Ceiling |
| :--- | :--- | :--- | :--- |
| **Peak** | Architecture, root-cause debugging, quant math, formal proofs | Assign to primary reasoning model (`Orchestrator` / `qwen3.5:9b`); zero interruption batching | Keep background daemons throttled |
| **Steady** | PR reviews, workflow pipelines, schema syncs, test suites | Execute structured Master Skill pipelines (`/code`, `/ship`, `/billing`) | `< 50%` host CPU/RAM load |
| **Recovery** | Inbox triage, calendar slots, 48h reminders, `"text us last"` recaps | Route to Nod fast lane (`127.0.0.1:11434` `qwen3.5:2b`, `think: false`) & Base44 auto-booking | `OLLAMA_KEEP_ALIVE=2m`, FIFO `concurrency=1` |

### Writing-Style & Tone Alignment Rules
1. Match the user's natural, direct human voice (short sentences, compact bullets only when listing >=3 items, zero `"As an AI..."` filler).
2. Enforce ~80% ASDSTE 100 readability on technical instructions and client updates.
3. Tailor density to channel: crisp 1–4 line answers in WhatsApp/group threads; structured tables with file links in IDE/report threads.
4. Strip leaked tokens, cross-user JIDs, internal file paths (for external recipients), and unauthorized entity details before send.

## 4. Fallback & Escalation Rules

- **3-Strike Escalation (Nod <-> Antigravity):** After 3 consecutive local errors on Nod, escalate raw logs to Antigravity over `127.0.0.1:58408` or `~/nod_antigravity_bridge/`.
- **Dual-Lane Degradation:** If Nod Bearer `58408` is offline (`embedded_hub`), execute WhatsApp/fast-lane tasks via local hub (`58409` / `11434`) and report honest offline error for deep Nod calls—never spoof Desktop `401` tokens.
- **Supervisor Freeze:** Pause execution immediately if worker confidence drops < 0.30, security < 50, or Mind-Virus flags viral propagation.
- **Meta-Tool Bottleneck (`autonomous-architect-protocol`):** Auto-deregister any new custom MCP helper if its first 3 live invocations fail.

## 5. Single-Pass Completion Criteria

- [ ] Tasks triaged by Energy Tier and active meetings/48h loops reconciled.
- [ ] All delegated actions verified via primary logs, HTTP codes, or test runs (zero fabrication).
- [ ] Outbound text passes Writing-Style + ~80% ASDSTE 100 + RBAC + secret-redaction checks.
- [ ] State persisted atomically with Harness v2.0 YAML metadata header.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `agent-harness-v2` | Global | [`SKILL.md`](./modules/agent-harness-v2/SKILL.md) | Absorbed into `/ops` |
| `agent-systems-unified-skill` | Global | [`SKILL.md`](./modules/agent-systems-unified-skill/SKILL.md) | Absorbed into `/ops` |
| `autonomous-architect-protocol` | Global | [`SKILL.md`](./modules/autonomous-architect-protocol/SKILL.md) | Absorbed into `/ops` |
| `delegation-diligence-loop` | Global | [`SKILL.md`](./modules/delegation-diligence-loop/SKILL.md) | Absorbed into `/ops` |
| `unified-ai-architecture-and-standards` | Global | [`SKILL.md`](./modules/unified-ai-architecture-and-standards/SKILL.md) | Absorbed into `/ops` |
| `icm-architect` | Global | [`SKILL.md`](./modules/icm-architect/SKILL.md) | Absorbed into `/ops` |
| `tri-perspective-collaboration` | Global | [`SKILL.md`](./modules/tri-perspective-collaboration/SKILL.md) | Absorbed into `/ops` |
| `nod-bridge-ops` | Global | [`SKILL.md`](./modules/nod-bridge-ops/SKILL.md) | Absorbed into `/ops` |
| `omniroute` | Global | [`SKILL.md`](./modules/omniroute/SKILL.md) | Absorbed into `/ops` |
| `composio-mcp` | Global | [`SKILL.md`](./modules/composio-mcp/SKILL.md) | Absorbed into `/ops` |
| `unigent` | Global | [`SKILL.md`](./modules/unigent/SKILL.md) | Absorbed into `/ops` |
| `typesafe-ai` | Global | [`SKILL.md`](./modules/typesafe-ai/SKILL.md) | Absorbed into `/ops` |
| `skillopt` | Global | [`SKILL.md`](./modules/skillopt/SKILL.md) | Absorbed into `/ops` |
| `nod-human-ops` | Local-Merged | [`SKILL.md`](./modules/nod-human-ops/SKILL.md) | Absorbed into `/ops` |
| `mas_orchestrator` | Local-Merged | [`SKILL.md`](./modules/mas_orchestrator/SKILL.md) | Absorbed into `/ops` |
| `ego-lite` | Local-Merged | [`SKILL.md`](./modules/ego-lite/SKILL.md) | Absorbed into `/ops` |

- **Companion Plugins:** `harness-engineering`, `subagent-orchestration`, `google-antigravity-sdk`, `base44-troubleshooter`
- **Companion MCP Servers:** `nod-local-bridge`, `whatsapp-bridge`, `lumina-mcp`, `github-mcp-server`
