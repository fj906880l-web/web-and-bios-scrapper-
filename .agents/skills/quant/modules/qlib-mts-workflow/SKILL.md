---
name: qlib-mts-workflow
description: >-
  Executes the declarative Qlib MTF/MTS daily quantitative trading workflow.
  Integrates point-in-time Expression Factor Engine (qlib.data), HMM Market
  Dynamics Adaptation, Unigent typed output validation, and FINRA risk caps.
---

# Qlib MTF/MTS Quantitative Trading Workflow

## Overview

This skill orchestrates the 5-step declarative daily trading workflow combining Microsoft Qlib expression factors (`qlib.data`), HMM Market Dynamics Adaptation (`test_hmm.py`), and Google Gemini AI market sentiment into a 4-pillar conviction score matrix.

## Dependencies

- `core/qlib_factor_engine.py`: Point-in-time factor calculator.
- `core/fusion_agent.py`: 4-Pillar Fusion & HMM Market Dynamics Engine.
- `scripts/run_qlib_mts_workflow.py`: Declarative workflow automation runner (`qrun`-style).
- `unigent`: Typed output schema validation (`logs/qlib_mts_daily_report.json`).

## Quick Start

Run the daily declarative workflow in simulation mode:

```bash
.venv/bin/python scripts/run_qlib_mts_workflow.py --dry-run --output logs/qlib_mts_daily_report.json
```

## Workflow Execution Steps

### 1. Data Ingestion & Point-in-Time Alignment

- Fetches real daily/intraday bar telemetry from YFinance / QuantPad.
- Enforces strict point-in-time alignment to eliminate look-ahead bias.

### 2. Qlib Factor Extraction

- Computes mathematical factor expressions:
  - `MA_Ratio_5_20`: `Mean($close, 5) / Mean($close, 20)`
  - `RSI_14`: `RSI($close, 14)`
  - `Volume_Ratio_20`: `$volume / Mean($volume, 20)`
  - `ATR_Spread_24`: `ATR(24) / $close`
  - `Price_Momentum_5D`: `$close / $close.shift(5) - 1.0`

### 3. HMM Market Dynamics Adaptation (Concept Drift)

- Detects market regime via HMM (`Bull`, `Bear`, `Volatile`).
- Auto-adjusts factor weights:
  - **Bull Phase**: 100% full factor weight.
  - **Bear Phase**: 60% factor weight (downweights bullish momentum).
  - **Volatile Phase**: 80% factor weight.

### 4. 4-Pillar Conviction Scoring

- Combines MTF Technicals (30%), Qlib Factors (30%), Gemini AI Sentiment (30%), and HMM Regime (10%).
- Trade Execution Threshold: Combined Conviction $\ge 0.70$.

### 5. Risk Enforcement & Order Dispatch

- **50% Absolute Capital Ceiling**: Max total allocation $\le 50\%$ equity.
- **25% Position Cap**: Max trade allocation $\le 25\%$ capital pool.
- **5% Hard Stop-Loss**: Proactively tightened to **4.9%**.

## Rate Limiting & Resource Constraints

- **Execution Time**: < 3.0 seconds per 50-symbol scan.
- **Memory Footprint**: < 250 MB RAM (100% compatible with $0/mo Google Cloud VPS `e2-micro`).
- **File Output**: All results written to `logs/qlib_mts_daily_report.json`.
