---
name: phoenix-reach-optimizer
description: >-
  Analyzes, scores, and optimizes social media posts and marketing copy based on the exact
  mathematical ranking weights of X's open-source Phoenix recommendation algorithm (xai-org/x-algorithm).
  Maximizes high-multiplier actions (Copy-Link +20.0, Mutual Reply +15.0) and dodges severe penalties
  (Report -234.0, Low-Fav Clickbait Dwell).
---

# Phoenix Reach Optimizer Skill

## Overview
Reverse-engineered directly from xAI's open-source recommendation system (`xai-org/x-algorithm`), this skill enables autonomous agents to systematically audit and optimize social posts for maximum algorithmic reach and engagement.

Key ranking signals embedded:
- **ShareViaCopyLink**: `+20.0` (The single highest positive multiplier)
- **BidirectionalFollowReply**: `+15.0` (Mutual follow dialogue)
- **Reply / Quote / DM Share**: `+5.0`
- **FollowAuthor**: `+4.0`
- **Retweet / Favorite**: `+1.0` / `+0.5`
- **External Link Friction**: `0.20` base weight with `0.75x` out-of-network penalty
- **Report Penalty**: `-234.0`
- **Mute / Not Interested**: `-58.8` / `-43.2`

## Dependencies
- Standard Python 3.10+ installation
- `/Users/malcolm/.gemini/config/scripts/phoenix_reach_optimizer.py`

## Quick Start
Analyze a draft post directly from the command line:

```bash
python3 /Users/malcolm/.gemini/config/skills/phoenix-reach-optimizer/scripts/phoenix_reach.py analyze \
  --text "Bookmark this quant trading blueprint for reference. What indicator do you rely on most?" \
  --has-media \
  --output ./reach_analysis.json
```

## Utility Scripts

### `phoenix_reach.py analyze`
Evaluates draft copy and outputs concrete tactical recommendations to maximize algorithmic distribution:
- `--text <string>`: Text copy to analyze.
- `--file <path>`: Alternatively, load text from a file.
- `--has-media`: Specify if visual media (image/video) is attached (+0.05 dwell boost).
- `--has-link`: Specify if an external link is in the main body (triggers anti-clickbait warning).
- `--output <path>`: Required output JSON file destination.

### `phoenix_reach.py score`
Computes the net Phoenix score using predicted action probabilities:
- `--probs-json <json_string>`: JSON mapping of predicted probabilities for actions.
- `--file <path>`: Path to probabilities JSON file.
- `--out-of-network`: Apply the 0.75x out-of-network discount.
- `--output <path>`: Required output JSON file destination.

## Workflow

### 1. Draft Pre-Flight Inspection
Before queuing or publishing any post via `social-scheduler-launcher.sh` or `social-media-vision-board`:
1. Run `phoenix_reach.py analyze` on the candidate text.
2. Read the resulting JSON artifact.
3. Check that the estimated multiplier is $\ge 1.4\times$.

### 2. Copy Structuring Guidelines
- **Include Save/Bookmark Triggers**: Mention "cheat sheet", "reference guide", "system breakdown", or "save this" to capture the `+20.0` copy-link signal.
- **End with Open-Ended Dialogue**: Conclude with a specific, opinion-inviting question to drive replies (`+5.0`) and mutual discussion (`+15.0`).
- **Never Put Links in the Main Post**: Move external links to the first reply comment. External links in main tweets face low weights (`+0.20`), out-of-network penalties (`0.75x`), and risk low-dwell clickbait penalties if users quickly bounce.

## Common Mistakes
1. **Posting naked external links**: Drops organic impressions by up to 60% due to out-of-network discounts.
2. **Generic broadcast without questions**: Yields zero replies, missing the high +15.0 mutual reply boost.
3. **Relying solely on Likes**: Likes carry only a `+0.5` weight, meaning one copy-link (+20.0) is worth 40 likes algorithmically.
