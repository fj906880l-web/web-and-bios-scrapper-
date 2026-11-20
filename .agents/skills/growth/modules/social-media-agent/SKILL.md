---
name: social-media-agent
description: "Handles creating marketing copy and posting event updates autonomously to Twitter (X) and LinkedIn using the Google Antigravity Python SDK and Playwright browser automation."
---

# Social Media & Marketing Subagent Skill

This workspace skill registers and describes the capability of the Social Media / Marketing Subagent to handle event distribution.

## Capabilities

- **Copywriting & Master Deck Template**: Leverages the Gemini API (via the `google-antigravity` SDK) to craft engaging messages adhering strictly to the Market Haven Master Deck Social Media Template:
  - **Dual-Pillar Focus**: Emphasizes Surplus Food Rescue & Distribution + Vocational Technology Education.
  - **X (Twitter)**: Short-form hook + dual mission summary + GoFundMe CTA (`https://gofund.me/7047dcec7`) + hashtags (`#MarketHaven #FoodSecurity #TechForGood #ZeroWaste #CommunityFirst`) + horizontal line + mandatory mini legal disclaimer.
  - **LinkedIn**: Structured header + dual-pillar breakdown + impact funding allocation + partnership CTAs + hashtags + horizontal line + mandatory legal & regulatory disclosure.
- **Playwright / Buffer Automation**: Publishes updates via Buffer API or Playwright browser automation.
- **Ledger Ingestion**: Syncs matching events from the local SQLite database (`market_haven.db`) and high-level JSON dataset (`data/social_posts_dataset.json`).

## Workflow Execution

To trigger the coordinator subagent execution (which runs the main social media loop and handles copy + media generation), run the script from the root of the project:

```bash
# Execute a dry-run check of the copy and media generation logic
python3.11 scripts/social_media_coordinator.py --dry-run

# Force a specific day's theme for previewing
python3.11 scripts/social_media_coordinator.py --force monday --dry-run

# Run the live coordinator flow
python3.11 scripts/social_media_coordinator.py
```

Standalone scripts can still be run for individual debugging:

```bash
python3.11 scripts/social_media_agent.py --dry-run
python3.11 scripts/content_calendar_agent.py --dry-run
```
