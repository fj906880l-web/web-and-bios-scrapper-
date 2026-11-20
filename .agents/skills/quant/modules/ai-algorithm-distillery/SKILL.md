---
name: ai-algorithm-distillery
description: >-
  Deterministic AI algorithm decision engine and resource calculator derived from the 38 foundational AI algorithms (Dave Defines). Computes RAG vector DB memory and token budgets, MoE parameter footprints, quantization/pruning compression ratios, cosine vector similarities, and algorithm selection trade-offs across all projects.
---

# AI Algorithm Distillery & Model Architecture Engine

## Overview
The `ai-algorithm-distillery` skill provides a deterministic mathematical engine and architectural decision framework derived from the 38 foundational algorithms that power modern Artificial Intelligence. It eliminates guesswork when designing ML pipelines, provisioning vector databases for RAG, calculating MoE VRAM budgets, planning quantization/pruning, and selecting optimal algorithms under latency, interpretability, and data-scale constraints.

## Dependencies
- Standard Python 3 runtime (`python3` or `uv run`).
- Zero external package dependencies (pure standard library).

## Quick Start
Run the CLI tool directly from anywhere on the machine:

```bash
python3 ~/.gemini/config/skills/ai-algorithm-distillery/scripts/ai_algorithm_distillery.py advisor --task "fraud detection classification" --data-size "large" --latency-sensitive --needs-interpretability
```

Or estimate RAG resource requirements:
```bash
python3 ~/.gemini/config/skills/ai-algorithm-distillery/scripts/ai_algorithm_distillery.py rag-estimate --doc-count 100000 --chunk-tokens 512 --embedding-dim 1536 --query-rps 25 --output /tmp/rag_plan.json
```

## Utility Scripts & Subcommands

The CLI script is located at `~/.gemini/config/skills/ai-algorithm-distillery/scripts/ai_algorithm_distillery.py`.

### 1. `advisor`
Recommends optimal algorithms and architectures based on engineering requirements.
- `--task`: Target task description (e.g. `classification`, `regression`, `clustering`, `rag`, `llm`, `timeseries`).
- `--data-size`: `small`, `medium`, or `large`.
- `--latency-sensitive`: Flag indicating sub-50ms inference requirement.
- `--needs-interpretability`: Flag indicating mandatory decision auditability (e.g. SHAP, linear weights).
- `--output`: Optional JSON file path to write results.

### 2. `rag-estimate`
Calculates vector storage footprints, HNSW graph index memory overhead, and token throughput for RAG pipelines.
- `--doc-count`: Total number of chunked documents in the knowledge base.
- `--chunk-tokens`: Average tokens per chunk (e.g. 512).
- `--embedding-dim`: Vector dimension (e.g. 1536 for text-embedding-3-small, 768 for Nomic/BERT).
- `--query-rps`: Projected queries per second.
- `--top-k`: Number of chunks retrieved per query (default: 5).
- `--precision`: Vector storage precision (`float32`, `float16`, `int8`).
- `--output`: Output file path.

### 3. `moe-budget`
Budgets active vs total parameter footprints, GPU VRAM requirements, and throughput efficiency for Mixture of Experts (MoE).
- `--total-params-b`: Total model parameters in billions (e.g. 47 for Mixtral 8x7B, 132 for DeepSeek).
- `--num-experts`: Total expert count (e.g. 8).
- `--active-experts`: Number of experts activated per token (e.g. 2).
- `--precision`: Model weight precision (`fp32`, `fp16`, `bf16`, `int8`, `int4`).
- `--output`: Output file path.

### 4. `quant-prune`
Calculates memory reduction factor, percentage savings, and parameter count adjustments under quantization (INT8/INT4) and structured weight pruning.
- `--base-params-b`: Base parameters in billions.
- `--current-precision`: Source precision (`fp32`, `fp16`).
- `--target-precision`: Quantized precision (`int8`, `int4`).
- `--prune-sparsity`: Fraction of weights pruned (0.0 to 0.8).
- `--output`: Output file path.

### 5. `similarity`
Computes Cosine Similarity, Euclidean Distance, Dot Product, and vector norms between two numerical coordinate vectors.
- `--vector1`: Comma-separated float coordinates (e.g. `"0.1, 0.4, 0.85"`).
- `--vector2`: Comma-separated float coordinates (e.g. `"0.12, 0.38, 0.9"`).
- `--output`: Output file path.

### 6. `explain`
Retrieves mathematical mechanics, computational complexity, assumptions, and deployment guidance for any of the 38 core AI algorithms.
- `--algorithm`: Algorithm key (e.g. `linear_regression`, `logistic_regression`, `knn`, `decision_tree`, `random_forest`, `gradient_boosting`, `naive_bayes`, `svm`, `pca`, `kmeans`, `matrix_factorization`, `mlp`, `cnn`, `rnn_lstm`, `attention_transformer`, `rag`, `moe`, `quantization_pruning`, `diffusion_models`, `reinforcement_learning_ppo`).
- `--output`: Output file path.

## Rate Limiting & Performance
- All calculations are pure deterministic CPU mathematics executed in sub-millisecond time.
- No network requests, API keys, or external service quotas are involved.

## Common Mistakes
1. **Confusing Total vs Active Parameters in MoE**: Total parameters dictate GPU VRAM storage requirements, while active parameters dictate inference FLOPs. Always use `moe-budget` to dimension both VRAM and compute.
2. **Ignoring HNSW Graph Memory Overhead in RAG**: Storing 1M vectors requires not just raw float array storage, but 1.3x - 1.5x additional RAM for the navigable small-world graph index. `rag-estimate` accounts for this automatically.
3. **Using Cosine Distance on Unnormalized Vectors**: Cosine similarity measures angle, whereas dot product includes magnitude. The `similarity` tool reports both explicitly.
