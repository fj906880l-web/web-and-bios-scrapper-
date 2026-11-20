#!/usr/bin/env python3
"""
Deterministic Single-Pass Runner & Dry-Run Verifier for Master Skill /ops.
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

MANIFEST: Dict[str, Any] = json.loads("{\n  \"name\": \"ops\",\n  \"version\": \"2.0.0\",\n  \"title\": \"Agent Orchestration, MCP Routing, Meetings, Energy Tasking & Style Sync\",\n  \"trigger\": \"/ops\",\n  \"aliases\": [\n    \"/ops\",\n    \"/sync\",\n    \"/orchestrate\",\n    \"/nod\",\n    \"/harness\",\n    \"/meetings\",\n    \"/energy\"\n  ],\n  \"parameters\": [\n    {\n      \"name\": \"objective\",\n      \"type\": \"string\",\n      \"default\": \"\",\n      \"desc\": \"Orchestration task, meeting/inbox triage, or bridge sync request\"\n    },\n    {\n      \"name\": \"energy\",\n      \"type\": \"enum(auto|peak|steady|recovery)\",\n      \"default\": \"auto\",\n      \"desc\": \"Operator energy tier for task batching and routing\"\n    },\n    {\n      \"name\": \"channel\",\n      \"type\": \"enum(internal|group|direct|bridge)\",\n      \"default\": \"internal\",\n      \"desc\": \"Target communication/alignment channel\"\n    },\n    {\n      \"name\": \"entity\",\n      \"type\": \"enum(all|charity|lumina|consulting)\",\n      \"default\": \"all\",\n      \"desc\": \"Organizational lane & RBAC scope\"\n    }\n  ],\n  \"stages\": [\n    {\n      \"id\": \"S1\",\n      \"title\": \"Harness Sync & 4-Asset Memory Hydration\",\n      \"depends_on\": [],\n      \"gate\": \"Memory hub hydrated and live bridge/service status observed.\",\n      \"artifacts\": \"harness_state_snapshot\"\n    },\n    {\n      \"id\": \"S2\",\n      \"title\": \"Energy-Based Tasking & Meeting Triage\",\n      \"depends_on\": [\n        \"S1\"\n      ],\n      \"gate\": \"Every task tagged with energy tier, owner entity (`Jeremiah`/`Fernando`/`DJ`), and next verified action.\",\n      \"artifacts\": \"energy_task_and_meeting_plan\"\n    },\n    {\n      \"id\": \"S3\",\n      \"title\": \"Concurrency, Model & MCP/API Routing\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"Zero unbounded worker pools or rate-limit loops; model & MCP route verified.\",\n      \"artifacts\": \"routing_decision_manifest\"\n    },\n    {\n      \"id\": \"S4\",\n      \"title\": \"Bounded Delegation, Bridge Dispatch & Durable Execution\",\n      \"depends_on\": [\n        \"S3\"\n      ],\n      \"gate\": \"Every delegated step verified by exit code / endpoint proof (`Diligence` pass).\",\n      \"artifacts\": \"delegation_execution_log\"\n    },\n    {\n      \"id\": \"S5\",\n      \"title\": \"Writing-Style, Tone & RBAC Alignment Gate\",\n      \"depends_on\": [\n        \"S4\"\n      ],\n      \"gate\": \"Message matches user's natural writing style with zero secret/PII leakage or bot filler.\",\n      \"artifacts\": \"aligned_outbound_payload\"\n    },\n    {\n      \"id\": \"S6\",\n      \"title\": \"Supervisor Gate, SkillOpt Reflection & EOD Debrief\",\n      \"depends_on\": [\n        \"S5\"\n      ],\n      \"gate\": \"Supervisor cleared (`confidence >= 0.30`, `security >= 80`); zero unverified claims.\",\n      \"artifacts\": \"supervisor_and_debrief_report\"\n    },\n    {\n      \"id\": \"S7\",\n      \"title\": \"Atomic State Persistence & Unified Delivery Ledger\",\n      \"depends_on\": [\n        \"S6\"\n      ],\n      \"gate\": \"All state files saved atomically with zero partial writes.\",\n      \"artifacts\": \"delivery_ledger_entry\"\n    }\n  ],\n  \"expected_modules\": [\n    \"agent-harness-v2\",\n    \"agent-systems-unified-skill\",\n    \"autonomous-architect-protocol\",\n    \"delegation-diligence-loop\",\n    \"unified-ai-architecture-and-standards\",\n    \"icm-architect\",\n    \"tri-perspective-collaboration\",\n    \"nod-bridge-ops\",\n    \"omniroute\",\n    \"composio-mcp\",\n    \"unigent\",\n    \"typesafe-ai\",\n    \"skillopt\",\n    \"nod-human-ops\",\n    \"mas_orchestrator\",\n    \"ego-lite\"\n  ],\n  \"plugin_integrations\": [\n    \"harness-engineering\",\n    \"subagent-orchestration\",\n    \"google-antigravity-sdk\",\n    \"base44-troubleshooter\"\n  ],\n  \"mcp_integrations\": [\n    \"nod-local-bridge\",\n    \"whatsapp-bridge\",\n    \"lumina-mcp\",\n    \"github-mcp-server\"\n  ]\n}")


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
