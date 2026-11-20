---
name: studio
description: >-
  Use when creating procedural motion graphics, 60s/90s vertical shorts, high-CTR thumbnails, interactive HTML/SVG/Mermaid explainers, Cartesia voiceovers, FaceTime voice calls, or Sol mascot videos. Combines Anti-Slop 5-stage animation, Generative Media Studio, Vision Board, and Brand Tokens.
version: "2.0.0"
---

# /studio — Procedural Motion Graphics, Visual Explainers, Voice & Anti-Slop Media

Single-pass Category Master Skill. Invoking `/studio` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/studio`
- **Compatible Aliases:** `/studio`, `/media`, `/video`, `/voice`, `/visual`
- **Absorbed Legacy Skills (8):** `/anti-slop-studio`, `/generative-media-studio`, `/multimodal-visual-explainer`, `/cartesia-voice`, `/agent-voice-facetime`, `/social-media-vision-board`, `/brand-identity`, `/sol-ai-sun-agent`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `topic` | `string` | `` | Subject, product, or trade/data story to turn into media |
| `format` | `enum(short_9x16|video_16x9|explainer_html|thumbnail|voice_call|storyboard)` | `short_9x16` | Target output format |
| `persona` | `enum(SOL|CODY|NICO|DOUG|NEUTRAL)` | `NEUTRAL` | Voice/character persona |
| `outdir` | `path` | `content/productions/latest` | Output directory for staged assets |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **Zero AI Slop:** Ban generic stock-gradient filler, buzzword fluff, mismatched audio-visual pacing, and repetitive templates; enforce ~80% ASDSTE 100 technical clarity.
- **Audio-First Discipline:** Generate and verify voice timing (`voice/audio.wav` + exposure sheet) BEFORE rendering frames so procedural motion locks tightly to cadence.
- **Brand & Dark-Mode Vision Board Standards:** Quant visuals use `#0f172a`/`#020617`/`#05070a` dark backgrounds, `#4ade80` demand/ROI, `#ef4444` stop hunts, `#2dd4bf` cyan callouts, `#a855f7` HMM signatures; respect `brand-identity` design tokens.
- **Mandatory NFA/SEC Disclaimers:** Every trading/crypto/options graphic, caption, or video overlay MUST embed compliant risk disclaimers (`Not financial advice. Past results != future profits.`).
- **Staging-Only Default:** Save rendered media/HTML locally and open/verify pixels visually before any external post (`AUTH:` required for publishing).

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Creative Brief, Brand Tokens & Compliance Framing
- **Depends On:** None (Entry Gate)
- **Inputs:** topic, persona, target format, brand tokens
- **Actions:** Select visual archetype (`Sol Open Mic`, `Quant Deep Dive`, `Trade Recap`, `Liquidity Guide`, `Interactive Explainer`), load `brand-identity` tokens, draft curiosity hook (0-10s pattern interrupt, 10-20s proof, 20-30s roadmap), and attach entity/NFA disclaimers.
- **Gate Check:** Script hook, brand palette, and compliance text defined with zero AI slop.
- **Artifacts:** `creative_brief_and_script.md`

### S2: Audio-First Voice & Speech Synthesis
- **Depends On:** `S1`
- **Inputs:** script text, persona ID, Cartesia/VAD bridge
- **Actions:** Generate clean voice audio via Cartesia AI (`cartesia-voice`) or `anti-slop-studio voice` (`voice/audio.wav`); for live conversational voice interfaces, configure `agent-voice-facetime` VAD WebSocket states (`ringing->connected->listening/thinking/speaking`).
- **Gate Check:** Audio asset generated, non-empty, audible clarity verified.
- **Artifacts:** `voice/audio.wav`

### S3: Exposure Sheet & Leica Reel Timing
- **Depends On:** `S2`
- **Inputs:** `voice/audio.wav`, word timestamps
- **Actions:** Compile frame-accurate `words/exposure_sheet.json` and `cues/leica_reel.json` mapping visual beats, callout arrows, and metric pills to audio cadence.
- **Gate Check:** Exposure sheet and Leica reel cues sync to audio duration with zero orphan cues.
- **Artifacts:** `words/exposure_sheet.json, cues/leica_reel.json`

