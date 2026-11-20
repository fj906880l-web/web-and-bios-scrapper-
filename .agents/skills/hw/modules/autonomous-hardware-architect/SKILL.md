---
name: autonomous-hardware-architect
version: 1.0.0
description: >-
  End-to-end autonomous hardware, mechanical CAD, and embedded firmware engineering
  skill. Activate whenever the user prompts for an electronic device, single-board
  computer (SBC), Raspberry Pi CM5/CM4 carrier board, ESP32/nRF52/STM32/RP2350
  embedded board, IoT or voice-assistant hub, sensor node, power board, custom PCB,
  KiCad schematic/layout, Gerber/BOM/CPL fab pack, build123d/CadQuery parametric
  enclosure, or reproducible OS image/firmware bring-up.
---

# Autonomous Hardware Architect

Execute a complete, fabrication-ready hardware, mechanical enclosure, and firmware bring-up workflow from a single high-level prompt—treating hardware engineering as a deterministic, code-driven software compiler pipeline inspired by Diode Computers' full-stack AI hardware synthesis.

## Operational Mode & Architecture Invariants

1. **Continuous Closed-Loop Execution (`planning-vs-fast` Rule)**:
   - Run **Stages 1 -> 5 end-to-end without stopping** between phases for routine approvals.
   - **Halt and escalate to Planning Mode ONLY on a physical contradiction** that cannot be resolved within user constraints:
     - Peak rail power exceeds negotiated input budget (e.g., >15 W demanded from a 5 V / 3 A port without 20 V PD).
     - Junction temperature $T_J > 0.85 \cdot T_{J,\max}$ inside the requested mechanical envelope.
     - Required edge-overhang connectors exceed available PCB perimeter length.
     - Irreconcilable SoM/MCU pin-multiplexing or voltage-domain conflict.
2. **Tri-Perspective Workspace & Digital Continuity (`tri-perspective-collaboration` Rule)**:
   - **ICM Folder-as-Architecture**: Create a clean target project workspace (e.g., `/Users/malcolm/.gemini/antigravity/scratch/<project-slug>/` if no workspace is open) with `GEMINI.md` as the sole root agent configuration file:
     ```text
     <project-slug>/
     ├── GEMINI.md                  # Workspace routing & hardware invariants
     ├── spec.md                    # Stage 1: Requirements R1..Rn, SoM trade-off, electrical/thermal math
     ├── hardware/
     │   ├── schematics/            # Stage 2: Code-driven generator + hierarchical .kicad_sch sheets
     │   └── pcb/                   # Stage 3: Programmatic layout script + .kicad_pcb + .dsn/.ses
     ├── fab/                       # Stages 1 & 3: bom.csv, gerbers.zip, cpl.csv, board.step, board.glb
     ├── enclosure/                 # Stage 4: board_sync.json + build123d/CadQuery script + .stl/.3mf
     ├── image/                     # Stage 5: build-image.py, config.txt, device-tree overlays
     └── firmware/                  # Stage 5: fetch-firmware.py, SHA256SUMS, manifest.json, FLASHING.md
     ```
   - **ECAD -> MCAD Tie-Breaker**: ECAD (`hardware/pcb/` and `fab/board.step`) is authoritative for electrical connectivity, board outline, hole locations, connector positions, and component heights. MCAD (`enclosure/`) MUST parse ECAD outputs via [`extract_board_geometry.py`](./scripts/extract_board_geometry.py)—never hardcode magic numbers.
   - **Atomic Gate Reducers**: Never advance to Stage $N+1$ until Stage $N$'s CLI verification gate exits `0`. Apply up to **3 self-healing fix-verify cycles** per gate using structured JSON diagnostics before emitting a Diagnostic Report.

---

## Pre-Flight Environment Check

Before Stage 1, verify local EDA, autorouting, CAD, and checksum tooling:

```bash
bash /Users/malcolm/.gemini/config/skills/autonomous-hardware-architect/scripts/bootstrap_env.sh --check --json
```

If tools are missing and installation is needed, run `bootstrap_env.sh --install` (supports Homebrew `kicad`, `freerouting`, OpenJDK, and isolated `uv`/`pip` venv packages `skidl`, `kicad-skip`, `build123d`, `cadquery`, `trimesh`).

---

## The 5-Stage Closed-Loop Engineering Pipeline

### Stage 1: Specification, Architecture & US-Sourceable BOM (`spec.md` & `fab/bom.csv`)

Read [`references/electrical_math_and_bom.md`](./references/electrical_math_and_bom.md) for exact equations and BOM schema.

