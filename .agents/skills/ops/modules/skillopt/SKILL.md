---
name: skillopt
description: "Self-evolving skill optimization framework for AI agents based on Microsoft SkillOpt and OKF (Observable Knowledge Framework) standards. Optimizes natural-language SKILL.md documents using trajectory reflection, patch aggregation, bounded editing, and validation gating without model fine-tuning."
---

# SkillOpt: Self-Evolving Skill Optimization Protocol (OKF Standard)

SkillOpt treats natural language skill files (`SKILL.md`) as a **trainable text state** for frozen LLM agents, standardized under the **Observable Knowledge Framework (OKF)**. Instead of mutating model weights, SkillOpt systematically improves skill performance on complex procedural tasks by performing bounded text updates (add/delete/replace) on `SKILL.md` documents validated against held-out benchmarks and registered in active OKF node databases.

---

## The 6-Stage SkillOpt + OKF Optimization Cycle

Whenever an agent or subagent encounters repeated failures, complex multi-step tasks, or suboptimal domain workflows, apply the 6-stage SkillOpt loop:

```
+------------------+     +-------------------+     +----------------------+
|  1. ROLLOUT      | --> |  2. REFLECT       | --> |  3. AGGREGATE        |
|  Run episodes &  |     |  Analyze traces & |     |  Combine candidate   |
|  log OKF nodes   |     |  identify patches |     |  text patches        |
+------------------+     +-------------------+     +----------------------+
                                                               |
+------------------+     +-------------------+                 v
|  6. OKF GATE     | <-- |  5. BOUNDED UPDATE| <-- +----------------------+
|  Validate &      |     |  Apply patches to |     |  4. SELECT EDITS     |
|  register node   |     |  SKILL.md file    |     |  Rank & prioritize   |
+------------------+     +-------------------+     +----------------------+
```

### Stage 1: Rollout & Trajectory Logging (OKF Standard)
- Execute task episodes using the candidate `SKILL.md` file.
- Log complete turn trajectories and register `OKFKnowledgeNode` metadata into `.skillopt/okf_registry.json`.

### Stage 2: Reflection & Patch Generation
- Analyze failure modes, redundant tool calls, missing preconditions, and unhandled edge cases across rollouts.
- Formulate precise, localized text modifications rather than full-document rewrites:
  - **ADD**: Insert new guidance, edge-case checks, or mandatory safety steps.
  - **REPLACE**: Clarify ambiguous instructions, update obsolete API signatures, or replace ineffective prompts.
  - **DELETE**: Remove contradictory or obsolete steps.

### Stage 3: Patch Aggregation
- Merge patch candidates from multiple rollout reflections into a unified delta set.
- Resolve conflicting edits by prioritizing patches that resolve severe runtime errors or verified bottlenecks.

### Stage 4: Selection & Ranking
- Select the top $k$ non-overlapping bounded patches with highest expected improvement.
- Ensure total edit size does not exceed 25% of the document to prevent concept drift.

### Stage 5: Bounded Text Update
- Apply selected patches strictly using exact line range replacement (`replace_file_content` / `multi_replace_file_content`).
- Maintain clean YAML frontmatter (`name`, `description`).

### Stage 6: OKF Validation Gating & Node Indexing
- Run the revised `SKILL.md` against held-out validation tasks or benchmark test scripts.
- **Accept Criteria**: Pass rate increases, zero regressions, and new node registered in OKF Active Database Registries.
- **Reject Criteria**: Performance degrades or validation fails $\rightarrow$ revert to previous candidate snapshot.
