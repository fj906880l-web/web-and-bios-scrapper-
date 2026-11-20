---
name: active-trade-allocation
description: >-
  Ensures that active trades exceeding the allocation threshold run to completion without immediate auto-liquidation, with excess shares sold off during weekly/monthly rebalances.
---

# Active Trade Allocation & Rebalancing

## Overview

This skill provides rules and guidelines for subagents handling trade sizing, allocation audits, and portfolio rebalancing. When a trade is placed but subsequently reaches or goes over the target allocation limit (e.g. 10% of total portfolio value), it must NOT be canceled, trimmed, or auto-liquidated immediately. It must run its course, hit its stops/limits, and only have its excess shares trimmed during a scheduled rebalancing cycle.

## Dependencies

- `google-antigravity-sdk` (for executing agent workflows)

## Quick Start

To configure an agent to enforce this allocation logic:

```python
from google.antigravity import Agent, LocalAgentConfig

config = LocalAgentConfig(
    skills_paths=[".agents/skills/active-trade-allocation"]
)
```

## Workflow

### 1. Pre-Trade Sizing Check

- Calculate maximum trade allocation (50% of available buying power).
- Submit trade with entry price and 4.9% stop-loss protection.

### 2. Post-Trade Hold Gate

- If a ticker is actively held, do not submit duplicate BUY orders (pre-classification duplicate check).
- If the market value of the position naturally grows or exceeds the 10% portfolio allocation threshold, **do not trigger immediate auto-liquidation or trim orders**.

### 3. Periodic Rebalancing

- Sell off the excess shares for overweight positions only during a scheduled weekly or monthly rebalance cycle using the rebalance script:

  ```bash
  uv run scripts/rebalance_portfolio.py
  ```

## Common Mistakes

- **Immediate Intraday Trimming**: Trimming or liquidating a position the moment it crosses the 10% limit to free up cash. This is prohibited; the trade must run to completion.
- **Missing Rebalance Cycles**: Forgetting to run the rebalance scripts weekly or monthly, leading to long-term portfolio concentration.
