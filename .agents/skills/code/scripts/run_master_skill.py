#!/usr/bin/env python3
"""
Deterministic Single-Pass Runner & Dry-Run Verifier for Master Skill /code.
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

MANIFEST: Dict[str, Any] = json.loads("{\n  \"name\": \"code\",\n  \"version\": \"2.0.0\",\n  \"title\": \"Context-Aware Software Craft, Algorithms & App Delivery\",\n  \"trigger\": \"/code\",\n  \"aliases\": [\n    \"/code\",\n    \"/build\",\n    \"/refactor\",\n    \"/teach\",\n    \"/fable-method\",\n    \"/fable-loop\",\n    \"/fable-domain\"\n  ],\n  \"parameters\": [\n    {\n      \"name\": \"task\",\n      \"type\": \"string\",\n      \"default\": \"\",\n      \"desc\": \"Engineering task, bug fix, domain bundle, or tutoring topic\"\n    },\n    {\n      \"name\": \"mode\",\n      \"type\": \"enum(build|refactor|plan|domain|teach|optimize)\",\n      \"default\": \"build\",\n      \"desc\": \"Workflow lane inside the single-pass pipeline\"\n    },\n    {\n      \"name\": \"target\",\n      \"type\": \"path\",\n      \"default\": \".\",\n      \"desc\": \"Project workspace root\"\n    }\n  ],\n  \"stages\": [\n    {\n      \"id\": \"S1\",\n      \"title\": \"Classify, Define Done & Gather 6 Context Inputs\",\n      \"depends_on\": [],\n      \"gate\": \"`INTENT:` and concrete verification criterion established; zero unresolved ambiguity.\",\n      \"artifacts\": \"context_map.json, INTENT_line\"\n    },\n    {\n      \"id\": \"S2\",\n      \"title\": \"3-Move Context Surfacing & U-Shaped Attention Bundle\",\n      \"depends_on\": [\n        \"S1\"\n      ],\n      \"gate\": \"Zero irrelevant log/build noise in context bundle; explicit assumptions stated.\",\n      \"artifacts\": \"u_shaped_context_bundle\"\n    },\n    {\n      \"id\": \"S3\",\n      \"title\": \"Algorithmic, Cloudflare/App & Performance Design\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"Design chosen with zero duplicate logic and bounded complexity.\",\n      \"artifacts\": \"committed_implementation_plan\"\n    },\n    {\n      \"id\": \"S4\",\n      \"title\": \"Surgical TDD Implementation (Two Hats & Micro-Diffs)\",\n      \"depends_on\": [\n        \"S3\"\n      ],\n      \"gate\": \"Diffs stay strictly inside declared scope with clean docstrings and zero duplicated helpers.\",\n      \"artifacts\": \"patched_source_and_tests\"\n    },\n    {\n      \"id\": \"S5\",\n      \"title\": \"Observational Verification, Twin Check & System Build\",\n      \"depends_on\": [\n        \"S4\"\n      ],\n      \"gate\": \"Targeted tests, surrounding suite, and build observed green post-final-edit.\",\n      \"artifacts\": \"verified_test_and_build_output\"\n    },\n    {\n      \"id\": \"S6\",\n      \"title\": \"Knowledge Write-Back & Outcome-First Report\",\n      \"depends_on\": [\n        \"S5\"\n      ],\n      \"gate\": \"`GEMINI.md` updated cleanly (zero `CLAUDE.md`) and all verification gates logged.\",\n      \"artifacts\": \"updated_GEMINI_md_and_report\"\n    }\n  ],\n  \"expected_modules\": [\n    \"context-aware-coding\",\n    \"surgical-code-craft\",\n    \"fable-method\",\n    \"fable-loop\",\n    \"fable-domain\",\n    \"cloudflare-os\",\n    \"cs-algorithmic-foundations\",\n    \"blast-master-system\",\n    \"error-handling-patterns\",\n    \"system-optimization-guide\",\n    \"teach\"\n  ],\n  \"plugin_integrations\": [\n    \"planning-vs-fast\",\n    \"goldie-gravity-launch\",\n    \"modern-web-guidance\",\n    \"firebase-basics\",\n    \"firebase-app-hosting-basics\",\n    \"firebase-auth-basics\",\n    \"firebase-firestore\",\n    \"firebase-data-connect\",\n    \"android-cli\",\n    \"xcode-project-setup\",\n    \"base44-cli\",\n    \"base44-sdk\"\n  ],\n  \"mcp_integrations\": [\n    \"github-mcp-server\",\n    \"firebase-mcp-server\",\n    \"chrome-devtools-mcp\"\n  ]\n}")


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
