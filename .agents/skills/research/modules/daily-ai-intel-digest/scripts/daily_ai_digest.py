#!/usr/bin/env python3
"""
Standalone execution utility for daily-ai-intel-digest skill.
Wraps the Daily AI Intel Reporter engine for agent workflows.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPORTER_PROJECT_DIR = Path("/Users/malcolm/.gemini/antigravity-ide/scratch/daily-ai-intel-reporter")
CLI_PATH = REPORTER_PROJECT_DIR / "src" / "cli.py"


def run_reporter_cli(args_list):
    if not CLI_PATH.exists():
        print(f"Error: Reporter engine not found at {CLI_PATH}", file=sys.stderr)
        sys.exit(1)
    cmd = [sys.executable, str(CLI_PATH)] + args_list
    proc = subprocess.run(cmd, cwd=str(REPORTER_PROJECT_DIR))
    sys.exit(proc.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Daily AI Intel & Observability Dispatcher (Agent Skill Utility)"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Action to execute")

    # Generate
    p_gen = subparsers.add_parser("generate", help="Generate fresh daily report")
    p_gen.add_argument("--send", action="store_true", help="Send to recipients")
    p_gen.add_argument("--format", choices=["both", "html", "markdown"], default="both")
    p_gen.add_argument("--transport", choices=["auto", "smtp", "sendmail", "spool"], default="auto")

    # Send
    p_send = subparsers.add_parser("send", help="Generate and send to all recipients")

    # Preview
    p_prev = subparsers.add_parser("preview", help="Preview latest briefing in terminal")

    # Schedule
    p_sched = subparsers.add_parser("schedule", help="Inspect or install daily schedule")
    p_sched.add_argument("--install", action="store_true", help="Install crontab and launchd daily schedule")
    p_sched.add_argument("--check", action="store_true", help="Check active schedule status")

    # Test
    subparsers.add_parser("test", help="Run system diagnostics")

    args, unknown = parser.parse_known_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    forward_args = [args.subcommand]
    if args.subcommand == "generate":
        if args.send:
            forward_args.append("--send")
        forward_args.extend(["--format", args.format, "--transport", args.transport])
    elif args.subcommand == "schedule":
        if args.install:
            forward_args.extend(["--install", "--install-launchd"])
        else:
            forward_args.append("--check")

    forward_args.extend(unknown)
    run_reporter_cli(forward_args)


if __name__ == "__main__":
    main()
