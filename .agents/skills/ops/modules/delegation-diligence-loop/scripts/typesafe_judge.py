#!/usr/bin/env python3
"""
TypeSafe System One Semantic Judgment Helper for Delegation-Diligence Loop.
Loads TYPESAFE_API_KEY securely from ~/.gemini/config/.env.
Never hardcodes credentials.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

ENV_PATH = os.path.expanduser("~/.gemini/config/.env")

def load_typesafe_key():
    if not os.path.exists(ENV_PATH):
        raise FileNotFoundError(f"Configuration file {ENV_PATH} not found.")
    
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("TYPESAFE_API_KEY="):
                return line.split("=", 1)[1].strip()
    
    raise ValueError("TYPESAFE_API_KEY not found in ~/.gemini/config/.env")

def judge(state: str, instruction: str, q_type: str = "choice", options: list = None):
    api_key = load_typesafe_key()
    url = "https://api.typesafe.ai/v1/systemone"
    
    if q_type == "choice":
        criteria = {opt: f"Evaluation outcome is {opt}" for opt in (options or ["Pass", "Fail"])}
        question_def = {
            "type": "choice",
            "instructions": instruction,
            "criteria": criteria
        }
    elif q_type == "noul":
        criteria = {
            "yes": f"Condition holds: {instruction}",
            "no": f"Condition does not hold: {instruction}"
        }
        question_def = {
            "type": "noul",
            "instructions": instruction,
            "criteria": criteria
        }
    elif q_type == "score":
        levels = options or ["Low", "Medium", "High"]
        question_def = {
            "type": "score",
            "instructions": instruction,
            "criteria": levels
        }
    else:
        raise ValueError(f"Unsupported primitive type: {q_type}")

    payload = {
        "model": "jev-latest",
        "state": state,
        "questions": {
            "diligence_check": question_def
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Antigravity-Delegation-Diligence/1.0"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        sys.stderr.write(f"HTTP Error {e.code}: {err_msg}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Execution error: {str(e)}\n")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="TypeSafe System One Multi-Primitive Judgment Runner")
    parser.add_argument("--state", required=True, help="Text state or summary to judge")
    parser.add_argument("--instruction", required=True, help="Specific question/instruction for judgment")
    parser.add_argument("--type", choices=["choice", "noul", "score"], default="choice", help="Primitive type (choice, noul, score)")
    parser.add_argument("--options", default="Pass,Fail", help="Comma-separated options or score levels")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    options = [opt.strip() for opt in args.options.split(",") if opt.strip()]
    
    res = judge(args.state, args.instruction, args.type, options)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        answer = res.get("answers", {}).get("diligence_check", {})
        if args.type == "choice":
            choice = answer.get("choice", "Unknown")
            conf = answer.get("confidence", 0.0)
            probs = answer.get("probabilities", {})
            print(f"Decision: {choice} (Confidence: {conf:.2%})")
            print(f"Probabilities: {probs}")
        elif args.type == "noul":
            prob = answer.get("noul", 0.0)
            print(f"Condition Probability (Noul): {prob:.2%}")
        elif args.type == "score":
            score_val = answer.get("score", 0.0)
            conf = answer.get("confidence", 0.0)
            legend = answer.get("legend", {})
            idx = str(int(round(score_val)))
            label = legend.get(idx, f"Level {score_val}")
            print(f"Score: {score_val} ({label}) [Confidence: {conf:.2%}]")

if __name__ == "__main__":
    main()
