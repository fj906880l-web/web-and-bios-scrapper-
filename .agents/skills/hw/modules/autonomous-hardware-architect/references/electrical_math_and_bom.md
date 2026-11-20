# Stage 1 Reference: Pre-Schematic Electrical Math & US-Sourceable BOM

Use these exact engineering formulas and component selection rules when drafting `spec.md` and `fab/bom.csv` in Stage 1. Show all numerical substitutions explicitly before generating any Stage 2 schematic code.

---

## 1. Compute Module vs. Chip-Down SoC Trade-Off Matrix

Always include a comparison table in `spec.md`:

| Criterion | Pre-Certified SoM (Default) | Chip-Down Bare SoC + Discrete RAM/Flash |
| :--- | :--- | :--- |
| **Examples** | Raspberry Pi CM5 / CM4, ESP32-S3-WROOM-1, nRF52840-QIAA module (Raytac MDBT50Q), nRF54L15 module | Broadcom BCM2712, Allwinner/Rockchip BGA + discrete LPDDR4X, bare ESP32-S3FN8 + discrete crystal/RF match |
| **PCB Stackup** | Standard 4-layer JLCPCB/OSH Park (`JLC04161H-7628` or `3313` controlled impedance) | 6–10 layer HDI microvia / blind-buried stackup for 0.4–0.65 mm pitch BGA escape |
| **High-Speed Memory** | Pre-routed & signal-integrity validated on module | Length/skew-matched LPDDR4/DDR4 byte lanes ($\pm 0.1\text{ mm}$) requiring SI simulation |
| **RF Certification** | Modular FCC / IC / CE grant transferable when following antenna trace/keepout guide | Full intentional-radiator lab testing (\$15k–\$40k+) |
| **Linux / RTOS Support** | Mainline Raspberry Pi OS, Debian, Home Assistant OS, ESP-IDF, Zephyr out-of-the-box | Vendor BSP kernel forks, NDA PMIC/DRAM init blobs |

**Decision Rule**: Select the **Pre-Certified SoM** unless the user explicitly requires ultra-miniature form factor (`< 25 x 25 mm`), high-volume BOM cost optimization (`> 10,000 units`), or explicitly specifies a chip-down MCU/SoC (e.g., `RP2350A`, `STM32G431` where internal flash/SRAM eliminates external DDR routing).

---

## 2. Concrete Pre-Schematic Electrical Calculations

### 2.1 USB-C Power Delivery Sink Negotiation (`CYPD3177-24LQXQ` or Equivalent)
- **Dead-Battery CC Pull-Downs**: `CYPD3177` integrates $5.1\text{ k}\Omega$ Rd terminations on `CC1`/`CC2` (do **not** add external $5.1\text{ k}\Omega$ pull-downs in parallel when using an integrated PD sink controller; add ESD diodes such as `TPD4E05U06` or `USBLC6-2SC6` on `CC1`/`CC2`/`D+`/`D-` rated $\ge 24\text{ V}$ on `CC` pins to survive $20\text{ V}$ VBUS-to-CC shorts).
- **CYPD3177 Voltage & Current Configuration Straps** (divider from `VDDD` $3.3\text{ V}$ to `GND`, per Infineon EZ-PD BCR datasheet table):
  - `VBUS_MIN` / `VBUS_MAX` resistor ratios set acceptable PDO window:
    - $5.0\text{ V}$: $R_{\text{up}} = \text{Open},\; R_{\text{dn}} = 0\,\Omega$ (GND)
    - $9.0\text{ V}$: $R_{\text{up}} = 10\text{ k}\Omega,\; R_{\text{dn}} = 1.96\text{ k}\Omega$ ($V_{\text{tap}} \approx 0.54\text{ V}$)
    - $12.0\text{ V}$: $R_{\text{up}} = 10\text{ k}\Omega,\; R_{\text{dn}} = 3.83\text{ k}\Omega$ ($V_{\text{tap}} \approx 0.91\text{ V}$)
    - $15.0\text{ V}$: $R_{\text{up}} = 10\text{ k}\Omega,\; R_{\text{dn}} = 6.81\text{ k}\Omega$ ($V_{\text{tap}} \approx 1.34\text{ V}$)
    - $20.0\text{ V}$: $R_{\text{up}} = 0\,\Omega,\; R_{\text{dn}} = \text{Open}$ (`VDDD`)
  - `ISNK_COARSE` / `ISNK_FINE` set required sink current ($1\text{ A} \dots 5\text{ A}$).
  - Verify `PFET` load-switch gate drive (`VBUS_FET_EN`) drives the input P-FET only after valid PDO contract negotiation.

### 2.2 Input Protection: TVS Clamping & Back-to-Back / Load-Switch P-FETs
1. **TVS Surge Clamp**:
   - Choose working standoff voltage $V_{RWM} \ge 1.10 \cdot V_{\text{bus,max}}$ (e.g., for $20\text{ V}$ PD, $V_{RWM} = 22\text{ V}$ or $24\text{ V}$ such as `SMBJ24CA` / `TPSMB24CA`).
   - Verify maximum clamping voltage $V_C(I_{PP}) < V_{\text{in,abs\_max}}$ of downstream buck converter and P-FET $V_{DS,\max}$ (e.g., `SMBJ24CA` clamps at $V_C = 38.9\text{ V}$ @ $15.5\text{ A}$ $10/1000\,\mu\text{s}$ -> require $60\text{ V}$ buck converter such as `TPS54360B` or `LMR36520` rated to $60\text{ V}\text{--}65\text{ V}$, and $40\text{ V}\text{--}60\text{ V}$ P-FET).
