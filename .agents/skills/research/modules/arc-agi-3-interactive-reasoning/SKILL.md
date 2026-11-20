---
name: arc-agi-3-interactive-reasoning
description: Automated protocol and operational playbook for ARC-AGI-3 interactive reasoning environments, REST API integration, session affinity management, and discrete topological grid planning.
version: 1.0.0
---

# ARC-AGI-3 Interactive Reasoning Protocol

This skill governs autonomous agent operation on ARC-AGI-3 benchmark environments.

## 1. REST API and Session Affinity
ARC-AGI-3 environments are stateful and require strict session affinity:
- Base URLs: `https://arcprize.org` or `https://three.arcprize.org`
- Authentication: Pass `X-API-Key` in all HTTP request headers.
- Session Cookies: Ensure all cookies received from `/api/scorecard/open`, `/api/cmd/RESET`, and `/api/cmd/ACTION*` (especially `GAMESESSION` and `AWSALBAPP-*`) are persisted across requests in an active HTTP session (`requests.Session()`).
- Endpoints:
  - `POST /api/scorecard/open`: Start an official tracked run.
  - `POST /api/cmd/RESET`: Initialize/reset a game session. Returns `guid` and first 64x64 frame.
  - `POST /api/cmd/ACTION1` to `ACTION5`, `ACTION7`: Simple 1-parameter actions (Up, Down, Left, Right, Interact, Undo).
  - `POST /api/cmd/ACTION6`: 2-parameter action requiring `x, y` integer coordinates.
  - `POST /api/scorecard/close`: Lock and finalize the scorecard, computing final RHAE score.

## 2. Discrete Spatial Representation
Do not feed raw 64x64 integer matrices directly into language model prompts. This causes rapid context depletion and spatial disorientation.
- Identify step size and player footprint (e.g. 5x5 entity on 5-pixel grid increments).
- Project the continuous frame into a discrete graph of walkable coordinates.
- Maintain an internal state map tracking obstacles, walls, doors, rotators, and interactable items.

## 3. RHAE Scoring Dynamics
Relative Human Action Efficiency (RHAE) evaluates:
$$\text{level\_score} = \left(\frac{\text{human\_baseline\_actions}}{\text{ai\_actions}}\right)^2 \quad (\le 1.15)$$
- Minimizing actions is quadratic in value: completing in fewer moves multiplies the score up to the 115% cap.
- Wandering or unconstrained exploration destroys the efficiency ratio. Use deterministic shortest-path algorithms (BFS or A*) for known transit paths.

## 4. Energy Management
- Monitor row 61 (energy bar).
- Each move consumes 2 energy units.
- Identify energy refill checkpoints (such as unlocked doors or energy pills) before embarking on long exploration paths to avoid timeout resets.
