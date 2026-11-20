---
name: mas_orchestrator
description: >-
  Intercepts ambiguous tasks and routes them strictly to specialized child agents via the supervisor model and Antigravity 2.0 Agent Manager.
---

# MAS Orchestrator Skill

## Overview
The MAS Orchestrator skill governs task decomposition, progressive context disclosure, sub-agent handoffs, guardrail tripwire enforcement, and final artifact verification within the Antigravity IDE workspace.

## Actions
- `route_task`: Analyzes incoming user requests, generates a structured execution plan, provisions task-scoped context windows, and dispatches to specialized sub-agents (`frontend`, `backend`, `browser`, `devops`, `guardrail`).
- `validate_artifact`: Invokes deterministic linters, unit tests, and policy guardrails before marking a task or sub-agent output complete.
- `execute_handoff`: Performs explicit handoffs (`transfer_to_X`) between sub-agent nodes with filtered context parameters.

## Harness Profile Wiring
This skill links directly to the sub-agent harness profiles located under `.agent/harnesses/`:
- Supervisor: [supervisor.yaml](file:///Users/malcolm/Downloads/trading-bot-/.agent/harnesses/supervisor.yaml)
- Frontend: [frontend.yaml](file:///Users/malcolm/Downloads/trading-bot-/.agent/harnesses/frontend.yaml)
- Backend: [backend.yaml](file:///Users/malcolm/Downloads/trading-bot-/.agent/harnesses/backend.yaml)
- Browser: [browser.yaml](file:///Users/malcolm/Downloads/trading-bot-/.agent/harnesses/browser.yaml)
- DevOps: [devops.yaml](file:///Users/malcolm/Downloads/trading-bot-/.agent/harnesses/devops.yaml)
- Guardrail: [guardrail.yaml](file:///Users/malcolm/Downloads/trading-bot-/.agent/harnesses/guardrail.yaml)

## Directives
1. Progressive Disclosure: Context files must be disclosed on demand to the specific sub-agent node processing the step.
2. Structured Monologue: Model thoughts and actions must be emitted as machine-readable typed NDJSON streams (`init`, `step_update`, `result`).
3. Zero Fake Data: All data processed during execution must be real broker/market telemetry or verifiable code ASTs.
