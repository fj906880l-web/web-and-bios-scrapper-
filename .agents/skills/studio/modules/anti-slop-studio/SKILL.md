---
name: anti-slop-studio
description: >-
  Antigravity 5-Stage Animation Studio Pipeline for zero-slop video and social media content creation.
  Based on Jake Van Clief's Disney 1930s animation studio methodology (Audio First -> Exposure Sheet
  -> Leica Reel -> Scene as Code & Pencil Tests -> Render & Multi-Platform Syndication).
  Use whenever generating social media videos, daily digests, client walkthroughs, or YouTube Shorts.
version: 2.0.0
---

# Anti-Slop 5-Stage Animation Studio Pipeline

## Overview
The `anti-slop-studio` skill provides an end-to-end, multi-stage production pipeline for creating high-retention, verified social media videos (9:16 vertical shorts and 16:9 landscape videos) without AI slop. 

Rooted in the 1930s Disney animation studio process (Jake Van Clief, [YouTube: EhWlGingCl0](https://youtu.be/EhWlGingCl0)), the pipeline enforces strict human-in-the-loop review contracts between isolated stages:
1. **Stage 1 (Voice)**: Director's brief + spoken script -> chunked audio synthesis -> human audio check.
2. **Stage 2 (Words)**: Audio transcription -> word-level exposure sheet -> script alignment discrepancy check.
3. **Stage 3 (Cues)**: Storyboard beats anchored to transcript phrases -> Leica reel timing table before graphics are drawn.
4. **Stage 4 (Scene)**: Modular visual components (Sol mascot, terminal code, 3D volatility surface) -> contact sheet pencil tests -> HTML5 synchronized sweatbox review.
5. **Stage 5 (Render)**: FFmpeg multi-track compositor -> dual-aspect MP4s -> high-CTR cybernetic thumbnails -> YouTube metadata & chapters.

---

## Dependencies
- `ffmpeg` (installed at `/opt/homebrew/bin/ffmpeg` or on PATH)
- `python3` (or `uv run python`) with `pillow` (>=11.0.0)
- `social-media-vision-board`: Visual design tokens, dark mode `#0b0f19`, and legal disclaimers
- `harness-engineering`: Agent Harness v2.0 verification and security gating

---

## Quick Start

### 1. Full Autonomous Production
Generate a complete, staged 9:16 vertical video with high-CTR thumbnails and metadata:

```bash
anti-slop-studio produce \
  --dir "content/productions/sol_trade_roast" \
  --topic "Sol Open Mic Bad Trade Roast" \
  --persona "SOL" \
  --ticker "TSLA" \
  --metric "-$8,400 P&L" \
  --ratio "9:16"
```

### 2. Backward-Compatible Call
```bash
uv run python scripts/generative_media_studio/director.py generate-short \
  --topic "Hidden Markov Regime Breakout" \
  --ticker "SPY" \
  --metric "+17.54% MO. RETURN" \
  --persona "CODY" \
  --outdir "media_outputs/social"
```

### 3. Generate High-CTR Cover Art / Thumbnail
```bash
anti-slop-studio generate-thumbnail \
  --title "Walk-Forward Regime Bot: +17.54% Alpha" \
  --subtitle "30-Day Multi-Broker Telemetry Audit" \
  --ticker "SPY" \
  --metric "+17.54% ALPHA" \
  --ratio "16:9" \
  --output "media_outputs/thumbnail.png"
```

---

## Utility Scripts & CLI Subcommands

The CLI entrypoint is located at `/Users/malcolm/.gemini/config/scripts/anti-slop-studio`:

### Subcommands:
- `anti-slop-studio init --dir <DIR> [--topic <TOPIC>] [--persona <PERSONA>]`
  Initializes standard folder structure with `CLAUDE.md`, `CONTEXT.md`, `brief.md`, and starter `script.md`.
- `anti-slop-studio voice --dir <DIR> [--persona <PERSONA>] [--reroll-chunk <ID>]`
  Synthesizes script into audio chunks in `voice/chunks/` and outputs master `voice/audio.wav`.
- `anti-slop-studio words --dir <DIR>`
  Extracts word-level timestamps into `words/exposure_sheet.json` and produces `words/alignment_diff.md`.
- `anti-slop-studio cues --dir <DIR> [--ratio 9:16|16:9]`
  Calculates the Leica Reel timing table (`cues/leica_reel.json` & `cues/leica_reel.md`).
- `anti-slop-studio scene --dir <DIR> [--ratio 9:16|16:9]`
  Renders keyframe stills in `scene/stills/`, builds the Contact Sheet (`scene/contact_sheet.png`), and generates `scene/sweatbox.html`.
- `anti-slop-studio render --dir <DIR> [--persona <PERSONA>]`
  Runs FFmpeg to render final video (`render/final_9x16.mp4`), thumbnails, and syndication metadata.
- `anti-slop-studio produce --dir <DIR> ...`
  Executes all 5 stages end-to-end.

---

## Workflow & Production Folder Structure

Every production follows a strict contract where each folder owns its intermediate artifacts:

```
production_dir/
  ├── CLAUDE.md          # Stage commands and project paths
  ├── CONTEXT.md         # Pipeline contract table and human review gates
  ├── brief.md           # Director's Brief (target audience, central metaphor, persona)
  ├── script.md          # Spoken script (read by voice clone / audio engine)
  ├── voice/             # Stage 1: audio.wav, audio_chunks/
  ├── words/             # Stage 2: exposure_sheet.json, words.tsv, alignment_diff.md
  ├── cues/              # Stage 3: storyboard.md, leica_reel.json, leica_reel.md
  ├── scene/             # Stage 4: stills/, contact_sheet.png (Pencil Test), sweatbox.html
  └── render/            # Stage 5: final_9x16.mp4, final_16x9.mp4, thumbnails, metadata.json
```

### Review Gates:
1. **Audio Gate**: Listen to `voice/audio.mp3`. If one chunk sounds robotic or slurred, reroll only that chunk (`--reroll-chunk <ID>`).
2. **Transcript Gate**: Review `words/alignment_diff.md`. Confirm all ticker symbols and technical terms are spelled accurately.
3. **Storyboard Gate**: Review `cues/leica_reel.md`. Ensure visual scene transitions align with key spoken phrases before drawing frames.
4. **Sweatbox Gate**: Open `scene/sweatbox.html` in a browser. Review audio playback synchronized with stills.
5. **Render Gate**: Play `render/final_9x16.mp4`. Verify subtitle sync, audio ducking, and thumbnail impact.

---

## Human Input & Approval Gate Email Notifications

Whenever ANY video production, media artifact, or social media post requires human input, review, sign-off, or approval:
- **Automatic Email Dispatch**: An automated HTML review email is immediately dispatched to **Malcolm (`fj906880l@gmail.com`)** via authenticated Gmail SMTP.
- **Embedded Artifacts & Links**: Emails include direct `file://` links to `sweatbox.html`, `contact_sheet.png`, `audio.mp3`, and `exposure_sheet.json`, with the pencil test contact sheet attached directly to the message.
- **Social Media Post Draft Alerts**: Any staged social media copy (X/Twitter, YouTube Shorts, LinkedIn, TikTok) in `content/pending/` or `PENDING_APPROVAL` status immediately emails Malcolm with the full draft text and approval commands.
- **Audit Ledger**: All dispatched notifications are immutably logged to `/Users/malcolm/.gemini/config/logs/human_review_ledger.jsonl`.

### Notification CLI Commands:
```bash
# Send human review alert for a video production
anti-slop-studio notify-review \
  --dir "content/productions/regime_alpha" \
  --stage "Stage 4: Sweatbox Review" \
  --reason "Pencil test contact sheet ready for director sign-off." \
  --topic "Regime Alpha Walkthrough" \
  --ticker "SPY" \
  --metric "+17.54% ALPHA"

# Send human review alert for a staged social media text post
anti-slop-studio notify-post \
  --title "SPY Breakout Staged Post" \
  --content "Gaussian HMM confirms institutional liquidity sweep on $SPY." \
  --platform "X" \
  --persona "CODY"
```

---

## Cross-Project Integration Map

The studio pipeline is actively integrated into:
- **`regime-trader` & `trading-bot-`**: `scripts/anti_slop_video_generator.py` produces daily alpha videos and Sunday 90s masterclasses, staging them into `content/pending/` and `content/approved/` with automatic email dispatch to Malcolm on review gates.
- **`daily-ai-intel-reporter`**: `src/anti_slop_video_digest.py` produces 60-second video digest shorts for daily newsletters via `python3 src/cli.py video`.
- **`market-haven-consulting`**: `scripts/produce_consulting_walkthrough.py` generates enterprise client walkthroughs.
- **`b2b`**: `scripts/generate_b2b_outreach_video.py` generates outbound video demos.
- **`nonprofit`**: `scripts/generate_donor_impact_video.py` generates transparent donor impact reports.
- **`allara-app`**: `scripts/generate_model_release_video.py` creates model release video cards.


---

## Unigent Stateful Agent Integration

To orchestrate the 5-stage studio pipeline from TypeScript/Bun using the Unigent SDK:

```bash
unigent /Users/malcolm/.gemini/config/scripts/anti_slop_studio/anti_slop_studio.ts \
  --topic "Regime Alpha Walkthrough" \
  --ticker "SPY" \
  --metric "+17.54% ALPHA" \
  --persona "CODY"
```

---

## Common Mistakes & Failure Modes

1. **Drawing Before Timing (The Slop Trap)**: Never animate or render frames before the Leica Reel is computed. Fixing a beat in a text file is 100x cheaper than re-rendering a video.
2. **Monolithic Audio**: Always generate audio in discrete chunks. Never generate a 90-second audio track as a single un-rerollable block.
3. **Skipping Exposure Sheet Diff**: Always inspect `alignment_diff.md` to ensure technical jargon (e.g. "HMM", "Sharpe", "p-value") is not slurred or dropped by TTS engines.
4. **Missing Legal Compliance**: All social media videos MUST include the mandatory disclaimer watermark: `⚠️ NFA — Research & Quantitative Telemetry Only`.