### S4: Procedural Motion Graphics & Scene-as-Code
- **Depends On:** `S3`
- **Inputs:** Leica reel cues, data/charts
- **Actions:** Generate programmatic scenes (`anti-slop-studio scene`, `generative_media_studio/director.py`, SVG/Canvas spring-physics motion, or self-contained interactive HTML5 explainers/Sweatbox players via `multimodal-visual-explainer` + `ui-pro-max`).
- **Gate Check:** Contact sheet (`scene/contact_sheet.png`) or standalone HTML builds cleanly without runtime errors.
- **Artifacts:** `scene/contact_sheet.png, scene/sweatbox.html`

### S5: Final Render & Pixel-Level Visual QA
- **Depends On:** `S4`
- **Inputs:** rendered `.mp4`, `.png` thumbnail, or HTML
- **Actions:** Render final `9:16` / `16:9` MP4 (`anti-slop-studio render`) and high-CTR thumbnail (`generate-thumbnail`); inspect actual rendered frames/HTML via `take_screenshot` or `ffprobe` to verify contrast, legibility, and zero clipping.
- **Gate Check:** Non-empty video/HTML/thumbnail verified visually and via `ffprobe`/file size check.
- **Artifacts:** `render/final.mp4, thumbnail.png`

### S6: Syndication Staging & Outcome Report
- **Depends On:** `S5`
- **Inputs:** verified media bundle
- **Actions:** Package platform-ready metadata/captions/disclaimers locally inside `outdir` (awaiting `AUTH:` before publishing) and report exact file paths and verification results.
- **Gate Check:** All rendered artifacts verified on disk with zero unauthorized external posts.
- **Artifacts:** `syndication_manifest.json`

## 4. Fallback & Escalation Rules

- **Cartesia/API Unavailable:** Fall back cleanly to local TTS / silent timed Leica reel + HTML5 interactive explainer while logging the missing API credential.
- **FFmpeg / Renderer Missing:** Output self-contained HTML5/SVG animated Sweatbox + storyboard frames and clearly report missing local binary.
- **Visual Clipping Detected in S5:** Adjust typography scale/margins and re-render up to 3 iterations before halting.

## 5. Single-Pass Completion Criteria

- [ ] Audio-first exposure sheet matches visual timing.
- [ ] Rendered MP4/HTML/thumbnail exists, is non-empty, and passed visual/pixel QA.
- [ ] Mandatory brand tokens and NFA/SEC or Charity disclaimers included.
- [ ] Zero unauthorized social publishes executed without explicit `AUTH:`.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `anti-slop-studio` | Global | [`SKILL.md`](./modules/anti-slop-studio/SKILL.md) | Absorbed into `/studio` |
| `generative-media-studio` | Global | [`SKILL.md`](./modules/generative-media-studio/SKILL.md) | Absorbed into `/studio` |
| `multimodal-visual-explainer` | Global | [`SKILL.md`](./modules/multimodal-visual-explainer/SKILL.md) | Absorbed into `/studio` |
| `cartesia-voice` | Global | [`SKILL.md`](./modules/cartesia-voice/SKILL.md) | Absorbed into `/studio` |
| `agent-voice-facetime` | Global | [`SKILL.md`](./modules/agent-voice-facetime/SKILL.md) | Absorbed into `/studio` |
| `social-media-vision-board` | Global | [`SKILL.md`](./modules/social-media-vision-board/SKILL.md) | Absorbed into `/studio` |
| `brand-identity` | Local-Merged | [`SKILL.md`](./modules/brand-identity/SKILL.md) | Absorbed into `/studio` |
| `sol-ai-sun-agent` | Local-Merged | [`SKILL.md`](./modules/sol-ai-sun-agent/SKILL.md) | Absorbed into `/studio` |

- **Companion Plugins:** `ui-pro-max`, `gemini-api-cli`, `generative_ui`
- **Companion MCP Servers:** `chrome-devtools-mcp`, `market-haven-social-media`
