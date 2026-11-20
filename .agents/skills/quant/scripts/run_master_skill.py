#!/usr/bin/env python3
"""
Deterministic Single-Pass Runner & Dry-Run Verifier for Master Skill /quant.
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

MANIFEST: Dict[str, Any] = json.loads("{\n  \"name\": \"quant\",\n  \"version\": \"2.0.0\",\n  \"title\": \"Quantitative Trading, Risk Gating & Local Unsloth/Soup/Ollama Fine-Tuning\",\n  \"trigger\": \"/quant\",\n  \"aliases\": [\n    \"/quant\",\n    \"/trade\",\n    \"/trading-bot\",\n    \"/soup\",\n    \"/unsloth\",\n    \"/finetune\"\n  ],\n  \"parameters\": [\n    {\n      \"name\": \"mode\",\n      \"type\": \"enum(audit|pipeline|finetune|telemetry|research)\",\n      \"default\": \"audit\",\n      \"desc\": \"Quant workflow lane\"\n    },\n    {\n      \"name\": \"target\",\n      \"type\": \"path\",\n      \"default\": \"/Users/malcolm/Downloads/trading-bot-\",\n      \"desc\": \"Trading or fine-tuning workspace\"\n    },\n    {\n      \"name\": \"recipe\",\n      \"type\": \"path\",\n      \"default\": \"\",\n      \"desc\": \"Optional Soup/Unsloth training recipe path\"\n    },\n    {\n      \"name\": \"live_exec\",\n      \"type\": \"bool\",\n      \"default\": \"false\",\n      \"desc\": \"Must remain false; live orders blocked absent explicit AUTH:\"\n    }\n  ],\n  \"stages\": [\n    {\n      \"id\": \"S1\",\n      \"title\": \"Firewall, Lock Isolation & Daemon FD Pre-Flight\",\n      \"depends_on\": [],\n      \"gate\": \"Live/paper locks isolated, `PIPE` FDs < 20, zero phantom tickers.\",\n      \"artifacts\": \"lock_and_fd_audit\"\n    },\n    {\n      \"id\": \"S2\",\n      \"title\": \"Live Multi-Source Market & News Telemetry Ingestion\",\n      \"depends_on\": [\n        \"S1\"\n      ],\n      \"gate\": \"All series timestamped, real-source backed, and free of NaN/stale gaps.\",\n      \"artifacts\": \"live_market_telemetry\"\n    },\n    {\n      \"id\": \"S3\",\n      \"title\": \"Algorithm Sizing & Local Fine-Tuning (Soup / Unsloth / Ollama)\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"Doctor/schema checks exit `0`; host load stays `<50%`; GGUF registered in Ollama cleanly.\",\n      \"artifacts\": \"distillery_and_model_artifact\"\n    },\n    {\n      \"id\": \"S4\",\n      \"title\": \"Qlib MTS/MTF Walk-Forward & DSR Evaluation\",\n      \"depends_on\": [\n        \"S2\"\n      ],\n      \"gate\": \"Walk-forward and DSR gates satisfied within <=50% buying-power cap.\",\n      \"artifacts\": \"qlib_mts_evaluation\"\n    },\n    {\n      \"id\": \"S5\",\n      \"title\": \"Paper Execution, Manual Adoption & Hard `AUTH:` Live Gate\",\n      \"depends_on\": [\n        \"S4\"\n      ],\n      \"gate\": \"Zero unapproved live orders; atomic persistence verified (`orders.json` / `risk_state.json`).\",\n      \"artifacts\": \"execution_gate_verdict\"\n    },\n    {\n      \"id\": \"S6\",\n      \"title\": \"Verification, Security Scan & Post-Mortem Memory Sync\",\n      \"depends_on\": [\n        \"S5\"\n      ],\n      \"gate\": \"All tests and security scans pass without touching live runtime locks.\",\n      \"artifacts\": \"quant_verification_summary\"\n    }\n  ],\n  \"expected_modules\": [\n    \"soup-finetuning-harness\",\n    \"ai-algorithm-distillery\",\n    \"active-trade-allocation\",\n    \"qlib-mts-workflow\",\n    \"quantpad-data-api\",\n    \"opennews-mcp\",\n    \"mcp-fd-and-bracket-audit\",\n    \"trading-bot-auditor\"\n  ],\n  \"plugin_integrations\": [],\n  \"mcp_integrations\": [\n    \"alpaca\",\n    \"robinhood-for-agents\",\n    \"QuiverQuant_MCP\",\n    \"alphavantage\",\n    \"quantpad\",\n    \"onchain-market-mcp\"\n  ]\n}")


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
