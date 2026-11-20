---
name: ego-lite
description: Lightweight Agent Memory, Persistent Ego Identity, and State Graph Protocol (Citrolabs Ego-Lite). Use when maintaining long-term subagent memory, tracking conversational state graphs, and resolving agent identity across subagent handoffs.
---

# Ego-Lite Agent Memory & Identity Protocol

Ego-Lite provides lightweight persistent memory, state graph tracking, and identity continuity across multi-agent executions for Regime Trader.

## Core Features
1. **Persistent Ego State (`ego_state.json`)**: Tracks active subagent identity, execution goals, and historical decisions across chat sessions.
2. **Context Graph Storage**: Stores key insights, past trade justifications, and verified error resolutions in a compressed JSONL database.
3. **Multi-Agent Handoff Validation**: Ensures child subagents inherit exact parent parameters, risk limits, and FINRA compliance constraints without losing context.

## Usage & API Integration

```python
from core.shared_memory_store import SharedMemoryStore

class EgoLiteManager:
    def __init__(self, agent_id: str = "regime_trader_lead"):
        self.agent_id = agent_id
        self.memory = SharedMemoryStore()

    def record_decision(self, ticker: str, decision: str, confidence: float, reasoning: str):
        payload = {
            "agent_id": self.agent_id,
            "ticker": ticker,
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning
        }
        self.memory.set(f"ego_lite:{ticker}", payload)
```

## System Architecture Integration
- **Hybrid Rule Engine Note**: Included in Hybrid Hardcoded System Architecture (Fast-Path Deterministic Rules + LLM Subagent).
- **Zero Fake Data Enforcement**: Memory entries must cite empirical log lines and verified `run_command` outputs; synthetic memory generation is strictly prohibited.
