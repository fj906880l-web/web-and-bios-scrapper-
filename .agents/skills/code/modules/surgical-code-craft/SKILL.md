---
name: surgical-code-craft
description: >-
  Surgical code editing, refactoring, and test-driven maintenance protocol
  based on the Software Craftsmanship Quartet (Fowler's Two Hats & Micro-Diffs,
  Beck's TDD sensory loop, Uncle Bob's Clean Boundaries & SRP, Brooks' Conceptual
  Integrity). Use whenever refactoring existing code, fixing non-trivial defects,
  modifying core business logic, or when instructed to edit surgically.
---

# Surgical Code Craft & Refactoring Protocol

A high-discipline code modification framework designed to eliminate agent regression errors, diff bloat, and broken abstractions. Built on the foundational doctrines of **Martin Fowler (*Refactoring*)**, **Kent Beck (*Test-Driven Development*)**, **Robert C. Martin (*Clean Architecture*)**, and **Frederick Brooks (*The Mythical Man-Month*)**.

---

## Overview

Autonomous coding agents frequently suffer from four critical failure modes:
1. **The Rewrite Trap:** Overwriting an entire 300-line module to adjust a 5-line bug, wiping out comments, types, and edge cases.
2. **Sensory Blindness:** Making unverified edits based on statistical token prediction rather than runtime test observations.
3. **Leaky Boundaries:** Tangling external I/O (APIs, WebSockets, DBs) directly inside core calculations and domain models.
4. **Style Drift:** Introducing alien design patterns, logging standards, or error handling mechanisms that violate the project's conceptual integrity.

`surgical-code-craft` mandates that every modification is isolated, verified, bounded, and stylistically coherent.

---

## Dependencies

* `fable-method`: Core cognitive problem-solving loop (Steps 0 through 6).
* `agent-harness-v2`: Runtime supervision, confidence scoring, and security gating.

---

## The Four Pillars of Surgical Craft

### 1. Fowler's Two-Hat Rule (Martin Fowler - *Refactoring*)
* **The Law:** You wear only one hat at a time:
  * **Hat 1: Change Behavior (Feature / Bugfix).** Observable behavior changes. Existing structure remains unchanged.
  * **Hat 2: Refactor (Restructure).** Structure improves. Observable behavior remains strictly invariant.
* **The Rule of Micro-Diffs:** Never rewrite what can be edited surgically. Use targeted replacement (`replace_file_content` targeting the specific function or block). If an edit exceeds 20% of the file, pause and verify whether you are unnecessarily destroying working code.

### 2. Beck's Sensory Feedback Loop (Kent Beck - *TDD*)
* **The Law:** The agent has no internal compiler or execution engine. Without automated tests, the agent is flying blind.
* **Characterization & Pinning Tests:**
  * Before refactoring legacy or tricky code, locate or create a characterization test (e.g., in `tests/`) that asserts current input/output behavior.
  * Execute the test suite (`pytest tests/...`, `npm test`, etc.) to establish a green baseline.
  * Apply the surgical edit.
  * Re-run the test suite to observe runtime success. Zero unverified assertions.

### 3. Uncle Bob's Clean Boundaries (Robert C. Martin - *Clean Architecture*)
* **The Law:** High-level domain logic must never depend on low-level implementation details.
* **Adapter Isolation:**
  * Core calculation engines (e.g. risk models, volatility sizing, order execution math) must remain pure functions or isolated classes that operate on plain data schemas.
  * External clients (e.g. QuiverQuant, broker endpoints, database drivers) must reside behind strict boundary interfaces/adapters.
  * When editing domain logic, never introduce direct third-party SDK calls or network requests.

### 4. Brooks' Conceptual Integrity (Fred Brooks - *The Mythical Man-Month*)
* **The Law:** A system must reflect a single, coherent design philosophy rather than a disjointed collection of prompt outputs.
* **Pattern Mirroring:**
  * Before writing code, inspect how existing files handle logging, error propagation, typing, and configuration.
  * Adopt the established idioms. If the project uses Pydantic, do not introduce `dataclasses` or raw `dict` schemas. If the project uses snake_case, do not use camelCase.

---

## The Surgical Execution Workflow

```
[1. PRE-FLIGHT]          Find or create characterization test. Run baseline: MUST BE GREEN.
      │
      ▼
[2. HAT SELECTION]       Declare: Hat 1 (Behavior Change) OR Hat 2 (Refactoring).
      │
      ▼
[3. SURGICAL CUT]        Apply targeted edit (replace_file_content). Keep diff under minimum necessary lines.
      │
      ▼
[4. OBSERVATION]         Re-run tests. Confirm green. If failed, rollback & diagnose (3-strike limit).
      │
      ▼
[5. TWIN CHECK]          Search codebase for identical defect pattern (TWINS: searched <pattern>).
      │
      ▼
[6. CLEAN EXIT]          Delete scratch/temporary test files. Report outcome-first.
```

### Step-by-Step Instructions

#### Step 1: Pre-Flight Baseline
Run the targeted test suite before touching any production file:
```bash
pytest tests/test_targeted_module.py
```
*If tests fail before you start, do not edit production code yet.* Document the existing failure first.

#### Step 2: Declare Intent & Hat
Write your mental state declaration:
```text
INTENT: Code currently does <X>; requirement expects <Y>; Hat: <Behavior | Refactor>.
```

#### Step 3: Execute the Surgical Cut
* Never overwrite the whole file unless authoring a brand-new file from scratch.
* Target the exact lines that require modification.
* Preserve all comments, docstrings, type hints, and neighboring methods.

#### Step 4: Verify by Observation
Run the automated test suite via shell command. Look for explicit `PASSED` signals. If output fails with a traceback, enter the 3-strike self-correction loop without asking the user for help.

#### Step 5: The Twin Check
If you resolved a bug, assume the same bug exists elsewhere. Run ripgrep across the workspace:
```text
TWINS: searched '<pattern>' - found <N> other occurrences across project.
```
Fix or document all identified twins.

---

## Common Mistakes & Anti-Patterns

| Failure Mode | What Happens | The Correct Practice |
| :--- | :--- | :--- |
| **The Blanket Overwrite** | Agent rewrites 250 lines to modify an `if` condition, breaking imports and comments. | Use `replace_file_content` targeting only the 5 affected lines. |
| **The "Looks Right" Trap** | Agent writes code, reads the diff, says "Done!", but never ran the test. | Always run the test command and visually confirm the exit code. |
| **The Boundary Leak** | Agent imports `requests` or an API client inside a pure mathematical helper. | Pass pure data into the function; keep I/O at the controller/adapter layer. |
| **The Paradigm Shift** | Agent introduces a completely new library or pattern not used anywhere else in the repo. | Read neighboring files first. Mirror existing error handling and types. |
