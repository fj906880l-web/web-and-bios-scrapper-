---
name: soup-finetuning-harness
description: >-
  Autonomous fine-tuning, adaptation, and local GGUF/Ollama artifact deployment harness using Soup CLI (MakazhanAlpamys/Soup) across Quantitative Trading Engine, Allora Platform, and Market Haven.
version: 1.0.0
---

# Soup Autonomous Model Adaptation & Fine-Tuning Harness

## Overview
This skill operationalizes **Soup CLI** (`MakazhanAlpamys/Soup`) as an autonomous fine-tuning, adaptation, and local artifact-exporting sub-agent skill across the Antigravity ecosystem:
1. **Quantitative Trading Engine (`regime-trader`)**: HMM regime telemetry parsing, risk invariant instruction tuning.
2. **Allora Platform (`allara-app`)**: Nuclear medicine technologist domain adaptation and DPO alignment.
3. **Market Haven Charity Platform (`market-haven`)**: Internal agent orchestration, donor communication drafting, and PII-sanitized instruction tuning.

The harness enforces isolated virtual environment execution, bit-exact layer-streamed training (`stream_layers: true`) to fit within 4.0 GB VRAM, pre-flight doctor validation, GGUF quantization, and direct local Ollama catalog registration without cloud endpoints.

---

## Architecture & Operational Boundary

```
                           +-----------------------------------------------+
                           |            ANTIGRAVITY IDE WORKSPACE          |
                           |   (Claude Code / Gemini / Local Orchestrator) |
                           +-----------------------+-----------------------+
                                                   |
                   +-------------------------------+-------------------------------+
                   |                               |                               |
       +-----------v-----------+       +-----------v-----------+       +-----------v-----------+
       |   Quantitative AI     |       |       Allora App      |       |  Market Haven Charity |
       |  (HMM Regimes/Risk)   |       |  (NucMed / Testing)   |       |   (Donations / Web)   |
       +-----------+-----------+       +-----------+-----------+       +-----------+-----------+
                   |                               |                               |
                   +-------------------------------+-------------------------------+
                                                   |
                                                   v
                         +-----------------------------------+
                         |    LUMINA MCP SOUP AGENT HARNESS   |
                         |  (Zero-SSH / Layer-Streaming /    |
                         |   Telemetry & Export Pipeline)    |
                         +-----------------+-----------------+
                                           |
                   +-----------------------+-----------------------+
                   |                                               |
                   v                                               v
       +-----------------------+                       +-----------------------+
       |   Soup Training Core  |                       | Artifact Exporter &   |
       |  (QLoRA / GRPO / DPO) |                       | Ollama Local Loader   |
       +-----------------------+                       +-----------------------+
```

1. **Isolation & Determinism**: All fine-tuning operations execute via isolated virtual environment runners (`soup-cli[train]`) under Python 3.10–3.12. Base models remain untouched; adapters are generated in isolated build workspaces.
2. **Resource Throttling**: Training jobs utilize layer streaming (`stream_layers: true`) to operate strictly within hardware VRAM ceilings (conserving GPU/VRAM bandwidth on edge nodes and workstations).
3. **Export Compatibility**: Built-in automated export merges LoRA adapters directly into target quantizations (`GGUF q4_k_m`) and registers them into the local Ollama catalog for live agent serving.

---

## Dependencies

- `soup-cli` (v0.75.1+ installed via `uv tool` or virtual environment runner under Python 3.10–3.12)
- `ollama` (Local service running at `http://localhost:11434` with CLI at `/usr/local/bin/ollama`)
- `harness-engineering` (Agent Harness v2.0 memory, security gating, and ISTL confidence tracking)

---

## Quick Start

### 1. Initialize a Project Recipe
```bash
python3 /Users/malcolm/.gemini/config/skills/soup-finetuning-harness/scripts/soup_tool_runner.py init \
  --template chat \
  --output /Users/malcolm/.gemini/antigravity-ide/scratch/config/soup_recipes/sample_chat.yaml
```

### 2. Run Pre-flight Doctor Verification
```bash
python3 /Users/malcolm/.gemini/config/skills/soup-finetuning-harness/scripts/soup_tool_runner.py doctor \
  --config /Users/malcolm/.gemini/antigravity-ide/scratch/config/soup_recipes/sample_chat.yaml \
  --output /tmp/doctor_report.json
```

### 3. Programmatic Execution in Agent Code
```python
from shared.harnesses.soup_agent_tool import SoupExecutionHarness, SoupBuildConfig
from pathlib import Path

harness = SoupExecutionHarness(workspace_root=Path("/Users/malcolm/.gemini/antigravity-ide/scratch"))
cfg = SoupBuildConfig(
    project_name="regime_trader",
    base_model="Qwen/Qwen2.5-Coder-7B",
    dataset_path=Path("/Users/malcolm/.gemini/antigravity-ide/scratch/regime-trader/data/train.jsonl"),
    recipe_template="code",
    output_dir=Path("/Users/malcolm/.gemini/antigravity-ide/scratch/artifacts/models/regime_trader_adapter"),
    stream_layers=True,
    quant_type="q4_k_m"
)
recipe_path = harness.generate_recipe(cfg)
is_valid = harness.preflight_doctor(recipe_path)
```

