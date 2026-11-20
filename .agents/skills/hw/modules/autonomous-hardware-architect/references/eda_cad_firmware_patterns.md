# Stages 2–5 Reference: Programmatic EDA, Autorouting, Parametric CAD & Pinned Firmware

Concrete patterns and failure-avoidance rules for Stages 2, 3, 4, and 5.

---

## 1. Stage 2: Code-Driven Hierarchical KiCad Schematics

### Why Code-Driven Schematics Are Mandatory
Hand-editing `.kicad_sch` `(wire (pts (xy ...)))` coordinates causes off-grid pin misses (`1.27 mm` vs `2.54 mm` grid), dangling nets, duplicate UUIDs, and silent short circuits. Always generate schematics programmatically:

- **Option A — KiCad S-Expression AST Builder (`kicad-skip` or pure-Python S-expr generator)**:
  - Read exact symbol pin locations from installed KiCad `.kicad_sym` libraries (`/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/*.kicad_sym` on macOS or `/usr/share/kicad/symbols/*.kicad_sym` on Linux).
  - Compute exact pin world coordinates `(sym_x + rot_x, sym_y - rot_y)` snapped to `1.27 mm` (`50 mil`) grid, attach named `(label "<NET_NAME>" ...)` or `(global_label ...)` / `(hierarchical_label ...)` directly onto each transformed pin endpoint, and emit unique RFC-4122 `uuid` v4 values for every symbol instance, pin, sheet, and net label.
- **Option B — `atopile` (`ato build`) or `SKiDL` (`generate_schematic()` / `generate_netlist()`)**:
  - Partition modules cleanly per functional sheet (`PowerInput`, `VoltageRails`, `ComputeCore`, `HighSpeedIO`, `Radios`, `AudioSensors`, `UIMech`).

### Preventing Common `kicad-cli sch erc` Violations
1. **`power_pin_not_driven`**: KiCad requires every net feeding a `power_in` pin (`GND`, `+3V3`, `+5V`, `VBUS`) to be driven by a `power_out` pin. Regulators whose output pin is typed `passive` (e.g., after an inductor or P-FET drain) will fail ERC unless you connect `power:PWR_FLAG` to that rail and to `GND`.
2. **`pin_not_connected`**: Every unused MCU/SoM/IC pin must carry an explicit `(no_connect (at X Y) (uuid ...))` marker—never leave pins floating.
3. **`multiple_net_names` / `hier_label_mismatch`**: Ensure every `(sheet_pin "NAME" ...)` on the parent root sheet matches a `(hierarchical_label "NAME" ...)` of compatible direction inside the child `.kicad_sch`.
4. **Symbol Footprint & MPN Properties**: Populate `Footprint`, `MPN`, and `Datasheet` properties directly inside each schematic symbol instance so schematic -> PCB sync (`Update PCB from Schematic`) is lossless.

---

## 2. Stage 3: Programmatic PCB Placement, Freerouting & Fab Export

### 2.1 Placement Algorithm (`hardware/pcb/place_and_route.py`)
1. **Board Outline & Keepouts First**:
   - Emit `Edge.Cuts` as a closed loop of 4 straight `gr_line` segments + 4 tangent `gr_arc` corners (e.g., $R = 3.0\text{ mm}$) so endpoints share exact floating-point coordinates to `1e-4 mm` (prevents `malformed_outline` DRC error!).
   - Place M2.5 (`2.7 mm` NPTH/PTH, `5.5 mm` pad/courtyard) or M3 (`3.2 mm` hole, `6.0 mm` pad/courtyard) mounting holes inset `4.0–5.0 mm` from board edges.
   - Add `(zone ... (keepout (tracks not_allowed) (vias not_allowed) (copperpour not_allowed)))` across all layers beneath PCB/chip antennas (ESP32/nRF/u.FL edge region).
2. **Perimeter Connector Placement**:
   - Place external I/O connectors along designated edges (`SOUTH` / `NORTH` / `WEST` / `EAST`) with datasheet overhang (e.g., USB-C mid-mount/top-mount lip `0.8–1.5 mm` past `Edge.Cuts`, RJ45 LED front face flush with `Edge.Cuts`).
   - Tag connector footprints or courtyard metadata clearly so `extract_board_geometry.py` detects exact port openings.
3. **Sub-Circuit Clustering & Decoupling Adjacency**:
   - Place SoM/MCU near board center; place buck inductor + input/output MLCCs within `< 3.0 mm` of buck `SW`/`VIN`/`GND` pins; place every `100 nF` bypass capacitor `< 2.5 mm` from its target IC `VDD` pin.

### 2.2 Headless Autorouting Loop (`freerouting`)
```bash
# 1. Export Specctra DSN via KiCad Python API (pcbnew)
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
  -c "import pcbnew; b=pcbnew.LoadBoard('hardware/pcb/board.kicad_pcb'); pcbnew.ExportSpecctraDSN(b, 'hardware/pcb/board.dsn')"

# 2. Run headless Freerouting CLI
java -Djava.awt.headless=true -jar "${FREEROUTING_JAR}" \
  -de hardware/pcb/board.dsn \
  -do hardware/pcb/board.ses \
  -mp 30

# 3. Re-import Specctra SES & refill copper pours
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
  -c "import pcbnew; b=pcbnew.LoadBoard('hardware/pcb/board.kicad_pcb'); pcbnew.ImportSpecctraSESSION(b, 'hardware/pcb/board.ses'); f=pcbnew.ZONE_FILLER(b); f.Fill(b.Zones()); pcbnew.SaveBoard('hardware/pcb/board.kicad_pcb', b)"
```

