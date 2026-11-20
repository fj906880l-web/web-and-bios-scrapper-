#!/usr/bin/env python3
"""extract_board_geometry.py — Deterministic ECAD-to-MCAD Geometry Sync Parser.

Parses KiCad `.kicad_pcb` S-expressions and optional `.step` models into a single
`board_sync.json` contract for Stage 4 parametric enclosure generation (`build123d` /
`CadQuery`), eliminating hardcoded mechanical magic numbers.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Union

SExpr = Union[str, list["SExpr"]]


def tokenize_sexpr(text: str) -> list[str]:
    """Tokenize a KiCad S-expression file without regex backtracking or eval."""
    tokens: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch in ("(", ")"):
            tokens.append(ch)
            i += 1
        elif ch == '"':
            buf = ['"']
            i += 1
            while i < n:
                c = text[i]
                if c == "\\" and i + 1 < n:
                    buf.append(text[i + 1])
                    i += 2
                    continue
                buf.append(c)
                i += 1
                if c == '"':
                    break
            tokens.append("".join(buf))
        else:
            start = i
            while i < n and (not text[i].isspace()) and text[i] not in ("(", ")"):
                i += 1
            tokens.append(text[start:i])
    return tokens


def parse_sexpr(text: str) -> SExpr:
    """Parse tokenized KiCad S-expression into nested Python lists."""
    tokens = tokenize_sexpr(text)
    stack: list[list[SExpr]] = [[]]
    for tok in tokens:
        if tok == "(":
            new_list: list[SExpr] = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif tok == ")":
            if len(stack) == 1:
                raise ValueError("Unbalanced closing parenthesis in .kicad_pcb")
            stack.pop()
        else:
            if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"':
                stack[-1].append(tok[1:-1])
            else:
                stack[-1].append(tok)
    if len(stack) != 1 or not stack[0]:
        raise ValueError("Invalid or incomplete S-expression in .kicad_pcb")
    return stack[0][0]


def find_children(node: SExpr, tag: str) -> list[list[SExpr]]:
    if not isinstance(node, list):
        return []
    return [
        child for child in node[1:]
        if isinstance(child, list) and len(child) > 0 and child[0] == tag
    ]


def find_first(node: SExpr, tag: str) -> list[SExpr] | None:
    matches = find_children(node, tag)
    return matches[0] if matches else None


def as_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def parse_step_bounds(step_path: Path) -> dict[str, float] | None:
    """Extract global X/Y/Z CARTESIAN_POINT bounds from an ISO-10303-21 STEP file."""
    if not step_path.is_file():
        return None
    content = step_path.read_text(encoding="utf-8", errors="ignore")
    scale = 25.4 if "INCH" in content[:4000].upper() and "MILLI" not in content[:4000].upper() else 1.0
    pt_re = re.compile(
        r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*,\s*"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*,\s*"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*\)\s*\)"
    )
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for match in pt_re.finditer(content):
        xs.append(float(match.group(1)) * scale)
        ys.append(float(match.group(2)) * scale)
        zs.append(float(match.group(3)) * scale)
    if not xs:
        return None
    return {
        "min_x_mm": round(min(xs), 4),
        "max_x_mm": round(max(xs), 4),
        "min_y_mm": round(min(ys), 4),
        "max_y_mm": round(max(ys), 4),
        "min_z_mm": round(min(zs), 4),
        "max_z_mm": round(max(zs), 4),
        "span_x_mm": round(max(xs) - min(xs), 4),
        "span_y_mm": round(max(ys) - min(ys), 4),
        "span_z_mm": round(max(zs) - min(zs), 4),
    }


def estimate_component_height(fp_lib_id: str, ref: str, value: str) -> float:
    """Fallback physical Z-height lookup (mm) when footprint property Height is unset."""
    key = f"{fp_lib_id} {ref} {value}".upper()
    if "RJ45" in key:
        return 13.5
    if "USB_A" in key or "USB-A" in key:
        return 7.2
    if "USB_C" in key or "TYPE-C" in key:
        return 3.26
    if "HDMI" in key:
        return 6.2
    if "AUDIO" in key or "JACK" in key:
        return 5.0
    if "CM5" in key or "CM4" in key or "COMPUTE_MODULE" in key:
        return 4.7
    if "ESP32" in key or "WROOM" in key or "NRF52" in key or "MDBT" in key:
        return 3.2
    if "INDUCTOR" in key or "SRP" in key or "IHLP" in key or ref.upper().startswith("L"):
        return 4.0
    if "TACT" in key or "SW_" in key or ref.upper().startswith("SW"):
        return 4.3
    if "LED" in key or ref.upper().startswith("D"):
        return 1.2
    return 1.8


def extract_footprint_property(fp_node: list[SExpr], prop_name: str) -> str:
    """Read KiCad 7/8 `property` or KiCad 6 `fp_text` values from a footprint node."""
    for prop in find_children(fp_node, "property"):
        if len(prop) >= 3 and str(prop[1]).lower() == prop_name.lower():
            return str(prop[2])
    for txt in find_children(fp_node, "fp_text"):
        if len(txt) >= 3 and str(txt[1]).lower() == prop_name.lower():
            return str(txt[2])
    return ""


def compute_footprint_local_bbox(fp_node: list[SExpr]) -> tuple[float, float, float, float]:
    """Compute local footprint courtyard/silkscreen/pad bounding box (min_x, max_x, min_y, max_y)."""
    xs: list[float] = []
    ys: list[float] = []
    preferred_layers = {"F.CrtYd", "B.CrtYd", "F.Fab", "B.Fab"}
    for tag in ("fp_rect", "fp_line"):
        for item in find_children(fp_node, tag):
            layer_node = find_first(item, "layer")
            layer_name = str(layer_node[1]) if layer_node and len(layer_node) > 1 else ""
            if preferred_layers and layer_name and layer_name not in preferred_layers:
                continue
            for pt_tag in ("start", "end"):
                pt = find_first(item, pt_tag)
                if pt and len(pt) >= 3:
                    xs.append(as_float(pt[1]))
                    ys.append(as_float(pt[2]))
    if not xs:
        for pad in find_children(fp_node, "pad"):
            at = find_first(pad, "at")
            sz = find_first(pad, "size")
            if at and len(at) >= 3:
                px, py = as_float(at[1]), as_float(at[2])
                pw = as_float(sz[1], 1.0) if sz and len(sz) >= 3 else 1.0
                ph = as_float(sz[2], 1.0) if sz and len(sz) >= 3 else 1.0
                xs.extend([px - pw / 2.0, px + pw / 2.0])
                ys.extend([py - ph / 2.0, py + ph / 2.0])
    if not xs:
        return (-1.0, 1.0, -1.0, 1.0)
    return (min(xs), max(xs), min(ys), max(ys))


def rotate_bbox(
    min_x: float, max_x: float, min_y: float, max_y: float, deg: float
) -> tuple[float, float, float, float]:
    rad = math.radians(-deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    corners = [(min_x, min_y), (min_x, max_y), (max_x, min_y), (max_x, max_y)]
    rxs = [cx * cos_a - cy * sin_a for cx, cy in corners]
    rys = [cx * sin_a + cy * cos_a for cx, cy in corners]
    return (min(rxs), max(rxs), min(rys), max(rys))


def parse_kicad_pcb(pcb_path: Path, step_path: Path | None = None) -> dict[str, Any]:
    tree = parse_sexpr(pcb_path.read_text(encoding="utf-8"))
    if not isinstance(tree, list) or not tree or tree[0] != "kicad_pcb":
        raise ValueError(f"{pcb_path} is not a valid kicad_pcb S-expression")

    # 1. Board thickness
    thickness_mm = 1.6
    general = find_first(tree, "general")
    if general:
        th_node = find_first(general, "thickness")
        if th_node and len(th_node) >= 2:
            thickness_mm = as_float(th_node[1], 1.6)

    # 2. Edge.Cuts outline geometry
    edge_xs: list[float] = []
    edge_ys: list[float] = []
    arc_radii: list[float] = []

    for tag in ("gr_rect", "gr_line", "gr_arc", "gr_poly"):
        for item in find_children(tree, tag):
            layer = find_first(item, "layer")
            if not layer or len(layer) < 2 or str(layer[1]) != "Edge.Cuts":
                continue
            for pt_tag in ("start", "mid", "end"):
                pt = find_first(item, pt_tag)
                if pt and len(pt) >= 3:
                    edge_xs.append(as_float(pt[1]))
                    edge_ys.append(as_float(pt[2]))
            pts = find_first(item, "pts")
            if pts:
                for xy in find_children(pts, "xy"):
                    if len(xy) >= 3:
                        edge_xs.append(as_float(xy[1]))
                        edge_ys.append(as_float(xy[2]))
            if tag == "gr_arc":
                s_pt = find_first(item, "start")
                e_pt = find_first(item, "end")
                if s_pt and e_pt and len(s_pt) >= 3 and len(e_pt) >= 3:
                    chord = math.hypot(
                        as_float(e_pt[1]) - as_float(s_pt[1]),
                        as_float(e_pt[2]) - as_float(s_pt[2]),
                    )
                    # Quarter-circle rounded corner chord = R * sqrt(2)
                    arc_radii.append(round(chord / math.sqrt(2.0), 3))

    if not edge_xs or not edge_ys:
        raise ValueError(f"No Edge.Cuts outline primitives found in {pcb_path}")

    min_x, max_x = min(edge_xs), max(edge_xs)
    min_y, max_y = min(edge_ys), max(edge_ys)
    width_mm = round(max_x - min_x, 4)
    height_mm = round(max_y - min_y, 4)
    cx_mm = round((min_x + max_x) / 2.0, 4)
    cy_mm = round((min_y + max_y) / 2.0, 4)
    corner_radius_mm = round(sum(arc_radii) / len(arc_radii), 3) if arc_radii else 0.0

    mounting_holes: list[dict[str, Any]] = []
    edge_ports: list[dict[str, Any]] = []
    hot_components: list[dict[str, Any]] = []
    leds: list[dict[str, Any]] = []
    max_top_h = 2.0
    max_bot_h = 0.0

    # Note: KiCad PCB Y-axis increases downward (SOUTH = max_y, NORTH = min_y, WEST = min_x, EAST = max_x)
    for fp in find_children(tree, "footprint") + find_children(tree, "module"):
        lib_id = str(fp[1]) if len(fp) >= 2 else ""
        at_node = find_first(fp, "at")
        if not at_node or len(at_node) < 3:
            continue
        fx = as_float(at_node[1])
        fy = as_float(at_node[2])
        frot = as_float(at_node[3], 0.0) if len(at_node) >= 4 else 0.0

        layer_node = find_first(fp, "layer")
        fp_layer = str(layer_node[1]) if layer_node and len(layer_node) >= 2 else "F.Cu"
        side = "bottom" if fp_layer.startswith("B.") else "top"

        ref = extract_footprint_property(fp, "Reference") or "UNK"
        val = extract_footprint_property(fp, "Value")
        h_prop = extract_footprint_property(fp, "Height") or extract_footprint_property(fp, "ComponentHeight")
        comp_h = as_float(h_prop, estimate_component_height(lib_id, ref, val))

        if side == "top":
            max_top_h = max(max_top_h, comp_h)
        else:
            max_bot_h = max(max_bot_h, comp_h)

        # Convert KiCad Y-down coordinates into CAD center-origin Y-up coordinates:
        # x_cad = fx - cx_mm, y_cad = cy_mm - fy
        x_rel = round(fx - cx_mm, 4)
        y_rel = round(cy_mm - fy, 4)

        l_min_x, l_max_x, l_min_y, l_max_y = compute_footprint_local_bbox(fp)
        r_min_x, r_max_x, r_min_y, r_max_y = rotate_bbox(l_min_x, l_max_x, l_min_y, l_max_y, frot)
        w_min_x, w_max_x = fx + r_min_x, fx + r_max_x
        w_min_y, w_max_y = fy + r_min_y, fy + r_max_y
        span_x = round(w_max_x - w_min_x, 4)
        span_y = round(w_max_y - w_min_y, 4)

        upper_key = f"{lib_id} {ref} {val}".upper()

        # Classify Mounting Holes
        if "MOUNTINGHOLE" in upper_key or ref.upper().startswith(("H", "MH")):
            drill_mm = 2.7
            pad_dia_mm = 5.4
            for pad in find_children(fp, "pad"):
                drill = find_first(pad, "drill")
                sz = find_first(pad, "size")
                if drill and len(drill) >= 2:
                    drill_mm = as_float(drill[1], drill_mm)
                if sz and len(sz) >= 2:
                    pad_dia_mm = as_float(sz[1], pad_dia_mm)
            mounting_holes.append({
                "ref": ref,
                "kicad_x_mm": round(fx, 4),
                "kicad_y_mm": round(fy, 4),
                "x_rel_center_mm": x_rel,
                "y_rel_center_mm": y_rel,
                "drill_mm": round(drill_mm, 3),
                "pad_dia_mm": round(pad_dia_mm, 3),
            })
            continue

        # Classify Edge / External I/O Connectors
        is_connector = any(
            kw in upper_key
            for kw in ("USB", "RJ45", "HDMI", "JACK", "MICROSD", "SD_CARD", "SMA", "BARREL", "CONN_EDGE")
        ) or (ref.upper().startswith("J") and "B2B" not in upper_key and "HEADER_INTERNAL" not in upper_key)

        edge_distances = {
            "WEST": abs(w_min_x - min_x),
            "EAST": abs(max_x - w_max_x),
            "NORTH": abs(w_min_y - min_y),
            "SOUTH": abs(max_y - w_max_y),
        }
        nearest_edge = min(edge_distances, key=edge_distances.get)  # type: ignore[arg-type]
        overhang_map = {
            "WEST": round(min_x - w_min_x, 4),
            "EAST": round(w_max_x - max_x, 4),
            "NORTH": round(min_y - w_min_y, 4),
            "SOUTH": round(w_max_y - max_y, 4),
        }
        overhang_mm = overhang_map[nearest_edge]

        if is_connector and (edge_distances[nearest_edge] <= 6.0 or overhang_mm > 0.0):
            opening_width = span_x if nearest_edge in ("NORTH", "SOUTH") else span_y
            edge_ports.append({
                "ref": ref,
                "value": val,
                "footprint": lib_id,
                "side": side,
                "edge": nearest_edge,
                "x_rel_center_mm": x_rel,
                "y_rel_center_mm": y_rel,
                "width_mm": round(max(opening_width, 4.0), 4),
                "height_mm": round(comp_h, 4),
                "z_offset_mm": 0.0 if side == "top" else round(-comp_h, 4),
                "overhang_mm": overhang_mm,
            })

        # Classify Hot Components for Passive Ventilation Louvers
        if any(
            kw in upper_key
            for kw in ("CM5", "CM4", "COMPUTE", "ESP32", "BUCK", "TPS54", "LMR36", "LAN78", "RTL8211", "NVME")
        ):
            hot_components.append({
                "ref": ref,
                "value": val,
                "side": side,
                "x_rel_center_mm": x_rel,
                "y_rel_center_mm": y_rel,
                "width_mm": round(span_x, 4),
                "length_mm": round(span_y, 4),
                "height_mm": round(comp_h, 4),
            })

        # Classify Status LEDs for Light-Pipe Openings
        if "LED" in upper_key and "RJ45" not in upper_key:
            leds.append({
                "ref": ref,
                "value": val,
                "side": side,
                "x_rel_center_mm": x_rel,
                "y_rel_center_mm": y_rel,
                "height_mm": round(comp_h, 4),
            })

    step_bounds = parse_step_bounds(step_path) if step_path else None
    if step_bounds:
        # Cross-check overall Z height against assembled 3D STEP if available
        est_top_from_step = round(max(0.0, step_bounds["span_z_mm"] - thickness_mm), 3)
        if est_top_from_step > max_top_h:
            max_top_h = est_top_from_step

    return {
        "schema_version": "1.0.0",
        "source_pcb": str(pcb_path.resolve()),
        "source_step": str(step_path.resolve()) if step_path and step_path.is_file() else None,
        "coordinate_convention": "CAD center-origin (0,0 at PCB center; +X=EAST, +Y=NORTH, +Z=TOP)",
        "board": {
            "width_mm": width_mm,
            "height_mm": height_mm,
            "thickness_mm": thickness_mm,
            "corner_radius_mm": corner_radius_mm,
            "kicad_bbox_mm": {
                "min_x": round(min_x, 4),
                "max_x": round(max_x, 4),
                "min_y": round(min_y, 4),
                "max_y": round(max_y, 4),
                "center_x": cx_mm,
                "center_y": cy_mm,
            },
            "max_top_component_height_mm": round(max_top_h, 3),
            "max_bottom_component_height_mm": round(max_bot_h, 3),
        },
        "step_bounds": step_bounds,
        "recommended_clearances_mm": {
            "port_radial_clearance_mm": 0.30,
            "board_perimeter_xy_gap_mm": 0.50,
            "lid_snap_or_lip_clearance_mm": 0.20,
        },
        "mounting_holes": mounting_holes,
        "edge_ports": edge_ports,
        "hot_components": hot_components,
        "leds": leds,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract exact PCB outline, holes, ports, LEDs, and thermal zones into board_sync.json"
    )
    parser.add_argument("--pcb", required=True, type=Path, help="Path to .kicad_pcb file")
    parser.add_argument("--step", type=Path, default=None, help="Optional assembled .step model path")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON path (enclosure/board_sync.json)")
    args = parser.parse_args()

    if not args.pcb.is_file():
        print(json.dumps({"ok": False, "error": f"PCB file not found: {args.pcb}"}), file=sys.stderr)
        return 1

    try:
        sync_data = parse_kicad_pcb(args.pcb, args.step)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sync_data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "output": str(args.output.resolve()),
        "board_width_mm": sync_data["board"]["width_mm"],
        "board_height_mm": sync_data["board"]["height_mm"],
        "mounting_holes": len(sync_data["mounting_holes"]),
        "edge_ports": len(sync_data["edge_ports"]),
        "hot_components": len(sync_data["hot_components"]),
        "leds": len(sync_data["leds"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
