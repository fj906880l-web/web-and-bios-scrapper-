#!/usr/bin/env python3
"""
Deterministic Single-Pass Runner & Dry-Run Verifier for Master Skill /growth.
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

MANIFEST: Dict[str, Any] = json.loads("{\n  \"name\": \"growth\",\n  \"version\": \"2.0.0\",\n  \"title\": \"Marketing Intel, Newsletter Publishing, Phoenix Reach & Charity/Consulting Ops\",\n  \"trigger\": \"/growth\",\n  \"aliases\": [\n    \"/growth\",\n    \"/marketing\",\n    \"/newsletter\",\n    \"/newsletter-writer\",\n    \"/social\",\n    \"/charity-ops\"\n  ],\n  \"parameters\": [\n    {\n      \"name\": \"mode\",\n      \"type\": \"enum(full|intel|newsletter|social|charity_sync|monday_trade)\",\n      \"default\": \"full\",\n      \"desc\": \"Growth execution lane\"\n    },\n    {\n      \"name\": \"cadence\",\n      \"type\": \"enum(wednesday|sunday|event_watch|monday|friday|adhoc)\",\n      \"default\": \"adhoc\",\n      \"desc\": \"Edition or weekly calendar slot\"\n    },\n    {\n      \"name\": \"competitor\",\n      \"type\": \"string\",\n      \"default\": \"\",\n      \"desc\": \"Optional competitor name/URL for intel mode\"\n    },\n    {\n      \"name\": \"publish\",\n      \"type\": \"bool\",\n      \"default\": \"false\",\n      \"desc\": \"Must remain false (staged/draft only) unless explicit AUTH: is given\"\n    }\n  ],\n  \"stages\": [\n    {\n      \"id\": \"S1\",\n      \"title\": \"Zero-Dependency Intel, Scraping & Telemetry Sync\",\n      \"depends_on\": [],\n      \"gate\": \"Primary URLs, dates, and live telemetry parsed with zero fabricated placeholders.\",\n      \"artifacts\": \"intel_and_telemetry_snapshot.json\"\n    },\n    {\n      \"id\": \"S2\",\n      \"title\": \"Fact Verification, Scoring & Entity Compliance\",\n      \"depends_on\": [\n        \"S1\"\n      ],\n      \"gate\": \"Every retained claim carries `[Reported|Claim|Analysis]` + cited source URL.\",\n      \"artifacts\": \"verified_claims_ledger.json\"\n    },\n    {\n      \"id\": \"S3\",\n      \"title\": \"Copy Synthesis & Phoenix Reach Optimization\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"Phoenix score positive with zero clickbait/report risk; all compliance footers attached.\",\n      \"artifacts\": \"staged_copy_and_phoenix_scores.json\"\n    },\n    {\n      \"id\": \"S4\",\n      \"title\": \"Cross-Channel Staging, Kit Tagging & Action Dispatch\",\n      \"depends_on\": [\n        \"S3\"\n      ],\n      \"gate\": \"Drafts staged with valid IDs (`status: draft`) and duplicate-day guards verified.\",\n      \"artifacts\": \"staged_kit_and_task_payloads\"\n    },\n    {\n      \"id\": \"S5\",\n      \"title\": \"Pre-Publish Compliance & `AUTH:` Gate\",\n      \"depends_on\": [\n        \"S4\"\n      ],\n      \"gate\": \"Either clean staged delivery or explicit `AUTH:` recorded for live action.\",\n      \"artifacts\": \"publish_gate_decision\"\n    },\n    {\n      \"id\": \"S6\",\n      \"title\": \"Unified Delivery Ledger & Metrics Summary\",\n      \"depends_on\": [\n        \"S5\"\n      ],\n      \"gate\": \"Logs consistent and zero unapproved live sends occurred.\",\n      \"artifacts\": \"growth_run_summary\"\n    }\n  ],\n  \"expected_modules\": [\n    \"competitor-marketing-intel\",\n    \"newsletter-writer\",\n    \"phoenix-reach-optimizer\",\n    \"kit-ai-connectors\",\n    \"web-scraping-mcp\",\n    \"content-calendar-agent\",\n    \"social-media-agent\",\n    \"notification-agent\",\n    \"income-stream-sync\",\n    \"monday-trade-post\",\n    \"social-notification-subagent\"\n  ],\n  \"plugin_integrations\": [],\n  \"mcp_integrations\": [\n    \"web-scraping-mcp\",\n    \"kit-bridge\",\n    \"market-haven-social-media\"\n  ]\n}")


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
