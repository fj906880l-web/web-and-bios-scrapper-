---
name: teach
description: "A stateful pedagogical tutoring agent that guides developers or users through complex concepts (e.g. Regime Trader architecture, Rubik's Cube solving) using stateful progress tracking, ZPD lessons, and cheat sheets in the repository."
---

# Stateful Tutoring (/teach) Skill

This skill turns the agent into a stateful, interactive tutor that tracks user progress across sessions using state files in the workspace.

## Tutoring Pipeline

When the user initiates a learning session (e.g. mentions "teach me", "tutor me", "solve Rubik's cube", or asks for a tutorial):

### 1. Initialization and Loading State
- The agent must read `.agents/teach_state.json` to find if a session is currently active.
- If no state file exists:
  - Present a welcoming prompt and list the pre-configured topics:
    1. **Regime Trader Architecture**: Understanding the quant engine, HMM regimes, risk manager, and multi-agent NLP parser.
    2. **FINRA & Trading Compliance**: Sizing stops, wash-trading checks, leverage, and compliance overrides.
    3. **Rubik's Cube Solving**: Learn the 3D spatial sequences, layer-by-layer method, and algorithms from memory.
    4. **Custom Topic**: Let the user choose any topic they want.
  - Run the python tutor script (`.agents/skills/teach/scripts/tutor.py --init "<chosen_topic>"`) to set up the file structure.

### 2. Delivering ZPD-based Lessons
- Run `.agents/skills/teach/scripts/tutor.py --next` to load the current lesson node details.
- Adapt the presentation to the **Zone of Proximal Development (ZPD)**:
  - Present information that is just slightly beyond their current verified level.
  - Provide clear diagrams, code examples (for programming topics), or spatial algorithms (for Rubik's Cube).
  - Explicitly ask the user to respond to the active quiz or challenge to verify their understanding.

### 3. Grading and State Progression
- When the user provides an answer:
  - Run `.agents/skills/teach/scripts/tutor.py --grade "<user_answer>"` to evaluate their response.
  - If correct, the script advances their tier and updates the cheat sheet `.agents/teach_cheatsheet.md`.
  - If incorrect, the script provides hints and keeps them on the current tier to reinforce learning.
  - Always print the grading feedback and run `--next` to show the next steps.
