---
name: nod-bridge-ops
description: >-
  Operational runbook and guardrails for the bidirectional Antigravity <-> Nod
  MCP bridge and local file handoff channel. Use when dispatching tasks to Nod,
  reading Nod's outbox responses, or troubleshooting Nod Desktop 401/403 boundaries.
version: 1.0.0
---

# Nod Bridge Operations (`Antigravity <-> Nod`)

## 1. Non-Hidden Handoff Paths (Mandatory)

- **Never** place shared cross-agent handoff folders inside hidden dot-folders (`~/.<dir>`). Nod's `LOCAL_FILES_*` guardrail rejects hidden paths as private/hidden.
- Always use the visible directory:
  - `~/nod_antigravity_bridge/inbox_for_nod/` (Antigravity → Nod tasks)
  - `~/nod_antigravity_bridge/outbox_from_nod/` (Nod → Antigravity replies/acks/artifacts)
- Enforce `.resolve()` containment checks on all reads and writes.

## 2. Respecting Nod Desktop Auth & Trust Boundaries

- **Desktop Mode (`401`):** Nod Desktop (`127.0.0.1:<port>`) intentionally rejects external HTTP requests without its internal `x-nod-desktop-token` (`{"error":"Open Nod in the desktop app."}`). Never extract, spoof, or bypass this token.
- **Bearer Server Mode:** Direct HTTP (`GET /api/health`, `GET /api/state`, `GET /api/configuration`, `GET /api/messages`, `POST /api/messages`, `GET /api/memory`) requires self-hosted Nod running with `PORT=58408`, `NOD_HOST=127.0.0.1`, `NOD_PUBLIC_URL=http://127.0.0.1:58408`, and a `>= 43`-character (`[A-Za-z0-9_-]`) `NOD_AUTH_TOKEN` in Nod's `.env` matching `NOD_API_TOKEN` in `~/.gemini/config/.env` (sent as `Authorization: Bearer <token>`).
- **Local Model Context Floor (`feat/local-zero-cloud`):** Loopback Ollama endpoints (`http://127.0.0.1:11434/v1`) require `contextWindow >= 65536` (`minimumContextTokens`). Use `qwen3.5:2b` (`2.55 GB` Q8_0 cached in `~/.ollama/models`, `262K` context, `OLLAMA_KEEP_ALIVE=2m`) on 16 GB / constrained hosts.
- **Action Review Model (`403`):** If Nod reports `"The action review model is unavailable."` during `LOCAL_FILES_READ`, the user must verify their provider key / trust model in Nod Desktop **Settings → Models**.

## 3. Bridge & Config Locations

- MCP Bridge: `/Users/malcolm/.gemini/antigravity/scratch/mcp_bridges/nod_mcp_bridge.py`
- MCP Registration: `"nod-local-bridge"` in `/Users/malcolm/.gemini/config/mcp_config.json`
- Exposed Tools: `nod_get_status`, `nod_dispatch_task`, `nod_query_context`, `antigravity_callback_status`

## 4. Event-Driven WhatsApp Reactive Trigger (No 30-Min Polling)

- **Live Listener (`messages.upsert`):** Trigger immediately when `type === "notify"`, `!msg.key.fromMe`, `msg.key.id` is unseen, and a teammate mentions `nod` or `rob` (with or without `@`). Enforce a `concurrency = 1` FIFO queue (matching `OLLAMA_NUM_PARALLEL=1`) and a short per-sender cooldown so bursty chats cannot spike Mac CPU > 50%.
- **Instant Acknowledgment:** Drop an immediate `🔵` reaction (`react`) and set `"composing"` presence (`sendPresenceUpdate`) before running model inference.
- **2-Tier Routing:**
  - *Fast Chat Lane (~1–6s):* Conversational messages, `@nod ready`, and status check-ins call local `http://127.0.0.1:11434/api/chat` (`qwen3.5:2b`, `think: false`) with a compact ~400-token `nod-human-ops` zero-fabrication prompt, sending a quoted `🔵 [ROB / NOD]` reply directly back to the group.
  - *Deep Agent Lane (~50–90s):* Explicit requests to inspect files, code, logs, or escalate to Antigravity — plus on-demand debrief phrases (`"text us last"`, `"daily debrief"`, `"daily wrap-up"`, `"eod recap"`, `"team wrap-up"`, replacing the daily `20:00` timer `task-757`) — send a `< 2s` ack (`"On it — checking live state..."`), dispatch `POST http://127.0.0.1:58408/api/messages` with `Authorization: Bearer <token>`, poll that `turnId` until completion, and send the verified reply.
- **Single-Socket & Reload Rule:** Never launch a second Baileys process against `~/.nod_whatsapp_auth`; after updating `whatsapp_mcp_bridge/index.mjs`, reload `whatsapp-bridge` once in Antigravity MCP settings.

## 5. Independent & Team-Capacity Topology

- **Shared Loopback Hub (`http://127.0.0.1:58409`, Bearer `NOD_API_TOKEN`):** Owns the single WhatsApp Baileys session without socket conflicts:
  - *Nod Solo (`--daemon`):* Standalone `node .../whatsapp_mcp_bridge/index.mjs --daemon` serves WhatsApp HTTP (`58409`) and fast/deep reactive replies (`11434` / `58408`) independently when Antigravity IDE is closed.
  - *Antigravity Solo (`embedded_hub`):* If Nod (`58408`) is stopped or offline, Antigravity still serves MCP WhatsApp tools (`wa_*`) and fast replies while deep Nod calls degrade cleanly with honest offline errors.
  - *Team Capacity (`proxy_to_hub`):* When `--daemon` holds `58409`, Antigravity's `whatsapp-bridge` MCP proxies `wa_get_status`, `wa_read_recent_messages`, and `wa_send_group_message` over `58409` with zero Baileys `440` session collisions; Nod simultaneously uses `58409/send`, `58409/messages`, and Antigravity talks to Nod on `58408`.
- **Atomic State Files (`~/.nod_whatsapp_auth/`, mode `0600`):** `rbac_policy.json` (roles, lanes, and 3-company `companyDataSources` Gmail/Drive/DB visibility), `sender_sessions.json` (isolated per-sender context, max 6 turns), and non-secret `bridge_snapshot.json` are persisted atomically via temp-file + `rename` (`node .../whatsapp_mcp_bridge/index.mjs --save-snapshot`). Reload `whatsapp-bridge` once in Antigravity MCP settings after updates.
- **Multi-Window IDE MCP Reload Order (Host-UI Only):** Never terminate Antigravity-managed MCP subprocesses from the agent shell. After updating `whatsapp_mcp_bridge/index.mjs` or `nod_mcp_bridge.py`, reload `whatsapp-bridge` (and `nod-local-bridge`) in the Antigravity window holding `127.0.0.1:58409` (`embedded_hub`) first — or close extra windows — then reload secondary window(s) so they attach cleanly in `proxy_to_hub` mode with zero Baileys `Stream Errored (conflict)` collisions.
- **Docker Auto-Restart Policy:** Keep Nod's 4 local containers (`nod-local-postgres-1`, `nod-local-workspace-network-1`, `nod-workspace`, `nod-browser`) configured with `--restart unless-stopped` so `127.0.0.1:54329` Postgres auto-recovers instead of leaving `127.0.0.1:58408` in HTTP `500`.
