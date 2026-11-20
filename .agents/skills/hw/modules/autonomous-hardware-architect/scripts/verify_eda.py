#!/usr/bin/env python3
"""verify_eda.py — Closed-Loop KiCad ERC, DRC, BOM & Manufacturing Pack Verifier.

Wraps `kicad-cli` for schematic ERC, PCB DRC (including unconnected net verification),
Gerber + Excellon drill packaging (`gerbers.zip`), centroid CPL export (`cpl.csv`),
and 3D `.step`/`.glb` export, returning structured JSON diagnostics with actionable
remediation hints for autonomous self-healing loops.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

PLACEHOLDER_TOKENS = {"TBD", "TODO", "UNKNOWN", "GENERIC", "N/A", "NONE", "PLACEHOLDER", "XXX"}
VALID_US_DISTRIBUTORS = {"DIGIKEY", "DIGI-KEY", "MOUSER", "NEWARK", "ARROW", "AVNET", "VERICAL"}
REQUIRED_BOM_COLUMNS = {
    "RefDes",
    "Qty",
    "MPN",
    "Manufacturer",
    "Description",
    "Package_Footprint",
    "Distributor",
    "Distributor_SKU",
}

ERC_REMEDIATION_MAP: dict[str, str] = {
    "power_pin_not_driven": (
        "Attach a `power:PWR_FLAG` symbol to this power net and to `GND` so KiCad sees an explicit power driver."
    ),
    "pin_not_connected": (
        "Wire the pin to its intended net or place an explicit `(no_connect (at X Y))` marker on unused pins."
    ),
    "pin_to_pin": (
        "Two output or power_out pins are shorted on the same net; insert isolation/series element or fix symbol pin type."
    ),
    "hier_label_mismatch": (
        "Ensure every `(sheet_pin ...)` on the parent schematic has an exact matching `(hierarchical_label ...)` in the child sheet."
    ),
    "multiple_net_names": (
        "Two different net labels touch the same wire segment; unify the net name across connected labels."
    ),
    "lib_symbol_issues": (
        "Embedded schematic symbol definition differs from library or is missing; re-embed clean symbol definition from KiCad `.kicad_sym`."
    ),
    "footprint_link_issues": (
        "Assign a valid `Library:Footprint` string in the symbol `Footprint` property matching installed KiCad `.pretty` libraries."
    ),
}

DRC_REMEDIATION_MAP: dict[str, str] = {
    "clearance": (
        "Increase spacing between offending copper items, narrow trace width to net-class minimum, or pull back copper pour clearance."
    ),
    "track_width": (
        "Increase trace width to meet or exceed board minimum (`>= 0.127 mm` for standard 4-layer fab) and net-class current rule."
    ),
    "via_annular_width": (
        "Increase via pad diameter (e.g., `0.60 mm` pad for `0.30 mm` drill) to satisfy annular ring minimum."
    ),
    "hole_clearance": (
        "Move traces/vias away from NPTH/mounting drill holes by at least `0.25-0.35 mm`."
    ),
    "malformed_outline": (
        "Ensure `Edge.Cuts` forms a single closed loop with exact shared endpoint coordinates (`<= 1e-4 mm` gap) and zero self-intersections."
    ),
    "courtyard_overlap": (
        "Separate overlapping component footprints so `F.CrtYd` / `B.CrtYd` polygons have `>= 0.15 mm` gap."
    ),
    "silk_over_copper": (
        "Move `RefDes` silkscreen text outside exposed solder-mask/pad openings or enable `subtract_mask_from_silk` during Gerber plot."
    ),
    "unconnected_items": (
        "Add `GND` stitching vias for isolated pour islands, spread congested pads by `0.5 mm`, and re-run `freerouting` + zone refill."
    ),
    "starved_thermal": (
        "Widen zone thermal spokes or shift adjacent vias obstructing copper pour connection to the pad."
    ),
}


def find_kicad_cli(explicit_path: str | None = None) -> str | None:
    if explicit_path:
        p = Path(explicit_path)
        return str(p) if p.is_file() else None
    which_hit = shutil.which("kicad-cli")
    if which_hit:
        return which_hit
    mac_default = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
    if mac_default.is_file():
        return str(mac_default)
    return None


def run_cmd(cmd: list[str], timeout_sec: int = 180) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def format_item_pos(item: dict[str, Any]) -> dict[str, Any]:
    pos = item.get("pos") or {}
    return {
        "description": item.get("description", ""),
        "uuid": item.get("uuid", ""),
        "x_mm": pos.get("x"),
        "y_mm": pos.get("y"),
    }


def parse_erc_payload(payload: dict[str, Any], ignore_warnings: bool = False) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    sheets = payload.get("sheets")
    if not isinstance(sheets, list):
        # Some kicad-cli versions place violations at top level
        sheets = [{"path": "/", "violations": payload.get("violations", [])}]

    for sheet in sheets:
        sheet_path = sheet.get("path", "/")
        for v in sheet.get("violations", []):
            sev = str(v.get("severity", "error")).lower()
            if sev == "excluded":
                continue
            v_type = str(v.get("type", "unknown"))
            entry = {
                "sheet": sheet_path,
                "type": v_type,
                "severity": sev,
                "description": v.get("description", ""),
                "items": [format_item_pos(it) for it in v.get("items", [])],
                "remediation_hint": ERC_REMEDIATION_MAP.get(
                    v_type,
                    "Inspect net connectivity and symbol pin electrical types in the schematic generator script.",
                ),
            }
            if sev == "warning" and ignore_warnings:
                warnings.append(entry)
            elif sev == "warning":
                warnings.append(entry)
                violations.append(entry)
            else:
                violations.append(entry)

    return {
        "erc_violation_count": len(violations),
        "erc_warning_count": len(warnings),
        "violations": violations,
    }


def parse_drc_payload(payload: dict[str, Any], ignore_warnings: bool = True) -> dict[str, Any]:
    drc_errors: list[dict[str, Any]] = []
    drc_warnings: list[dict[str, Any]] = []
    unconnected: list[dict[str, Any]] = []

    for v in payload.get("violations", []) + payload.get("schematic_parity", []):
        sev = str(v.get("severity", "error")).lower()
        if sev == "excluded":
            continue
        v_type = str(v.get("type", "unknown"))
        entry = {
            "type": v_type,
            "severity": sev,
            "description": v.get("description", ""),
            "items": [format_item_pos(it) for it in v.get("items", [])],
            "remediation_hint": DRC_REMEDIATION_MAP.get(
                v_type,
                "Adjust component placement, trace width/clearance, or copper zone settings and re-run DRC.",
            ),
        }
        if sev == "warning":
            drc_warnings.append(entry)
            if not ignore_warnings:
                drc_errors.append(entry)
        else:
            drc_errors.append(entry)

    for u in payload.get("unconnected_items", []):
        sev = str(u.get("severity", "error")).lower()
        if sev == "excluded":
            continue
        unconnected.append({
            "type": "unconnected_items",
            "severity": sev,
            "description": u.get("description", "Unconnected net between pads"),
            "items": [format_item_pos(it) for it in u.get("items", [])],
            "remediation_hint": DRC_REMEDIATION_MAP["unconnected_items"],
        })

    return {
        "drc_violation_count": len(drc_errors),
        "drc_warning_count": len(drc_warnings),
        "unconnected_net_count": len(unconnected),
        "violations": drc_errors,
        "warnings": drc_warnings,
        "unconnected_nets": unconnected,
    }


def verify_bom_csv(bom_path: Path) -> dict[str, Any]:
    if not bom_path.is_file():
        return {
            "valid": False,
            "line_count": 0,
            "errors": [f"BOM file not found: {bom_path}"],
        }

    errors: list[str] = []
    line_count = 0
    with bom_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing_cols = sorted(REQUIRED_BOM_COLUMNS - headers)
        if missing_cols:
            return {
                "valid": False,
                "line_count": 0,
                "errors": [f"BOM missing required columns: {', '.join(missing_cols)}"],
            }

        for idx, row in enumerate(reader, start=2):
            line_count += 1
            ref = (row.get("RefDes") or "").strip()
            mpn = (row.get("MPN") or "").strip()
            mfr = (row.get("Manufacturer") or "").strip()
            fp = (row.get("Package_Footprint") or "").strip()
            dist = (row.get("Distributor") or "").strip()
            sku = (row.get("Distributor_SKU") or "").strip()
            qty_raw = (row.get("Qty") or "0").strip()
            lifecycle = (row.get("Lifecycle_Status") or "Active").strip()

            if not ref:
                errors.append(f"Row {idx}: Empty RefDes.")
            for field_name, val in (
                ("MPN", mpn),
                ("Manufacturer", mfr),
                ("Package_Footprint", fp),
                ("Distributor_SKU", sku),
            ):
                if not val or val.upper() in PLACEHOLDER_TOKENS:
                    errors.append(f"Row {idx} ({ref or 'no-ref'}): Invalid or placeholder {field_name}='{val}'.")

            try:
                if int(qty_raw) <= 0:
                    errors.append(f"Row {idx} ({ref}): Qty must be >= 1, got '{qty_raw}'.")
            except ValueError:
                errors.append(f"Row {idx} ({ref}): Non-integer Qty '{qty_raw}'.")

            dist_tokens = {tok.strip().upper() for tok in dist.replace("/", ",").split(",") if tok.strip()}
            if not (dist_tokens & VALID_US_DISTRIBUTORS):
                errors.append(
                    f"Row {idx} ({ref}): Distributor '{dist}' is not an authorized US distributor "
                    f"({', '.join(sorted(VALID_US_DISTRIBUTORS))})."
                )

            if any(bad in lifecycle.upper() for bad in ("OBSOLETE", "NRND", "EOL")):
                errors.append(f"Row {idx} ({ref}): Disallowed component lifecycle '{lifecycle}' for MPN '{mpn}'.")

    if line_count == 0:
        errors.append("BOM contains 0 component rows.")

    return {
        "valid": len(errors) == 0,
        "line_count": line_count,
        "errors": errors,
    }


def export_fab_pack(kicad_cli: str, pcb_path: Path, fab_dir: Path) -> dict[str, Any]:
    fab_dir.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, str | None] = {
        "gerbers_zip": None,
        "cpl_csv": None,
        "board_step": None,
        "board_glb": None,
    }
    errors: list[str] = []

    with tempfile.TemporaryDirectory(prefix="gerbers_") as tmp_gerb_str:
        tmp_gerb = Path(tmp_gerb_str)
        gerb_cmd = [
            kicad_cli,
            "pcb",
            "export",
            "gerbers",
            "--layers",
            "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
            "--subtract-soldermask",
            "-o",
            str(tmp_gerb) + "/",
            str(pcb_path),
        ]
        rc_g, _, err_g = run_cmd(gerb_cmd)
        if rc_g != 0:
            errors.append(f"Gerber export failed (rc={rc_g}): {err_g}")

        drill_cmd = [
            kicad_cli,
            "pcb",
            "export",
            "drill",
            "--format",
            "excellon",
            "--excellon-units",
            "mm",
            "-o",
            str(tmp_gerb) + "/",
            str(pcb_path),
        ]
        rc_d, _, err_d = run_cmd(drill_cmd)
        if rc_d != 0:
            errors.append(f"Drill export failed (rc={rc_d}): {err_d}")

        exported_files = sorted(p for p in tmp_gerb.iterdir() if p.is_file())
        if exported_files and rc_g == 0 and rc_d == 0:
            gerbers_zip = fab_dir / "gerbers.zip"
            with zipfile.ZipFile(gerbers_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for fpath in exported_files:
                    zf.write(fpath, arcname=fpath.name)
            artifacts["gerbers_zip"] = str(gerbers_zip.resolve())
        elif not exported_files:
            errors.append("Gerber/drill export produced zero output files.")

    cpl_csv = fab_dir / "cpl.csv"
    rc_pos, _, err_pos = run_cmd([
        kicad_cli,
        "pcb",
        "export",
        "pos",
        "--format",
        "csv",
        "--units",
        "mm",
        "--side",
        "both",
        "-o",
        str(cpl_csv),
        str(pcb_path),
    ])
    if rc_pos == 0 and cpl_csv.is_file():
        artifacts["cpl_csv"] = str(cpl_csv.resolve())
    else:
        errors.append(f"CPL position export failed (rc={rc_pos}): {err_pos}")

    step_file = fab_dir / "board.step"
    rc_step, _, err_step = run_cmd([
        kicad_cli,
        "pcb",
        "export",
        "step",
        "--subst-models",
        "--force",
        "-o",
        str(step_file),
        str(pcb_path),
    ])
    if rc_step == 0 and step_file.is_file():
        artifacts["board_step"] = str(step_file.resolve())
    else:
        errors.append(f"STEP 3D export failed (rc={rc_step}): {err_step}")

    # Optional GLB export (supported in KiCad 8+)
    glb_file = fab_dir / "board.glb"
    rc_glb, _, _ = run_cmd([
        kicad_cli,
        "pcb",
        "export",
        "glb",
        "--subst-models",
        "--force",
        "-o",
        str(glb_file),
        str(pcb_path),
    ])
    if rc_glb == 0 and glb_file.is_file():
        artifacts["board_glb"] = str(glb_file.resolve())

    return {
        "ok": len(errors) == 0,
        "artifacts": artifacts,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run kicad-cli ERC, DRC, BOM verification, and Gerber/CPL/STEP exports with JSON self-healing output."
    )
    parser.add_argument("--sch", type=Path, default=None, help="Root .kicad_sch schematic file")
    parser.add_argument("--pcb", type=Path, default=None, help="Target .kicad_pcb board file")
    parser.add_argument("--bom", type=Path, default=None, help="Path to fab/bom.csv for US-sourcing validation")
    parser.add_argument("--fab-dir", type=Path, default=None, help="Output directory for gerbers.zip, cpl.csv, board.step")
    parser.add_argument("--kicad-cli", type=str, default=None, help="Explicit path to kicad-cli binary")
    parser.add_argument("--erc-json", type=Path, default=None, help="Parse an existing KiCad ERC JSON report")
    parser.add_argument("--drc-json", type=Path, default=None, help="Parse an existing KiCad DRC JSON report")
    parser.add_argument("--strict-warnings", action="store_true", help="Treat ERC/DRC warnings as blocking violations")
    parser.add_argument("--output", type=Path, default=None, help="Write structured JSON report to file")
    args = parser.parse_args()

    if not any([args.sch, args.pcb, args.bom, args.erc_json, args.drc_json]):
        parser.error("Provide at least one of --sch, --pcb, --bom, --erc-json, or --drc-json.")

    kicad_cli = find_kicad_cli(args.kicad_cli)
    missing_tools: list[str] = []
    overall_ok = True

    report: dict[str, Any] = {
        "ok": True,
        "kicad_cli": kicad_cli,
        "missing_tools": missing_tools,
        "erc": None,
        "drc": None,
        "bom": None,
        "fab_export": None,
    }

    # 1. BOM Validation
    if args.bom is not None:
        bom_res = verify_bom_csv(args.bom)
        report["bom"] = bom_res
        if not bom_res["valid"]:
            overall_ok = False

    # 2. ERC Verification
    if args.erc_json is not None:
        payload = json.loads(args.erc_json.read_text(encoding="utf-8"))
        erc_res = parse_erc_payload(payload, ignore_warnings=not args.strict_warnings)
        report["erc"] = erc_res
        if erc_res["erc_violation_count"] > 0:
            overall_ok = False
    elif args.sch is not None:
        if not args.sch.is_file():
            report["erc"] = {"erc_violation_count": 1, "errors": [f"Schematic file not found: {args.sch}"]}
            overall_ok = False
        elif not kicad_cli:
            missing_tools.append("kicad-cli")
            report["erc"] = {
                "erc_violation_count": -1,
                "errors": ["kicad-cli not installed; run `bash scripts/bootstrap_env.sh --install`."],
            }
            overall_ok = False
        else:
            with tempfile.NamedTemporaryFile(suffix=".erc.json", delete=False) as tf:
                tmp_erc = Path(tf.name)
            try:
                rc, stdout_s, stderr_s = run_cmd([
                    kicad_cli,
                    "sch",
                    "erc",
                    "--format",
                    "json",
                    "--exit-code-violations",
                    "-o",
                    str(tmp_erc),
                    str(args.sch),
                ])
                if tmp_erc.is_file() and tmp_erc.stat().st_size > 0:
                    payload = json.loads(tmp_erc.read_text(encoding="utf-8"))
                    erc_res = parse_erc_payload(payload, ignore_warnings=not args.strict_warnings)
                    erc_res["exit_code"] = rc
                    report["erc"] = erc_res
                    if erc_res["erc_violation_count"] > 0 or rc not in (0, 5):
                        if erc_res["erc_violation_count"] > 0 or rc != 0:
                            overall_ok = False
                else:
                    report["erc"] = {
                        "erc_violation_count": 1,
                        "exit_code": rc,
                        "errors": [stderr_s or stdout_s or "kicad-cli sch erc failed to emit JSON"],
                    }
                    overall_ok = False
            finally:
                tmp_erc.unlink(missing_ok=True)

    # 3. DRC Verification & Fab Export
    if args.drc_json is not None:
        payload = json.loads(args.drc_json.read_text(encoding="utf-8"))
        drc_res = parse_drc_payload(payload, ignore_warnings=not args.strict_warnings)
        report["drc"] = drc_res
        if drc_res["drc_violation_count"] > 0 or drc_res["unconnected_net_count"] > 0:
            overall_ok = False
    elif args.pcb is not None:
        if not args.pcb.is_file():
            report["drc"] = {"drc_violation_count": 1, "unconnected_net_count": 0, "errors": [f"PCB not found: {args.pcb}"]}
            overall_ok = False
        elif not kicad_cli:
            if "kicad-cli" not in missing_tools:
                missing_tools.append("kicad-cli")
            report["drc"] = {
                "drc_violation_count": -1,
                "unconnected_net_count": -1,
                "errors": ["kicad-cli not installed; run `bash scripts/bootstrap_env.sh --install`."],
            }
            overall_ok = False
        else:
            with tempfile.NamedTemporaryFile(suffix=".drc.json", delete=False) as tf:
                tmp_drc = Path(tf.name)
            try:
                rc, stdout_s, stderr_s = run_cmd([
                    kicad_cli,
                    "pcb",
                    "drc",
                    "--format",
                    "json",
                    "--schematic-parity",
                    "--exit-code-violations",
                    "-o",
                    str(tmp_drc),
                    str(args.pcb),
                ])
                if tmp_drc.is_file() and tmp_drc.stat().st_size > 0:
                    payload = json.loads(tmp_drc.read_text(encoding="utf-8"))
                    drc_res = parse_drc_payload(payload, ignore_warnings=not args.strict_warnings)
                    drc_res["exit_code"] = rc
                    report["drc"] = drc_res
                    if drc_res["drc_violation_count"] > 0 or drc_res["unconnected_net_count"] > 0:
                        overall_ok = False
                else:
                    report["drc"] = {
                        "drc_violation_count": 1,
                        "unconnected_net_count": 0,
                        "exit_code": rc,
                        "errors": [stderr_s or stdout_s or "kicad-cli pcb drc failed to emit JSON"],
                    }
                    overall_ok = False
            finally:
                tmp_drc.unlink(missing_ok=True)

            # Export Fab Pack only when DRC + Unconnected pass cleanly
            if args.fab_dir is not None and overall_ok:
                fab_res = export_fab_pack(kicad_cli, args.pcb, args.fab_dir)
                report["fab_export"] = fab_res
                if not fab_res["ok"]:
                    overall_ok = False

    report["ok"] = overall_ok
    rendered = json.dumps(report, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