### 2.3 DRC Self-Healing Rules
- **`clearance` / `track_width`**: Widen spacing around high-voltage (`20 V VBUS` -> `>= 0.25 mm` clearance) or shrink BGA/QFN neck-down trace width to fab capability (`0.127 mm` / `5 mil` min track/space for standard 4-layer JLCPCB).
- **`unconnected_items`**: Add `GND` stitching vias (`0.3 mm` drill / `0.6 mm` pad) near isolated ground islands, or slightly spread congested connector fanout components by `0.5–1.0 mm` and re-run `freerouting`.
- **`silk_over_copper` / `silk_overlap`**: Move `RefDes` silkscreen labels outside pad/solder-mask openings or disable fab-only overlapping labels before final Gerber export.

---

## 3. Stage 4: Board-Synced Parametric Enclosure (`build123d` / `CadQuery`)

### Consuming `enclosure/board_sync.json`
Never duplicate `WIDTH = 100.0` in Python CAD files. Always load `board_sync.json` generated by `scripts/extract_board_geometry.py`:

```python
import json
from pathlib import Path
from build123d import (
    Align, Axis, Box, BuildPart, BuildSketch, Circle, Cylinder,
    FilletPolyline, Locations, Mode, Plane, RectangleRounded,
    export_mesher, export_stl, Mesher,
)

sync = json.loads(Path("enclosure/board_sync.json").read_text())
pcb_w = sync["board"]["width_mm"]
pcb_h = sync["board"]["height_mm"]
pcb_t = sync["board"]["thickness_mm"]
wall = 2.4          # 6 perimeters @ 0.4 mm nozzle
board_gap = 0.5     # XY clearance around PCB perimeter
port_tol = 0.30     # 0.25-0.35 mm radial port clearance
standoff_h = max(3.5, sync["board"]["max_bottom_component_height_mm"] + 1.0)
inner_h = standoff_h + pcb_t + sync["board"]["max_top_component_height_mm"] + 2.5
```

### Mandatory Mechanical Features
1. **Bottom Shell (`bottom_shell.stl`)**:
   - Outer filleted shell (`pcb_w + 2*(board_gap + wall)`, `pcb_h + 2*(board_gap + wall)`).
   - Integral PCB standoffs at exact `(hole["x_rel_center_mm"], hole["y_rel_center_mm"])` coordinates with pilot bores (`2.2 mm` for M2.5 self-tap or `3.6 mm` for M2.5 heat-set brass insert) + recessed counterbores on exterior floor if using through-screws.
   - Perimeter alignment lip (`1.2 mm` wide, `1.5 mm` tall, `0.20 mm` radial mating clearance between top and bottom shells).
2. **Top Shell (`top_shell.stl`)**:
   - Port cutouts subtracted on matching `NORTH`/`SOUTH`/`EAST`/`WEST` walls using `(port["width_mm"] + 2*port_tol)` by `(port["height_mm"] + 2*port_tol)` positioned at `z = floor_t + standoff_h + pcb_t + port["z_offset_mm"]`.
   - Passive ventilation louvers (`2.0 mm` wide x `14.0 mm` slots on `4.0 mm` pitch) centered above every entry in `sync["hot_components"]`.
   - Light-pipe cylindrical holes (`2.0 mm` diameter) directly above every entry in `sync["leds"]`.
   - Screw-boss mating pillars descending from top ceiling to `0.2 mm` above PCB top copper around mounting holes.
3. **Export**:
   - Export `bottom_shell.stl`, `top_shell.stl`, and multi-body `assembly.3mf` (`Mesher` in `build123d`).
   - If the user requests sheet metal (SendCutSend), generate flat-pattern `.dxf` + bent `.step` using uniform sheet gauge (`1.5 mm` 5052-H32 aluminum, inside bend radius $R_{\text{bend}} = 1.5\text{ mm}$, $K = 0.38$).

---

## 4. Stage 5: Reproducible OS Image & Pinned Firmware Bring-Up

### Required Files
1. `firmware/SHA256SUMS`: Standard GNU coreutils format (`<64-hex-sha256>  <filename>`). Every remote artifact URL in `fetch-firmware.py` and `build-image.py` must be pinned to an immutable release tag/version (e.g., `https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2025-05-13/2025-05-13-raspios-bookworm-arm64-lite.img.xz`) and cross-checked against `SHA256SUMS`.
2. `image/config.txt` & `image/overlays/<board>-overlay.dts`: Map exact GPIO numbers from Stage 2 (`dtoverlay=i2s-mmap`, `dtparam=i2c_arm=on`, `dtoverlay=uart2`, custom GPIO LEDs/buttons/reset lines).
3. `image/build-image.py`: Supports `--dry-run` (validates `config.txt`, device-tree syntax, pin conflict checks against schematic GPIO map, and `SHA256SUMS` integrity without requiring root `losetup`/`mount`, emitting `firmware/manifest.json`).
4. `firmware/fetch-firmware.py`: Supports `--verify-pins` and `--dry-run` (confirms HTTPS-only URLs, immutable version tags, matching entries in `SHA256SUMS`, and verifies downloaded blobs in quarantine before moving into `firmware/blobs/`).
5. `firmware/FLASHING.md`: Step-by-step bench bring-up guide:
   - Visual inspection & multimeter continuity/resistance check across `VBUS`, `+5V`, `+3V3`, `GND` before applying power.
   - Current-limited bench supply / USB-C PD negotiation check (`20 V` / `12 V` / `5 V` test points).
   - Boot-mode jumper (`nRPIBOOT` / `BOOT0`) + exact flash command (`rpiboot`, `bmaptool` / `dd`, `esptool.py`, or `universal-silabs-flasher`).
   - First-boot SSH/serial health check verifying I2C bus scan (`i2cdetect -y 1`), audio (`aplay -l` / `arecord -l`), Ethernet link, and radio coprocessor enumeration.
