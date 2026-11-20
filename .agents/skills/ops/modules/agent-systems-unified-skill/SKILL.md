---
name: agent-systems-unified-skill
description: >
  Unified skill for building reliable, interoperable AI agent systems. Covers four linked topics:
  (A) concurrency model selection (async vs threads vs processes), (B) zero-downtime releases
  (blue/green + expand/contract DB migrations), (C) durable AI agent runs (resumable streams,
  durable execution, idempotency), and (D) agent-to-agent communication (ACP -> A2A, plus MCP).
  Each topic includes decision rules, checklists, and a mapped list of GitHub repos. Load this when
  designing, reviewing, or operating multi-agent systems, long-running agent jobs, or agent APIs.
version: 1.0.0
created: 2026-11-17
sources:
  - "Video 1: Async vs Threads (creator: @rick.theengineer)"
  - "Video 2: Blue/Green deployments (creator: @rick.theengineer)"
  - "Video 3: Durable AI agent streaming / resumable streams / durable execution (creator: @rick.theengineer)"
  - "https://www.ibm.com/think/topics/agent-communication-protocol (IBM Think, published 2025-06-11)"
  - "GitHub repos listed in Section 6"
---

# Agent Systems Unified Skill

## 0. How an agent should use this file

1. Read the **routing table** and jump to the matching skill. Do not apply all four skills to every task.
2. Treat each "Rules" block as defaults. Override only with a stated reason.
3. Treat the "Repo map" (Section 6) as pointers. Entries marked `◇` were not re-verified at write time. Confirm the repo and version before pinning a dependency.
4. If a rule here conflicts with an explicit user instruction, follow the user and say so.

| If the task involves... | Go to |
|---|---|
| Handling many simultaneous requests, slow I/O, CPU-heavy work, "should this be async?" | **Skill A** |
| Shipping a new version without downtime, rollback, schema changes | **Skill B** |
| Agent runs that take minutes, dropped connections, worker crashes, retries, double-charging risk | **Skill C** |
| Agents talking to other agents or to tools, protocol choice, interoperability | **Skill D** |
| Designing a whole multi-agent platform | **Section 7 (how the skills compose)** |

### Local Workspace Alignment (Antigravity + Nod + Harness v2)
- **Concurrency & Resource Cap (Skill A):** Keep local machine load below **50%** (16 GB RAM Mac). Default to `async` I/O for MCP/API/Nod calls and bound worker or local-LLM concurrency; use lightweight local models (`<= 1 GB`, e.g., Ollama `qwen2.5:1.5b` at `http://127.0.0.1:11434`).
- **Releases (Skill B):** Pair with `verified-release-and-ui-craft` for zero-downtime blue/green rollouts and expand/contract schema changes.
- **Durable Runs (Skill C):** Aligns with `agent-harness-v2` (`A-01` Task State Machine: `pending` -> `running` -> `succeeded`/`failed`), per-step checkpoints, and stable `Idempotency-Key`s on external side effects.
- **Protocols & Nod Bridge (Skill D):** Use **MCP** for tool/data access and **A2A** for peer agent interoperability (treat ACP as legacy/archived). For Antigravity <-> Nod coordination, use `nod-bridge-ops` (`nod-local-bridge` MCP + visible `~/nod_antigravity_bridge/` handoff folders).

---

## Skill A: Pick the right concurrency model

### Core ideas
- A **thread** is a sequence of instructions run by the OS inside a **process**. Each thread has its own stack. All threads in a process share the same memory.
- **Synchronous = blocking.** The thread waits for the result before doing anything else. Example from the source: 1,000 requests, each waiting 100 ms on a database, handled one at a time = **100 seconds**, with the CPU idle almost the whole time.
- **Concurrency** = many tasks making progress by taking turns. **Parallelism** = many tasks running at the same instant on different cores. They solve different problems.

### Fix 1: multithreading
- One thread per request. While one thread is blocked on I/O, others run. On a multi-core CPU, threads can run truly simultaneously.
- Costs: each thread needs stack memory (10,000 threads gets expensive), and the CPU pays a **context-switch** cost when swapping between them.
- Shared memory causes **race conditions**. Example: two threads both read `count = 5`, each adds 1, both write `6`, and the expected `7` is lost. **Locks** prevent this by making threads take turns, at the price of waiting and added complexity.

