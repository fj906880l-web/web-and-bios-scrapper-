---
name: growth
description: >-
  Use when executing competitor marketing intelligence, Convergence Weekly v2 newsletter research/drafting, X Phoenix reach optimization, Kit AI tagging/broadcast staging, zero-dependency web scraping, or Charity/Trading social calendars and GoFundMe/Gumroad income-stream telemetry sync in one pass.
version: "2.0.0"
---

# /growth — Marketing Intel, Newsletter Publishing, Phoenix Reach & Charity/Consulting Ops

Single-pass Category Master Skill. Invoking `/growth` executes the full pipeline below from start to finish in one go without manual handoffs, partial stops, or fragmented prompts.

## 1. Trigger, Parameters & Invocation Schema

- **Primary Slash Trigger:** `/growth`
- **Compatible Aliases:** `/growth`, `/marketing`, `/newsletter`, `/newsletter-writer`, `/social`, `/charity-ops`
- **Absorbed Legacy Skills (11):** `/competitor-marketing-intel`, `/newsletter-writer`, `/phoenix-reach-optimizer`, `/kit-ai-connectors`, `/web-scraping-mcp`, `/content-calendar-agent`, `/social-media-agent`, `/notification-agent`, `/income-stream-sync`, `/monday-trade-post`, `/social-notification-subagent`
- **Deterministic Runner:** [`scripts/run_master_skill.py`](./scripts/run_master_skill.py) (`--dry-run --json`, `--preflight`, `--list-modules`, `--run-tests`)

| Parameter | Type | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `mode` | `enum(full|intel|newsletter|social|charity_sync|monday_trade)` | `full` | Growth execution lane |
| `cadence` | `enum(wednesday|sunday|event_watch|monday|friday|adhoc)` | `adhoc` | Edition or weekly calendar slot |
| `competitor` | `string` | `` | Optional competitor name/URL for intel mode |
| `publish` | `bool` | `false` | Must remain false (staged/draft only) unless explicit AUTH: is given |

```bash
# Single-pass dry-run & pre-flight verification
python3 ./scripts/run_master_skill.py --dry-run --json
```

## 2. Non-Negotiable Guardrails & Domain Invariants

- **Evidence Separation & `[Gap]` Discipline:** Strictly separate Competitor Moves (`playbook.md`) from Public Market Reactions; flag unverified inferences `[Inference]` and missing data `[Gap]`; label every newsletter claim `Reported`, `Claim`, or `Analysis` with primary sources.
- **Draft-Only & `AUTH:**` Gate: Stage newsletters (`MH 1: 5638273`, `MH 2: 5638304`, `MH 3: 5638317`) and Base44 `EmailQueue` / Kit Account `2966097` payloads strictly as `draft`/`staged_preview`; zero live blasts without explicit `AUTH:`.
- **Charity 501(c)(3) Guardrail:** Market Haven Charity outreach targets direct donations, corporate sponsorships, and institutional grants ONLY—never engage paid marketing agencies; include GoFundMe (`https://gofund.me/7047dcec7`) and mandatory mini legal disclaimers.
- **Quant / Trading Social Guardrail:** `monday-trade-post` and `social-notification-subagent` require live broker/scanner pre-flight and mandatory NFA/SEC disclaimers; zero mock ROI numbers.
- **Zero-Paid Scraping & API Hygiene:** Use local `web-scraping-mcp` (`search_sources`, `scrape_page`, `extract_json_ld`, `extract_table`) first; enforce CAN-SPAM compliance and `1 msg/sec` webhook rate limit.

## 3. Explicit Execution Order & Step Dependencies

Execute every stage strictly in topological order; never skip an upstream gate unless an earlier stage explicitly marks it optional for the active `mode`.

### S1: Zero-Dependency Intel, Scraping & Telemetry Sync
- **Depends On:** None (Entry Gate)
- **Inputs:** RSS/web targets, `web-scraping-mcp`, GoFundMe/Gumroad webhooks, broker telemetry
- **Actions:** Run `web-scraping-mcp` (`search_sources`/`scrape_page`/`extract_json_ld`) to collect competitor moves + market reactions (`competitor-marketing-intel`), 5-domain news for Convergence Weekly (`AI`, `Robotics`, `Electronics`, `Utilities`, `Healthcare Tech`), or `income-stream-sync` GoFundMe/Gumroad totals.
- **Gate Check:** Primary URLs, dates, and live telemetry parsed with zero fabricated placeholders.
- **Artifacts:** `intel_and_telemetry_snapshot.json`

### S2: Fact Verification, Scoring & Entity Compliance
- **Depends On:** `S1`
- **Inputs:** raw claims, draft stories, entity rules
- **Actions:** Run Convergence 4-point verification gate (Source, Cross-Check, Freshness, Hype check; cut unsourced items; alert `MH 3` only if verification >= 90 and severity >= 85), enforce 501(c)(3) zero-paid-ads check for Charity, and verify real trade logs for `monday-trade-post`.
- **Gate Check:** Every retained claim carries `[Reported|Claim|Analysis]` + cited source URL.
- **Artifacts:** `verified_claims_ledger.json`

