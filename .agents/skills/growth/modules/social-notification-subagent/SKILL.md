---
name: social-notification-subagent
description: Unified Social Media Orchestrator Swarm & Multi-Channel Notification Subagent. Manages Cody & Nico personas, Cartesia AI voice tags, Buffer posting schedules, Discord webhooks, and HTML trade notifications.
---

# Social & Notification Subagent Workflow

## Overview

This skill orchestrates the unified Social Media and System Notification pipelines for Regime Trader Bot, reading configuration and schedule bounds directly from:

- `market_haven_social_dashboard.html`
- `antigravity_social_execution_prompt.md`
- `core/unified_social_notification_agent.py`

## Core Responsibilities

1. **Cody Mascot Persona (Polar Bear Quant & Roast Master)**
   - Weekly schedule cadence (Sun: Validation Review, Mon: Live Preview, Tue: Signal Breakdown, Wed: Order-Book Delta, Thu: Options Squeeze, Fri: Market-Close Roast, Sat: Weekly Recap).
   - Voice: Cartesia `sonic-english`, `gruff-analyst-baritone`, 0.95x speed. Inline SSML tags (`[chuckle]`, `[sigh]`, `[deadpan]`, `[siren-fx]`, `[frost-sizzle]`).

2. **Nico Persona (ANTIGRAVITY-TRADER-01)**
   - 2x/Daily cadence (Morning Alpha Alert & Midday Order-Book Depth).
   - Bilingual EN/ES flipping protocol with **Bright Yellow (`#FFD700`)** captions for English and **Cyan/Teal (`#00E5FF`)** captions for Spanish.
   - Voice: Cartesia `sonic-multilingual`, `barbershop-guy-energetic`, 1.00x speed.

3. **Buffer & Social Media Dispatch**
   - HITL Social Approval Gatekeeper (`DRAFT` → `APPROVED` → `PUBLISHED`).
   - Appends `"NFA — research purposes only"` (FINRA compliance tag) on all trade posts.

4. **Multi-Channel System Notifications**
   - Discord Embed Broadcaster (`#polar-bear`, `#bull-momentum`, `#bear-breakdown`, `#telemetry-health`).
   - Morning Brew HTML Email Trade Notifications across Alpaca & OANDA.

5. **Character Design/Voice Lock & 4-Trigger Retrieval Alignment (`core/character_template_registry.py` & `core/trigger_retrieval_router.py`)**
   - **Deterministic Visual & Character Design Tokens:** Every social and newsletter visual prompt injects verified turnaround tokens from `config/character_voice_templates.json` (`NICO_V1`: silver/chrome-blue humanoid android, glowing cyan temple circuitry, round purple/violet sunglasses, crisp white button-down dress shirt, charcoal slacks; `CODY_V1`: upright photorealistic white polar bear, brown/olive MOLLE tactical plate-carrier vest, leather aviator goggles on forehead). Zero freeform visual prompt drift.
   - **Immutable Voice Lock & Pre-Publish Guard (`VoiceAndTemplateGuard`):** Enforces Cody (`sonic-english`, `gruff-analyst-baritone`, English-only, inline SSML tags) and Nico (`sonic-multilingual`, `barbershop-guy-energetic`, EN `#FFD700` / ES `#00E5FF` caption protocol), mandatory NFA/FINRA disclosures, and deterministic rejection/rewriting of generic corporate AI filler.
   - **Strict 1-to-1 Trigger-Matched Retrieval (`Trade` | `Breaking News` | `Saturday` | `Tuesday`):**
     - `Trade`: Deterministic structured query (`monitoring/trade_notifications_stream.jsonl`, `monitoring/orders.json`, `monitoring/trade_ledger.json`) gated by `is_valid_broker_order_id`; halts fail-closed on missing structured fields (zero watchlist substitution or `$100.00` price defaults).
     - `Breaking News`: Verified `published_at` recency window ($\le 180$ min) + SHA-256 deduplication + active house positioning/regime lookup.
     - `Saturday`: Strict 7-day `[now - 7d, now]` closed/open trade, 4-broker performance, and weekly regime shift aggregation (zero stale prior-week leakage).
     - `Tuesday`: Rolling Monday–Tuesday week-to-date action + active `orders.json` bracket setups + forward mid-week macro/options-skew catalysts.
   - **Context-to-Template Audit Trail:** Logs `(character_id + version, template_id, trigger_type, source_records + timestamps)` to `monitoring/template_alignment_audit.jsonl` on every generation payload.

## Execution Command

```bash
.venv/bin/python core/unified_social_notification_agent.py
.venv/bin/python scripts/verify_8_path_alignment_dryrun.py
```
