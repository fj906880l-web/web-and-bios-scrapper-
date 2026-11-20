# Antigravity Unified Category Master Skills & Workflows

**Standard:** Google Gemini / Antigravity IDE Category Master Hierarchy (`v2.0.0`)
**Scope:** Global `~/.gemini/config/skills/` & All Synced Workspaces
**Single-Pass Contract:** Typing any `/<master-skill>` executes all stages end-to-end in one pass with deterministic gates, fallback escalation, and zero partial stops.

---

## 1. Category Master Skills (`9` Unified `/` Triggers)

| Slash Trigger | Primary File | Domain Scope | Preserved Sub-Skill Modules |
| :--- | :--- | :--- | :--- |
| **`/ship`** | `ship/SKILL.md` | Verified Security Hardening, Adversarial QA & Release Sealing | `verified-release-and-ui-craft, shift-left-ai-security, daily-security-workflow, vanta-security-scaling-guardrails, developer-isolation-blast-radius, static-code-analysis, fable-judge, try-harder-poc-validation` |
| **`/code`** | `code/SKILL.md` | Context-Aware Software Craft, Algorithms & App Delivery | `context-aware-coding, surgical-code-craft, fable-method, fable-loop, fable-domain, cloudflare-os, cs-algorithmic-foundations, blast-master-system, error-handling-patterns, system-optimization-guide, teach` |
| **`/ops`** | `ops/SKILL.md` | Agent Orchestration, MCP Routing, Meetings, Energy Tasking & Style Sync | `agent-harness-v2, agent-systems-unified-skill, autonomous-architect-protocol, delegation-diligence-loop, unified-ai-architecture-and-standards, icm-architect, tri-perspective-collaboration, nod-bridge-ops, omniroute, composio-mcp, unigent, typesafe-ai, skillopt, nod-human-ops, mas_orchestrator, ego-lite` |
| **`/studio`** | `studio/SKILL.md` | Procedural Motion Graphics, Visual Explainers, Voice & Anti-Slop Media | `anti-slop-studio, generative-media-studio, multimodal-visual-explainer, cartesia-voice, agent-voice-facetime, social-media-vision-board, brand-identity, sol-ai-sun-agent` |
| **`/hw`** | `hw/SKILL.md` | Autonomous Hardware, KiCad PCB, Mechanical CAD & Firmware Compiler | `autonomous-hardware-architect` |
| **`/growth`** | `growth/SKILL.md` | Marketing Intel, Newsletter Publishing, Phoenix Reach & Charity/Consulting Ops | `competitor-marketing-intel, newsletter-writer, phoenix-reach-optimizer, kit-ai-connectors, web-scraping-mcp, content-calendar-agent, social-media-agent, notification-agent, income-stream-sync, monday-trade-post, social-notification-subagent` |
| **`/billing`** | `billing/SKILL.md` | Stripe Payments, Connect KYC, Apps, Projects & Metronome Usage Billing | `stripe-best-practices, stripe-docs, stripe-apps, stripe-directory, stripe-pay, stripe-projects, upgrade-stripe, connect-recommend, connect-required-verification-information, metronome` |
| **`/quant`** | `quant/SKILL.md` | Quantitative Trading, Risk Gating & Local Unsloth/Soup/Ollama Fine-Tuning | `soup-finetuning-harness, ai-algorithm-distillery, active-trade-allocation, qlib-mts-workflow, quantpad-data-api, opennews-mcp, mcp-fd-and-bracket-audit, trading-bot-auditor` |
| **`/research`** | `research/SKILL.md` | Reverse Engineering, EGE-2 Epistemics, Math/ARC & Technical Learning | `rea, reverse-engineer-anything, ege2-quantum-epistemics, epistemic-math-frontier, arc-agi-3-interactive-reasoning, daily-ai-intel-digest, technical-learning-workflow, nod-research` |

---

## 2. Built-In Platform Slash Workflows

| Slash Command | Purpose |
| :--- | :--- |
| **`/goal <task>`** | Long-running autonomous execution loop with auto-recovery until verified done |
| **`/schedule <cron_or_seconds> <prompt>`** | Recurring cron or one-shot timer trigger |
| **`/plan <task>`** | Structured planning mode before surgical execution |
| **`/grill-me <topic>`** | Interactive interview to resolve architecture/design ambiguity |
| **`/learn <lesson>`** | Capture verified operational lessons into permanent memory |
| **`/compact`** | Summarize and free context window budget |

---

## 3. Preserved Module Access & Deterministic Dry-Run

Every Master Skill preserves 100% of its absorbed granular skills, scripts, references, assets, and tests inside `./modules/<granular-skill>/` and provides a deterministic runner:

```bash
python3 /Users/malcolm/.gemini/config/skills/<master>/scripts/run_master_skill.py --dry-run --json
```
