---
name: generative-media-studio
description: Multi-modal generative media studio for AI agents. Generates full 60s/90s vertical short videos, high-CTR thumbnails, voiceovers, video clipping/shorts creation, and social syndication packages.
version: 1.0.0
---

# Generative Media Studio Skill

This skill equips Antigravity AI agents with an end-to-end multi-modal media production engine. It generates high-engagement vertical short videos (9:16), cinematic YouTube thumbnails (16:9), AI character voiceovers (Cody & Nico), video clipping with virality scoring, and social packaging for YouTube Shorts, TikTok, Instagram Reels, X (Twitter), and Discord.

---

## 1. Quick Start & Capabilities

### Full Multi-Modal Short Video Generation

Generates script, voiceover, 9:16 animated video canvas, subtitles, thumbnail, and social captions:

```bash
uv run python scripts/generative_media_studio/director.py generate-short \
  --topic "Hidden Markov Regime Breakout" \
  --ticker "SPY" \
  --metric "+17.54% MO. RETURN" \
  --persona "CODY" \
  --outdir "media_outputs/shorts"
```

### High-CTR Thumbnail & Cover Art

Generates bold, high-contrast thumbnails with cybernetic gradients and metrics pills:

```bash
uv run python scripts/generative_media_studio/director.py generate-thumbnail \
  --title "Hidden Markov Regime Bot: +17.54% Gains" \
  --subtitle "Full 30-Day Multi-Broker Telemetry Audit" \
  --ticker "SPY" \
  --metric "+17.54% REALIZED ALPHA" \
  --ratio "16:9" \
  --output "media_outputs/sample_thumbnail.png"
```

### AI Video Clipping & Virality Scoring

Analyzes long-form MP4 videos and extracts ranked vertical 9:16 clips:

```bash
uv run python scripts/generative_media_studio/director.py clip-video \
  --input "logs/daily_quant_update.mp4" \
  --outdir "media_outputs/clips" \
  --duration 45.0
```

---

## 2. Python API Integration

```python
from scripts.generative_media_studio.director import generate_full_short_package
from scripts.generative_media_studio.thumbnail_generator import generate_thumbnail_card
from scripts.generative_media_studio.speech_synth import synthesize_speech
from scripts.generative_media_studio.video_stitcher import render_video
from scripts.generative_media_studio.clipping import clip_video_pipeline

# 1. Generate full package
package = generate_full_short_package(
    topic="Daily Quant Alpha Review",
    ticker="NVDA",
    metric_pill="+86% WIN RATE",
    persona="CODY",
    output_dir="media_outputs/nvda_short"
)
print("Video created at:", package["assets"]["video_mp4"])
print("Thumbnail at:", package["assets"]["thumbnail_16_9"])
```

---

## 3. Architecture & Modularity

1. **`director.py`**: Central orchestrator coordinating text $\to$ audio $\to$ visuals $\to$ video $\to$ distribution package.
2. **`speech_synth.py`**: Dual-engine voice synthesizer (Cartesia Sonic API + high-fidelity system fallback).
3. **`thumbnail_generator.py`**: PIL/TrueType generator for 16:9 landscape cards and 9:16 vertical cover arts with dynamic ticker & win rate badges.
4. **`video_stitcher.py`**: FFmpeg compositor producing 60fps/H.264 MP4 videos with auto-timed captions and brand overlays.
5. **`clipping.py`**: Intelligent video splitter with virality heuristic scoring and auto-crop to 9:16.

---

## 4. Compliance & Invariants

- **Zero Fake Data**: All performance numbers and metrics embedded into media MUST originate from authentic telemetry or state logs.
- **Mandatory Disclaimer**: Every generated video and social caption must include the educational notice: `⚠️ NFA — Research & Quantitative Telemetry Only`.
