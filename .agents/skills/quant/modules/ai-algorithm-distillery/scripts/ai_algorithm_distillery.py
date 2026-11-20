#!/usr/bin/env python3
"""
AI Algorithm Distillery CLI Tool
Derived from Dave Defines: "Every AI Concept Explained Intuitively!" (38 Core AI Algorithms)

Provides deterministic calculators, architectural estimators, similarity metrics,
and model selection decision logic for modern AI and ML systems.
"""

import argparse
import json
import math
import sys
import os
from typing import Dict, Any, List

# 38 Algorithms Knowledge Base extracted from Video 1
ALGORITHM_CATALOG: Dict[str, Dict[str, Any]] = {
    "linear_regression": {
        "name": "Linear Regression",
        "category": "Supervised / Regression",
        "intuition": "Minimizes squared residuals between continuous predictions and targets (spring-tension line of best fit).",
        "complexity": "O(N * D) training with gradient descent, O(D) inference",
        "assumptions": ["Linear relationship", "Homoscedasticity", "Independence of errors", "Normality of residuals"],
        "when_to_use": "Baseline continuous forecasting, interpretable feature coefficients, financial pricing baselines."
    },
    "logistic_regression": {
        "name": "Logistic Regression",
        "category": "Supervised / Classification",
        "intuition": "Passes linear combination through a Sigmoid (or Softmax) function to map unbounded scores to probabilities [0, 1].",
        "complexity": "O(N * D) training, O(D) inference",
        "assumptions": ["Linearity in log-odds", "Absence of multicollinearity"],
        "when_to_use": "Binary or multiclass probability calibration, baseline classification, churn prediction."
    },
    "knn": {
        "name": "K-Nearest Neighbors",
        "category": "Lazy Learning / Instance-Based",
        "intuition": "Zero training phase; memorizes dataset and classifies or regresses query based on majority vote of K closest Euclidean points.",
        "complexity": "O(1) training, O(N * D) brute-force inference (reduced via KD-Tree/Ball-Tree)",
        "assumptions": ["Proximity implies similarity", "Low to moderate dimensionality (avoids curse of dimensionality)"],
        "when_to_use": "Small non-linear datasets, recommendation cold-starts, prototype matching."
    },
    "decision_tree": {
        "name": "Decision Tree",
        "category": "Supervised / Tree-Based",
        "intuition": "Hierarchical greedy feature splitting maximizing Information Gain (Entropy reduction) or minimizing Gini Impurity.",
        "complexity": "O(N * D * log N) training, O(log N) inference",
        "assumptions": ["Axis-aligned decision boundaries"],
        "when_to_use": "Rule-based decision extraction, non-linear tabular data without scaling requirement."
    },
    "random_forest": {
        "name": "Random Forest",
        "category": "Ensemble / Bagging",
        "intuition": "Ensemble of decorrelated decision trees trained on bootstrap samples and random feature subsets; cancels out variance.",
        "complexity": "O(T * N * D * log N) training, O(T * depth) inference",
        "assumptions": ["Independence between individual tree errors"],
        "when_to_use": "Robust tabular classification/regression with low tuning overhead and high variance resistance."
    },
    "gradient_boosting": {
        "name": "Gradient Boosting (GBDT / XGBoost / LightGBM)",
        "category": "Ensemble / Boosting",
        "intuition": "Sequential residual correction: each successive shallow tree fits the pseudo-residuals (negative gradient of loss) of previous trees.",
        "complexity": "O(T * N * D) training, O(T * depth) inference",
        "assumptions": ["Low noise in target variables, careful learning rate regularization"],
        "when_to_use": "Gold standard for tabular competition benchmarks, structured fraud detection, click-through prediction."
    },
    "naive_bayes": {
        "name": "Naive Bayes",
        "category": "Probabilistic / Generative",
        "intuition": "Applies Bayes' theorem assuming conditional independence of all features given the class label.",
        "complexity": "O(N * D) training, O(D) inference",
        "assumptions": ["Conditional feature independence (naive)"],
        "when_to_use": "Text classification, spam filtering, high-dimensional streaming data where speed is paramount."
    },
    "svm": {
        "name": "Support Vector Machine (SVM)",
        "category": "Supervised / Margin Maximization",
        "intuition": "Constructs maximum-margin hyperplanes in transformed Hilbert space using kernel trick; bounded by support vectors.",
        "complexity": "O(N^2 * D) to O(N^3) training, O(SV * D) inference",
        "assumptions": ["Separability in kernel space"],
        "when_to_use": "Medium-sized high-dimensional datasets (genomics, text categorization, image classification)."
    },
    "pca": {
        "name": "Principal Component Analysis (PCA)",
        "category": "Unsupervised / Dimensionality Reduction",
        "intuition": "Computes eigenvectors of covariance matrix to project data onto orthogonal axes of maximum variance.",
        "complexity": "O(min(N*D^2, N^2*D)) computation",
        "assumptions": ["Linearity, high variance captures signal, orthogonal components"],
        "when_to_use": "Compressing feature spaces, data visualization, eliminating multicollinearity."
    },
    "kmeans": {
        "name": "K-Means Clustering",
        "category": "Unsupervised / Partitioning",
        "intuition": "Iterative Expectation-Maximization: assigns points to closest centroids, recalculates centroids as cluster means until convergence.",
        "complexity": "O(I * K * N * D)",
        "assumptions": ["Spherical, equal-variance clusters, Euclidean metric"],
        "when_to_use": "Customer segmentation, vector quantization, exploratory data clustering."
    },
    "matrix_factorization": {
        "name": "Matrix Factorization (SVD / ALS)",
        "category": "Collaborative Filtering / Latent Factors",
        "intuition": "Decomposes sparse user-item interaction matrix R (M x N) into dense user U (M x K) and item V (N x K) latent matrices.",
        "complexity": "O(K * non_zeros) per iteration",
        "assumptions": ["Low-rank latent affinity structure"],
        "when_to_use": "Personalized recommendation engines, rating prediction, collaborative matrix completion."
    },
    "mlp": {
        "name": "Multi-Layer Perceptron (MLP)",
        "category": "Deep Learning / Feedforward",
        "intuition": "Universal approximator stacking affine transforms (W*x + b) interleaved with non-linear activation functions (ReLU, GELU).",
        "complexity": "O(N * sum(L_i * L_{i+1})) per epoch",
        "assumptions": ["Differentiable loss functions, gradient-based backpropagation"],
        "when_to_use": "Universal non-linear mapping, tabular neural architectures, classification/regression heads."
    },
    "cnn": {
        "name": "Convolutional Neural Network (CNN)",
        "category": "Deep Learning / Computer Vision",
        "intuition": "Parameter-sharing sliding filters exploit spatial locality and translation equivariance to extract hierarchical visual features.",
        "complexity": "O(H * W * C_in * C_out * K_h * K_w)",
        "assumptions": ["Spatial locality and stationarity in 2D/3D grids"],
        "when_to_use": "Image classification, audio spectrogram processing, medical imaging."
    },
    "rnn_lstm": {
        "name": "Recurrent Neural Networks & LSTM",
        "category": "Deep Learning / Sequential",
        "intuition": "Recurrent state loops with input, forget, and output gating mechanisms to mitigate vanishing gradients in sequence modeling.",
        "complexity": "O(T * H^2) per sequence where T is length, H is hidden dimension",
        "assumptions": ["Temporal continuity and Markovian context transitions"],
        "when_to_use": "Time-series forecasting, streaming sequential sensors, speech processing."
    },
    "attention_transformer": {
        "name": "Attention Mechanism & Transformers",
        "category": "Deep Learning / Sequence & Multi-Modal",
        "intuition": "Computes dynamic pairwise affinity matrices: Softmax(Q * K^T / sqrt(d_k)) * V; processes all sequence tokens in parallel.",
        "complexity": "O(T^2 * D) standard attention, O(T * D) linear attention",
        "assumptions": ["Permutation invariance modulo positional embeddings"],
        "when_to_use": "Large language models (LLMs), vision transformers (ViT), code synthesis, multimodal understanding."
    },
    "rag": {
        "name": "Retrieval-Augmented Generation (RAG)",
        "category": "System Architecture / Hybrid AI",
        "intuition": "Decouples parametric reasoning (LLM) from dynamic non-parametric knowledge (vector DB + dense embeddings) to eliminate hallucinations.",
        "complexity": "Vector query O(log M) with HNSW, context generation O(T_prompt + T_gen)",
        "assumptions": ["Semantically relevant context retrieved via cosine similarity improves answer truthfulness"],
        "when_to_use": "Enterprise search, knowledge-grounded chatbots, documentation Q&A."
    },
    "moe": {
        "name": "Mixture of Experts (MoE)",
        "category": "Model Architecture / Sparse Computation",
        "intuition": "Splits feedforward layers into E experts; a gating router activates only top-K experts per token, unlocking massive capacity at low FLOPs.",
        "complexity": "Total parameters = E * P_expert; Active parameters = K * P_expert (K << E)",
        "assumptions": ["Specialization across modular subnetworks with balanced routing load"],
        "when_to_use": "High-efficiency scaling of LLMs (e.g. Mixtral, GPT-4, Grok), low-latency high-parameter inference."
    },
    "quantization_pruning": {
        "name": "Quantization & Pruning",
        "category": "Model Optimization / Compression",
        "intuition": "Quantization maps FP32/FP16 weights to INT8/INT4 discrete grids; pruning eliminates near-zero weights to sparsify computation.",
        "complexity": "Reduces memory footprint by 2x-8x; enables INT8/INT4 Tensor Core acceleration",
        "assumptions": ["Neural networks are overparameterized and resilient to small precision perturbations"],
        "when_to_use": "Edge deployment, GPU VRAM reduction, high-throughput model serving."
    },
    "diffusion_models": {
        "name": "Diffusion Models",
        "category": "Generative / Stochastic",
        "intuition": "Gradually corrupts data with Gaussian noise in forward pass, then trains a U-Net / DiT to reverse the noise trajectory step-by-step.",
        "complexity": "O(Steps * U-Net_FLOPs) inference",
        "assumptions": ["Continuous Markovian noise scheduling"],
        "when_to_use": "State-of-the-art photorealistic image, video, and audio synthesis."
    },
    "reinforcement_learning_ppo": {
        "name": "Reinforcement Learning (PPO / DQN)",
        "category": "Reinforcement Learning / Decision Control",
        "intuition": "Optimizes sequential decisions via Bellman value backups (DQN) or clipped policy gradient ratio bounds (PPO) to maximize discounted rewards.",
        "complexity": "Environment simulation bound + policy backward pass",
        "assumptions": ["Markov Decision Process (MDP), exploration vs exploitation balance"],
        "when_to_use": "RLHF for language models, algorithmic execution, autonomous robotics."
    }
}


