#!/usr/bin/env python3
"""
Deterministic Single-Pass Runner & Dry-Run Verifier for Master Skill /research.
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

MANIFEST: Dict[str, Any] = json.loads("{\n  \"name\": \"research\",\n  \"version\": \"2.0.0\",\n  \"title\": \"Reverse Engineering, EGE-2 Epistemics, Math/ARC & Technical Learning\",\n  \"trigger\": \"/research\",\n  \"aliases\": [\n    \"/research\",\n    \"/rea\",\n    \"/ege2\",\n    \"/math\",\n    \"/arc\",\n    \"/intel\",\n    \"/learn-repo\"\n  ],\n  \"parameters\": [\n    {\n      \"name\": \"mode\",\n      \"type\": \"enum(research|rea|ege2|math|arc|intel|learn)\",\n      \"default\": \"research\",\n      \"desc\": \"Primary investigation engine\"\n    },\n    {\n      \"name\": \"target\",\n      \"type\": \"string\",\n      \"default\": \"\",\n      \"desc\": \"Binary/app path, URL/GitHub/YouTube target, conjecture, or topic\"\n    },\n    {\n      \"name\": \"corpus\",\n      \"type\": \"bool\",\n      \"default\": \"false\",\n      \"desc\": \"Enforce large-corpus coverage manifest (`references/corpus.md`)\"\n    }\n  ],\n  \"stages\": [\n    {\n      \"id\": \"S1\",\n      \"title\": \"Mode Routing & EGE-2 Epistemic Grounding\",\n      \"depends_on\": [],\n      \"gate\": \"Mode selected, hard constraints explicit, Q-Graph Tier hierarchy initialized.\",\n      \"artifacts\": \"epistemic_scope_and_manifest\"\n    },\n    {\n      \"id\": \"S2\",\n      \"title\": \"Primary Source & Artifact Evidence Collection\",\n      \"depends_on\": [\n        \"S1\"\n      ],\n      \"gate\": \"Every candidate claim linked to direct primary URL/file/address/command output.\",\n      \"artifacts\": \"primary_evidence_bundle\"\n    },\n    {\n      \"id\": \"S3\",\n      \"title\": \"Cross-Source Correlation, QUBO & Barrier Auditing\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"Contradictions surfaced transparently; zero heuristic-as-proof conflation.\",\n      \"artifacts\": \"correlated_analysis_matrix\"\n    },\n    {\n      \"id\": \"S4\",\n      \"title\": \"Deliverable & Tool Artifact Construction\",\n      \"depends_on\": [\n        \"S3\"\n      ],\n      \"gate\": \"Deliverable preserves uncertainty, units, and primary citations.\",\n      \"artifacts\": \"research_artifact_output\"\n    },\n    {\n      \"id\": \"S5\",\n      \"title\": \"Live Verification, Security & Mind-Virus Gate\",\n      \"depends_on\": [\n        \"S4\"\n      ],\n      \"gate\": \"Verification observed passing with zero security or viral-payload issues.\",\n      \"artifacts\": \"research_verification_gate\"\n    },\n    {\n      \"id\": \"S6\",\n      \"title\": \"Permanent Knowledge & Q-Graph Distillation\",\n      \"depends_on\": [\n        \"S5\"\n      ],\n      \"gate\": \"Memory distilled cleanly and all claims traceable to primary sources.\",\n      \"artifacts\": \"distilled_knowledge_record\"\n    }\n  ],\n  \"expected_modules\": [\n    \"rea\",\n    \"reverse-engineer-anything\",\n    \"ege2-quantum-epistemics\",\n    \"epistemic-math-frontier\",\n    \"arc-agi-3-interactive-reasoning\",\n    \"daily-ai-intel-digest\",\n    \"technical-learning-workflow\",\n    \"nod-research\"\n  ],\n  \"plugin_integrations\": [\n    \"science\",\n    \"data-agent-kit-plugin\"\n  ],\n  \"mcp_integrations\": [\n    \"rea\",\n    \"web-scraping-mcp\",\n    \"data-agent-kit-plugin_dak-notebook\"\n  ]\n}")


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