---

## Multi-Project Configuration & Matrix

| Project Domain | Base Model Target | Adaptation Task | Target Quant / Runtime | Safety / Isolation Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Quantitative Trading AI** (`regime-trader`) | `Qwen/Qwen2.5-Coder-7B` | HMM regime telemetry parsing & execution syntax | `q4_k_m` → Local Ollama | Strict 0-loss gradient validation; zero hallucination on risk limits |
| **Allora Platform** (`allara-app`) | `meta-llama/Llama-3.1-8B` | Adaptive nuclear medicine technologist exam logic | `q4_k_m` → Mobile / Web Edge | Grounded clinical knowledge; DPO alignment against official item banks |
| **Market Haven Platform** (`market-haven`) | `mistralai/Mistral-7B-Instruct` | Internal agent orchestration & workflow drafting | `q5_k_m` → Desktop Node | Strict PII filtering; deterministic outputs for donor and campaign docs |

---

## Utility Scripts (CLI Runner)

The companion tool runner is located at `scripts/soup_tool_runner.py`. In accordance with harness standards, all CLI subcommands support `--output <file.json>` for deterministic agent parsing:

1. **`doctor`**: Checks system environment, dependencies, GPU detection, and verifies recipe schemas.
   ```bash
   python3 scripts/soup_tool_runner.py doctor [--config path/to/soup.yaml] --output report.json
   ```
2. **`init`**: Generates a standardized template recipe (`chat`, `code`, `tool-calling`, `reasoning`).
   ```bash
   python3 scripts/soup_tool_runner.py init --template code --output recipe.yaml
   ```
3. **`validate-recipe`**: Validates a recipe against Soup v0.75+ strict schema rules.
   ```bash
   python3 scripts/soup_tool_runner.py validate-recipe --config recipe.yaml --output val.json
   ```
4. **`matrix-verify`**: Executes pre-flight validation across all 3 ecosystem project configurations.
   ```bash
   python3 scripts/soup_tool_runner.py matrix-verify --output matrix_report.json
   ```
5. **`export-deploy`**: Automates GGUF quantization and local Ollama model registration.
   ```bash
   python3 scripts/soup_tool_runner.py export-deploy --model adapter_dir --name model_name --output deploy.json
   ```

---

## Common Mistakes & Troubleshooting

1. **Deprecated Schema Keys in `soup.yaml`**:
   - In Soup v0.75+, unknown keys are refused immediately.
   - Do NOT use `model: base: ...`; use top-level `base: ...`.
   - Do NOT use `data.max_seq_length`; use `data.max_length`.
   - Do NOT use `training.learning_rate`; use `training.lr`.
   - Do NOT use `optimizer: "adamw"`; use `optimizer: "adamw_torch"` or omit for standard AdamW.
2. **OOM on Edge GPU / Laptop**:
   - Always ensure `training.stream_layers: true` is enabled.
   - Set `batch_size: 1` and accumulate gradients (`gradient_accumulation_steps: 4` or `8`).
3. **Missing Ollama Model**:
   - Ensure the Ollama daemon is running (`ollama list`).
   - If `soup export` completes but Ollama fails, check file permissions on `.Modelfile` and target GGUF path.

---

## Model Asset & Checkpoint Security Protocol (Harness v2.1 Compliance)

All model fine-tuning, adapter merging, and checkpoint ingestion under Soup must comply with Section 7 of the Unified Antigravity Harness² Specification:
1. **Serialization Risk**: Treat `.pt`, `.pth`, `.bin`, and `.joblib` files as executable-risk artifacts. Prefer SafeTensors format for base weights and exported adapters.
2. **Quarantine & Hash Verification**: Before passing checkpoints or adapters into `soup-cli` or Ollama, download into a quarantine directory and verify against the publisher's recorded SHA-256 hash.
3. **PyTorch Loading Constraints**: When torch checkpoint loading is necessary, enforce `weights_only=True` on patched runtime releases, execute offline in disposable environments, and disable auto-import of external modules.
4. **HTTPS Enforcement**: Always fetch base models and manifests over HTTPS from official verified registries (e.g. Hugging Face, official Ollama library). Reject untrusted plain-HTTP links or domain-style links (such as `http://tokenizer.pt/` or `http://generator.pt/`).
5. **Component Boundary Isolation**: Never mix tokenizers, generators, or config files across differing model task families or architectures.

