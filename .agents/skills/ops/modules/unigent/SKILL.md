---
name: unigent
description: Build stateful agent workflows with typed outputs, reusable tools, session forks, file checkpoints, and ordinary TypeScript using the Unigent SDK. Use when creating agent workflows, parsing script arguments with Standard Schema/Zod, using Bun standalone scripts, configuring agent backends (Pi agent SDK, Claude CLI, Codex CLI), or writing model-free tests.
---

# Unigent Stateful Agent Workflows & SDK

Unigent is a TypeScript framework and CLI tool for building stateful agent workflows with typed outputs, reusable tools, session forks, file checkpoints, and ordinary TypeScript/Bun scripts.

## Quick Reference & Commands

- **Run Bun standalone script with Unigent**:
  ```bash
  unigent script.ts "Prompt / Input"
  ```
- **Interactive TUI Mode**:
  ```bash
  unigent tui script.ts "Prompt / Input"
  ```
- **Direct Bun Execution**:
  ```bash
  chmod +x script.ts
  ./script.ts "Prompt / Input"
  ```

## Key SDK Concepts & Usage Patterns

### 1. Parsing Arguments (`args`)
Use `args()` to parse CLI arguments via Zod or Standard Schema with automatic `--help` and `-i` (interactive prompt) support:

```typescript
import { args } from "unigent-sdk";
import { z } from "zod";

// Single string input
const prompt = await args(z.string().min(1), {
  description: "Task prompt for the agent workflow",
  usage: '"Prompt description"',
});

// Object schema for CLI flags
const config = await args(
  z.object({
    keyword: z.string().describe("Target keyword"),
    count: z.number().int().positive().default(1),
    cache: z.boolean().default(true),
  })
);
```

### 2. Creating Agents & Defining Backends
Unigent supports multiple harness adapters (`piAgent`, `claudeCli`, `codexCli`):

```typescript
import { agent, piAgent, claudeCli, codexCli, createFileCheckpointStore } from "unigent-sdk";
import { z } from "zod";

const defaults = {
  backend: piAgent(), // or claudeCli(), codexCli()
  checkpoint: createFileCheckpointStore(".unigent/checkpoints.jsonl"),
  limits: { turnDuration: "5m" as const },
};

const writer = agent({ ...defaults, name: "writer", model: "model-a" });
const reviewer = agent({ ...defaults, name: "reviewer", model: "model-b" });
```

### 3. Harness Adapter Capabilities & Restrictions

| Capability | Pi agent SDK | Claude CLI | Codex CLI |
| --- | --- | --- | --- |
| Prose, structured output, tools | Yes | Yes (ephemeral local MCP) | Yes (ephemeral local MCP) |
| Cost reporting & budgets | Yes | Yes | No |
| Session continuation & forks | Yes | Yes | Yes |
| Permissions | Unrestricted | Bypassed default (`permissions: "cli"`) | Bypassed default (`permissions: "cli"`) |

### 4. Checkpoint Deduplication & Resumption
Checkpoints reuse successful stateless runs across reruns:
```typescript
// Skip checkpoint for fresh stateful turns
const freshRun = agent.with({ checkpoint: false });
```

### 5. Testing Without a Model (`test` subpath)
Use `createScriptedBackend` or `createTestBackend` for model-free unit tests:

```typescript
import { agent } from "unigent-sdk";
import { createScriptedBackend } from "unigent-sdk/test";
import { z } from "zod";

const backend = createScriptedBackend([
  {
    toolCalls: [
      { name: "unigent_return", input: { value: { result: "Success" } } },
    ],
  },
]);

const subject = agent({ name: "subject", backend, model: "test" });
const result = await subject.run("Run test task", z.object({ result: z.string() }));
```