### S3: Copy Synthesis & Phoenix Reach Optimization
- **Depends On:** `S2`
- **Inputs:** verified claims, `phoenix_reach.py`, brand/newsletter templates
- **Actions:** Compile Convergence Weekly v2 HTML/copy or Top 3 monthly playbooks (`competitor-marketing-intel`) or Mon/Wed/Fri calendar posts (`content-calendar-agent` / `social-media-agent`); score and refine copy via `phoenix_reach.py` (maximizing Copy-Link `+20.0` / Mutual Reply `+15.0` and dodging Report `-234.0` penalties).
- **Gate Check:** Phoenix score positive with zero clickbait/report risk; all compliance footers attached.
- **Artifacts:** `staged_copy_and_phoenix_scores.json`

### S4: Cross-Channel Staging, Kit Tagging & Action Dispatch
- **Depends On:** `S3`
- **Inputs:** Kit MCP (`2966097`), Base44 `EmailQueue`, Nod/Antigravity queues
- **Actions:** Stage draft broadcast in Kit (`kit-bridge`: `kit_draft_broadcast`, never auto-send), sync subscriber tags (`Monthly $10/mo`, `Yearly $80/yr`), emit ready-to-run Antigravity/Nod build tasks from intel playbooks, and record calendar/notification drafts.
- **Gate Check:** Drafts staged with valid IDs (`status: draft`) and duplicate-day guards verified.
- **Artifacts:** `staged_kit_and_task_payloads`

### S5: Pre-Publish Compliance & `AUTH:` Gate
- **Depends On:** `S4`
- **Inputs:** staged assets, user conversation words
- **Actions:** Verify CAN-SPAM links, favicon/HTML hygiene, and NFA/501(c)(3) disclosures; halt before any external send/post unless `AUTH: user said "..."` authorizes live publication.
- **Gate Check:** Either clean staged delivery or explicit `AUTH:` recorded for live action.
- **Artifacts:** `publish_gate_decision`

### S6: Unified Delivery Ledger & Metrics Summary
- **Depends On:** `S5`
- **Inputs:** verification logs
- **Actions:** Update local cadence/calendar/notification logs atomically and deliver outcome summary with `PENDING:` for awaiting live publish approval.
- **Gate Check:** Logs consistent and zero unapproved live sends occurred.
- **Artifacts:** `growth_run_summary`

## 4. Fallback & Escalation Rules

- **Missing Primary Source:** Cut unverified story/claim (`cut_for_lack_of_sources`) rather than inventing or softening uncertainty.
- **Server Offline (Charity `:**3050` or Kit OAuth expired): Persist staged draft/telemetry locally, report exact HTTP/OAuth diagnostic (`kit_connect_oauth_status`), and avoid retrying blindly.
- **Off-Day Calendar Trigger:** Skip Mon/Wed/Fri autopost cleanly unless `--force <day>` is explicitly specified.

## 5. Single-Pass Completion Criteria

- [ ] Every claim verified and tagged (`Reported`/`Claim`/`Analysis`, `[Inference]`/`[Gap]`).
- [ ] Newsletter/social drafts scored via `phoenix_reach.py` and staged in `draft` mode only.
- [ ] Entity-specific legal/charitable guardrails verified intact.
- [ ] Zero unapproved live broadcasts, tweets, or emails sent.
- [ ] Agent Harness v2.0 metadata header (`confidence`, `security_score`, `assets_loaded`, `skills_used`, `supervisor_status`, `flags`) plus `INTENT:` / `TWINS:` / `AUTH:` / `PENDING:` lines included in final outcome report.

## 6. Preserved Sub-Skill Modules & Plugin Integrations

Every underlying sub-skill, script, reference, asset, and test suite is preserved verbatim below without losing edge cases:

| Preserved Module | Origin | Definition Link | Status |
| :--- | :--- | :--- | :--- |
| `competitor-marketing-intel` | Global | [`SKILL.md`](./modules/competitor-marketing-intel/SKILL.md) | Absorbed into `/growth` |
| `newsletter-writer` | Global | [`SKILL.md`](./modules/newsletter-writer/SKILL.md) | Absorbed into `/growth` |
| `phoenix-reach-optimizer` | Global | [`SKILL.md`](./modules/phoenix-reach-optimizer/SKILL.md) | Absorbed into `/growth` |
| `kit-ai-connectors` | Global | [`SKILL.md`](./modules/kit-ai-connectors/SKILL.md) | Absorbed into `/growth` |
| `web-scraping-mcp` | Global | [`SKILL.md`](./modules/web-scraping-mcp/SKILL.md) | Absorbed into `/growth` |
| `content-calendar-agent` | Local-Merged | [`SKILL.md`](./modules/content-calendar-agent/SKILL.md) | Absorbed into `/growth` |
| `social-media-agent` | Local-Merged | [`SKILL.md`](./modules/social-media-agent/SKILL.md) | Absorbed into `/growth` |
| `notification-agent` | Local-Merged | [`SKILL.md`](./modules/notification-agent/SKILL.md) | Absorbed into `/growth` |
| `income-stream-sync` | Local-Merged | [`SKILL.md`](./modules/income-stream-sync/SKILL.md) | Absorbed into `/growth` |
| `monday-trade-post` | Local-Merged | [`SKILL.md`](./modules/monday-trade-post/SKILL.md) | Absorbed into `/growth` |
| `social-notification-subagent` | Local-Merged | [`SKILL.md`](./modules/social-notification-subagent/SKILL.md) | Absorbed into `/growth` |

- **Companion Plugins:** None
- **Companion MCP Servers:** `web-scraping-mcp`, `kit-bridge`, `market-haven-social-media`