def compute_vector_similarity(v1: List[float], v2: List[float]) -> Dict[str, float]:
    """Computes cosine similarity, dot product, and euclidean distance."""
    if len(v1) != len(v2):
        raise ValueError(f"Vector dimensions do not match: {len(v1)} vs {len(v2)}")
    if len(v1) == 0:
        raise ValueError("Vectors cannot be empty")

    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    euclidean = math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

    cosine = (dot / (norm1 * norm2)) if (norm1 > 0 and norm2 > 0) else 0.0

    return {
        "dimension": len(v1),
        "cosine_similarity": round(cosine, 6),
        "dot_product": round(dot, 6),
        "euclidean_distance": round(euclidean, 6),
        "norm_v1": round(norm1, 6),
        "norm_v2": round(norm2, 6)
    }


def estimate_rag_architecture(
    doc_count: int,
    avg_chunk_tokens: int,
    embedding_dim: int,
    query_rps: float,
    retrieved_k: int = 5,
    precision: str = "float32"
) -> Dict[str, Any]:
    """Calculates vector DB memory footprint, indexing overhead, and token bandwidth."""
    bytes_per_val = 4 if precision.lower() == "float32" else (2 if precision.lower() in ("float16", "bfloat16") else 1)
    
    total_tokens = doc_count * avg_chunk_tokens
    raw_vector_bytes = doc_count * embedding_dim * bytes_per_val
    raw_vector_mb = raw_vector_bytes / (1024 * 1024)
    
    # HNSW graph overhead (~1.2x to 1.5x of raw vectors for M=16, efConstruction=200)
    hnsw_overhead_mb = raw_vector_mb * 1.35
    total_ram_required_mb = raw_vector_mb + hnsw_overhead_mb

    # Retrieval token throughput
    tokens_per_second = query_rps * retrieved_k * avg_chunk_tokens

    return {
        "doc_chunks": doc_count,
        "avg_chunk_tokens": avg_chunk_tokens,
        "embedding_dim": embedding_dim,
        "precision": precision,
        "total_corpus_tokens": total_tokens,
        "raw_vector_storage_mb": round(raw_vector_mb, 2),
        "hnsw_index_memory_mb": round(hnsw_overhead_mb, 2),
        "recommended_vector_ram_mb": round(total_ram_required_mb, 2),
        "query_rps": query_rps,
        "top_k": retrieved_k,
        "inbound_retrieval_tokens_per_sec": round(tokens_per_second, 1),
        "monthly_retrieval_tokens": round(tokens_per_second * 3600 * 24 * 30)
    }


