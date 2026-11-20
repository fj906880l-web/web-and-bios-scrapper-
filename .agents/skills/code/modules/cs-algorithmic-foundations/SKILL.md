---
name: cs-algorithmic-foundations
description: >-
  Deterministic systems engineering and foundational computer science algorithmic engine derived from the 23 core CS algorithms (Dave Defines). Solves Dijkstra shortest-path routing, Edmonds-Karp network max-flow bottlenecks, deadlock/circular wait detection, Huffman/LZ77 compression evaluations, virtual memory paging/cache simulations (LRU/FIFO/LFU), and distributed consensus quorum checks across all projects.
---

# CS Algorithmic Foundations & Systems Optimizer

## Overview
The `cs-algorithmic-foundations` skill provides a deterministic systems algorithm engine derived from the 23 foundational computer science algorithms that power operating systems, networking, distributed databases, compilers, and storage engines. It provides tools to benchmark compression ratios, verify deadlock-free dependency graphs, calculate optimal graph routing, identify network throughput bottlenecks, simulate cache paging policies, and guarantee distributed consensus quorum safety across all software projects.

## Dependencies
- Standard Python 3 runtime (`python3` or `uv run`).
- Zero external package dependencies (pure standard library).

## Quick Start
Run the CLI tool directly from anywhere on the machine:

```bash
# Check lock graph for deadlocks
python3 ~/.gemini/config/skills/cs-algorithmic-foundations/scripts/cs_algorithmic_foundations.py deadlock-check --deps-json '{"TaskA": ["TaskB"], "TaskB": ["TaskC"], "TaskC": ["TaskA"]}'
```

Or calculate shortest path:
```bash
python3 ~/.gemini/config/skills/cs-algorithmic-foundations/scripts/cs_algorithmic_foundations.py graph-route --graph-json '{"S": {"A": 2, "B": 5}, "A": {"B": 1, "T": 4}, "B": {"T": 2}}' --start "S" --end "T"
```

## Utility Scripts & Subcommands

The CLI script is located at `~/.gemini/config/skills/cs-algorithmic-foundations/scripts/cs_algorithmic_foundations.py`.

### 1. `deadlock-check`
Analyzes directed task or lock acquisition graphs using 3-color DFS to detect circular wait deadlocks.
- `--deps-json`: JSON dictionary mapping resource/task names to lists of dependencies.
- `--output`: Optional output JSON file path.

### 2. `graph-route`
Calculates optimal paths and costs across weighted networks using Dijkstra's algorithm with priority queues.
- `--graph-json`: JSON adjacency list with edge weights (e.g. `{"A": {"B": 3.5, "C": 1.0}}`).
- `--start`: Origin node name.
- `--end`: Target node name.
- `--output`: Output file path.

### 3. `max-flow`
Computes maximum network throughput and isolates the bottleneck Min-Cut edges using the Edmonds-Karp algorithm (Ford-Fulkerson with BFS augmenting paths).
- `--capacity-json`: JSON dictionary of directed edge capacities.
- `--source`: Source node name.
- `--sink`: Sink node name.
- `--output`: Output file path.

### 4. `compression-eval`
Computes Shannon entropy, Huffman prefix tree encoding, and LZ77 sliding-window dictionary compression on text or data payloads.
- `--text`: Input text string or payload to evaluate.
- `--output`: Output file path.

### 5. `cache-simulate`
Simulates virtual memory page replacement and cache eviction policies (LRU, FIFO, LFU) across access reference streams.
- `--references`: Comma-separated list of page/item keys (e.g. `"A, B, C, A, D, B, E"`).
- `--capacity`: Cache capacity integer.
- `--policy`: Eviction policy (`lru`, `fifo`, `lfu`).
- `--output`: Output file path.

### 6. `consensus-simulate`
Simulates Raft/Paxos distributed consensus quorum requirements and fault tolerance under node crash failures.
- `--cluster-size`: Total node count $N$ (e.g. 3, 5, 7).
- `--active-nodes`: Comma-separated list of active, reachable node IDs.
- `--output`: Output file path.

### 7. `hash-integrity`
Computes cryptographic SHA-256 digests and demonstrates the cryptographic avalanche effect by flipping 1 bit and verifying tamper resistance.
- `--text`: Input text string.
- `--output`: Output file path.

### 8. `explain`
Retrieves mathematical mechanics, computational complexity, and systems applications for any of the 23 foundational CS algorithms.
- `--algorithm`: Algorithm key (e.g. `turing_machine`, `lambda_calculus`, `von_neumann`, `quicksort`, `mergesort`, `hashtable`, `btree`, `garbage_collection`, `bfs`, `dfs`, `dijkstra`, `max_flow_min_cut`, `deadlock_detection`, `paging_lru`, `tcp_congestion_control`, `raft_paxos_consensus`, `public_key_cryptography`, `cryptographic_hash`, `huffman_coding`, `lz_compression`, `monte_carlo`, `inverted_index`, `mapreduce`).
- `--output`: Output file path.

## Rate Limiting & Performance
- Pure deterministic standard library mathematics with instant local sub-millisecond execution.
- No network requests, API keys, or cloud dependencies.

## Common Mistakes
1. **Supplying Negative Edge Weights to Dijkstra**: Dijkstra's greedy selection assumes non-negative weights. If negative weights exist, Bellman-Ford must be used instead.
2. **Even-Numbered Consensus Clusters**: Deploying clusters with even nodes (e.g. 4 nodes) requires 3 nodes for a quorum ($\lfloor 4/2 \rfloor + 1 = 3$), which tolerates only 1 failure—identical to a 3-node cluster. Always use odd node counts ($2F + 1$) to maximize fault tolerance.
3. **Overlooking Thrashing in LRU Caching**: If working set size exceeds cache capacity in cyclic sequential access, LRU yields 0% hit ratio. Use `cache-simulate` to benchmark access patterns prior to provisioning cache sizes.