1. **Requirements Matrix (`R1`..`Rn`)**: Translate the user prompt into a numbered table in `spec.md` covering Compute, I/O & Connectors, Wireless/RF, Power Architecture, Mechanical Envelope, and OS/Firmware Deliverables, each with a measurable verification target.
2. **Compute Module vs. Chip-Down SoC Trade-Off**:
   - Explicitly compare a pre-certified System-on-Module (e.g., **Raspberry Pi CM5 / CM4**, **ESP32-S3-WROOM-1**, **nRF52840 / nRF54L15 module**, **STM32WB5MMG**) against a chip-down SoC.
   - **Default to pre-certified, mainline-Linux/Zephyr-supported SoMs** to avoid NDA datasheets, unvalidated high-speed DDR4/DDR5 length-matching, and FCC/CE intentional-radiator recertification—unless the user explicitly requests chip-down.
3. **Pre-Schematic Electrical & Thermal Math (`spec.md`)**:
   - **USB-C PD Sink Negotiation**: Calculate `CYPD3177` (or `STUSB4500` / `CH224K`) `VBUS_MIN`, `VBUS_MAX`, `ISNK` configuration resistor dividers and `CC1`/`CC2` $5.1\text{ k}\Omega$ Rd dead-battery pull-downs.
   - **Input Protection**: Size back-to-back P-FETs or ideal-diode controller ($V_{DS}$, $V_{GS}$ clamp, $I_D^2 \cdot R_{DS(\text{on})}$ conduction loss) and bidirectional/unidirectional TVS diode ($V_{RWM} \ge V_{\text{bus,max}}$, clamping $V_C < V_{\text{abs,max}}$ at peak pulse current $I_{PP}$).
   - **Buck / LDO Regulators**: Show exact feedback divider ($V_{\text{out}} = V_{\text{ref}} \cdot (1 + R_{\text{top}}/R_{\text{bot}})$ using standard E96 1% values), UVLO turn-on/turn-off dividers, inductor ripple current $\Delta I_L$ ($20\%\text{--}40\%$ of $I_{\text{out,max}}$), saturation margin $I_{\text{sat}} \ge 1.3 \cdot I_{L,\text{peak}}$, and output capacitor ripple.
   - **Rail Thermal Budget**: Tabulate per-rail current, regulator efficiency $\eta$, power dissipation $P_D$, package $\theta_{JA}$, and junction temperature $T_J = T_A + P_D \cdot \theta_{JA}$ at $T_A = 45\,^\circ\text{C}$.
4. **US-Sourceable BOM (`fab/bom.csv`)**:
   - Select real, active, in-stock manufacturer part numbers (MPNs) stocked at US distributors (**DigiKey**, **Mouser**, **Newark**) plus **LCSC** assembly SKUs where applicable.
   - Record `RefDes,Qty,MPN,Manufacturer,Description,Package_Footprint,Distributor,Distributor_SKU,LCSC_Part,Unit_USD,Lifecycle_Status` in `fab/bom.csv`. Validate with `verify_eda.py --bom fab/bom.csv`.

---

### Stage 2: Code-Driven Hierarchical Schematics (`hardware/schematics/`)

Read [`references/eda_cad_firmware_patterns.md`](./references/eda_cad_firmware_patterns.md) (Section 1) before generating schematic code.

1. **Programmatic Generation Only**:
   - **Never hand-guess raw graphical wire `(x, y)` coordinates in `.kicad_sch` files.**
   - Write a deterministic generator script (`hardware/schematics/generate_schematics.py` or `atopile` / `tscircuit` source) using Python `SKiDL`, `kicad-skip`, `atopile`, or `tscircuit` S-expression/netlist builders.
   - Partition the design into up to **7 clean hierarchical functional sheets** referenced from root `<project>.kicad_sch`:
     1. `01_power_input_protection.kicad_sch` — USB-C / barrel jack, EMI ferrite, TVS clamp, P-FET reverse protection, PD sink controller.
     2. `02_voltage_rails.kicad_sch` — Synchronous buck converters (5 V, 3.3 V) and low-noise LDOs (1.8 V / analog).
     3. `03_compute_core.kicad_sch` — Compute Module (CM5/CM4 B2B connectors) or MCU core, boot switches, WDT, RTC, debug UART/SWD.
     4. `04_high_speed_io_storage.kicad_sch` — USB 2.0/3.0 hubs, Gigabit Ethernet PHY/magnetics, NVMe M.2 / microSD storage, ESD arrays.
     5. `05_rf_embedded_radios.kicad_sch` — Zigbee / Thread / Matter / Wi-Fi / BLE co-processor modules, $\pi$-matching / keepout notes, u.FL / PCB antennas.
     6. `06_audio_sensors_peripherals.kicad_sch` — I2S DAC/codec, MEMS microphone array, environmental sensors, I2C level shifters.
     7. `07_ui_mechanical.kicad_sch` — Addressable RGB / status LEDs, tactile buttons, grounded/isolated M2.5/M3 mounting holes, fiducials.
