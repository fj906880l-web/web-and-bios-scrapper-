---
name: try-harder-poc-validation
description: Enforce skill-first execution with creative fallback ("Try Harder") and end-to-end Proof of Concept validation ("PoC or GTFO"). Use when a task invokes a skill that fails or is incomplete, during security testing or bug bounty hunting, or whenever a finding or hypothesis needs full end-to-end verification before reporting.
---
# try-harder-poc-validation

Follow defined skills first to match preferred workflows, but never stop when a skill is incomplete or fails. Switch to independent exploration ("Try Harder") and validate every finding end-to-end with a complete Proof of Concept ("PoC or GTFO").

## When to Use

- When executing a task that matches an existing skill or documented workflow.
- When a skill hits an edge case, lacks coverage, or fails to produce a working result.
- When performing security research, bug bounty hunting, or debugging where surface-level indicators are not enough.
- Before reporting any vulnerability, bug, or root cause that has only been inferred rather than proven.

## Steps

### 1. Start with the Skill

- Invoke the relevant skill or documented workflow first so the task follows preferred tools, conventions, and output formats.
- Note where the skill succeeds and where it hits a limitation, error, or gap.

### 2. Fall Back to Exploration ("Try Harder")

- If the skill is not comprehensive enough or fails, do not stop or report a dead end.
- Pivot to independent exploration and creative problem-solving using underlying tools, primitives, or alternative approaches.
- Iterate on hypotheses and test edge cases until you either resolve the obstacle or exhaust realistic avenues.

### 3. Validate End-to-End ("PoC or GTFO")

- Never stop at speculative claims such as "this looks like it might be vulnerable" or "this appears to work."
- Build and execute a full, reproducible Proof of Concept (PoC) that demonstrates the real impact or behavior end-to-end.
- Confirm the exact reproduction steps, inputs, and observed outputs before presenting the final result.

## Gotchas

- **Stopping at the first skill failure:** Treating a skill's limitation as the end of the task wastes the problem-solving capability available. Always pivot to direct exploration when a skill stalls.
- **Reporting unverified leads as findings:** Flagging theoretical issues without an end-to-end PoC creates noise and false positives. Keep investigating until you have concrete proof.
- **Abandoning the skill too early:** Skipping the skill entirely bypasses established workflows and conventions. Always try the skill first, then fall back to exploration only when needed.
