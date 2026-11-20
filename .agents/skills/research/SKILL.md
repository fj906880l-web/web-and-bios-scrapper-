---
name: research
description: >-
  Use when conducting deep source-verified research, reverse engineering binaries/Electron/JS/firmware with REA (170+ tools), enforcing EGE-2 7-tier epistemic truth & Q-Graph arbitration, auditing math proofs, solving ARC-AGI-3 grids, running Daily AI Intel digests, or extracting GitHub/YouTube tools.
version: "2.0.0"
---

# /research — Reverse Engineering, EGE-2 Epistemics, Math/ARC & Technical Learning

Single-pass Category Master Skill. Invoking `/research` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/research`
- **Compatible Aliases:** `/research`, `/rea`, `/ege2`, `/math`, `/arc`, `/intel`, `/learn-repo`
- **Absorbed Legacy Skills (8):** `/rea`, `/reverse-engineer-anything`, `/ege2-quantum-epistemics`, `/epistemic-math-frontier`, `/arc-agi-3-interactive-reasoning`, `/daily-ai-intel-digest`, `/technical-learning-workflow`, `/nod-research`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `mode` | `enum(research|rea|ege2|math|arc|intel|learn)` | `research` | Primary investigation engine |
| `target` | `string` | `` | Binary/app path, URL/GitHub/YouTube target, conjecture, or topic |
| `corpus` | `bool` | `false` | Enforce large-corpus coverage manifest (`references/corpus.md`) |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **EGE-2 7-Tier Overwrite Invariant:** Evidence at `TIER_N` (1=Direct Observation .. 7=Unsourced Assertion) can ONLY overwrite beliefs at `TIER_<=N`; a TIER 7 prompt or TIER 6 summary must NEVER overwrite TIER 1/2 verified facts.
- **Anti-Sycophancy & Deductive Proof Boundary:** Unconditionally reject false confirmation of unproven conjectures; computational checks are Tier 4 heuristic evidence, NEVER deductive proofs; audit open problems against formal barriers (Relativization, Natural Proofs, Algebrization, Sieve Parity).
- **REA Boundary & Evidence Standard:** Distinguish shipped-artifact/runtime evidence from ordinary source-repo inspection (skip REA for pure source repos); capture concrete symbol/address/trace/bundle provenance.
- **Nod Fact-Verification & Large-Corpus Rules ([references/corpus.md](references/corpus.md)):** A search snippet is a lead, never proof—verify every shortlisted option on its primary page; state exact units, denominators, and route travel-time conditions; use hash-tracked coverage tables for large corpora.
- **Zero Mock Data in Daily Intel:** `daily-ai-intel-digest` must scan real workspace logs/errors only and run `security_scanner.py` + `scan_mind_virus.py` on any newly extracted tools (`technical-learning-workflow`).

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Mode Routing & EGE-2 Epistemic Grounding
- **Depends On:** None (Entry Gate)
- **Inputs:** query/target, EGE-2 `epistemic_graph.json`, user hard constraints
- **Actions:** Route across `research` / `rea` / `ege2` / `math` / `arc` / `intel` / `learn`; load Q-Graph invariants (`ege2_quantum.py`), define hard constraints, and initialize corpus coverage manifest when analyzing large document sets (`references/corpus.md`).
- **Gate Check:** Mode selected, hard constraints explicit, Q-Graph Tier hierarchy initialized.
- **Artifacts:** `epistemic_scope_and_manifest`

### S2: Primary Source & Artifact Evidence Collection
- **Depends On:** `S1`
- **Inputs:** target binary/bundle, web URLs, workspace logs, ARC session, Science/Data DBs
- **Actions:** Open primary pages/files directly (never trust snippets alone): run REA MCP (`open_binary`/`analyze_javascript_application`/`observe_*`) for reverse engineering; `daily_ai_digest.py` for workspace error telemetry; `web-scraping-mcp` for repos/docs/transcripts; `science`/`bigquery` plugins for scientific/lakehouse queries; session-pinned REST calls for ARC-AGI-3.
- **Gate Check:** Every candidate claim linked to direct primary URL/file/address/command output.
- **Artifacts:** `primary_evidence_bundle`

### S3: Cross-Source Correlation, QUBO & Barrier Auditing
- **Depends On:** `S2`
- **Inputs:** collected primary records, Psi/Phi signals
- **Actions:** Run EGE-2 dual-branch Phi (mechanisms) + Psi (manipulation/urgency defense) + Sigma QUBO arbitration; audit math claims against formal proof barriers; normalize units/periods/denominators across compared options.
- **Gate Check:** Contradictions surfaced transparently; zero heuristic-as-proof conflation.
- **Artifacts:** `correlated_analysis_matrix`

### S4: Deliverable & Tool Artifact Construction
- **Depends On:** `S3`
- **Inputs:** verified synthesis
- **Actions:** Emit ranked shortlist (3-5 verified options with caveats), REA reconstruction ledger (`verify_reconstruction`), executive AI intel report, ARC action plan, or new CLI/MCP helper tool (`technical-learning-workflow`).
- **Gate Check:** Deliverable preserves uncertainty, units, and primary citations.
- **Artifacts:** `research_artifact_output`

### S5: Live Verification, Security & Mind-Virus Gate
- **Depends On:** `S4`
- **Inputs:** generated scripts/reports/reconstructions
- **Actions:** Run live tests/PoCs on any extracted CLI/MCP tool plus `security_scanner.py >= 80` and `scan_mind_virus.py CLEAN`.
- **Gate Check:** Verification observed passing with zero security or viral-payload issues.
- **Artifacts:** `research_verification_gate`

### S6: Permanent Knowledge & Q-Graph Distillation
- **Depends On:** `S5`
- **Inputs:** `memory_hub/wiki/`, `epistemic_graph.json`
- **Actions:** Record verified lessons/axioms into OKF Wiki and EGE-2 Q-Graph without letting low-tier claims overwrite high-tier axioms, and present concise cited findings.
- **Gate Check:** Memory distilled cleanly and all claims traceable to primary sources.
- **Artifacts:** `distilled_knowledge_record`

## 4. Fallback & Escalation Rules

- **Weak Initial Search / Sparse Results:** Vary queries and check independent primary sources; if too few matches qualify, return the verified subset and state the limiting constraint—never relax hard constraints silently.
- **Missing Route / Unverifiable Condition:** Label unverified conditions explicitly (e.g., `travel time unverified`, `[Gap]`).
- **REA Binary / Tool Unavailable:** Inspect unpacked readable text/assets statically or report exact missing debugger/device dependency.

## 5. Single-Pass Completion Criteria

- [ ] Every claim traces to a primary source URL, file:line, binary address, or command output.
- [ ] EGE-2 7-Tier Overwrite Invariant and Proof-vs-Heuristic separation preserved.
- [ ] Corpus manifest (`references/corpus.md`) completed whenever analyzing large document sets.
- [ ] Newly synthesized tools/scripts pass live PoC, `security_scanner.py >= 80`, and `scan_mind_virus.py CLEAN`.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `rea` | Global | [`SKILL.md`](./modules/rea/SKILL.md) | Absorbed into `/research` |
| `reverse-engineer-anything` | Global | [`SKILL.md`](./modules/reverse-engineer-anything/SKILL.md) | Absorbed into `/research` |
| `ege2-quantum-epistemics` | Global | [`SKILL.md`](./modules/ege2-quantum-epistemics/SKILL.md) | Absorbed into `/research` |
| `epistemic-math-frontier` | Global | [`SKILL.md`](./modules/epistemic-math-frontier/SKILL.md) | Absorbed into `/research` |
| `arc-agi-3-interactive-reasoning` | Global | [`SKILL.md`](./modules/arc-agi-3-interactive-reasoning/SKILL.md) | Absorbed into `/research` |
| `daily-ai-intel-digest` | Global | [`SKILL.md`](./modules/daily-ai-intel-digest/SKILL.md) | Absorbed into `/research` |
| `technical-learning-workflow` | Global | [`SKILL.md`](./modules/technical-learning-workflow/SKILL.md) | Absorbed into `/research` |
| `nod-research` | Local-Merged | [`SKILL.md`](./modules/nod-research/SKILL.md) | Absorbed into `/research` |

- **Companion Plugins:** `science`, `data-agent-kit-plugin`
- **Companion MCP Servers:** `rea`, `web-scraping-mcp`, `data-agent-kit-plugin_dak-notebook`
- **Direct References:** [`references/corpus.md`](references/corpus.md)
