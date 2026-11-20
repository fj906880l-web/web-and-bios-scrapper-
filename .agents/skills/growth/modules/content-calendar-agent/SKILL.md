---
name: content-calendar-agent
description: >-
  Automated weekly social media content calendar for Market Haven nonprofit.
  Posts themed content 3x/week (Motivation Monday, Community Wednesday, Fun Fact Friday)
  to Twitter/X and LinkedIn using Gemini AI content generation and Playwright automation.
---

# Content Calendar Agent

## Overview

This skill manages Market Haven's automated social media posting schedule. It generates
fresh, themed content using the Google Antigravity SDK (Gemini) and posts to Twitter/X
and LinkedIn via Playwright browser automation.

## Dependencies

- **social-media-agent**: Base social media posting capability with Playwright
- **google-antigravity-sdk**: Gemini AI for content generation

## Quick Start

```bash
# Preview what would be posted today (no actual posting)
python3.11 scripts/content_calendar_agent.py --dry-run

# Run live posting for today's theme
python3.11 scripts/content_calendar_agent.py

# Force a specific day's content (useful for testing)
python3.11 scripts/content_calendar_agent.py --force monday --dry-run
python3.11 scripts/content_calendar_agent.py --force wednesday --dry-run
python3.11 scripts/content_calendar_agent.py --force friday --dry-run
```

## Content Schedule

| Day       | Theme                 | Content Type                                       |
|-----------|-----------------------|----------------------------------------------------|
| Monday    | 🔥 Motivation Monday  | Unique motivational quotes about community service |
| Wednesday | 🤝 Community Spotlight| Local Northern VA charity events & volunteering    |
| Friday    | 💡 Fun Fact Friday    | Lesser-known facts about nonprofits & food rescue  |

## Workflow

### 1. Day Check

The script checks the current day of the week. If it's not Monday, Wednesday, or Friday,
it exits gracefully with no action.

### 2. Duplicate Prevention

The script checks `data/content_calendar.json` to see if a post for today's theme has
already been made. If so, it skips to prevent duplicate posts.

### 3. Content Generation

Uses the Gemini Agent (via Google Antigravity SDK) to generate fresh, unique content
based on the day's theme. Falls back to curated default content if the API is unavailable.

### 4. Post Formatting

Formats content into platform-specific templates:

- **Twitter**: Brief, under 280 characters, includes hashtags and GoFundMe link
- **LinkedIn**: Professional 2-3 paragraph format with CTA and hashtags

### 5. Automated Posting

Posts to both platforms via Playwright headless browser automation using stored credentials.

### 6. Logging

Records each post in `data/content_calendar.json` with full content, timestamps, and
platform-specific status flags.

## Automation

The social media loop runs automatically via the Next.js background worker in `src/lib/db.ts` triggering `scripts/social_media_coordinator.py`:

- **Daily Window**: Executed at exactly 12:00 PM local time daily.
- **Startup Check**: If the server starts between 12:00 PM and 5:00 PM and no post has been made today yet, it runs immediately and schedules subsequent runs for 12:00 PM daily. Otherwise, it waits until 12:00 PM.

## Common Mistakes

1. **Running on non-posting days**: The script gracefully skips non-posting days (Tue/Thu/Sat/Sun).
   Use `--force` to override for testing.
2. **Duplicate posts**: The log file prevents same-day duplicates. Delete the entry from
   `data/content_calendar.json` if you need to re-post.
3. **Playwright not installed**: Run `python3.11 -m playwright install chromium` if browsers
   are missing.
