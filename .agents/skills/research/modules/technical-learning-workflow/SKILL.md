---
name: technical-learning-workflow
description: Systematically analyze GitHub repositories and YouTube educational videos to extract actionable knowledge, create custom CLI tools, MCP servers, agent tools and skills, verify functionality, perform security reviews, autonomously implement improvements and refactors, and convert research into production-ready assets.
---

# Master Prompt: Technical Learning & Implementation Workflow

## Objective
Systematically analyze GitHub repositories and educational videos to extract actionable knowledge, verify it against authoritative sources, autonomously implement improvements, and convert it into deployable skills, notes, CLI tools, MCP servers, and code for production systems.

---

## Part 1: GitHub Repository Analysis Protocol

### Step 1 — First Impression (5 minutes)
1. Read `README.md` top-to-bottom for purpose, features, and quick-start.
2. Check the repo stats: stars, forks, last commit date, open issues/PRs.
3. Identify the license and maintenance status.

### Step 2 — Architecture Mapping (15–30 minutes)
1. **Directory structure**: List top-level folders and their roles.
2. **Entry points**: Find `main`, `index`, `app`, or `server` files.
3. **Dependencies**: Scan `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, etc.
4. **Core modules**: Identify the folders/files that contain the "business logic."
5. **Configuration**: Note `.env`, `config/`, `docker-compose.yml`, `k8s/` manifests.

### Step 3 — Deep Code Read (30–60 minutes)
1. Trace a single user journey or API call end-to-end.
2. Read key functions/classes with docstrings/comments.
3. Look for tests (`tests/`, `__tests__/`, `*.spec.*`) to understand expected behavior.
4. Check for CI/CD pipelines (`.github/workflows/`, `.gitlab-ci.yml`).

### Step 4 — Documentation Audit
1. Read all `.md` files: `CONTRIBUTING.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `docs/`.
2. Check the Wiki or hosted docs site.
3. Look for ADRs (Architecture Decision Records) or RFCs.

### Step 5 — Hands-On Validation
1. Clone the repo and run it locally following the README.
2. Run the test suite: `npm test`, `pytest`, `cargo test`, etc.
3. Make a small modification (e.g., change a config, add a log) and observe behavior.

### Step 6 — Implementation & Scaling Assessment
1. **Compatibility**: Does it match our stack (language, runtime, license)?
2. **Integration**: Can it be imported as a library, or must it run as a service?
3. **Scaling**: Does it support horizontal scaling, connection pooling, caching, async processing?
4. **Security**: Check for CVEs, secrets in code, auth mechanisms.
5. **Decision**: Fork/customize, import as dependency, or rewrite from scratch?

---

## Part 2: YouTube Video Learning Protocol

### Step 1 — Pre-View Setup
1. Note the video title, channel, publish date, and length.
2. Check the channel's credibility (subscriber count, other videos, credentials).
3. Identify the core topic and what you need to learn from it.

### Step 2 — Active Viewing (Watch Entire Length)
1. **First pass**: Watch without pausing; mark timestamps for key concepts.
2. **Second pass**: Pause at each key timestamp. Transcribe or screenshot diagrams.
3. **Third pass**: Watch at 1.25–1.5× speed to confirm nothing was missed.

### Step 3 — Note Synthesis
Create structured notes with the following sections:
- **Core Concept**: One-sentence summary.
- **Key Timestamps**: `MM:SS — What was covered`.
- **Code/Diagrams**: Copy-paste or screenshot any shown.
- **Claims Made**: List every technical assertion.
- **Questions Raised**: Anything unclear or that needs verification.

### Step 4 — Cross-Reference & Verification
For every technical claim in the video:
1. Check official documentation (MDN, docs.python.org, kubernetes.io, etc.).
2. Cross-check with a textbook or peer-reviewed paper (if applicable).
3. Search Stack Overflow, GitHub issues, or RFCs for community consensus.
4. Run any code snippets independently to confirm they work.
5. Flag any outdated, deprecated, or incorrect information.

