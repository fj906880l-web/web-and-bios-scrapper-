#!/usr/bin/env python3
"""
Deterministic Single-Pass Runner & Dry-Run Verifier for Master Skill /ship.
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

MANIFEST: Dict[str, Any] = json.loads("{\n  \"name\": \"ship\",\n  \"version\": \"2.0.0\",\n  \"title\": \"Verified Security Hardening, Adversarial QA & Release Sealing\",\n  \"trigger\": \"/ship\",\n  \"aliases\": [\n    \"/ship\",\n    \"/release\",\n    \"/audit\",\n    \"/verify-release\"\n  ],\n  \"parameters\": [\n    {\n      \"name\": \"target\",\n      \"type\": \"path\",\n      \"default\": \".\",\n      \"desc\": \"Repository, directory, or build dir to audit/seal\"\n    },\n    {\n      \"name\": \"mode\",\n      \"type\": \"enum(full|diff|ui|release|daily)\",\n      \"default\": \"full\",\n      \"desc\": \"Execution focus while preserving mandatory gates\"\n    },\n    {\n      \"name\": \"dist_dir\",\n      \"type\": \"path\",\n      \"default\": \"./dist\",\n      \"desc\": \"Release artifact directory for SHA-256 sealing\"\n    },\n    {\n      \"name\": \"threshold\",\n      \"type\": \"int\",\n      \"default\": \"80\",\n      \"desc\": \"Minimum SAST security score required to unblock delivery\"\n    }\n  ],\n  \"stages\": [\n    {\n      \"id\": \"S1\",\n      \"title\": \"Pre-Flight, Secret Hygiene & DLP Intake\",\n      \"depends_on\": [],\n      \"gate\": \"Zero verified live secrets exposed; `.env` mode == `600`.\",\n      \"artifacts\": \"pre_flight_secrets_report\"\n    },\n    {\n      \"id\": \"S2\",\n      \"title\": \"Blast-Radius, Vanta Guardrails & Crypto Separation\",\n      \"depends_on\": [\n        \"S1\"\n      ],\n      \"gate\": \"Zero prohibited crypto primitives (`MD5`, `SHA-1`, `ECB`, raw SHA password hashes); zero container host-root escapes.\",\n      \"artifacts\": \"guardrails_crypto_audit.json\"\n    },\n    {\n      \"id\": \"S3\",\n      \"title\": \"Static Analysis (SAST), Mind-Virus & Audit Ledger\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"SAST score >= 80/100 and Mind-Virus verdict == `CLEAN`.\",\n      \"artifacts\": \"sast_mind_virus_gate\"\n    },\n    {\n      \"id\": \"S4\",\n      \"title\": \"Cloudflare 6-Phase Hunt, Fable Judge & Try-Harder PoC\",\n      \"depends_on\": [\n        \"S3\"\n      ],\n      \"gate\": \"Every finding backed by observed execution/counter-evidence; zero unverified completeness claims.\",\n      \"artifacts\": \"adversarial_judge_verdict\"\n    },\n    {\n      \"id\": \"S5\",\n      \"title\": \"Tactile Anti-Slop UI, Accessibility & Runtime QA\",\n      \"depends_on\": [\n        \"S3\"\n      ],\n      \"gate\": \"Zero AI slop boilerplate phrases/chrome; zero blocking console/a11y errors.\",\n      \"artifacts\": \"ui_quality_audit\"\n    },\n    {\n      \"id\": \"S6\",\n      \"title\": \"Release Artifact Sealing & Integrity Manifest\",\n      \"depends_on\": [\n        \"S4\",\n        \"S5\"\n      ],\n      \"gate\": \"`verify-manifest` exits `0` with `mismatches == []` and `missing == []`.\",\n      \"artifacts\": \"SHA256SUMS.json\"\n    },\n    {\n      \"id\": \"S7\",\n      \"title\": \"Release Verdict & Outcome-First Report\",\n      \"depends_on\": [\n        \"S6\"\n      ],\n      \"gate\": \"All 6 earlier stages green or blocker explicitly surfaced with remediation diff.\",\n      \"artifacts\": \"release_verdict_summary\"\n    }\n  ],\n  \"expected_modules\": [\n    \"verified-release-and-ui-craft\",\n    \"shift-left-ai-security\",\n    \"daily-security-workflow\",\n    \"vanta-security-scaling-guardrails\",\n    \"developer-isolation-blast-radius\",\n    \"static-code-analysis\",\n    \"fable-judge\",\n    \"try-harder-poc-validation\"\n  ],\n  \"plugin_integrations\": [\n    \"expert-testing-debugging\",\n    \"a11y-debugging\",\n    \"cookie-debugging\",\n    \"debug-optimize-lcp\",\n    \"memory-leak-debugging\",\n    \"firebase-security-rules-auditor\",\n    \"accidental-data-loss-prevention\"\n  ],\n  \"mcp_integrations\": [\n    \"chrome-devtools-mcp\",\n    \"github-mcp-server\",\n    \"firebase-mcp-server\"\n  ]\n}")


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
