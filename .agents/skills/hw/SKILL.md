---
name: hw
description: >-
  Use when designing electronic hardware, custom PCBs, KiCad hierarchical schematics, Gerber/BOM/CPL fab packs, build123d/CadQuery parametric enclosures, or reproducible OS/firmware images. Executes pre-flight tooling -> spec/math -> ERC=0 -> DRC=0 -> ECAD-synced CAD -> pinned SHA256SUMS in one pass.
version: "2.0.0"
---

# /hw — Autonomous Hardware, KiCad PCB, Mechanical CAD & Firmware Compiler

Single-pass Category Master Skill. Invoking `/hw` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/hw`
- **Compatible Aliases:** `/hw`, `/hardware`, `/pcb`, `/cad`, `/firmware`
- **Absorbed Legacy Skills (1):** `/autonomous-hardware-architect`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `project_slug` | `string` | `hardware-project` | Target workspace directory name |
| `prompt` | `string` | `` | Device requirements, SoM/MCU preference, enclosure & IO constraints |
| `mode` | `enum(full|preflight|eda|cad|firmware)` | `full` | Full 5-stage compiler run or targeted verification gate |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **Physical Contradiction Gate ONLY:** Run Stages 0->5 end-to-end without stopping for routine approvals; halt ONLY on irreconcilable physical contradictions (>15W on 5V/3A port without 20V PD, Tj > 0.85*Tj_max, perimeter overflow, irreconcilable pin-mux/voltage conflict).
- **ECAD -> MCAD Tie-Breaker:** ECAD (`hardware/pcb/*.kicad_pcb` & `fab/board.step`) is authoritative; MCAD MUST consume `extract_board_geometry.py` (`enclosure/board_sync.json`) and never hardcode mechanical magic numbers.
- **Zero Hand-Guessed `.kicad_sch` Wires:** Generate schematics programmatically via `SKiDL`/`kicad-skip`/`atopile`/`tscircuit` with explicit `PWR_FLAG` and `no_connect` markers.
- **Mandatory Zero-Violation Gates:** Never advance past Stage 2 until `erc_violations == 0`, Stage 3 until `drc_violations == 0` and `unconnected_nets == 0`, or Stage 4 until meshes are watertight 2-manifold with `interference_count == 0`.
- **Immutable Cryptographic Pinning:** Pin all OS images/bootloaders/firmwares to immutable HTTPS version tags with 64-hex `firmware/SHA256SUMS` (never `latest`).

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S0: Pre-Flight Tooling & Workspace Layout
- **Depends On:** None (Entry Gate)
- **Inputs:** local host tooling (`kicad-cli`, `freerouting`, Java, Python CAD/EDA)
- **Actions:** Run `bash ./modules/autonomous-hardware-architect/scripts/bootstrap_env.sh --check --json` (and `--install` if needed); create ICM folder layout (`GEMINI.md`, `spec.md`, `hardware/{schematics,pcb}`, `fab/`, `enclosure/`, `image/`, `firmware/`).
- **Gate Check:** `bootstrap_env.sh` exits `0` and workspace tree exists with `GEMINI.md`.
- **Artifacts:** `GEMINI.md, bootstrap_status.json`

### S1: Requirements Matrix, Electrical/Thermal Math & US BOM
- **Depends On:** `S0`
- **Inputs:** `references/electrical_math_and_bom.md`
- **Actions:** Write numbered `R1..Rn` specs in `spec.md`, prefer pre-certified SoMs (CM5/CM4/ESP32-S3/nRF52/nRF54), calculate USB-C PD dividers, TVS/P-FET protection, E96 buck feedback/inductor ripple/Tj at Ta=45C, and produce US-sourceable `fab/bom.csv`; run `verify_eda.py --bom fab/bom.csv`.
- **Gate Check:** `verify_eda.py --bom` exits `0` with zero missing lifecycle/distributor fields.
- **Artifacts:** `spec.md, fab/bom.csv`

### S2: Programmatic Hierarchical Schematics & ERC=0
- **Depends On:** `S1`
- **Inputs:** `references/eda_cad_firmware_patterns.md`, `spec.md`
- **Actions:** Author `hardware/schematics/generate_schematics.py` partitioning up to 7 hierarchical `.kicad_sch` sheets (`01_power_input_protection`..`07_ui_mechanical`) with `PWR_FLAG`/`no_connect`; run `verify_eda.py --sch ... --bom fab/bom.csv --output hardware/schematics/erc_report.json`.
- **Gate Check:** `verify_eda.py` exits `0` (`erc_violations == 0`).
- **Artifacts:** `hardware/schematics/*.kicad_sch, erc_report.json`

### S3: Programmatic PCB Layout, Autorouting, DRC=0 & Fab Pack
- **Depends On:** `S2`
- **Inputs:** validated netlist, `Edge.Cuts`, net classes
- **Actions:** Run `hardware/pcb/place_and_route.py` (mounting holes & RF keepouts first, flush edge-overhang ports, decoupling `<2.5mm`, tight buck loops), export `.dsn` -> headless `freerouting` -> `.ses` -> zone refills, and run `verify_eda.py --sch ... --pcb ... --bom ... --fab-dir fab --output fab/eda_verification.json`.
- **Gate Check:** `verify_eda.py` exits `0` (`drc_violations == 0`, `unconnected_nets == 0`, non-empty `gerbers.zip`, `cpl.csv`, `board.step`).
- **Artifacts:** `fab/gerbers.zip, fab/cpl.csv, fab/board.step, fab/eda_verification.json`

### S4: ECAD-Synced Parametric Enclosure & Manifold Check
- **Depends On:** `S3`
- **Inputs:** `hardware/pcb/*.kicad_pcb`, `fab/board.step`
- **Actions:** Run `extract_board_geometry.py` -> `enclosure/board_sync.json`; author `enclosure/generate_enclosure.py` (`build123d`/`CadQuery`) with `0.25-0.35mm` radial port clearances, concentric bosses, thermal louvers, and light-pipes; export `.stl`/`.3mf` and validate with `verify_mesh.py`.
- **Gate Check:** `verify_mesh.py` exits `0` (watertight 2-manifold, positive volume, `interference_count == 0`).
- **Artifacts:** `enclosure/board_sync.json, enclosure/*.stl, enclosure/assembly.3mf, enclosure/mesh_verification.json`

### S5: Reproducible OS Image & Pinned Firmware Bring-Up
- **Depends On:** `S2`, `S4`
- **Inputs:** Stage 2 GPIO pinout, pinned HTTPS releases
- **Actions:** Generate `image/build-image.py` + `config.txt`/`.dtbo`, `firmware/fetch-firmware.py`, `firmware/SHA256SUMS`, `firmware/manifest.json`, `firmware/FLASHING.md`, and run `fetch-firmware.py --verify-pins --dry-run` + `build-image.py --dry-run`.
- **Gate Check:** Both dry-runs exit `0` and all `SHA256SUMS` pass 64-hex verification.
- **Artifacts:** `firmware/SHA256SUMS, firmware/manifest.json, firmware/FLASHING.md`

## 4. Fallback & Escalation Rules

- **3 Self-Healing Cycles per CLI Gate:** Parse structured JSON errors from `verify_eda.py` or `verify_mesh.py` and iterate placement/clearances/netlist up to 3 times before halting with a Diagnostic Report.
- **Physical Contradiction Escalation:** Stop immediately and invoke Planning Mode only when electrical, thermal, perimeter, or pin-mux budgets are physically impossible under user constraints.
- **Missing KiCad/Freerouting in Dry Environment:** Run `bootstrap_env.sh --check --json`, report exact missing host binaries, and verify generator scripts/math syntactically without fabricating fab pass results.

## 5. Single-Pass Completion Criteria

- [ ] `verify_eda.py` passes with `erc_violations == 0`, `drc_violations == 0`, `unconnected_nets == 0`.
- [ ] `fab/{bom.csv,gerbers.zip,cpl.csv,board.step}` exist and pass validation.
- [ ] `verify_mesh.py` confirms watertight 2-manifold enclosures with `interference_count == 0`.
- [ ] Firmware dry-runs and 64-hex `SHA256SUMS` pass verification.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `autonomous-hardware-architect` | Global | [`SKILL.md`](./modules/autonomous-hardware-architect/SKILL.md) | Absorbed into `/hw` |

- **Companion Plugins:** None
- **Companion MCP Servers:** None