### Step 5 — Asset & Tool Synthesis
Convert verified knowledge into reusable, functional assets:
1. **Markdown Note**: Save in `knowledge-base/<topic>.md` with front-matter (date, source, verified-by).
2. **Code Snippet**: Save in `snippets/<language>/<topic>.<ext>` with comments linking to source.
3. **Skill Prompt**: Write a reusable prompt template for future AI-assisted coding on this topic.
4. **Custom CLI / MCP Tool**: Build dedicated CLI commands, stdio MCP servers, or custom agent tools derived from the researched code/architecture.
5. **Implementation Ticket**: Create a task/ticket in your project tracker with acceptance criteria.

---

## Part 3: Tool, MCP & Skill Creation Protocol

When research yields an opportunity for custom tooling (CLI, MCP Server, Agent Tool, or Skill):

### Step 1 — Asset Scoping
1. **CLI Tool**: Build lightweight, non-interactive CLI scripts for recurring shell commands or data processing.
2. **MCP Server**: Package complex integrations (APIs, databases, web tools) into standard stdio MCP servers registered in `mcp_config.json`.
3. **Agent Skill**: Create structured `SKILL.md` instruction sets in `/Users/malcolm/.gemini/config/skills/`.

### Step 2 — Functional Runtime Verification
1. **Execution Test**: Run the generated CLI/MCP tool locally against test parameters.
2. **Task Validation**: Confirm the tool successfully completes the exact task displayed/requested in the research source.
3. **Non-Breaking Verification**: Ensure the addition does not break or mutate existing tool contracts or environment settings.

### Step 3 — Security Audit & Sanity Review
1. **Injection & Credential Safety**: Verify no hardcoded secrets, safe path handling, and sanitized shell inputs.
2. **Sandboxing & Boundaries**: Constrain execution scope to safe working directories and bounded memory/CPU limits.
3. **Third-Party Review**: Run static review and schema verification before registering or launching.

### Step 4 — Controlled Launch & Registration
1. Register the MCP server or skill into global/workspace configuration.
2. Log audit details and verify that live invocation succeeds across subagents.

---

## Part 4: Autonomous Self-Improvement & Execution Protocol

Whenever research, testing, code review, or runtime execution reveals potential improvements or bugs:

1. **Proactive Self-Implementation**: Do not ask the user for permission to execute routine optimizations, bug fixes, refactors, or code improvements. Implement them directly.
2. **Autonomous Tool & Skill Refinement**: Continually optimize existing CLI tools, MCP servers, scripts, and skills whenever new best practices or faster patterns are discovered.
3. **Self-Correction & Verification Loop**:
   - Detect sub-optimal paths or test failures immediately.
   - Formulate and apply the precise code modification.
   - Re-run verification commands (`pytest`, `npm test`, dry-runs) to empirically confirm the fix worked.
   - Record post-mortems and lessons learned for persistent agent memory.

---

## Part 5: Integration, Security & Scaling Checklist

Before deploying any learned component into production:
- [ ] Component runs in local/dev environment.
- [ ] Custom CLI, MCP tool, or Skill functionally verified with live dry-run.
- [ ] Security audit completed (no hardcoded secrets, injection protection, sandboxed execution).
- [ ] Autonomous improvements and refactors applied and validated.
- [ ] Unit and integration tests pass.
- [ ] Performance benchmarked under expected load.
- [ ] Monitoring and logging added.
- [ ] Documentation updated for team onboarding.
- [ ] Rollback plan defined.
- [ ] Zero functional regressions on existing tools/agents.

---

# EXAMPLES

---

## Example A: GitHub Repo Analysis — "meilisearch/meilisearch"

### 1. First Impression
- **Purpose**: Fast, typo-tolerant search engine (Algolia alternative).
- **Stats**: 45k+ stars, actively maintained, Rust codebase.
- **License**: MIT — safe for commercial use.