def budget_moe_architecture(
    total_params_b: float,
    num_experts: int,
    active_experts: int,
    precision: str = "fp16"
) -> Dict[str, Any]:
    """Calculates active vs total parameter footprint and memory requirements for MoE models."""
    if active_experts > num_experts:
        raise ValueError(f"Active experts ({active_experts}) cannot exceed total experts ({num_experts})")
    
    bits_per_param = {"fp32": 32, "fp16": 16, "bf16": 16, "int8": 8, "int4": 4}.get(precision.lower(), 16)
    bytes_per_param = bits_per_param / 8.0

    # Total disk/VRAM size for all parameters
    total_memory_gb = (total_params_b * 1e9 * bytes_per_param) / (1024 ** 3)
    
    # Active parameter estimation (shared attention params + active expert MLP params)
    shared_ratio = 0.20
    expert_ratio = 0.80
    
    shared_params_b = total_params_b * shared_ratio
    single_expert_params_b = (total_params_b * expert_ratio) / num_experts
    active_params_b = shared_params_b + (active_experts * single_expert_params_b)
    
    active_compute_gb = (active_params_b * 1e9 * bytes_per_param) / (1024 ** 3)
    compute_efficiency_factor = round(total_params_b / active_params_b, 2)

    return {
        "total_parameters_billion": total_params_b,
        "total_experts": num_experts,
        "active_experts_per_token": active_experts,
        "precision": precision,
        "active_parameters_billion": round(active_params_b, 2),
        "compute_efficiency_ratio": f"{compute_efficiency_factor}x speedup vs dense equivalent",
        "total_vram_required_gb": round(total_memory_gb, 2),
        "active_compute_vram_gb": round(active_compute_gb, 2),
        "recommended_min_gpu_vram_gb": round(total_memory_gb * 1.25, 2)
    }