### Fix 2: asynchronous (event loop)
- One thread runs an **event loop**. When a task hits an `await` on I/O, it hands control back to the loop. The OS notifies the loop when the data is ready. The loop resumes that task where it left off.
- Result: one thread, tiny memory, thousands of open connections, no idle waiting. Available in JavaScript and Python via `async`/`await`.
- **Weakness:** if one task does heavy CPU work without yielding, the whole loop freezes and every other task stalls.

### Language-specific notes (from the source)
- **Go:** goroutines multiplex many tasks onto a few real threads.
- **Java:** virtual threads give a similar many-tasks-on-few-threads model.
- **Python:** the **GIL** lets only one thread run Python bytecode at a time, so threads don't speed up CPU-bound Python. Newer versions offer an optional no-GIL build. For heavy math, use **multiple processes** (each gets its own core).

### Rules
1. **I/O-bound work** (network calls, databases, LLM API calls, file/socket waits) -> default to **async**.
2. **CPU-bound work** (number crunching, parsing huge payloads, local model inference loops) -> use **parallelism**: threads in languages without a GIL, or multiple processes in Python.
3. **Never run CPU-heavy code directly inside an event loop.** Offload it to a process/thread pool or a worker.
4. Use **locks or message passing** whenever threads share mutable state. Prefer not sharing at all.
5. For agent systems: most agent work (model calls, tool calls, web fetches) is I/O-bound, so an async orchestrator with worker processes for CPU tasks is the default shape.

### Quick checklist
- [ ] Is the bottleneck waiting (I/O) or computing (CPU)?
- [ ] Any blocking call inside an `async` function? (Replace it or push it to an executor.)
- [ ] Any shared mutable state across threads? (Add locking or remove the sharing.)
- [ ] Thread/connection count bounded?

---

## Skill B: Zero-downtime releases (blue/green + safe DB changes)

### The problem
Deploying a new version straight into production means a bug (for example a broken checkout) hits **every customer immediately**.

### Blue/green pattern
- Keep **two identical environments**. **Blue** = current live version (example: v1.4.2, 100% of traffic). **Green** = idle environment where the new version is deployed (example: v2.0.0).
- A load balancer listener (example: ALB on :443) forwards to **target groups** (`blue-tg`, `green-tg`) with weights. Users only see whichever group has traffic.
- Flow:
  1. Deploy the new version to green with **0% traffic**.
  2. **Test green directly** (login, cart, payments, an order insert, a health check). In the source's example, a `/payments` check returned 502, caught before any customer saw it. Fix, redeploy as v2.0.1, retest.
  3. **Switch traffic** blue -> green. This is the important moment.
  4. **Watch the 5xx error rate** after the switch.
  5. If it climbs and an alarm fires, **switch straight back to blue** (last known good). Do **not** rebuild/redeploy the old version, which is slow. Blue is already running.
- Optional: shift **gradually** (3% -> 25% -> 50% -> 100%) while watching errors, so a bad release only reaches a slice of users.
- Mental model from the source: stage behind the curtain. The audience sees one stage; you swap them when ready; if something breaks, swap back.

### The database trap
Blue and green usually share **one database**. If green's release **renames a column**, green expects the new name, and blue (your rollback target) still expects the old one. Rolling back then fails with `column "total_price" does not exist`.