### 2. Architecture Mapping
```
meilisearch/
├── meilisearch/          # Core search engine binary
├── milli/                # Indexing library (Rust)
├── meilisearch-types/    # Shared types
├── benchmarks/           # Performance tests
├── docker-compose.yml    # Easy local spin-up
└── .github/workflows/    # CI for Rust tests + Docker builds
```
- **Entry point**: `meilisearch/src/main.rs`
- **Core module**: `milli/` — handles inverted index, tokenization, ranking.
- **Config**: Environment variables + CLI flags (see `--help`).

### 3. Deep Code Read
- Traced an HTTP search request: `main.rs` → `search.rs` → `milli::search()`.
- Found ranking rules in `milli/src/search.rs`: `words`, `typo`, `proximity`, `attribute`, `exactness`.
- Tests in `milli/tests/` validate index creation and search relevance.

### 4. Documentation Audit
- `README.md`: Quick start with Docker.
- `docs/`: Full documentation site (deployed to docs.meilisearch.com).
- `CONTRIBUTING.md`: Rust formatting with `rustfmt`, testing with `cargo test`.

### 5. Hands-On Validation
```bash
docker run -p 7700:7700 getmeili/meilisearch:latest
# Uploaded 10k JSON documents via REST API
# Search latency: ~2ms for typo-tolerant queries
```

### 6. Implementation & Scaling Assessment
- **Compatibility**: Runs as standalone binary or Docker container. REST API — language-agnostic.
- **Integration**: Use official SDKs (JS, Python, Go) or raw HTTP. No code changes needed in our app.
- **Scaling**: Official docs recommend 1 master + N replicas for high availability. Index is memory-mapped; RAM scales with index size.
- **Decision**: Deploy as a sidecar service. Use `meilisearch-js` SDK in our Node.js backend. Start with single instance; scale to replica cluster when QPS > 1,000.

---

## Example B: GitHub Repo Analysis — "langchain-ai/langchain"

### 1. First Impression
- **Purpose**: Framework for building LLM-powered applications.
- **Stats**: 90k+ stars, monorepo (Python + JS/TS), very active.
- **License**: MIT.

### 2. Architecture Mapping
```
langchain/
├── libs/
│   ├── langchain/           # Core Python package
│   ├── langchain-community/ # Third-party integrations
│   ├── langchain-core/      # Base abstractions
│   └── langchain-text-splitters/
├── cookbook/                # Example notebooks
├── docs/                    # API reference + guides
└── .github/workflows/       # Massive CI matrix (Python 3.8–3.12, OS matrix)
```
- **Entry point**: `libs/langchain/langchain/__init__.py`
- **Core abstraction**: `libs/langchain-core/langchain_core/runnables/` — LCEL (LangChain Expression Language).

### 3. Deep Code Read
- Traced a `chain.invoke()` call through `RunnableSequence` → `RunnableParallel` → individual `RunnableLambda` nodes.
- Found that `langchain-core` is designed to be lightweight; heavy integrations live in `langchain-community`.
- Tests use `pytest` with extensive mocking for LLM API calls.

### 4. Documentation Audit
- `cookbook/` has 50+ Jupyter notebooks for real-world patterns (RAG, agents, extraction).
- `docs/docs/concepts/` explains LCEL, callbacks, memory architecture.

### 5. Hands-On Validation
```python
from langchain_core.runnables import RunnableLambda
chain = RunnableLambda(lambda x: x["input"].upper()) | RunnableLambda(lambda x: {"output": x})
assert chain.invoke({"input": "hello"}) == {"output": "HELLO"}
```

### 6. Implementation & Scaling Assessment
- **Compatibility**: Python 3.9+. We use Python 3.11 — compatible.
- **Integration**: Install only `langchain-core` + specific integrations to avoid bloat (`pip install langchain-openai`).
- **Scaling**: LCEL chains are stateless — can run in FastAPI endpoints behind a load balancer. Use Redis for `ChatMessageHistory` persistence. Async support via `ainvoke()`.
- **Decision**: Adopt `langchain-core` for chain composition. Avoid `langchain` meta-package to reduce dependency surface. Write custom `Runnable` classes for our internal APIs.

