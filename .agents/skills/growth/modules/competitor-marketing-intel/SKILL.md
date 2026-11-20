---
name: competitor-marketing-intel
description: >-
  Autonomous marketing intelligence and execution workflow that separates
  competitor moves (reverse-engineer-marketing playbook.md) from public market
  reactions (Agent Reach / web scraping), builds a unified chronological timeline,
  flags [Inference] and [Gap] evidence, and outputs the Top 3 monthly
  playbooks with ready-to-run Antigravity and Nod build tasks.
---
# Competitor Marketing Intelligence & Playbook Synthesizer

Reverse-engineer target competitor marketing strategies using verified public evidence, correlate actions against real market reactions, and distill validated opportunities into ranked monthly execution playbooks and Antigravity/Nod build tasks.

## Inputs & Context

Gather these inputs before synthesizing final recommendations (mark missing items as `[Gap]`):
- **Target Competitor:** Competitor name and primary URL.
- **Company, Product, ICP & Value Prop:** Target entity (`Market Haven Business Consulting`, `Lumina Trading`, etc.), offering, ideal customer profile, and differentiation.
- **Monthly Marketing Budget & Bandwidth:** Available spend, active channels, tooling, and team/agent capacity.
- **Research Output 1 (`playbook.md`):** Dated competitor moves, positioning shifts, pricing/offer changes, traffic curves, and plays (`reverse-engineer-marketing` skill from `coreyhaines31/marketingskills`).
- **Research Output 2 (Public Footprint / Agent Reach):** Live public evidence across X/Twitter, Reddit, YouTube transcripts, GitHub, and reviews capturing real customer and audience reactions.

## Research Stack & Compliance Boundaries

- **Action Extraction (`reverse-engineer-marketing`):** Map dated launches, funnel changes, messaging tests, and channel experiments.
- **Reaction Extraction (`Agent Reach` / `web-scraping-mcp`):** Gather verifiable public comments, threads, reviews, and engagement signals — never fabricate traffic, engagement numbers, or quotes.
- **Non-Profit Guardrail:** For **Market Haven Charity (501(c)(3))**, restrict plays strictly to organic education, grant partnerships, and direct donor/sponsor outreach — never engage paid advertising or paid marketing vendors for the non-profit.
- **Google Gemini / Antigravity Workspace Standard:** Frame automation deliverables strictly as Antigravity and Nod agent build tasks adhering to `GEMINI.md` and `.agents/` conventions.

## Execution Rules

1. **Separate Action from Reaction:** Treat `playbook.md` strictly as *what the competitor did*, and Agent Reach / scraping output strictly as *how the market responded*.
2. **Unified Chronological Timeline:** Merge dated competitor moves and dated audience reactions into one chronological timeline before drawing conclusions.
3. **Keep Only Validated Plays:** Retain a play only when both the competitor action and aligned audience/market reaction evidence exist.
4. **Explicitly Tag `[Inference]` and `[Gap]`:** Prefix every deduction with `[Inference]`, mark missing data as `[Gap]`, and list exact follow-up search queries or checks required to close critical gaps.
5. **Filter & Rank by Monthly Fit:** Drop plays exceeding the entity's monthly budget, channels, or team bandwidth; rank remaining plays by what can ship **this month**.

## Required Output — Top 3 Playbooks This Month

For each of the Top 3 ranked plays, output:
1. **Play Name & Summary:** Clear title and concise business thesis.
2. **The Insight:** Grounded in the merged timeline, strictly separating observed facts from `[Inference]` and explicit `[Gap]` notes.
3. **Dated Proof:** Exact dates, public URLs/channel signals, and observed audience reaction evidence.
4. **Ready-to-Install Playbook:** Step-by-step execution plan tailored to budget, channels, and entity compliance rules.
5. **Antigravity / Nod Build Task:** Concrete build specification (scripts, landing pages, tracking, content automation, or agent schedules) ready for immediate execution in Antigravity and Nod.