2. **Mandatory ERC Gate**:
   - Attach explicit `PWR_FLAG` symbols on every non-power-output supply rail (`VBUS`, `+5V`, `+3V3`, `GND`) and explicit no-connect (`no_connect`) markers on intentionally unused pins.
   - Run the verification wrapper until `erc_violations == 0`:
     ```bash
     python3 /Users/malcolm/.gemini/config/skills/autonomous-hardware-architect/scripts/verify_eda.py \
       --sch hardware/schematics/<project>.kicad_sch \
       --bom fab/bom.csv \
       --output hardware/schematics/erc_report.json
     ```

---

### Stage 3: Programmatic PCB Placement, Routing & Fab Pack (`hardware/pcb/` & `fab/`)

Read [`references/eda_cad_firmware_patterns.md`](./references/eda_cad_firmware_patterns.md) (Section 2) before layout and routing.

1. **Deterministic Placement (`hardware/pcb/place_and_route.py`)**:
   - Generate board outline on `Edge.Cuts` with rounded corner radii ($R = 2.0\text{--}4.0\text{ mm}$), M2.5/M3 mounting holes with courtyard keepouts, and RF antenna copper/plane keepout zones **first**.
   - Place **edge-overhang connectors** (USB-C, RJ45, USB-A, HDMI, microSD, SMA/u.FL) flush or overhanging the board perimeter for clean enclosure port access.
   - Cluster sub-circuits spatially by hierarchical schematic sheet; place decoupling capacitors (`100 nF` / `10 uF`) within `< 2.5 mm` of IC power pins on the same copper side, and buck switching loops tight on `F.Cu`.
2. **Headless Autorouting & Copper Pours**:
   - Define net classes: Power (`0.5–1.5 mm` per IPC-2152 current math), Signal (`0.15–0.20 mm`), USB $90\,\Omega$ differential pairs, Ethernet/PCIe $100\,\Omega$ differential pairs, plus continuous `GND` pours on internal/outer layers (`In1.Cu`/`B.Cu`).
   - Export Specctra `.dsn` (`pcbnew.ExportSpecctraDSN`), invoke headless `freerouting` CLI (`java -jar freerouting.jar -de board.dsn -do board.ses -mp 30`), re-import `.ses` (`pcbnew.ImportSpecctraSESSION`), and refill all copper zones.
3. **Mandatory DRC & Manufacturing Pack Gate**:
   - Loop placement nudges, net-class clearances, via stitching, and rerouting until **0 DRC violations and 0 unconnected nets**:
     ```bash
     python3 /Users/malcolm/.gemini/config/skills/autonomous-hardware-architect/scripts/verify_eda.py \
       --sch hardware/schematics/<project>.kicad_sch \
       --pcb hardware/pcb/<project>.kicad_pcb \
       --bom fab/bom.csv \
       --fab-dir fab \
       --output fab/eda_verification.json
     ```
   - Confirm `fab/gerbers.zip` (Gerbers + Excellon drills), `fab/cpl.csv` (pick-and-place centroids), and `fab/board.step` (plus `fab/board.glb` when supported by installed KiCad) are generated and non-empty.

---

### Stage 4: Board-Synced Parametric Enclosure (`enclosure/`)

Read [`references/eda_cad_firmware_patterns.md`](./references/eda_cad_firmware_patterns.md) (Section 3) before modeling CAD.

1. **Extract Exact ECAD Geometry (Zero Magic Numbers)**:
   - Run `extract_board_geometry.py` to parse `hardware/pcb/<project>.kicad_pcb` and `fab/board.step` into `enclosure/board_sync.json`:
     ```bash
     python3 /Users/malcolm/.gemini/config/skills/autonomous-hardware-architect/scripts/extract_board_geometry.py \
       --pcb hardware/pcb/<project>.kicad_pcb \
       --step fab/board.step \
       --output enclosure/board_sync.json
     ```
