---
name: tri-perspective-collaboration
description: Tri-Perspective Synthesis (SpacetimeDB x Jake Van Clief ICM x Theo t3.gg) for multi-human and multi-agent real-time collaborative development, live data streaming, and cross-workspace synchronization.
---

# Tri-Perspective Synthesis & Multi-Project Collaboration Skill

This skill documents the unified architecture combining **SpacetimeDB in-memory reactive reducers**, **Jake Van Clief's Interpretable Context Methodology (ICM)**, and **Theo (t3.gg) end-to-end type safety & DX**.

---

## The 3 Foundational Pillars

### 1. SpacetimeDB Reactive State Bus (State & Sync Layer)
- **Database = Application Server**: State transitions are processed as pure, in-memory reducers (`reduce_action(state, action) -> new_state`).
- **Atomic Rollback**: If an assertion or invariant fails, the state transaction aborts cleanly with zero side-effects or orphaned disk files.
- **Direct WebSockets Fan-out**: Connected clients and partner devices receive live state mutations instantly over WebSockets.

### 2. Jake Van Clief's ICM (Agent Context Layer)
- **Folder Structure as Architecture**: Workspaces are partitioned into bounded, numbered stages (`01_ingest/`, `02_build/`, `03_verify/`, `04_publish/`).
- **Desk vs. Drawer Token Discipline**: Agents load only the active stage `CONTEXT.md` (<5,000 tokens), preventing context drift and hallucinations.
- **Cold-Agent Walk-Test**: Validate every stage contract by executing a memory-less subagent simulation.

### 3. Theo (t3.gg) Type Safety & Developer Experience (DX Tier)
- **End-to-End Type Safety**: Zod & Pydantic schemas validating all WebSocket frames, tool descriptors, and webhook payloads.
- **1-Command Scaffolding**: Single CLI command (`lumina`) boots the daemon, serves the Monaco IDE, and renders an ASCII QR code for smartphone/partner pairing.
- **Dynamic Multi-Tier RBAC**: Super Admin, Co-Admin, Reviewer (Co-Pilot), and Spectator (Viewer).

---

## Multi-Project & Collaborator Invariants

1. **Multi-Tenant Attribution**: Every code diff, AST mutation, or stage artifact must carry explicit author attribution (e.g., `[Malcolm (Lead)]` vs `[DJ Fisher (Codex)]`).
2. **50% Capital & Risk Guardrail**: Automated trading pipelines must enforce that single-trade capital allocations never exceed 50%.
3. **Zero-Leak DLP Scanning**: All real-time WebSocket payloads and Git micro-commits must pass through Shannon entropy & regex DLP sanitizers before disk persistence.
4. **Cold-Agent Walk-Test Gate**: Workspaces must pass the memory-less Cold-Agent Walk-Test simulator before publication.
5. **Cross-Workspace Synchronization**: File edits across registered projects (`trading-bot-`, `allora-app`, `charitywebsite`) must sync bidirectionally with directory-traversal prevention.