---

## Example C: YouTube Video Analysis — "System Design: How Discord Stores Trillions of Messages"

### 1. Pre-View Setup
- **Channel**: ByteByteGo (System design experts, 1M+ subs).
- **Length**: 18:42.
- **Goal**: Understand Discord's migration from MongoDB to Cassandra/ScyllaDB for message storage.

### 2. Active Viewing Timestamps
- `02:15` — Original stack: MongoDB + single replica set. Hit write throughput limits.
- `05:30` — Migration to Cassandra: time-series partitioning by `channel_id + bucket`.
- `08:45` — Hot partition problem: popular channels caused single-node overload.
- `11:20` — Solution: Move to ScyllaDB (C++ Cassandra rewrite) + auto-sharding.
- `14:00` — Message ID structure: Snowflake-like (time + sequence + node ID).
- `16:30` — Read path: Query recent bucket first, paginate backward.

### 3. Note Synthesis
```markdown
## Discord Message Storage Architecture
**Source**: ByteByteGo YouTube, "How Discord Stores Trillions of Messages"
**Date**: 2024-03-15
**Verified**: Partial

### Core Concept
Discord migrated from MongoDB → Cassandra → ScyllaDB to handle
linearly growing message write volume with predictable read latency.

### Key Design Decisions
1. **Partition Key**: `(channel_id, message_bucket)` where bucket = time window.
2. **Hot Partitions**: Solved by ScyllaDB's shard-per-core model.
3. **ID Generation**: Snowflake-style for time-ordered, k-sortable IDs.

### Code Pattern (Conceptual)
```python
bucket = message.timestamp.strftime("%Y-%m")
partition_key = (channel_id, bucket)
```
```

### 4. Cross-Reference & Verification
- **Claim**: "Cassandra has hot partition issues."
  - **Verified**: True. DataStax docs and ACM paper "Cassandra: A Decentralized Structured Storage System" confirm partition key design is critical for even distribution.
- **Claim**: "ScyllaDB is 10× faster than Cassandra."
  - **Verified**: Partially true. ScyllaDB benchmarks (scylladb.com) show 10× throughput on identical hardware, but only with proper shard-aware drivers. Community benchmarks on Hacker News show 3–5× in real-world mixed workloads.
- **Claim**: "Snowflake IDs eliminate need for separate timestamp index."
  - **Verified**: True. Twitter engineering blog and Discord's own engineering blog confirm this.

### 5. Skill/Note Configuration

**Saved Note**: `knowledge-base/distributed-systems/message-storage-at-scale.md`

**Code Snippet** (`snippets/python/snowflake_id.py`):
```python
import time
import dataclasses

@dataclasses.dataclass(frozen=True)
class Snowflake:
    epoch: int = 1288834974657  # Twitter epoch

    def generate(self, sequence: int, node_id: int = 1) -> int:
        timestamp = int((time.time() * 1000) - self.epoch)
        return (timestamp << 22) | (node_id << 12) | sequence
```

**Skill Prompt** (`skills/message-storage-design.md`):
```markdown
When designing a message/feed storage system:
1. Use time-bucketed partition keys (channel_id + month/week).
2. Generate time-ordered IDs (Snowflake, ULID, KSUID) to avoid secondary indexes on timestamp.
3. Evaluate ScyllaDB vs Cassandra if write throughput > 100K msgs/sec per node.
4. Always test for hot partitions with real access patterns before production.
```

**Implementation Ticket**:
```markdown
Title: Evaluate ScyllaDB for notification feed storage
AC:
- [ ] Benchmark write throughput on current PostgreSQL vs ScyllaDB
- [ ] Implement time-bucketed partition key in test cluster
- [ ] Measure p99 read latency for last 50 messages query
- [ ] Document migration plan from PostgreSQL
```

---

## Example D: YouTube Video Analysis — "Kubernetes Controllers Deep Dive"