def evaluate_quantization_and_pruning(
    base_params_b: float,
    current_precision: str = "fp16",
    target_precision: str = "int4",
    prune_sparsity: float = 0.0
) -> Dict[str, Any]:
    """Calculates model compression, memory reduction, and parameter savings."""
    precision_bits = {"fp32": 32, "fp16": 16, "bf16": 16, "int8": 8, "int4": 4}
    
    p_curr = precision_bits.get(current_precision.lower(), 16)
    p_target = precision_bits.get(target_precision.lower(), 4)
    
    base_size_gb = (base_params_b * 1e9 * (p_curr / 8.0)) / (1024 ** 3)
    quantized_size_gb = (base_params_b * 1e9 * (p_target / 8.0)) / (1024 ** 3)
    
    effective_params_b = base_params_b * (1.0 - prune_sparsity)
    pruned_and_quantized_gb = (effective_params_b * 1e9 * (p_target / 8.0)) / (1024 ** 3)
    
    total_savings_pct = (1.0 - (pruned_and_quantized_gb / base_size_gb)) * 100.0

    return {
        "base_parameters_billion": base_params_b,
        "current_precision": current_precision,
        "target_precision": target_precision,
        "pruning_sparsity_pct": round(prune_sparsity * 100, 1),
        "original_size_gb": round(base_size_gb, 2),
        "quantized_only_size_gb": round(quantized_size_gb, 2),
        "final_pruned_quantized_size_gb": round(pruned_and_quantized_gb, 2),
        "memory_reduction_factor": round(base_size_gb / pruned_and_quantized_gb, 2),
        "total_savings_percent": round(total_savings_pct, 1)
    }


