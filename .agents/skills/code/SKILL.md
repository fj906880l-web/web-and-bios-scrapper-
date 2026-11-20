---
name: code
description: >-
  Use when planning, building, refactoring, debugging, or teaching software systems end-to-end. Combines Fable Method (Steps 0-6), Fable Loop & Domain bundle creation, IBM Context-Aware Coding (6 inputs, 3-move surfacing, U-shaped attention), Surgical Code Craft (Fowler/Beck TDD), 23 CS algorithmic foundations, Cloudflare Workers/DO, B.L.A.S.T., error patterns, and ZPD tutoring.
version: "2.0.0"
---

# /code — Context-Aware Software Craft, Algorithms & App Delivery

Single-pass Category Master Skill. Invoking `/code` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/code`
- **Compatible Aliases:** `/code`, `/build`, `/refactor`, `/teach`, `/fable-method`, `/fable-loop`, `/fable-domain`
- **Absorbed Legacy Skills (11):** `/context-aware-coding`, `/surgical-code-craft`, `/fable-method`, `/fable-loop`, `/fable-domain`, `/cloudflare-os`, `/cs-algorithmic-foundations`, `/blast-master-system`, `/error-handling-patterns`, `/system-optimization-guide`, `/teach`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `task` | `string` | `` | Engineering task, bug fix, domain bundle, or tutoring topic |
| `mode` | `enum(build|refactor|plan|domain|teach|optimize)` | `build` | Workflow lane inside the single-pass pipeline |
| `target` | `path` | `.` | Project workspace root |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **Zero `CLAUDE.md` / `.claude/` Residue:** Strictly use `GEMINI.md` and `.agents/` workspace conventions.
- **Intent & Spec Authority Gate:** Before editing behavior, write `INTENT: code does <X>; expected <Y>; spec says <Z>` from actual primary docs/tests; surface contradictions immediately.
- **Recall Gate:** Never invent API signatures, library flags, or lockfile versions from memory; read installed source, lockfiles (`context-aware-coder deps`), or official docs first.
- **Blast & Error Discipline:** Separate `RecoverableError` (explicit bounded retries + backoff) from `UnrecoverableError`; enforce WAL mode, pooling, and O(1)/bounded memory budgets.
- **Standing Prohibitions:** Never commit/push without `AUTH:`, never weaken tests to force green, never touch secrets/locks outside scope.

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Classify, Define Done & Gather 6 Context Inputs
- **Depends On:** None (Entry Gate)
- **Inputs:** task prompt, repository root, `GEMINI.md`
- **Actions:** Run Fable Step 0-1 (classify Task vs Question vs Plan-first; define verifiable Done); extract all 6 IBM Context Inputs via `context_aware_coder.py` (`repo-map`, `deps`, `tests`, `GEMINI.md`, code pointers, `INTENT:`). In `teach` mode, initialize `.agents/teach_state.json` via `tutor.py --init`.
- **Gate Check:** `INTENT:` and concrete verification criterion established; zero unresolved ambiguity.
- **Artifacts:** `context_map.json, INTENT_line`

### S2: 3-Move Context Surfacing & U-Shaped Attention Bundle
- **Depends On:** `S1`
- **Inputs:** 6 context inputs, unrelated noise filtered
- **Actions:** Execute `context_aware_coder.py interview` & `bundle`: anchor `GEMINI.md` rules/Intent at start, relevant AST/file slices in middle, lockfile versions + test commands at end. For new domains (`mode=domain`), run `fable-domain` research to assemble domain reference.
- **Gate Check:** Zero irrelevant log/build noise in context bundle; explicit assumptions stated.
- **Artifacts:** `u_shaped_context_bundle`

### S3: Algorithmic, Cloudflare/App & Performance Design
- **Depends On:** `S2`
- **Inputs:** architecture constraints, scale targets
- **Actions:** Evaluate complexity/graph/cache/consensus choices via `cs_algorithmic_foundations.py`; apply Cloudflare Workers/DO capability boundaries, ZCode/Monaco conventions, B.L.A.S.T. 3-layer A.N.T. structure, and `system-optimization-guide` (SQLite WAL, pooling, Parquet caching).
- **Gate Check:** Design chosen with zero duplicate logic and bounded complexity.
- **Artifacts:** `committed_implementation_plan`

### S4: Surgical TDD Implementation (Two Hats & Micro-Diffs)
- **Depends On:** `S3`
- **Inputs:** targeted files in declared scope
- **Actions:** Write/verify failing test first (Beck Red-Green-Refactor), apply Fowler micro-diffs keeping refactoring separate from behavior edits, enforce clean SRP boundaries and typed Result/Exception handling. In `teach` mode, deliver ZPD lesson via `tutor.py --next` and grade via `--grade`.
- **Gate Check:** Diffs stay strictly inside declared scope with clean docstrings and zero duplicated helpers.
- **Artifacts:** `patched_source_and_tests`

### S5: Observational Verification, Twin Check & System Build
- **Depends On:** `S4`
- **Inputs:** test command, linter, build command
- **Actions:** Run scoped tests + surrounding suite + build/lint; search entire codebase for matching wrong patterns and record `TWINS: searched <pattern> - found <N> other sites: <files or none>`; run up to 3 self-correction cycles on failures.
- **Gate Check:** Targeted tests, surrounding suite, and build observed green post-final-edit.
- **Artifacts:** `verified_test_and_build_output`

### S6: Knowledge Write-Back & Outcome-First Report
- **Depends On:** `S5`
- **Inputs:** verified conventions, deliverables
- **Actions:** Persist discovered project invariants back into `GEMINI.md` via `context_aware_coder.py learn`, clean scratch artifacts, and output outcome-first report with `INTENT:` and `TWINS:` lines.
- **Gate Check:** `GEMINI.md` updated cleanly (zero `CLAUDE.md`) and all verification gates logged.
- **Artifacts:** `updated_GEMINI_md_and_report`

## 4. Fallback & Escalation Rules

- **Ambiguous Scope / Plan-First Trigger:** If two materially different deliverables exist and evidence cannot settle which one, or outward actions are requested without `AUTH:`, halt at S1/S3 and surface the recommendation.
- **3-Strike Self-Correction:** After 3 failed fix-verify cycles or missing toolchain/credentials, stop and report exact tracebacks + hypothesis.
- **Mode Specialization:** Automatically branch cleanly into `teach` (ZPD tutoring), `domain` (`fable-domain` bundle synthesis), or `plan` (S1-S3 stop) when requested.

## 5. Single-Pass Completion Criteria

- [ ] Every behavior change preceded by verified `INTENT:` line and lockfile/source check.
- [ ] Scoped + full surrounding tests and build/lint observed passing after final edit.
- [ ] `TWINS:` search executed and reported for every bug fix.
- [ ] Zero `CLAUDE.md` / `.claude/` residue and clean workspace.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `context-aware-coding` | Global | [`SKILL.md`](./modules/context-aware-coding/SKILL.md) | Absorbed into `/code` |
| `surgical-code-craft` | Global | [`SKILL.md`](./modules/surgical-code-craft/SKILL.md) | Absorbed into `/code` |
| `fable-method` | Global | [`SKILL.md`](./modules/fable-method/SKILL.md) | Absorbed into `/code` |
| `fable-loop` | Global | [`SKILL.md`](./modules/fable-loop/SKILL.md) | Absorbed into `/code` |
| `fable-domain` | Global | [`SKILL.md`](./modules/fable-domain/SKILL.md) | Absorbed into `/code` |
| `cloudflare-os` | Global | [`SKILL.md`](./modules/cloudflare-os/SKILL.md) | Absorbed into `/code` |
| `cs-algorithmic-foundations` | Global | [`SKILL.md`](./modules/cs-algorithmic-foundations/SKILL.md) | Absorbed into `/code` |
| `blast-master-system` | Local-Merged | [`SKILL.md`](./modules/blast-master-system/SKILL.md) | Absorbed into `/code` |
| `error-handling-patterns` | Local-Merged | [`SKILL.md`](./modules/error-handling-patterns/SKILL.md) | Absorbed into `/code` |
| `system-optimization-guide` | Local-Merged | [`SKILL.md`](./modules/system-optimization-guide/SKILL.md) | Absorbed into `/code` |
| `teach` | Local-Merged | [`SKILL.md`](./modules/teach/SKILL.md) | Absorbed into `/code` |

- **Companion Plugins:** `planning-vs-fast`, `goldie-gravity-launch`, `modern-web-guidance`, `firebase-basics`, `firebase-app-hosting-basics`, `firebase-auth-basics`, `firebase-firestore`, `firebase-data-connect`, `android-cli`, `xcode-project-setup`, `base44-cli`, `base44-sdk`
- **Companion MCP Servers:** `github-mcp-server`, `firebase-mcp-server`, `chrome-devtools-mcp`
