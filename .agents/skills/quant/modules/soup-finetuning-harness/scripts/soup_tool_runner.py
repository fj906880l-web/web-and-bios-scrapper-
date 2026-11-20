#!/usr/bin/env python3
"""
Antigravity Soup Tool Runner CLI
Operational utility script for the Soup Autonomous Model Adaptation Skill.
Adheres to Agent Harness v2.0 & workflow-skill-creator standard (CLI pattern, file output).
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SoupToolRunner")

DEFAULT_SOUP_PATH = Path("/Users/malcolm/.local/bin/soup")
DEFAULT_WORKSPACE_ROOT = Path("/Users/malcolm/.gemini/antigravity-ide/scratch")


def find_soup_binary() -> str:
    """Finds the soup executable path."""
    if DEFAULT_SOUP_PATH.is_file() and os.access(DEFAULT_SOUP_PATH, os.X_OK):
        return str(DEFAULT_SOUP_PATH)
    which_path = shutil.which("soup")
    if which_path:
        return which_path
    raise FileNotFoundError("soup executable not found on PATH or at ~/.local/bin/soup")


def run_command_safe(cmd: List[str], timeout_sec: int = 120) -> Dict[str, Any]:
    """Runs a subprocess command without shell=True, capturing output safely."""
    start_time = time.monotonic()
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False
        )
        duration = time.monotonic() - start_time
        return {
            "command": cmd,
            "returncode": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "duration_seconds": round(duration, 3),
            "status": "success" if res.returncode == 0 else "failed"
        }
    except subprocess.TimeoutExpired as e:
        return {
            "command": cmd,
            "returncode": -1,
            "stdout": e.stdout or "",
            "stderr": f"Command timed out after {timeout_sec}s",
            "duration_seconds": timeout_sec,
            "status": "timeout"
        }
    except Exception as e:
        return {
            "command": cmd,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "duration_seconds": round(time.monotonic() - start_time, 3),
            "status": "error"
        }


def write_output_file(data: Any, output_path: Optional[str]) -> None:
    """Writes JSON data to the target output file or stdout if not specified."""
    if output_path:
        target = Path(output_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, indent=2)
        print(f"Success! Output written to: {target}")
    else:
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))


def cmd_doctor(args: argparse.Namespace) -> int:
    """Runs pre-flight doctor checks, optionally verifying a recipe."""
    soup_bin = find_soup_binary()
    cmd = [soup_bin, "doctor"]
    if args.config:
        cmd.extend(["--config", str(Path(args.config).resolve())])

    result = run_command_safe(cmd)
    
    # Parse key outputs
    is_valid_config = True
    config_details = "No config supplied"
    if args.config:
        if "Config validation error" in result["stdout"] or "unknown config key" in result["stdout"]:
            is_valid_config = False
            config_details = "Config rejected by Soup doctor schema validator"
        elif "Every setting this config writes is read" in result["stdout"]:
            is_valid_config = True
            config_details = "Valid schema: every setting verified on backend"
        else:
            is_valid_config = (result["returncode"] == 0)
            config_details = "Config validation completed"

    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "passed" if (result["returncode"] == 0 and is_valid_config) else "failed",
        "doctor_returncode": result["returncode"],
        "config_checked": str(args.config) if args.config else None,
        "is_valid_config": is_valid_config,
        "config_summary": config_details,
        "raw_stdout": result["stdout"],
        "raw_stderr": result["stderr"]
    }

    write_output_file(payload, args.output)
    return 0 if payload["status"] == "passed" else 1


def cmd_init(args: argparse.Namespace) -> int:
    """Generates a standard Soup recipe template."""
    soup_bin = find_soup_binary()
    template = args.template
    out_file = Path(args.output).resolve() if args.output else Path("soup.yaml").resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Soup CLI init creates soup.yaml in the cwd
    tmp_dir = out_file.parent / f".soup_init_tmp_{int(time.time())}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        cmd = [soup_bin, "init", "--template", template]
        res = subprocess.run(cmd, cwd=str(tmp_dir), capture_output=True, text=True, check=False)
        generated_soup = tmp_dir / "soup.yaml"
        if generated_soup.is_file():
            content = generated_soup.read_text(encoding="utf-8")
            out_file.write_text(content, encoding="utf-8")
            print(f"Success! Recipe initialized to: {out_file}")
            return 0
        else:
            logger.error("Failed to generate template: %s", res.stderr)
            return 1
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)


def cmd_validate_recipe(args: argparse.Namespace) -> int:
    """Validates a recipe strictly against Soup v0.75+ rules."""
    recipe_path = Path(args.config).resolve()
    if not recipe_path.is_file():
        err_payload = {"status": "error", "error": f"File not found: {recipe_path}"}
        write_output_file(err_payload, args.output)
        return 1

    content = recipe_path.read_text(encoding="utf-8")
    issues = []
    
    # Static checks for known v0.75 breaking schema changes
    if "model:" in content and "base:" in content:
        # Check if model.base is nested
        lines = [line.strip() for line in content.splitlines()]
        if any(line == "model:" for line in lines):
            issues.append("Nested 'model:' block detected. Use top-level 'base: <id>' instead.")
    if "max_seq_length:" in content:
        issues.append("Found 'max_seq_length:'. In Soup v0.75+, use 'data.max_length:' instead.")
    if "learning_rate:" in content:
        issues.append("Found 'learning_rate:'. In Soup v0.75+, use 'training.lr:' instead.")
    if "optimizer: \"adamw\"" in content or "optimizer: 'adamw'" in content:
        issues.append("optimizer='adamw' is not in allowed list. Use 'adamw_torch' or omit.")

    soup_bin = find_soup_binary()
    doctor_res = run_command_safe([soup_bin, "doctor", "--config", str(recipe_path)])
    
    if "Config validation error" in doctor_res["stdout"]:
        issues.append("Soup doctor rejected config: " + doctor_res["stdout"].split("Config validation error:")[-1].strip()[:200])

    is_valid = len(issues) == 0 and doctor_res["returncode"] == 0
    payload = {
        "recipe_path": str(recipe_path),
        "is_valid": is_valid,
        "issues_found": issues,
        "doctor_returncode": doctor_res["returncode"],
        "status": "valid" if is_valid else "invalid"
    }

    write_output_file(payload, args.output)
    return 0 if is_valid else 1


def cmd_matrix_verify(args: argparse.Namespace) -> int:
    """Verifies all three ecosystem project recipes in the workspace."""
    workspace = Path(args.workspace).resolve() if args.workspace else DEFAULT_WORKSPACE_ROOT
    recipes_dir = workspace / "config" / "soup_recipes"
    
    projects = {
        "regime_trader": recipes_dir / "regime_trader_soup.yaml",
        "allora_app": recipes_dir / "allora_app_soup.yaml",
        "market_haven": recipes_dir / "market_haven_soup.yaml"
    }

    soup_bin = find_soup_binary()
    matrix_results = {}
    overall_success = True

    for proj, r_path in projects.items():
        if not r_path.is_file():
            matrix_results[proj] = {
                "file": str(r_path),
                "exists": False,
                "valid": False,
                "error": "Recipe file does not exist"
            }
            overall_success = False
            continue

        doc_res = run_command_safe([soup_bin, "doctor", "--config", str(r_path)])
        is_clean = (doc_res["returncode"] == 0 and "Config validation error" not in doc_res["stdout"])
        matrix_results[proj] = {
            "file": str(r_path),
            "exists": True,
            "valid": is_clean,
            "returncode": doc_res["returncode"],
            "summary": "Verified against Soup v0.75+ schema" if is_clean else doc_res["stdout"][:200]
        }
        if not is_clean:
            overall_success = False

    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "workspace": str(workspace),
        "overall_status": "passed" if overall_success else "failed",
        "matrix": matrix_results
    }

    write_output_file(payload, args.output)
    return 0 if overall_success else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Soup Autonomous Model Adaptation Skill Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Run environment and recipe pre-flight checks")
    p_doc.add_argument("--config", "-c", type=str, help="Path to soup.yaml recipe")
    p_doc.add_argument("--output", "-o", type=str, required=True, help="File to write JSON report")

    # init
    p_init = subparsers.add_parser("init", help="Initialize a template recipe")
    p_init.add_argument("--template", "-t", type=str, default="chat", choices=["chat", "code", "tool-calling", "reasoning"])
    p_init.add_argument("--output", "-o", type=str, required=True, help="Output recipe file path")

    # validate-recipe
    p_val = subparsers.add_parser("validate-recipe", help="Strictly validate recipe against Soup v0.75+")
    p_val.add_argument("--config", "-c", type=str, required=True, help="Path to recipe file")
    p_val.add_argument("--output", "-o", type=str, required=True, help="File to write validation result")

    # matrix-verify
    p_mat = subparsers.add_parser("matrix-verify", help="Verify all multi-project recipes in ecosystem")
    p_mat.add_argument("--workspace", "-w", type=str, default=str(DEFAULT_WORKSPACE_ROOT), help="Workspace root")
    p_mat.add_argument("--output", "-o", type=str, required=True, help="File to write matrix report")

    args = parser.parse_args()

    if args.command == "doctor":
        sys.exit(cmd_doctor(args))
    elif args.command == "init":
        sys.exit(cmd_init(args))
    elif args.command == "validate-recipe":
        sys.exit(cmd_validate_recipe(args))
    elif args.command == "matrix-verify":
        sys.exit(cmd_matrix_verify(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