2. **Parametric CAD Generation (`enclosure/generate_enclosure.py`)**:
   - Using `build123d` (preferred) or `CadQuery`, load `enclosure/board_sync.json` and model a two-piece bottom-tray + top-shell enclosure (screw-boss M2.5/M3 heat-set/self-tap or snap-fit lip):
     - **Perimeter Port Cutouts**: Expand each edge connector's bounding box by **`0.25–0.35 mm` radial print clearance** plus recessed chamfer for plug shrouds.
     - **PCB Standoffs & Bosses**: Align bosses concentrically to `mounting_holes` from `board_sync.json` with bottom-side component clearance ($\ge 3.0\text{ mm}$).
     - **Passive Thermal Louvers**: Cut slotted ventilation grilles directly over `hot_components` coordinates (`CM5`, buck converters, Ethernet PHY).
     - **Status Light-Pipe Openings**: Drill aligned cylindrical apertures (`1.8–2.5 mm`) directly above `leds` coordinates.
   - Export `enclosure/bottom_shell.stl`, `enclosure/top_shell.stl`, `enclosure/assembly.3mf` (and flat-pattern `.dxf` / `.step` sheet-metal variants for SendCutSend if requested).
3. **Mandatory Watertight Manifold & Interference Gate**:
   - Verify all exported meshes are watertight, 2-manifold, positive-volume, and clear of PCB/component bounding-box collisions:
     ```bash
     python3 /Users/malcolm/.gemini/config/skills/autonomous-hardware-architect/scripts/verify_mesh.py \
       --meshes enclosure/bottom_shell.stl enclosure/top_shell.stl enclosure/assembly.3mf \
       --board-sync enclosure/board_sync.json \
       --pcb-step fab/board.step \
       --output enclosure/mesh_verification.json
     ```

---

### Stage 5: Reproducible OS Image & Pinned Firmware Tooling (`image/` & `firmware/`)

Read [`references/eda_cad_firmware_patterns.md`](./references/eda_cad_firmware_patterns.md) (Section 4) before writing firmware scripts.

1. **Deterministic Image & Firmware Tooling**:
   - Author `image/build-image.py` (customizes Raspberry Pi OS / Debian / Buildroot / Yocto image, injects `image/config.txt` and compiled `.dtbo` device-tree overlays matching exact Stage 2 GPIO pin assignments for I2S, I2C, SPI, UART, fan PWM, and LEDs).
   - Author `firmware/fetch-firmware.py` and coprocessor flashers (`rpiboot`, `esptool.py`, `universal-silabs-flasher`, `openocd`, or `dfu-util` wrapper scripts).
2. **Cryptographic Pinning (`firmware/SHA256SUMS`)**:
   - Pin every upstream OS image, bootloader (`usbboot`), and MCU/radio firmware release to an **immutable HTTPS version tag URL** (never `latest` or unpinned branches).
   - Commit exact 64-hex SHA-256 digests in `firmware/SHA256SUMS` and enforce hash verification prior to extraction or flashing.
3. **Mandatory Dry-Run & Bring-Up Gate**:
   - Execute `python3 firmware/fetch-firmware.py --verify-pins --dry-run` and `python3 image/build-image.py --dry-run` in the terminal.
   - Validate `SHA256SUMS` format, emit `firmware/manifest.json` (recording board revision, GPIO map, artifact URLs, SHA-256 digests, and build timestamp), and write a concise `firmware/FLASHING.md` hardware bring-up checklist (smoke-test rail check -> USB-C PD voltage check -> eMMC/MCU flash -> peripheral self-test).

---

## Companion Scripts Reference

| Script | Purpose | Success Exit Criterion |
| :--- | :--- | :--- |
| [`scripts/bootstrap_env.sh`](./scripts/bootstrap_env.sh) | Idempotent check/installer for `kicad-cli`, `freerouting`, Java, `skidl`, `kicad-skip`, `build123d`, `cadquery`, `trimesh`, and checksum utilities | Exits `0` when environment state is reported (`--check`) or provisioned (`--install`) |
| [`scripts/verify_eda.py`](./scripts/verify_eda.py) | Runs `kicad-cli` ERC, DRC, Gerber/Drill zipping, CPL centroid export, 3D STEP/GLB export, and `bom.csv` schema/distributor audit; emits structured JSON remedies | Exits `0` iff `erc_violations == 0`, `drc_violations == 0`, `unconnected_nets == 0`, and BOM/fab exports succeed |
| [`scripts/extract_board_geometry.py`](./scripts/extract_board_geometry.py) | Parses `.kicad_pcb` S-expressions and `.step` geometry into `enclosure/board_sync.json` (outline, holes, edge ports, LEDs, hot ICs) | Exits `0` and writes non-empty `board_sync.json` |
| [`scripts/verify_mesh.py`](./scripts/verify_mesh.py) | Verifies `.stl`/`.3mf` watertight 2-manifold topology, non-degenerate triangles, port clearances, and bounding-box interference vs PCB `.step` / `board_sync.json` | Exits `0` iff all meshes are watertight manifold and `interference_count == 0` |
