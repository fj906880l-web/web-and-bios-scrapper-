---
name: cloudflare-os
description: Agent workspace built on Cloudflare Workers and Durable Objects for creating web apps and gadgets, capability-based access control, real-time multiplayer collaboration, and sandboxed agent execution. Use when developing Cloudflare OS applications, setting up Workers/Durable Objects/Dynamic Workers, configuring Gatekeeper integrations, or deploying to Cloudflare/workerd.
---

# Cloudflare OS & Gadgets Architecture

Cloudflare OS is an open agent workspace built on Cloudflare Workers and Durable Objects. It enables building real-time multiplayer apps (Gadgets), sharing reusable app templates (Blueprints), and running AI agents in secure sandboxed environments.

## Core Architectural Concepts

1. **Gadgets & Durable Objects**:
   - Each Gadget is a stateful web application backed by a Cloudflare Durable Object.
   - Provides real-time multiplayer collaboration and state synchronization out of the box (using Yjs).
2. **Cap'n Web & RPC**:
   - Extremely low-boilerplate RPC layer between client iframe and server Worker.
   - Server methods can be called directly by agents using Code Mode.
3. **Sandboxed Security & Dynamic Workers**:
   - Backend runs in a Dynamic Worker with external internet access disabled by default.
   - Client code runs in a sandboxed iframe communicating via `postMessage()`.
   - Access to external APIs requires explicit capability introductions via Workers Bindings.
4. **Blueprints**:
   - Share code copy templates so users run their own local or hosted instance of an app without server central management.

## Development & Execution Commands

- **Local Execution (via Wrangler / workerd)**:
  ```bash
  pnpm run-local
  ```
  App access: `http://localhost:8787` (Data stored in `.wrangler`)

- **Frontend & Backend Separated Dev**:
  ```bash
  # Terminal 1: Backend server
  pnpm dev-server

  # Terminal 2: Frontend client
  pnpm dev-client
  ```
  App access: `http://localhost:3000`

- **Deploying**:
  - Online deployment flow: `https://os.cloudflare.app/deploy`
  - Deployment starter repo: `https://github.com/cloudflare/cloudflare-os-starter`

## Gatekeeper Integrations & Capability Access

Gatekeepers manage authenticated access to third-party services. Configure third-party OAuth / credentials under their respective packages:
- GitHub API: `packages/gatekeeper-github`
- Google API: `packages/gatekeeper-google`
- Cloudflare API: `packages/gatekeeper-cloudflare`
- Supabase API: `packages/gatekeeper-supabase`
- Notion API: `packages/gatekeeper-notion`
- Confluence API: `packages/gatekeeper-confluence`
- Slack / Spotify / ZoomInfo / HomeAssistant / Email Workers

## Capability-Based Access Control Rule
Agents and Gadgets have **zero initial access**. To grant access to a resource (e.g. GitHub repo, Google Drive file), introduce the resource explicitly via UI link or parameter.
