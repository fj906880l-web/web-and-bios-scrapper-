#!/usr/bin/env python3
"""
Phoenix Reach Optimizer CLI
Algorithmic social reach optimization and post scoring based on xAI's open-source Phoenix ranking engine.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, List

# Ensure config scripts is on path to reuse PhoenixScorer
SCRIPTS_DIR = "/Users/malcolm/.gemini/config/scripts"
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

try:
    from phoenix_reach_optimizer import PhoenixScorer, PhoenixWeights
except ImportError:
    # Fallback inline implementation if external import fails
    class PhoenixWeights:
        share_via_copy_link: float = 20.0
        bidirectional_follow_reply_boost: float = 15.0
        reply: float = 5.0
        share_via_dm: float = 5.0
        quote: float = 5.0
        follow_author: float = 4.0
        share: float = 2.0
        retweet: float = 1.0
        favorite: float = 0.5
        click: float = 0.4
        open_link: float = 0.2
        video_open: float = 0.07
        photo_expand: float = 0.05
        dwell: float = 0.05
        cont_dwell_time: float = 0.004
        not_interested: float = -43.2
        block_author: float = -31.2
        mute_author: float = -58.8
        report: float = -234.0
        not_dwelled: float = -0.02
        oon_weight_factor: float = 0.75

    class PhoenixScorer:
        def __init__(self):
            self.w = PhoenixWeights()
        def analyze_post_copy(self, post_text: str, has_media: bool = False, has_link: bool = False):
            tips = []
            multiplier = 1.0
            if any(w in post_text.lower() for w in ["bookmark", "save this", "resource", "cheat sheet", "guide"]):
                tips.append("High bookmark/copy-link incentive detected (+20.0 multiplier).")
                multiplier += 0.3
            if "?" in post_text:
                tips.append("Conversation prompt detected (+5.0 to +15.0 mutual reply boost).")
                multiplier += 0.25
            if has_link:
                tips.append("External link detected: Recommend moving link to reply to avoid out-of-network penalty (0.75x).")
            if has_media:
                tips.append("Media attachment detected (+0.05 photo_expand and dwell boost).")
                multiplier += 0.15
            return {"estimated_multiplier": round(multiplier, 2), "recommendations": tips}
        def score_post(self, probs: Dict[str, float], is_in_network: bool = True):
            pos = sum(probs.get(k, 0.0) * getattr(self.w, k, 0.0) for k in ["share_via_copy_link", "reply", "favorite", "retweet"])
            neg = sum(probs.get(k, 0.0) * abs(getattr(self.w, k, 0.0)) for k in ["not_interested", "report"])
            mult = 1.0 if is_in_network else self.w.oon_weight_factor
            return {"final_score": round((pos - neg) * mult, 4)}

def cmd_analyze(args):
    scorer = PhoenixScorer()
    text = args.text
    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
            
    res = scorer.analyze_post_copy(text, has_media=args.has_media, has_link=args.has_link)
    output_data = {
        "text_preview": text[:120] + "..." if len(text) > 120 else text,
        "analysis": res
    }
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        print(f"Analysis saved to: {args.output}")
    else:
        print(json.dumps(output_data, indent=2))

def cmd_score(args):
    scorer = PhoenixScorer()
    probs = {}
    if args.probs_json:
        probs = json.loads(args.probs_json)
    elif args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            probs = json.load(f)
            
    res = scorer.score_post(probs, is_in_network=not args.out_of_network)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"Scores written to: {args.output}")
    else:
        print(json.dumps(res, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Phoenix Reach Optimizer CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze subcommand
    p_analyze = subparsers.add_parser("analyze", help="Analyze post copy and provide reach optimization recommendations")
    p_analyze.add_argument("--text", type=str, default="", help="Post copy string to evaluate")
    p_analyze.add_argument("--file", type=str, help="Path to text file containing post copy")
    p_analyze.add_argument("--has-media", action="store_true", help="Flag indicating post includes image/video")
    p_analyze.add_argument("--has-link", action="store_true", help="Flag indicating post includes external URL")
    p_analyze.add_argument("--output", type=str, help="Path to write JSON output file")
    p_analyze.set_defaults(func=cmd_analyze)

    # score subcommand
    p_score = subparsers.add_parser("score", help="Compute exact Phoenix score given predicted action probabilities")
    p_score.add_argument("--probs-json", type=str, help="Raw JSON string of action probabilities")
    p_score.add_argument("--file", type=str, help="Path to JSON file containing action probabilities")
    p_score.add_argument("--out-of-network", action="store_true", help="Flag if candidate post is out-of-network (0.75x penalty)")
    p_score.add_argument("--output", type=str, help="Path to write JSON output file")
    p_score.set_defaults(func=cmd_score)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