### 1. Pre-View Setup
- **Channel**: The Linux Foundation / CNCF (Official Kubernetes channel).
- **Length**: 42:15.
- **Goal**: Understand how to write a custom Kubernetes controller for our internal CRD.

### 2. Active Viewing Timestamps
- `04:00` — Controller pattern: Watch → Diff → Act → Update Status.
- `09:30` — client-go `Informer` vs `ListerWatcher` — when to use each.
- `18:45` — Workqueue pattern: rate limiting, requeuing on failure.
- `28:10` — OwnerReferences and garbage collection for child resources.
- `35:00` — Testing controllers with `envtest` (no real cluster needed).

### 3. Note Synthesis
```markdown
## Kubernetes Controller Architecture
**Source**: CNCF YouTube, "Kubernetes Controllers Deep Dive"
**Date**: 2024-01-10
**Verified**: Yes (official Kubernetes project channel)

### Core Loop
1. **Inform**: Informer caches objects, triggers event handlers.
2. **Enqueue**: Add object key to workqueue with rate limiting.
3. **Reconcile**: Fetch latest state from API server, compare with desired state, apply changes.
4. **Update Status**: Write observed state back to `.status` subresource.

### Key Pattern: OwnerReferences
When a controller creates child resources (Pods, Services), set:
```yaml
ownerReferences:
- apiVersion: apps/v1
  kind: Deployment
  name: parent-deployment
  uid: <parent-uid>
```
This enables automatic garbage collection when parent is deleted.
```

### 4. Cross-Reference & Verification
- **Claim**: "Use `workqueue` instead of raw channels for production controllers."
  - **Verified**: True. Official `sample-controller` repo and "Programming Kubernetes" book (O'Reilly, 2019) both emphasize this for rate limiting and deduplication.
- **Claim**: "`envtest` spins up a local control plane without etcd."
  - **Verified**: True. controller-runtime docs confirm `envtest` uses a compiled `etcd` + `apiserver` binary for fast integration tests.

### 5. Skill/Note Configuration

**Saved Note**: `knowledge-base/kubernetes/custom-controller-pattern.md`

**Code Snippet** (`snippets/go/controller-reconcile.go`):
```go
func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var app mygroupv1.MyApp
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // Desired state
    deployment := r.desiredDeployment(app)

    // Apply
    if err := r.applyDeployment(ctx, deployment); err != nil {
        return ctrl.Result{RequeueAfter: 30 * time.Second}, err
    }

    // Update status
    app.Status.Ready = true
    return ctrl.Result{}, r.Status().Update(ctx, &app)
}
```

**Skill Prompt** (`skills/kubernetes-controller-dev.md`):
```markdown
When writing a Kubernetes controller:
1. Use controller-runtime, not raw client-go, for faster development.
2. Always implement `Reconcile` as idempotent (same input → same output).
3. Set `OwnerReferences` on all created child resources.
4. Use `envtest` for unit tests; use Kind for e2e tests.
5. Expose Prometheus metrics for reconcile latency and error rate.
```

---

# SUMMARY TEMPLATE (Reusable)

After completing either protocol, fill out this summary:

```markdown
## Learning Summary: [Topic/Repo/Video Name]
**Date**: YYYY-MM-DD
**Time Invested**: X hours
**Source**: [URL]

### What It Is
[1-paragraph summary]

### How It Works
[Architecture, key mechanisms, data flow]

### Verified Claims
| Claim | Source | Verdict |
|-------|--------|---------|
| ...   | ...    | ✅/⚠️/❌ |

### How to Implement in Our System
[Specific integration steps, files to modify, dependencies to add]

### Scaling Considerations
[Performance limits, horizontal scaling strategy, bottlenecks]

### Artifacts Created
- [ ] Note saved to: `knowledge-base/...`
- [ ] Code snippet saved to: `snippets/...`
- [ ] Skill prompt saved to: `skills/...`
- [ ] Custom CLI / MCP server / tool created: `...`
- [ ] Implementation ticket created: [Link]
```