2. **Reverse-Polarity / Inrush P-FET (`DMP4025SSD` / `SQJ401EP` / Ideal Diode `LM74700-Q1`)**:
   - Gate-source Zener clamp ($10\text{ V}\text{--}12\text{ V}$, e.g., `BZT52C12`) + gate resistor ($10\text{ k}\Omega\text{--}47\text{ k}\Omega$) so $|V_{GS}| \le 12\text{ V} < V_{GS,\max}$ ($20\text{ V}$) when $V_{\text{BUS}} = 20\text{ V}$.
   - Conduction power loss:
     $$P_{\text{FET}} = N_{\text{FET}} \cdot I_{\text{in,max}}^2 \cdot R_{DS(\text{on}),\text{hot}}, \quad R_{DS(\text{on}),\text{hot}} \approx 1.4 \cdot R_{DS(\text{on}),25^\circ\text{C}}$$
   - Keep $P_{\text{FET}} < 0.35\text{ W}$ for SO-8 / PowerDI3333 without heatsink.

### 2.3 Synchronous Buck Regulator Math
1. **Feedback Resistor Divider** (using standard E96 1% values):
   $$V_{\text{out}} = V_{\text{ref}} \left(1 + \frac{R_{\text{top}}}{R_{\text{bot}}}\right) \implies R_{\text{top}} = R_{\text{bot}} \left(\frac{V_{\text{out}}}{V_{\text{ref}}} - 1\right)$$
   Compute actual nominal output voltage $V_{\text{out,actual}}$ with chosen E96 values and verify $|\Delta V / V_{\text{out}}| < 1.0\%$.
2. **Input UVLO Divider**:
   $$V_{\text{start}} = V_{\text{EN,rise}}\left(1 + \frac{R_{\text{uv,top}}}{R_{\text{uv,bot}}}\right) + I_{\text{EN,hyst}} \cdot R_{\text{uv,top}}$$
   Ensure $V_{\text{start}}$ is safely below minimum input rail (e.g., $V_{\text{start}} \approx 4.3\text{ V}$ for $5\text{ V}$ fallback or $10.5\text{ V}$ for $12\text{ V}$-minimum PD) and above regulator minimum $V_{\text{IN}}$.
3. **Inductor Value, Ripple Current & Saturation Margin**:
   $$D = \frac{V_{\text{out}}}{V_{\text{in,max}} \cdot \eta}, \quad \Delta I_L = \frac{V_{\text{out}} \cdot (1 - D)}{f_{\text{sw}} \cdot L}, \quad I_{L,\text{peak}} = I_{\text{out,max}} + \frac{\Delta I_L}{2}$$
   Target ripple ratio $r = \Delta I_L / I_{\text{out,max}} \in [0.20, 0.40]$ and choose shielded molded power inductor (e.g., Bourns `SRP` or Vishay `IHLP`) with $I_{\text{sat}} \ge 1.30 \cdot I_{L,\text{peak}}$ and $I_{\text{rms}} \ge 1.20 \cdot I_{\text{out,max}}$.
4. **Output Capacitance & Effective MLCC Derating**:
   - Account for Class-II X5R/X7R DC bias capacitance loss ($40\%\text{--}60\%$ loss at rated DC voltage in 0603/0805 packages; prefer 0805/1206 $25\text{ V}$ or $16\text{ V}$ X7R MLCCs on $5\text{ V}$/$3.3\text{ V}$ rails).
   - Output voltage ripple:
     $$\Delta V_{\text{out}} \approx \Delta I_L \left(\text{ESR} + \frac{1}{8 \cdot f_{\text{sw}} \cdot C_{\text{eff}}}\right) \le 1\% \cdot V_{\text{out}}$$

### 2.4 System Power & Thermal Budget Table
Include a complete rail & thermal rollup table in `spec.md` at ambient $T_A = 45\,^\circ\text{C}$ inside the enclosure:

$$P_{D,\text{buck}} = P_{\text{out}} \left(\frac{1}{\eta} - 1\right), \quad P_{D,\text{LDO}} = (V_{\text{in}} - V_{\text{out}}) \cdot I_{\text{out}}, \quad T_J = T_A + P_D \cdot \theta_{JA}$$

**Hard Gate**: Every component must satisfy $T_J \le 0.85 \cdot T_{J,\max}$ (typically $\le 105\,^\circ\text{C}$ for $125\,^\circ\text{C}$-rated silicon). If any LDO dissipates $> 0.4\text{ W}$ in SOT-23/SOT-223, replace it with a synchronous buck converter.

---

## 3. US-Sourceable BOM Standards (`fab/bom.csv`)

Every line item in `fab/bom.csv` MUST use this exact header schema:

```csv
RefDes,Qty,MPN,Manufacturer,Description,Package_Footprint,Distributor,Distributor_SKU,LCSC_Part,Unit_USD,Lifecycle_Status
```

### Sourcing Guardrails
1. **Authorized US Stock**: Every IC, connector, crystal, inductor, and SoM must be an active MPN stocked by **DigiKey**, **Mouser**, or **Newark** (plus optional **LCSC** C-code for turnkey PCBA).
2. **Zero Placeholders**: Never emit `TBD`, `GENERIC`, `UNKNOWN`, or `N/A` in `MPN`, `Manufacturer`, `Package_Footprint`, or `Distributor_SKU` (for passives where LCSC turnkey assembly is secondary, `LCSC_Part` may hold a valid JLCPCB basic part like `C1525` or `DIRECT_US`).
3. **Footprint-to-KiCad Exact Mapping**: `Package_Footprint` must match a real KiCad standard library or generated project library footprint (e.g., `Capacitor_SMD:C_0603_1608Metric`, `Resistor_SMD:R_0603_1608Metric`, `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12`, `Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm`).