def advise_algorithm(
    task: str,
    data_size: str,
    latency_sensitive: bool,
    needs_interpretability: bool
) -> Dict[str, Any]:
    """Recommends optimal algorithmic approaches based on engineering criteria."""
    task_clean = task.lower().strip()
    recommendations = []

    if "regress" in task_clean or "forecast" in task_clean or "predict_continuous" in task_clean:
        if needs_interpretability:
            recommendations.append({"algo": "Linear Regression", "reason": "Exact coefficient interpretability and low computational cost."})
        if not latency_sensitive and data_size in ("medium", "large"):
            recommendations.append({"algo": "Gradient Boosting (GBDT)", "reason": "Highest tabular accuracy and handles non-linearities automatically."})
        if "time" in task_clean or "sequence" in task_clean:
            recommendations.append({"algo": "LSTM / Transformer", "reason": "Captures multi-horizon temporal dependencies and autoregressive state."})

    elif "classif" in task_clean or "categor" in task_clean:
        if needs_interpretability:
            recommendations.append({"algo": "Logistic Regression / Decision Tree", "reason": "Direct probability calibration and transparent decision boundaries."})
        if data_size == "small":
            recommendations.append({"algo": "Random Forest / Naive Bayes", "reason": "Low variance on small samples and resistant to overfitting."})
        elif data_size in ("medium", "large"):
            recommendations.append({"algo": "Gradient Boosting (LightGBM/XGBoost)", "reason": "Dominant tabular benchmark winner with optimal memory cache usage."})

    elif "cluster" in task_clean or "unsupervised" in task_clean:
        recommendations.append({"algo": "K-Means", "reason": "Fast, scalable O(N) spherical partitioning."})
        recommendations.append({"algo": "PCA", "reason": "Dimensionality reduction before clustering to eliminate noisy orthogonal dimensions."})

    elif "search" in task_clean or "retriev" in task_clean or "qa" in task_clean:
        recommendations.append({"algo": "RAG (Dense Vector Embeddings + HNSW Index)", "reason": "Decouples dynamic factual grounding from parametric LLM weights."})

    elif "llm" in task_clean or "generat" in task_clean:
        if latency_sensitive:
            recommendations.append({"algo": "Mixture of Experts (MoE) + INT4 Quantization", "reason": "Sparse sub-network gating achieves high parameter reasoning with edge inference speeds."})
        else:
            recommendations.append({"algo": "Dense Causal Transformer (GPT architecture)", "reason": "Standard autoregressive scaling with maximum context coherence."})
    else:
        recommendations.append({"algo": "Random Forest / Gradient Boosting", "reason": "Default workhorse for structured datasets."})
        recommendations.append({"algo": "Transformer", "reason": "Default for unstructured text, code, or multimodal datasets."})

    return {
        "query_task": task,
        "data_size": data_size,
        "latency_sensitive": latency_sensitive,
        "needs_interpretability": needs_interpretability,
        "recommended_approaches": recommendations
    }


