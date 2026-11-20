#!/usr/bin/env python3
"""
Deterministic Single-Pass Runner & Dry-Run Verifier for Master Skill /studio.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

SKILL_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = SKILL_ROOT / "modules"

MANIFEST: Dict[str, Any] = json.loads("{\n  \"name\": \"studio\",\n  \"version\": \"2.0.0\",\n  \"title\": \"Procedural Motion Graphics, Visual Explainers, Voice & Anti-Slop Media\",\n  \"trigger\": \"/studio\",\n  \"aliases\": [\n    \"/studio\",\n    \"/media\",\n    \"/video\",\n    \"/voice\",\n    \"/visual\"\n  ],\n  \"parameters\": [\n    {\n      \"name\": \"topic\",\n      \"type\": \"string\",\n      \"default\": \"\",\n      \"desc\": \"Subject, product, or trade/data story to turn into media\"\n    },\n    {\n      \"name\": \"format\",\n      \"type\": \"enum(short_9x16|video_16x9|explainer_html|thumbnail|voice_call|storyboard)\",\n      \"default\": \"short_9x16\",\n      \"desc\": \"Target output format\"\n    },\n    {\n      \"name\": \"persona\",\n      \"type\": \"enum(SOL|CODY|NICO|DOUG|NEUTRAL)\",\n      \"default\": \"NEUTRAL\",\n      \"desc\": \"Voice/character persona\"\n    },\n    {\n      \"name\": \"outdir\",\n      \"type\": \"path\",\n      \"default\": \"content/productions/latest\",\n      \"desc\": \"Output directory for staged assets\"\n    }\n  ],\n  \"stages\": [\n    {\n      \"id\": \"S1\",\n      \"title\": \"Creative Brief, Brand Tokens & Compliance Framing\",\n      \"depends_on\": [],\n      \"gate\": \"Script hook, brand palette, and compliance text defined with zero AI slop.\",\n      \"artifacts\": \"creative_brief_and_script.md\"\n    },\n    {\n      \"id\": \"S2\",\n      \"title\": \"Audio-First Voice & Speech Synthesis\",\n      \"depends_on\": [\n        \"S1\"\n      ],\n      \"gate\": \"Audio asset generated, non-empty, audible clarity verified.\",\n      \"artifacts\": \"voice/audio.wav\"\n    },\n    {\n      \"id\": \"S3\",\n      \"title\": \"Exposure Sheet & Leica Reel Timing\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"Exposure sheet and Leica reel cues sync to audio duration with zero orphan cues.\",\n      \"artifacts\": \"words/exposure_sheet.json, cues/leica_reel.json\"\n    },\n    {\n      \"id\": \"S4\",\n      \"title\": \"Procedural Motion Graphics & Scene-as-Code\",\n      \"depends_on\": [\n        \"S3\"\n      ],\n      \"gate\": \"Contact sheet (`scene/contact_sheet.png`) or standalone HTML builds cleanly without runtime errors.\",\n      \"artifacts\": \"scene/contact_sheet.png, scene/sweatbox.html\"\n    },\n    {\n      \"id\": \"S5\",\n      \"title\": \"Final Render & Pixel-Level Visual QA\",\n      \"depends_on\": [\n        \"S4\"\n      ],\n      \"gate\": \"Non-empty video/HTML/thumbnail verified visually and via `ffprobe`/file size check.\",\n      \"artifacts\": \"render/final.mp4, thumbnail.png\"\n    },\n    {\n      \"id\": \"S6\",\n      \"title\": \"Syndication Staging & Outcome Report\",\n      \"depends_on\": [\n        \"S5\"\n      ],\n      \"gate\": \"All rendered artifacts verified on disk with zero unauthorized external posts.\",\n      \"artifacts\": \"syndication_manifest.json\"\n    }\n  ],\n  \"expected_modules\": [\n    \"anti-slop-studio\",\n    \"generative-media-studio\",\n    \"multimodal-visual-explainer\",\n    \"cartesia-voice\",\n    \"agent-voice-facetime\",\n    \"social-media-vision-board\",\n    \"brand-identity\",\n    \"sol-ai-sun-agent\"\n  ],\n  \"plugin_integrations\": [\n    \"ui-pro-max\",\n    \"gemini-api-cli\",\n    \"generative_ui\"\n  ],\n  \"mcp_integrations\": [\n    \"chrome-devtools-mcp\",\n    \"market-haven-social-media\"\n  ]\n}")


def verify_dag(stages: List[Dict[str, Any]]) -> Any:
    seen = set()
    for st in stages:
        for dep in st.get("depends_on", []):
            if dep not in seen:
                return False, f"Stage {st['id']} depends on unresolved/later stage {dep}"
        seen.add(st["id"])
    return True, "acyclic_topological_order_ok"


def check_modules() -> Dict[str, Any]:
    expected = MANIFEST["expected_modules"]
    present = []
    missing = []
    scripts = []
    tests = []
    for mod in expected:
        mod_dir = MODULES_DIR / mod
        skill_md = mod_dir / "SKILL.md"
        if mod_dir.is_dir() and skill_md.is_file():
            present.append(mod)
            for p in sorted(mod_dir.rglob("*")):
                if p.is_file() and p.suffix in (".py", ".sh"):
                    rel = str(p.relative_to(SKILL_ROOT))
                    if "/tests/" in f"/{rel}" or p.name.startswith("test_"):
                        tests.append(rel)
                    else:
                        scripts.append(rel)
        else:
            missing.append(mod)
    return {
        "expected": len(expected),
        "present": len(present),
        "missing": missing,
        "helper_scripts": scripts,
        "module_tests": tests,
    }


def run_preflight() -> Dict[str, Any]:
    skill_md_ok = (SKILL_ROOT / "SKILL.md").is_file()
    mod_report = check_modules()
    dag_ok, dag_msg = verify_dag(MANIFEST["stages"])
    ready = bool(skill_md_ok and dag_ok and not mod_report["missing"])
    return {
        "skill": MANIFEST["name"],
        "trigger": MANIFEST["trigger"],
        "version": MANIFEST["version"],
        "skill_md_exists": skill_md_ok,
        "dag_valid": dag_ok,
        "dag_status": dag_msg,
        "modules_expected": mod_report["expected"],
        "modules_verified": mod_report["present"],
        "missing_modules": mod_report["missing"],
        "helper_scripts_count": len(mod_report["helper_scripts"]),
        "module_tests_count": len(mod_report["module_tests"]),
        "single_pass_ready": ready,
    }


def run_dry_run(mode: str) -> Dict[str, Any]:
    pre = run_preflight()
    trace = [
        {
            "step": idx,
            "stage_id": st["id"],
            "title": st["title"],
            "depends_on": st["depends_on"],
            "gate": st["gate"],
            "status": "DRY_RUN_READY" if pre["single_pass_ready"] else "BLOCKED",
        }
        for idx, st in enumerate(MANIFEST["stages"], 1)
    ]
    pre["mode"] = mode
    pre["execution_trace"] = trace
    return pre


def run_module_tests() -> Dict[str, Any]:
    mod_report = check_modules()
    results = []
    all_ok = True
    for rel in mod_report["module_tests"]:
        test_path = SKILL_ROOT / rel
        proc = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        ok = proc.returncode == 0
        if not ok:
            all_ok = False
        results.append({"test": rel, "returncode": proc.returncode, "passed": ok})
    return {"tests_run": len(results), "all_passed": all_ok, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Runner for Master Skill {MANIFEST['trigger']}")
    parser.add_argument("--dry-run", action="store_true", help="Verify full single-pass DAG & modules")
    parser.add_argument("--preflight", action="store_true", help="Check SKILL.md, DAG, and modules")
    parser.add_argument("--list-modules", action="store_true", help="List preserved granular modules")
    parser.add_argument("--run-tests", action="store_true", help="Run preserved Python module tests")
    parser.add_argument("--mode", default="default", help="Optional workflow mode")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON")
    args = parser.parse_args()

    if args.list_modules:
        out = check_modules()
    elif args.run_tests:
        out = run_module_tests()
        if not out["all_passed"]:
            print(json.dumps(out, indent=2) if args.json else out)
            return 1
    elif args.preflight:
        out = run_preflight()
    else:
        out = run_dry_run(args.mode)

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(out, indent=2))

    if "single_pass_ready" in out and not out["single_pass_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
