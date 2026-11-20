---
name: delegation-diligence-loop
description: "Strategic execution and supervisory loop for AI agent delegation and continuous verification. Implements the Claude Academy Delegation-Diligence 4D framework combined with Fable Method, Agent Harness v2.0 supervision, and TypeSafe System One judgment verification."
version: 1.0.0
trigger: /delegation-diligence-loop
---

# The Delegation-Diligence Loop

> **Core Philosophy (Claude Academy 4D Framework):**
> High-performance AI collaboration is governed by the continuous, bidirectional tension between **Delegation** (strategic judgment of what tasks to entrust to an AI and under what constraints) and **Diligence** (the mandatory responsibility of verifying outputs by direct observation, auditing security, and holding final accountability).

```
   ┌────────────────────────────────────────────────────────┐
   │                1. DELEGATION PHASE                     │
   │  • Problem Awareness (scope, reversibility, risk)       │
   │  • Platform Awareness (model capabilities & limits)    │
   │  • Boundary Enclosure (permissions, tools, timeouts)   │
   └───────────────────────────┬────────────────────────────┘
                               │ (Task Execution / Subagent Handoff)
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                 2. DILIGENCE PHASE                     │
   │  • Direct Observation (tests ran, numbers counted)     │
   │  • Shift-Left Security (<80 score blocks delivery)     │
   │  • TypeSafe Verification (typed semantic judgments)    │
   │  • Anti-Sycophancy & Truth Invariant Enforcement       │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │             3. RECONCILIATION & FEEDBACK               │
   │  • Diligence findings update future Delegation limits  │
   │  • Shrink agent autonomy on repeated failure (>2 errs) │
   │  • Expand delegation only after proven track record    │
   └────────────────────────────────────────────────────────┘
```

---

## 1. Phase 1: Delegation Protocol

Before handing off any subtask to a subagent, tool pipeline, or model execution loop, execute the **3-Point Awareness Gate**:

### 1.1 Problem Awareness
* **Is the ask reversible or irreversible?**
  * *Reversible:* Local file edits, local test executions, read operations, scratch analysis. Proceed autonomously.
  * *Irreversible / Outward-Facing:* Git push, deployments, database drops/truncates, sending emails/messages, touching production keys. **Requires explicit user authorization (`AUTH: user said "..."`)**.
* **Is the scope bounded?** Name the exact target files and outputs before delegating. Do not grant unbounded directory write access.

### 1.2 Platform Awareness
* **Can the model/tool actually answer this?**
  * If the answer lives in accessible files/tools: Delegate with exact tool access.
  * If the answer requires solving an open research problem or non-existent capability: Do NOT delegate to an open-ended loop; return an honest hand-back.
* **Select the Execution Layer:**
  * Fast structured decision/routing: Use **TypeSafe System One (`jev-latest`)** primitives (`choice`, `score`, `noul`).
  * Complex multi-step code/refactor: Delegate to a specialized background subagent (`subagent-orchestration`) with isolated workspace (`branch` mode).

---

## 2. Phase 2: Diligence Protocol

Diligence is **non-negotiable**. Never accept an agent deliverable or model response at face value without empirical evidence.

### 2.1 The 4 Diligence Checks
1. **Observation Over Inference:** The deliverable is not complete because the code "looks right." You must observe execution output (unit tests pass, exit code 0, metrics endpoint returns 200).
2. **Security Gating (Shift-Left Security):** Scan code deliverables with `security_scanner.py`. Any score $< 80$ or presence of exposed API keys/secrets blocks delivery immediately.
3. **TypeSafe Semantic Judgment:** For critical factual, compliance, or classification steps, query the TypeSafe System One model via the helper script (`scripts/typesafe_judge.py`) using `TYPESAFE_API_KEY` from the secure environment to obtain calibrated probabilities.
4. **Anti-Sycophancy / Structural Truth Check:** Verify that the output does not flatter the user by claiming unearned results or pretending impossible tasks are completed.

---

## 3. Phase 3: Feedback & Authority Calibration

The Delegation-Diligence loop is dynamic:
* **Success (+):** When subagents complete tasks with green diligence checks, maintain or gradually expand delegation boundaries.
* **Failure (-):** When diligence catches a failure:
  * Attempt 1: Surgical self-correction based on exact error output.
  * Attempt 2: Re-evaluate assumptions and retry with alternative approach.
  * Attempt 3: Hard freeze. Halt execution, generate diagnostic report, and escalate to human supervisor.
* **Authority Shrinkage:** If an agent hallucinates or violates constraints, immediately strip its execution permissions and require human-in-the-loop approval.

---

## 4. Operational Commands & Integration

### TypeSafe Verification Helper
When performing semantic verification under this skill, use the bundled CLI tool:
```bash
python3 /Users/malcolm/.gemini/config/skills/delegation-diligence-loop/scripts/typesafe_judge.py \
  --state "Summary or code to verify" \
  --instruction "Does this satisfy all criteria without security violations?" \
  --options "Pass,Fail"
```

### Response Header Requirement
When executing tasks under this skill, prepend the Harness v2.0 metadata:
```yaml
---
confidence: <0.00-0.99>
security_score: <0-100>
assets_loaded: [list]
skills_used: [delegation-diligence-loop, typesafe-ai]
supervisor_status: <active / intervened / cleared>
flags: [diligence-verified]
---
```