**Fix: expand / contract (parallel change)**
1. **ADD** the new column (keep the old one).
2. **RUN BOTH:** app writes to both columns.
3. **MIGRATE:** backfill old rows (example: `UPDATE orders SET order_total = total_price WHERE order_total IS NULL;`, 128,540 rows in the source's demo).
4. **REMOVE** the old column only once the old version can never be rolled back to.

### Rules
1. Never ship schema changes that break the previous app version. Every schema state must work with **both** current and previous code.
2. Test the idle environment with real checks **before** any traffic moves.
3. Define rollback in advance: it should be a **traffic switch**, not a rebuild.
4. Gate promotion and rollback on **metrics** (5xx rate, latency), ideally automated.
5. Drop old columns/tables in a **later** release, never the same one that introduces the replacement.

### Quick checklist
- [ ] Green passes smoke tests at 0% traffic
- [ ] Old version still works against the current schema
- [ ] Error-rate alarm wired to the new target group
- [ ] Rollback = flip weights back (tested)
- [ ] Destructive schema step deferred

---

## Skill C: Durable AI agent runs

### The problem
A normal streamed chat reply is tied to one open HTTP connection. The server calls the model, tokens sit in server memory, and if the connection drops, **anything not saved is gone**. For a 3-second chat answer that's annoying. For a **20-minute agent run** (search docs, write code, run tests) it's a failure.

### Layer 1: Resumable stream
- **Don't run the work inside the request.** A **background worker** runs the whole job (example: `job 42`) to completion.
- The worker appends output to a **durable log** (Redis Streams or a Postgres table), each entry with a **sequence number**.
- The browser just **watches the log**. On reconnect it says "I'm watching job 42, last seen #57" (example: `GET /jobs/42/stream`). The server **replays everything after 57**, then continues live.

```text
client --POST /chat--> API --enqueue--> queue --> WORKER (runs job 42)
                                                    |
                                          append tokens/events (seq #1..#N)
                                                    v
                                           DURABLE LOG (Redis Stream / Postgres)
client --GET /jobs/42/stream?after=57--> API --replay #58.. then live tail
```

### Layer 2: Durable execution
- Every **finished step** is saved as a **checkpoint** in a database (example record: job id, step number, step name, status `done`, result).
- If the worker crashes at step 7, another worker **resumes at step 7**. Steps 1 to 6 are **not re-run**, which also means model calls are **paid for once**, not twice.
- **Side effects need idempotency.** If an agent already did something irreversible (charge a card, send an email), a retry must not repeat it. Send a **unique idempotency key** with the action, derived from job and step (example: `Idempotency-Key: job42-step7` on a payment request). The same key on every retry makes the provider treat retries as one action.

```python
# Sketch only: checkpointed step runner with idempotency key
def run_step(job_id, step_no, name, fn):
    cp = db.get_checkpoint(job_id, step_no)
    if cp and cp.status == "done":
        return cp.result                       # replay, do not re-execute
    key = f"{job_id}-step{step_no}"            # stable across retries
    result = fn(idempotency_key=key)
    db.save_checkpoint(job_id, step_no, name, "done", result)
    return result
```

### Layer 3: Durable agent
- Because the work lives in the worker and the log, **nobody has to keep a browser tab open**. The user can close the tab, the job keeps running, and a later visit reconnects and replays from the log.
- *(Provenance note: the source clip lists this as the third part of a three-part series and shows the "tab closed, job still running" idea at the end. It may be explored in more depth in a separate video.)*

### Build vs buy (the source's rule of thumb)
- **Short chats on a single server** -> build it yourself (Redis Streams for live output, Postgres for state).
- **Long multi-step agents, or serverless functions that time out** (example: a 20-minute run vs a 15-minute function limit) -> use a **workflow / durable-execution framework**.

### Rules
1. Long-running work **never** executes inside the user's request/response.
2. Persist output as an **append-only, sequence-numbered log** and make clients resume by sequence number.
3. **Checkpoint after every completed step**, and make resume skip completed steps.
4. Every external side effect carries an **idempotency key** that is stable across retries.
5. Choose a framework when runs exceed platform timeouts or need human-approval waits, retries, or multi-day durability.

### Quick checklist
- [ ] Job id returned immediately; work runs in a worker
- [ ] Stream is resumable from `last_seen_seq`
- [ ] Checkpoint written per step; resume path tested by killing a worker mid-run
- [ ] Idempotency keys on payments, emails, writes to third parties
- [ ] Platform timeout < run length? Then use a durable-execution engine

---

## Skill D: Agent-to-agent communication (ACP, A2A, MCP)

### What ACP is (per IBM)
- **Agent Communication Protocol (ACP)** is an open standard for **agent-to-agent** communication, originally introduced by IBM's **BeeAI**, meant to replace siloed agents with interoperable systems.
- Key features IBM lists: **REST-based** (plain HTTP conventions), **no SDK required** (usable from cURL, Postman, a browser; an SDK exists for convenience), **offline discovery** (agents can embed metadata in their packages so they can be found even when not running, which suits scale-to-zero), and **async-first with sync supported** (good for long-running tasks).
- ACP does **not** manage workflows, deployments, or coordination itself. It standardizes how agents talk so orchestration can work across different agents. BeeAI was the orchestration/deployment system built on top.
- Problem it addresses: without a standard, N agents can need N(N-1)/2 bespoke integrations, across different frameworks (LangChain, crewAI, AutoGen, custom), auth models, and data formats.
- IBM's example: a manufacturer's scheduling agent asks a logistics provider's agent for shipping options and ETAs. Each side wraps its agent in a protocol interface, so no custom per-partner integration is needed and internals stay private.

### ⚠ Current status (important)
IBM's page carries a note that ACP **has merged with A2A under the Linux Foundation**, with the ACP team winding down active development and contributing to A2A. The `i-am-bee/acp` GitHub repo is **archived** and points to a migration guide. **For new work, target A2A.** Use ACP knowledge to understand the concepts and to read existing ACP code.

### ACP vs MCP vs A2A (summary)
| | MCP | ACP (legacy) | A2A (current standard for agent-to-agent) |
|---|---|---|---|
| Purpose | One model <-> many tools/data/context | Independent agents <-> agents | Independent agents <-> agents |
| Origin | Anthropic | IBM BeeAI | Google, donated to Linux Foundation |
| Mental model | Give a worker better tools | Form teams of workers | Form teams of workers |
| Transport style | JSON-RPC | REST/HTTP | JSON-RPC 2.0 over HTTP(S); streaming via SSE; async push notifications |
| Discovery | Server/tool listing | Manifest; works offline | **Agent Cards** |
| Status | Active | Archived, merged into A2A | Active, Linux Foundation project |

IBM's own framing: MCP = "one model, many tools"; ACP/A2A = "many agents working as peers". They are **complementary layers**, not rivals.

IBM's critique of MCP *for agent-to-agent use*: limited fine-grained (delta) streaming, no shared memory across agents on different servers, no defined message-body structure (hurts interoperability), and heavier JSON-RPC/SDK requirements.

### Rules
1. **Tools/data into one agent** -> MCP. **Agent to agent** -> A2A (ACP only for legacy).
2. Expose each agent through a **discoverable card/manifest** describing skills, endpoints, and auth.
3. Prefer **async + streaming** for anything long-running, and pair with Skill C (durable log + checkpoints) so protocol-level tasks survive crashes.
4. Keep agents **opaque**: share inputs/outputs, not internal memory, prompts, or tool implementations.
5. Plan for identity, delegation, and cross-org auth before connecting to outside agents. (IBM's ACP roadmap named identity federation, secure access delegation, multi-registry discovery, and agent sharing as open areas.)

### Minimal ACP shape (legacy reference, own sketch)
```python
# Legacy ACP-style server: decorate a function to expose it as an agent.
# acp_sdk is archived; for new builds use the A2A SDKs in Section 6.
from acp_sdk.server import Server
server = Server()

@server.agent()
async def my_agent(messages):
    # 1) convert protocol messages -> your framework's input
    # 2) run your model/framework
    # 3) yield protocol-formatted output
    ...

server.run()
```

---

## 6. Repo map: topic -> GitHub

Legend: **✔** = confirmed via search during this session. **◇** = well-known canonical repo from general knowledge, not re-verified here; confirm before pinning.

### Skill D: protocols
| Repo | What it is | Status |
|---|---|---|
| `github.com/a2aproject/A2A` | A2A spec; normative `specification/a2a.proto`; Apache-2.0; Linux Foundation | ✔ |
| `github.com/a2aproject/a2a-python` | Python SDK (`pip install a2a-sdk`) | ✔ |
| `github.com/a2aproject/a2a-js` | JS/TS SDK (`npm install @a2a-js/sdk`) | ✔ |
| `github.com/a2aproject/a2a-go` | Go SDK (`go get github.com/a2aproject/a2a-go`) | ✔ |
| `github.com/a2aproject/a2a-java` | Java SDK | ✔ |
| `github.com/a2aproject/a2a-samples` | Sample clients/servers/framework integrations | ✔ |
| `github.com/a2aproject/a2a-inspector` | Validation tooling for A2A agents | ✔ |
| `github.com/a2aproject/a2a-cli` | Official CLI for discovering/messaging A2A agents | ✔ |
| `github.com/i-am-bee/acp` | ACP spec (OpenAPI), Python/TS SDKs, examples. **Archived Aug 27, 2025**; points to migration guide | ✔ |
| `github.com/i-am-bee/beeai-platform` | Platform to discover/run/share agents; hosts ACP→A2A migration guide | ✔ (referenced from ACP README) |
| `github.com/i-am-bee/beeai-framework` | BeeAI agent framework | ✔ (referenced from ACP README) |
| `github.com/modelcontextprotocol/modelcontextprotocol` | MCP specification, schema (TypeScript-first, JSON Schema), official docs (modelcontextprotocol.io), MIT | ◇ (forks' READMEs confirmed contents) |

Docs: `a2a-protocol.org`, `agentcommunicationprotocol.dev`, `modelcontextprotocol.io`.

### Skill C: durable execution / resumable streams
| Repo | Notes | Status |
|---|---|---|
| `github.com/temporalio/temporal` | Replay-based durable execution; self-hosted service + workers; multi-language SDKs | ✔ |
| `github.com/inngest/inngest` | Event-driven, step-based durable functions; replays saved step results | ✔ |
| `github.com/dbos-inc/dbos-transact-py` | Python library; checkpoints workflows/steps into **Postgres** (no separate orchestrator) | ✔ |
| `github.com/dbos-inc/dbos-transact-ts` | TypeScript version of DBOS | ✔ |
| `github.com/triggerdotdev/trigger.dev` | Background jobs / durable runs for long tasks | ✔ |
| `github.com/restatedev/restate` | Durable execution runtime (low-latency, push-based) | ◇ |
| `github.com/langchain-ai/langgraph` | Agent graphs with checkpointers for resume | ◇ |
| `github.com/redis/redis` | Redis Streams (append-only log for resumable output) | ◇ |

Pattern mapping: **Redis Streams / Postgres table = Layer 1 durable log**. **Temporal / Inngest / DBOS / Restate / LangGraph checkpointer = Layer 2 checkpoints**. Idempotency keys are applied at the call to the external provider (for example payments APIs).

### Skill B: blue/green and progressive delivery
| Repo | Notes | Status |
|---|---|---|
| `github.com/argoproj/argo-rollouts` | Kubernetes controller: blue-green, canary, metric-based promotion/rollback | ✔ |
| `github.com/argoproj/rollouts-demo` | Demo app for Argo Rollouts | ✔ |
| `github.com/xataio/pgroll` | Zero-downtime, reversible Postgres schema migrations (expand/contract style) | ◇ |

The video's concrete example uses an AWS Application Load Balancer with two target groups and an RDS Postgres database. Argo Rollouts is the Kubernetes-native equivalent of the same idea.

### Skill A: concurrency runtimes
| Repo | Relevance | Status |
|---|---|---|
| `github.com/python/cpython` | `asyncio`, the GIL, optional free-threaded build | ◇ |
| `github.com/golang/go` | Goroutine scheduler (many tasks on few threads) | ◇ |
| `github.com/openjdk/jdk` | Java virtual threads | ◇ |
| `github.com/nodejs/node` | JavaScript event loop in practice | ◇ |

---

## 7. How the skills compose in one multi-agent system

```text
        user / client
             |  (resumable stream, Skill C layer 1)
             v
        API gateway ------------------ blue/green target groups (Skill B)
             |
             v
     orchestrator agent  <== async event loop for I/O (Skill A)
        |        |
   A2A (Skill D)  MCP (Skill D)
        |        |
  peer agents   tools / data
        |
   each long task = durable job: checkpoints + idempotency keys (Skill C layer 2)
   output = append-only sequence log (Skill C layer 1)
   CPU-heavy steps = worker processes, never in the event loop (Skill A)
   releases = flip traffic, expand/contract schema (Skill B)
```

Design order of operations when building a new agent platform:
1. Choose protocols: **MCP for tools, A2A for peers** (Skill D).
2. Make every agent task a **durable job** with a resumable log and checkpoints (Skill C).
3. Run the orchestrator **async**, push CPU work to worker processes (Skill A).
4. Ship via **blue/green** with expand/contract migrations and metric-gated rollback (Skill B).

---

## 8. Agent do / don't summary

**Do**
- Return a job id fast; run the work elsewhere.
- Resume by sequence number; skip completed checkpoints.
- Attach idempotency keys to every external side effect.
- Keep both app versions compatible with the live schema.
- Keep CPU work out of the event loop.
- Use A2A for new agent-to-agent links; MCP for tools.

**Don't**
- Hold an HTTP request open for the whole run.
- Re-run finished steps (it repeats model costs and side effects).
- Rename or drop a column in the same release that depends on the new one.
- Block an event loop with heavy computation.
- Start new work on archived ACP code without checking the migration guide.

---

## 9. Provenance and caveats

- **Videos:** the three source clips are short vertical explainers by @rick.theengineer. The content above was reconstructed from on-screen diagrams and captions. The audio was **not transcribed**, so specifics narrated only in speech may be missing, and exact figures should be treated as the video's illustrative examples.
- **Video 3** is framed as a three-part idea (resumable stream, durable execution, durable agent). Part 3 appears only at the very end of this clip.
- **IBM article:** summarized in my own words from the page as fetched. IBM notes the page may not reflect ACP's current status because ACP merged into A2A.
- **Repo list:** star counts and activity change. Re-check each repo's README and latest release before depending on it.
