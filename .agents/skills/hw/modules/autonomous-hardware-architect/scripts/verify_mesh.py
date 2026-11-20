#!/usr/bin/env python3
"""verify_mesh.py — Watertight 2-Manifold & PCB Interference Verifier for Stage 4 CAD.

Validates `.stl` (binary & ASCII) and `.3mf` enclosure files for:
  1. Watertight 2-manifold half-edge topology (`boundary_edges == 0`, `non_manifold_edges == 0`).
  2. Positive enclosed volume (`signed_volume_mm3 > 0`) and zero degenerate triangles.
  3. Exact 3D Triangle-vs-AABB Separating Axis Theorem (SAT) collision checks against
     the PCB substrate and tall component volumes from `board_sync.json` / `board.step`
     (with screw-boss exemptions around `mounting_holes`).
"""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

Vec3 = tuple[float, float, float]
Tri = tuple[Vec3, Vec3, Vec3]
AABB = tuple[float, float, float, float, float, float]  # min_x, max_x, min_y, max_y, min_z, max_z


def sub3(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross3(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot3(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm3(a: Vec3) -> float:
    return math.sqrt(dot3(a, a))


def load_stl_triangles(path: Path) -> list[Tri]:
    raw = path.read_bytes()
    if len(raw) >= 84:
        tri_count = struct.unpack_from("<I", raw, 80)[0]
        expected_len = 84 + tri_count * 50
        if expected_len == len(raw) and tri_count > 0:
            tris: list[Tri] = []
            offset = 84
            for _ in range(tri_count):
                vals = struct.unpack_from("<12fH", raw, offset)
                v0: Vec3 = (vals[3], vals[4], vals[5])
                v1: Vec3 = (vals[6], vals[7], vals[8])
                v2: Vec3 = (vals[9], vals[10], vals[11])
                tris.append((v0, v1, v2))
                offset += 50
            return tris

    # Fallback: ASCII STL
    text = raw.decode("utf-8", errors="ignore")
    vert_re = re.compile(
        r"vertex\s+([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s+"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s+"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)",
        re.IGNORECASE,
    )
    verts: list[Vec3] = [
        (float(m.group(1)), float(m.group(2)), float(m.group(3)))
        for m in vert_re.finditer(text)
    ]
    return [(verts[i], verts[i + 1], verts[i + 2]) for i in range(0, len(verts) - 2, 3)]


def apply_affine_3mf(pt: Vec3, transform_str: str | None) -> Vec3:
    if not transform_str:
        return pt
    vals = [float(x) for x in transform_str.strip().split()]
    if len(vals) != 12:
        return pt
    # 3MF 4x3 row-major affine matrix: m00 m01 m02 m10 m11 m12 m20 m21 m22 m30 m31 m32
    x, y, z = pt
    nx = vals[0] * x + vals[3] * y + vals[6] * z + vals[9]
    ny = vals[1] * x + vals[4] * y + vals[7] * z + vals[10]
    nz = vals[2] * x + vals[5] * y + vals[8] * z + vals[11]
    return (nx, ny, nz)


def load_3mf_bodies(path: Path) -> list[tuple[str, list[Tri]]]:
    bodies: list[tuple[str, list[Tri]]] = []
    with zipfile.ZipFile(path, "r") as zf:
        model_files = [n for n in zf.namelist() if n.lower().endswith(".model")]
        if not model_files:
            raise ValueError(f"No .model XML found inside 3MF archive {path}")

        mesh_by_id: dict[str, list[Tri]] = {}
        comp_by_id: dict[str, list[tuple[str, str | None]]] = {}
        build_items: list[tuple[str, str | None]] = []

        for mname in model_files:
            xml_bytes = zf.read(mname)
            root = ET.fromstring(xml_bytes)
            unit = (root.attrib.get("unit") or "millimeter").lower()
            unit_scale = {
                "millimeter": 1.0,
                "centimeter": 10.0,
                "meter": 1000.0,
                "inch": 25.4,
                "foot": 304.8,
                "micron": 0.001,
            }.get(unit, 1.0)

            for elem in root.iter():
                tag = elem.tag.split("}")[-1]
                if tag == "object":
                    obj_id = elem.attrib.get("id", f"obj_{len(mesh_by_id)}")
                    for child in elem:
                        ctag = child.tag.split("}")[-1]
                        if ctag == "mesh":
                            v_list: list[Vec3] = []
                            t_list: list[Tri] = []
                            for mchild in child:
                                mtag = mchild.tag.split("}")[-1]
                                if mtag == "vertices":
                                    for vnode in mchild:
                                        if vnode.tag.split("}")[-1] == "vertex":
                                            v_list.append((
                                                float(vnode.attrib["x"]) * unit_scale,
                                                float(vnode.attrib["y"]) * unit_scale,
                                                float(vnode.attrib["z"]) * unit_scale,
                                            ))
                                elif mtag == "triangles":
                                    for tnode in mchild:
                                        if tnode.tag.split("}")[-1] == "triangle":
                                            i1 = int(tnode.attrib["v1"])
                                            i2 = int(tnode.attrib["v2"])
                                            i3 = int(tnode.attrib["v3"])
                                            t_list.append((v_list[i1], v_list[i2], v_list[i3]))
                            mesh_by_id[obj_id] = t_list
                        elif ctag == "components":
                            comps: list[tuple[str, str | None]] = []
                            for cnode in child:
                                if cnode.tag.split("}")[-1] == "component":
                                    comps.append((cnode.attrib.get("objectid", ""), cnode.attrib.get("transform")))
                            comp_by_id[obj_id] = comps
                elif tag == "build":
                    for item in elem:
                        if item.tag.split("}")[-1] == "item":
                            build_items.append((item.attrib.get("objectid", ""), item.attrib.get("transform")))

        def collect_obj(obj_id: str, tf: str | None) -> list[Tri]:
            if obj_id in mesh_by_id:
                return [
                    (
                        apply_affine_3mf(t[0], tf),
                        apply_affine_3mf(t[1], tf),
                        apply_affine_3mf(t[2], tf),
                    )
                    for t in mesh_by_id[obj_id]
                ]
            out: list[Tri] = []
            for sub_id, sub_tf in comp_by_id.get(obj_id, []):
                sub_tris = collect_obj(sub_id, sub_tf)
                out.extend(
                    (
                        apply_affine_3mf(t[0], tf),
                        apply_affine_3mf(t[1], tf),
                        apply_affine_3mf(t[2], tf),
                    )
                    for t in sub_tris
                )
            return out

        if build_items:
            for idx, (oid, tf) in enumerate(build_items):
                tris = collect_obj(oid, tf)
                if tris:
                    bodies.append((f"{path.name}#item{idx}_obj{oid}", tris))
        else:
            for oid, tris in mesh_by_id.items():
                bodies.append((f"{path.name}#obj{oid}", tris))

    return bodies


def analyze_manifold_and_volume(triangles: list[Tri], weld_decimals: int = 5) -> dict[str, Any]:
    """Verify exact half-edge watertight 2-manifoldness, volume, and bounding box."""
    if not triangles:
        return {
            "triangle_count": 0,
            "vertex_count": 0,
            "is_watertight": False,
            "is_manifold": False,
            "boundary_edge_count": 0,
            "non_manifold_edge_count": 0,
            "degenerate_triangle_count": 0,
            "signed_volume_mm3": 0.0,
            "bbox_mm": None,
        }

    vert_index: dict[tuple[int, int, int], int] = {}
    welded_verts: list[Vec3] = []
    scale = 10 ** weld_decimals

    def get_vid(pt: Vec3) -> int:
        key = (round(pt[0] * scale), round(pt[1] * scale), round(pt[2] * scale))
        vid = vert_index.get(key)
        if vid is None:
            vid = len(welded_verts)
            vert_index[key] = vid
            welded_verts.append(pt)
        return vid

    directed_edges: Counter[tuple[int, int]] = Counter()
    undirected_edges: Counter[tuple[int, int]] = Counter()
    degenerate_count = 0
    signed_vol_6 = 0.0

    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []

    for v0, v1, v2 in triangles:
        xs.extend([v0[0], v1[0], v2[0]])
        ys.extend([v0[1], v1[1], v2[1]])
        zs.extend([v0[2], v1[2], v2[2]])

        i0, i1, i2 = get_vid(v0), get_vid(v1), get_vid(v2)
        area2 = norm3(cross3(sub3(v1, v0), sub3(v2, v0)))
        if i0 == i1 or i1 == i2 or i2 == i0 or area2 < 1e-10:
            degenerate_count += 1
            continue

        for a, b in ((i0, i1), (i1, i2), (i2, i0)):
            directed_edges[(a, b)] += 1
            u_edge = (a, b) if a < b else (b, a)
            undirected_edges[u_edge] += 1

        # 6 * tetrahedron signed volume from origin
        signed_vol_6 += dot3(v0, cross3(v1, v2))

    boundary_edges = 0
    non_manifold_edges = 0
    for (u, v), count_uv in directed_edges.items():
        count_vu = directed_edges.get((v, u), 0)
        if count_vu == 0:
            boundary_edges += count_uv
        if count_uv > 1:
            non_manifold_edges += count_uv - 1

    for _, total_shared in undirected_edges.items():
        if total_shared != 2:
            if total_shared > 2:
                non_manifold_edges += 1

    signed_vol = signed_vol_6 / 6.0
    is_watertight = (
        len(triangles) >= 4
        and degenerate_count == 0
        and boundary_edges == 0
        and non_manifold_edges == 0
        and signed_vol > 1e-6
    )
    is_manifold = (
        len(triangles) >= 4
        and degenerate_count == 0
        and non_manifold_edges == 0
    )

    return {
        "triangle_count": len(triangles),
        "vertex_count": len(welded_verts),
        "is_watertight": is_watertight,
        "is_manifold": is_manifold,
        "boundary_edge_count": boundary_edges,
        "non_manifold_edge_count": non_manifold_edges,
        "degenerate_triangle_count": degenerate_count,
        "signed_volume_mm3": round(signed_vol, 4),
        "bbox_mm": {
            "min_x": round(min(xs), 4),
            "max_x": round(max(xs), 4),
            "min_y": round(min(ys), 4),
            "max_y": round(max(ys), 4),
            "min_z": round(min(zs), 4),
            "max_z": round(max(zs), 4),
            "span_x": round(max(xs) - min(xs), 4),
            "span_y": round(max(ys) - min(ys), 4),
            "span_z": round(max(zs) - min(zs), 4),
        },
    }


def triangle_intersects_aabb(tri: Tri, box: AABB) -> bool:
    """Exact 3D Triangle-vs-AABB Separating Axis Theorem (Akenine-Moller SAT)."""
    min_x, max_x, min_y, max_y, min_z, max_z = box
    cx = 0.5 * (min_x + max_x)
    cy = 0.5 * (min_y + max_y)
    cz = 0.5 * (min_z + max_z)
    ex = 0.5 * (max_x - min_x)
    ey = 0.5 * (max_y - min_y)
    ez = 0.5 * (max_z - min_z)
    if ex <= 0.0 or ey <= 0.0 or ez <= 0.0:
        return False

    v0 = (tri[0][0] - cx, tri[0][1] - cy, tri[0][2] - cz)
    v1 = (tri[1][0] - cx, tri[1][1] - cy, tri[1][2] - cz)
    v2 = (tri[2][0] - cx, tri[2][1] - cy, tri[2][2] - cz)

    # 1. Box face normals (X, Y, Z)
    if min(v0[0], v1[0], v2[0]) > ex or max(v0[0], v1[0], v2[0]) < -ex:
        return False
    if min(v0[1], v1[1], v2[1]) > ey or max(v0[1], v1[1], v2[1]) < -ey:
        return False
    if min(v0[2], v1[2], v2[2]) > ez or max(v0[2], v1[2], v2[2]) < -ez:
        return False

    f0 = sub3(v1, v0)
    f1 = sub3(v2, v1)
    f2 = sub3(v0, v2)

    # 2. 9 cross-product axes (box basis x triangle edges)
    extents = (ex, ey, ez)
    basis = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    for u in basis:
        for edge in (f0, f1, f2):
            axis = cross3(u, edge)
            if abs(axis[0]) < 1e-12 and abs(axis[1]) < 1e-12 and abs(axis[2]) < 1e-12:
                continue
            p0 = dot3(v0, axis)
            p1 = dot3(v1, axis)
            p2 = dot3(v2, axis)
            r = extents[0] * abs(axis[0]) + extents[1] * abs(axis[1]) + extents[2] * abs(axis[2])
            if min(p0, p1, p2) > r or max(p0, p1, p2) < -r:
                return False

    # 3. Triangle plane normal
    normal = cross3(f0, f1)
    d = dot3(normal, v0)
    r_n = ex * abs(normal[0]) + ey * abs(normal[1]) + ez * abs(normal[2])
    if abs(d) > r_n:
        return False

    return True


def is_near_mounting_boss(tri: Tri, holes: list[dict[str, Any]], boss_radius_mm: float = 4.5) -> bool:
    cx = (tri[0][0] + tri[1][0] + tri[2][0]) / 3.0
    cy = (tri[0][1] + tri[1][1] + tri[2][1]) / 3.0
    for h in holes:
        hx = float(h.get("x_rel_center_mm", 0.0))
        hy = float(h.get("y_rel_center_mm", 0.0))
        r_allow = max(boss_radius_mm, float(h.get("pad_dia_mm", 5.4)) * 0.75)
        if math.hypot(cx - hx, cy - hy) <= r_allow:
            return True
    return False


def parse_step_span(step_path: Path) -> dict[str, float] | None:
    if not step_path.is_file():
        return None
    text = step_path.read_text(encoding="utf-8", errors="ignore")
    scale = 25.4 if "INCH" in text[:4000].upper() and "MILLI" not in text[:4000].upper() else 1.0
    pt_re = re.compile(
        r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*,\s*"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*,\s*"
        r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*\)\s*\)"
    )
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for m in pt_re.finditer(text):
        xs.append(float(m.group(1)) * scale)
        ys.append(float(m.group(2)) * scale)
        zs.append(float(m.group(3)) * scale)
    if not xs:
        return None
    return {
        "span_x": round(max(xs) - min(xs), 4),
        "span_y": round(max(ys) - min(ys), 4),
        "span_z": round(max(zs) - min(zs), 4),
    }


def check_pcb_interference(
    all_body_tris: list[tuple[str, list[Tri]]],
    overall_bbox: dict[str, float],
    board_sync: dict[str, Any] | None,
    step_span: dict[str, float] | None,
    pcb_z_bottom_mm: float | None,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    pcb_w = 0.0
    pcb_h = 0.0
    pcb_t = 1.6
    holes: list[dict[str, Any]] = []
    hot_ics: list[dict[str, Any]] = []
    standoff_guess = 3.5

    if board_sync:
        b = board_sync.get("board", {})
        pcb_w = float(b.get("width_mm", 0.0))
        pcb_h = float(b.get("height_mm", 0.0))
        pcb_t = float(b.get("thickness_mm", 1.6))
        bot_h = float(b.get("max_bottom_component_height_mm", 0.0))
        standoff_guess = max(3.5, bot_h + 1.0)
        holes = list(board_sync.get("mounting_holes", []))
        hot_ics = list(board_sync.get("hot_components", []))
    elif step_span:
        pcb_w = step_span["span_x"]
        pcb_h = step_span["span_y"]

    if pcb_w <= 0.0 or pcb_h <= 0.0:
        return {"checked": False, "interference_count": 0, "issues": []}

    # 1. Overall XY Envelope Fit Check (Enclosure outer span must exceed PCB + 2 * 1.2 mm wall)
    min_outer_x = pcb_w + 2.4
    min_outer_y = pcb_h + 2.4
    if overall_bbox["span_x"] < min_outer_x or overall_bbox["span_y"] < min_outer_y:
        issues.append({
            "type": "enclosure_smaller_than_pcb",
            "description": (
                f"Enclosure XY span ({overall_bbox['span_x']:.2f} x {overall_bbox['span_y']:.2f} mm) "
                f"is smaller than PCB + minimum walls ({min_outer_x:.2f} x {min_outer_y:.2f} mm)."
            ),
            "remediation_hint": (
                "Re-read `board_sync.json` width_mm/height_mm and add `2 * (board_xy_gap + wall_thickness)`."
            ),
        })

    # 2. Exact 3D Triangle-vs-AABB SAT Check against PCB substrate interior & hot ICs
    # Determine PCB Z bottom in enclosure coordinates (default: floor_thickness 2.0 + standoff_guess above min_z)
    z0 = pcb_z_bottom_mm if pcb_z_bottom_mm is not None else (overall_bbox["min_z"] + 2.0 + standoff_guess)
    # Shrink XY by 0.8 mm from PCB edge so legitimate perimeter board-support ledges do not false-trigger
    inset = 0.8
    pcb_core_aabb: AABB = (
        -0.5 * pcb_w + inset,
        0.5 * pcb_w - inset,
        -0.5 * pcb_h + inset,
        0.5 * pcb_h - inset,
        z0 + 0.05,
        z0 + pcb_t - 0.05,
    )

    ic_aabbs: list[tuple[str, AABB]] = []
    for ic in hot_ics:
        ix = float(ic.get("x_rel_center_mm", 0.0))
        iy = float(ic.get("y_rel_center_mm", 0.0))
        iw = max(1.0, float(ic.get("width_mm", 4.0)) - 0.4)
        il = max(1.0, float(ic.get("length_mm", 4.0)) - 0.4)
        ih = max(0.5, float(ic.get("height_mm", 2.0)) - 0.15)
        if ic.get("side", "top") == "top":
            ic_aabbs.append((
                str(ic.get("ref", "IC")),
                (ix - 0.5 * iw, ix + 0.5 * iw, iy - 0.5 * il, iy + 0.5 * il, z0 + pcb_t + 0.1, z0 + pcb_t + ih),
            ))

    for body_name, tris in all_body_tris:
        pcb_hits = 0
        sample_tri: Tri | None = None
        for tri in tris:
            if is_near_mounting_boss(tri, holes):
                continue
            if triangle_intersects_aabb(tri, pcb_core_aabb):
                pcb_hits += 1
                if sample_tri is None:
                    sample_tri = tri
        if pcb_hits > 0 and sample_tri is not None:
            issues.append({
                "type": "pcb_substrate_collision",
                "body": body_name,
                "colliding_triangles": pcb_hits,
                "sample_vertex_mm": [round(c, 3) for c in sample_tri[0]],
                "pcb_z_band_mm": [round(pcb_core_aabb[4], 3), round(pcb_core_aabb[5], 3)],
                "remediation_hint": (
                    "An internal rib, boss, or wall intersects the PCB substrate plane; check standoff Z height "
                    "and mounting hole `(x_rel_center_mm, y_rel_center_mm)` alignment."
                ),
            })

        for ic_ref, ic_box in ic_aabbs:
            ic_hits = sum(1 for tri in tris if triangle_intersects_aabb(tri, ic_box))
            if ic_hits > 0:
                issues.append({
                    "type": "component_keepout_collision",
                    "body": body_name,
                    "component_ref": ic_ref,
                    "colliding_triangles": ic_hits,
                    "component_aabb_mm": [round(v, 3) for v in ic_box],
                    "remediation_hint": (
                        f"Top shell or internal feature collides with {ic_ref}; increase enclosure internal Z height "
                        "or shorten top-ceiling standoff boss length."
                    ),
                })

    return {
        "checked": True,
        "assumed_pcb_z_bottom_mm": round(z0, 3),
        "interference_count": len(issues),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify .stl/.3mf enclosure meshes for watertight 2-manifold geometry and PCB interference."
    )
    parser.add_argument("--meshes", nargs="+", required=True, type=Path, help="List of .stl or .3mf files to verify")
    parser.add_argument("--board-sync", type=Path, default=None, help="Path to enclosure/board_sync.json")
    parser.add_argument("--pcb-step", type=Path, default=None, help="Optional path to fab/board.step")
    parser.add_argument(
        "--pcb-z-bottom",
        type=float,
        default=None,
        help="Explicit Z coordinate (mm) of bottom PCB copper in enclosure world space",
    )
    parser.add_argument("--output", type=Path, default=None, help="Write JSON verification report to file")
    args = parser.parse_args()

    mesh_reports: list[dict[str, Any]] = []
    all_bodies: list[tuple[str, list[Tri]]] = []
    overall_ok = True

    global_min = [float("inf"), float("inf"), float("inf")]
    global_max = [float("-inf"), float("-inf"), float("-inf")]

    for mpath in args.meshes:
        if not mpath.is_file():
            mesh_reports.append({
                "file": str(mpath),
                "ok": False,
                "error": f"Mesh file does not exist: {mpath}",
            })
            overall_ok = False
            continue

        suffix = mpath.suffix.lower()
        try:
            if suffix == ".stl":
                loaded = [(mpath.name, load_stl_triangles(mpath))]
            elif suffix == ".3mf":
                loaded = load_3mf_bodies(mpath)
            else:
                raise ValueError(f"Unsupported mesh extension '{suffix}' (expected .stl or .3mf)")
        except Exception as exc:
            mesh_reports.append({"file": str(mpath), "ok": False, "error": str(exc)})
            overall_ok = False
            continue

        for bname, tris in loaded:
            stats = analyze_manifold_and_volume(tris)
            remediations: list[str] = []
            if not stats["is_watertight"]:
                overall_ok = False
                if stats["boundary_edge_count"] > 0:
                    remediations.append(
                        f"Found {stats['boundary_edge_count']} open boundary half-edges; ensure solid boolean operations produce closed shells."
                    )
                if stats["non_manifold_edge_count"] > 0:
                    remediations.append(
                        f"Found {stats['non_manifold_edge_count']} non-manifold edges; avoid zero-thickness touching faces (overlap boolean cuts by 0.05 mm)."
                    )
                if stats["degenerate_triangle_count"] > 0:
                    remediations.append(
                        f"Found {stats['degenerate_triangle_count']} zero-area degenerate triangles; avoid tiny sliver fillets."
                    )
                if stats["signed_volume_mm3"] <= 0:
                    remediations.append(
                        "Signed mesh volume is <= 0 (inverted face normals or empty solid)."
                    )

            bbox = stats["bbox_mm"]
            if bbox:
                global_min[0] = min(global_min[0], bbox["min_x"])
                global_min[1] = min(global_min[1], bbox["min_y"])
                global_min[2] = min(global_min[2], bbox["min_z"])
                global_max[0] = max(global_max[0], bbox["max_x"])
                global_max[1] = max(global_max[1], bbox["max_y"])
                global_max[2] = max(global_max[2], bbox["max_z"])

            mesh_reports.append({
                "file": str(mpath.resolve()),
                "body": bname,
                "ok": stats["is_watertight"],
                **stats,
                "remediation_hints": remediations,
            })
            all_bodies.append((bname, tris))

    board_sync_data: dict[str, Any] | None = None
    if args.board_sync and args.board_sync.is_file():
        board_sync_data = json.loads(args.board_sync.read_text(encoding="utf-8"))
    step_span = parse_step_span(args.pcb_step) if args.pcb_step else None

    interference_report: dict[str, Any] = {"checked": False, "interference_count": 0, "issues": []}
    if all_bodies and global_min[0] < float("inf"):
        overall_bbox = {
            "min_x": round(global_min[0], 4),
            "max_x": round(global_max[0], 4),
            "min_y": round(global_min[1], 4),
            "max_y": round(global_max[1], 4),
            "min_z": round(global_min[2], 4),
            "max_z": round(global_max[2], 4),
            "span_x": round(global_max[0] - global_min[0], 4),
            "span_y": round(global_max[1] - global_min[1], 4),
            "span_z": round(global_max[2] - global_min[2], 4),
        }
        interference_report = check_pcb_interference(
            all_bodies,
            overall_bbox,
            board_sync_data,
            step_span,
            args.pcb_z_bottom,
        )
        if interference_report["interference_count"] > 0:
            overall_ok = False

    final_report = {
        "ok": overall_ok,
        "meshes_verified": len(mesh_reports),
        "meshes": mesh_reports,
        "pcb_interference": interference_report,
    }
    rendered = json.dumps(final_report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