def main():
    parser = argparse.ArgumentParser(description="AI Algorithm Distillery Engine (Video 1 Deconstruction)")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: explain
    p_exp = subparsers.add_parser("explain", help="Explain an AI concept from the 38-algorithm catalog")
    p_exp.add_argument("--algorithm", type=str, required=True, help="Algorithm key (e.g., linear_regression, transformer, moe, rag, diffusion_models)")
    p_exp.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: rag-estimate
    p_rag = subparsers.add_parser("rag-estimate", help="Calculate RAG vector storage, RAM, and token budgets")
    p_rag.add_argument("--doc-count", type=int, required=True, help="Number of document chunks")
    p_rag.add_argument("--chunk-tokens", type=int, required=True, help="Average tokens per chunk")
    p_rag.add_argument("--embedding-dim", type=int, default=1536, help="Embedding dimension (e.g. 1536 for OpenAI, 768 for small)")
    p_rag.add_argument("--query-rps", type=float, default=5.0, help="Expected query requests per second")
    p_rag.add_argument("--top-k", type=int, default=5, help="Number of chunks retrieved per query")
    p_rag.add_argument("--precision", type=str, default="float32", choices=["float32", "float16", "int8"], help="Vector storage precision")
    p_rag.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: moe-budget
    p_moe = subparsers.add_parser("moe-budget", help="Compute Mixture of Experts VRAM and efficiency ratios")
    p_moe.add_argument("--total-params-b", type=float, required=True, help="Total parameters in billions (e.g. 47 for Mixtral 8x7B)")
    p_moe.add_argument("--num-experts", type=int, required=True, help="Total number of experts (e.g. 8)")
    p_moe.add_argument("--active-experts", type=int, required=True, help="Active experts routed per token (e.g. 2)")
    p_moe.add_argument("--precision", type=str, default="fp16", choices=["fp32", "fp16", "bf16", "int8", "int4"], help="Model weight precision")
    p_moe.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: quant-prune
    p_qp = subparsers.add_parser("quant-prune", help="Calculate quantization and pruning VRAM savings")
    p_qp.add_argument("--base-params-b", type=float, required=True, help="Base parameters in billions (e.g. 70)")
    p_qp.add_argument("--current-precision", type=str, default="fp16", choices=["fp32", "fp16", "int8"])
    p_qp.add_argument("--target-precision", type=str, default="int4", choices=["int8", "int4"])
    p_qp.add_argument("--prune-sparsity", type=float, default=0.20, help="Pruning sparsity ratio (0.0 to 0.8)")
    p_qp.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: similarity
    p_sim = subparsers.add_parser("similarity", help="Compute Cosine, Euclidean, and Dot Product similarity")
    p_sim.add_argument("--vector1", type=str, required=True, help="Comma-separated floats for vector 1")
    p_sim.add_argument("--vector2", type=str, required=True, help="Comma-separated floats for vector 2")
    p_sim.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: advisor
    p_adv = subparsers.add_parser("advisor", help="Recommend optimal algorithm for a given engineering task")
    p_adv.add_argument("--task", type=str, required=True, help="Task type (e.g., classification, regression, clustering, rag, llm)")
    p_adv.add_argument("--data-size", type=str, default="medium", choices=["small", "medium", "large"])
    p_adv.add_argument("--latency-sensitive", action="store_true", help="Set flag if sub-50ms latency is mandatory")
    p_adv.add_argument("--needs-interpretability", action="store_true", help="Set flag if explainability/SHAP is required")
    p_adv.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    args = parser.parse_args()

    result = {}
    if args.subcommand == "explain":
        key = args.algorithm.lower().replace("-", "_").replace(" ", "_")
        if key in ALGORITHM_CATALOG:
            result = ALGORITHM_CATALOG[key]
        else:
            matches = [k for k in ALGORITHM_CATALOG if key in k]
            if matches:
                result = ALGORITHM_CATALOG[matches[0]]
            else:
                available = list(ALGORITHM_CATALOG.keys())
                result = {"error": f"Algorithm '{args.algorithm}' not found.", "available_algorithms": available}

    elif args.subcommand == "rag-estimate":
        result = estimate_rag_architecture(
            doc_count=args.doc_count,
            avg_chunk_tokens=args.chunk_tokens,
            embedding_dim=args.embedding_dim,
            query_rps=args.query_rps,
            retrieved_k=args.top_k,
            precision=args.precision
        )

    elif args.subcommand == "moe-budget":
        result = budget_moe_architecture(
            total_params_b=args.total_params_b,
            num_experts=args.num_experts,
            active_experts=args.active_experts,
            precision=args.precision
        )

    elif args.subcommand == "quant-prune":
        result = evaluate_quantization_and_pruning(
            base_params_b=args.base_params_b,
            current_precision=args.current_precision,
            target_precision=args.target_precision,
            prune_sparsity=args.prune_sparsity
        )

    elif args.subcommand == "similarity":
        v1 = [float(x.strip()) for x in args.vector1.split(",") if x.strip()]
        v2 = [float(x.strip()) for x in args.vector2.split(",") if x.strip()]
        result = compute_vector_similarity(v1, v2)

    elif args.subcommand == "advisor":
        result = advise_algorithm(
            task=args.task,
            data_size=args.data_size,
            latency_sensitive=args.latency_sensitive,
            needs_interpretability=args.needs_interpretability
        )

    # Format JSON
    json_str = json.dumps(result, indent=2)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"Success! Output written to: {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
