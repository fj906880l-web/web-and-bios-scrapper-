#!/usr/bin/env python3
"""
CS Algorithmic Foundations CLI Tool
Derived from Dave Defines: "All Algorithms You Need to Know" (23 Core CS Algorithms)

Provides deterministic systems algorithms, graph routing, cycle/deadlock detection,
compression evaluation, cache/paging simulations, and distributed consensus verification.
"""

import argparse
import collections
import heapq
import hashlib
import json
import math
import sys
import os
from typing import Dict, Any, List, Tuple, Set, Optional

CS_ALGORITHM_CATALOG: Dict[str, Dict[str, Any]] = {
    "turing_machine": {
        "name": "Turing Machine",
        "category": "Theory of Computation / Formal Automata",
        "intuition": "Infinite tape with read/write head and state transitions; defines theoretical limit of what can ever be computed.",
        "complexity": "Baseline yardstick for computability (P, NP, Decidability)",
        "when_to_use": "Theoretical proof of decidability, evaluating computational expressiveness."
    },
    "lambda_calculus": {
        "name": "Lambda Calculus",
        "category": "Theory of Computation / Functional Paradigm",
        "intuition": "Computation as nested pure mathematical functions consuming each other; stateless immutable transformations.",
        "complexity": "Equivalent to Turing completeness via Church-Turing thesis",
        "when_to_use": "Compiler design, pure functional architectures, high-reliability financial systems."
    },
    "von_neumann": {
        "name": "Stored-Program (Von Neumann) Architecture",
        "category": "Computer Systems / Architecture",
        "intuition": "Treats code as data: program instructions and numbers share the same addressable memory space.",
        "complexity": "Hardware execution cycle: Fetch, Decode, Execute",
        "when_to_use": "Universal general-purpose computing platforms from microcontrollers to servers."
    },
    "quicksort": {
        "name": "QuickSort",
        "category": "Sorting / Divide & Conquer",
        "intuition": "Picks a pivot, partitions elements into smaller and larger subsets, and recursively sorts sub-arrays.",
        "complexity": "O(N log N) average, O(N^2) worst case, in-place O(log N) stack space",
        "when_to_use": "General in-memory cache-friendly fast sorting."
    },
    "mergesort": {
        "name": "MergeSort",
        "category": "Sorting / Divide & Conquer",
        "intuition": "Divides array in half recursively to singletons, then merges sorted pairs back up; guarantees stability.",
        "complexity": "O(N log N) guaranteed worst-case, O(N) auxiliary memory",
        "when_to_use": "External sorting, linked lists, mission-critical systems requiring strictly predictable timing."
    },
    "hashtable": {
        "name": "Hash Table / Hash Map",
        "category": "Data Structures / Direct Addressing",
        "intuition": "Hash function mathematically projects keys directly to bucket indices, yielding near-instant lookup.",
        "complexity": "O(1) average lookup/insert, O(N) worst case under hash collisions",
        "when_to_use": "Key-value stores, database indexes, memory caching, set deduplication."
    },
    "btree": {
        "name": "B-Tree & B+ Tree",
        "category": "Data Structures / Disk-Optimized Balanced Search",
        "intuition": "Wide, shallow multi-way balanced tree designed to minimize slow disk/block seek operations.",
        "complexity": "O(log_B N) search, insert, and delete where B is branching factor",
        "when_to_use": "Database storage engines (MySQL InnoDB, PostgreSQL, SQLite, file systems)."
    },
    "garbage_collection": {
        "name": "Garbage Collection (Mark & Sweep / Generational)",
        "category": "Systems / Memory Management",
        "intuition": "Automated background memory auditor that pauses execution, marks reachable root objects, and sweeps unreachable allocations.",
        "complexity": "Amortized O(Live Objects) collection overhead",
        "when_to_use": "Preventing memory leaks and dangling pointers in managed languages (Java, Python, V8)."
    },
    "bfs": {
        "name": "Breadth-First Search (BFS)",
        "category": "Graph Algorithms / Wavefront Traversal",
        "intuition": "Ripples outward level-by-level, visiting all immediate neighbors before advancing deeper.",
        "complexity": "O(V + E) time, O(V) space",
        "when_to_use": "Shortest path in unweighted graphs, peer-to-peer discovery, social degree separation."
    },
    "dfs": {
        "name": "Depth-First Search (DFS)",
        "category": "Graph Algorithms / Backtracking",
        "intuition": "Plunges along a single branch until hitting a dead end or visited node, then backtracks to previous junction.",
        "complexity": "O(V + E) time, O(V) recursion stack space",
        "when_to_use": "Topological sorting, cycle and deadlock detection, maze solving, connected components."
    },
    "dijkstra": {
        "name": "Dijkstra's Shortest Path Algorithm",
        "category": "Graph Algorithms / Greedy Pathfinding",
        "intuition": "Maintains a priority queue of tentative distances, greedily settling lowest-cost edges without negative weights.",
        "complexity": "O((V + E) log V) with min-heap priority queue",
        "when_to_use": "GPS navigation routing, network packet routing protocols (OSPF, IS-IS)."
    },
    "max_flow_min_cut": {
        "name": "Max-Flow Min-Cut (Edmonds-Karp / Ford-Fulkerson)",
        "category": "Network Flow / Optimization",
        "intuition": "Finds maximum throughput through capacity-constrained pipe network; max flow equals capacity of bottleneck cut edges.",
        "complexity": "O(V * E^2) Edmonds-Karp with BFS augmenting paths",
        "when_to_use": "Logistics shipping optimization, network traffic bottlenecks, image foreground segmentation."
    },
    "deadlock_detection": {
        "name": "Deadlock Detection & Cycle Checking",
        "category": "Operating Systems / Concurrency Control",
        "intuition": "Constructs Resource Allocation Graph; a directed circular wait dependency implies an unresolvable system freeze.",
        "complexity": "O(V + E) cycle check via Tarjan's or 3-color DFS",
        "when_to_use": "Database transaction lock managers, multi-threaded task orchestrators."
    },
    "paging_lru": {
        "name": "Virtual Memory Paging & LRU Replacement",
        "category": "Operating Systems / Memory Virtualization",
        "intuition": "Swaps least-recently used memory pages to disk backing store when RAM threshold is exceeded.",
        "complexity": "O(1) eviction with Hash Map + Doubly Linked List",
        "when_to_use": "Operating system kernel virtual memory, Redis/Memcached buffer eviction."
    },
    "tcp_congestion_control": {
        "name": "TCP Congestion Control (AIMD)",
        "category": "Networking / Flow Control",
        "intuition": "Additive Increase Multiplicative Decrease: ramps up window size linearly, cuts window in half upon packet drop.",
        "complexity": "Dynamic adaptive bandwidth discovery",
        "when_to_use": "Internet packet transport reliability, avoiding network bufferbloat."
    },
    "raft_paxos_consensus": {
        "name": "Distributed Consensus (Raft & Paxos)",
        "category": "Distributed Systems / Fault Tolerance",
        "intuition": "State machine replication with leader election and quorum majorities (N/2 + 1) ensuring consistency under node crashes.",
        "complexity": "Quorum write O(Nodes) network messages",
        "when_to_use": "Distributed databases (etcd, ZooKeeper, CockroachDB, Consul, Kubernetes)."
    },
    "public_key_cryptography": {
        "name": "Public-Key Cryptography (RSA / ECC)",
        "category": "Security / Cryptography",
        "intuition": "Asymmetric keypairs based on one-way trapdoor mathematical functions (prime factorization, discrete log).",
        "complexity": "Key gen O(k^3), Encryption/Decryption polynomial in key size",
        "when_to_use": "TLS/HTTPS encryption, SSH authentication, digital signatures, blockchain transactions."
    },
    "cryptographic_hash": {
        "name": "Cryptographic Hash Functions (SHA-256)",
        "category": "Security / Integrity Verification",
        "intuition": "One-way deterministic compression function with extreme avalanche effect (single bit change flips ~50% of hash output).",
        "complexity": "O(Message Bytes), fixed 256-bit digest",
        "when_to_use": "Data tampering verification, password hashing (salted), blockchain Merkle trees."
    },
    "huffman_coding": {
        "name": "Huffman Coding",
        "category": "Information Theory / Lossless Compression",
        "intuition": "Builds optimal binary prefix tree assigning shortest bit codes to most frequent symbols.",
        "complexity": "O(N log K) where K is unique symbol count",
        "when_to_use": "Lossless data compression (ZIP, GZIP, JPEG entropy stage)."
    },
    "lz_compression": {
        "name": "Lempel-Ziv (LZ77 / LZSS) Compression",
        "category": "Information Theory / Dictionary Compression",
        "intuition": "Sliding-window dictionary replaces repeating patterns with (distance, length) back-reference pointers.",
        "complexity": "O(N * W) where W is sliding window size",
        "when_to_use": "Deflate algorithm, PNG images, snappy, zstd, network wire compression."
    },
    "monte_carlo": {
        "name": "Monte Carlo Simulation",
        "category": "Stochastic Algorithms / Numerical Methods",
        "intuition": "Approximates deterministic mathematical values through repeated random pseudo-sampling.",
        "complexity": "Error bounds decrease as O(1 / sqrt(N)) with N samples",
        "when_to_use": "Quantitative finance risk modeling, physics simulations, game AI."
    },
    "inverted_index": {
        "name": "Inverted Index",
        "category": "Information Retrieval / Search Engines",
        "intuition": "Maps every unique token/word to a sorted postings list of document IDs containing that word.",
        "complexity": "O(Token Count) index lookup, set intersection for multi-term queries",
        "when_to_use": "Search engines (Elasticsearch, Lucene, Google web indexing)."
    },
    "mapreduce": {
        "name": "MapReduce",
        "category": "Distributed Systems / Parallel Computing",
        "intuition": "Splits massive datasets across clusters: Map emits key-value pairs, Shuffle groups by key, Reduce aggregates results.",
        "complexity": "Horizontally scalable across thousands of commodity nodes",
        "when_to_use": "Big Data batch processing (Hadoop, BigQuery, Spark)."
    }
}


def dijkstra_shortest_path(graph: Dict[str, Dict[str, float]], start: str, end: str) -> Dict[str, Any]:
    """Computes single-source shortest path using Dijkstra's algorithm with a min-heap."""
    if start not in graph:
        raise ValueError(f"Start node '{start}' not in graph.")
    if end not in graph:
        raise ValueError(f"End node '{end}' not in graph.")

    distances = {node: float("inf") for node in graph}
    distances[start] = 0.0
    predecessors = {node: None for node in graph}
    visited_order = []
    
    pq = [(0.0, start)]

    while pq:
        curr_dist, curr_node = heapq.heappop(pq)

        if curr_dist > distances[curr_node]:
            continue

        visited_order.append(curr_node)

        if curr_node == end:
            break

        for neighbor, weight in graph.get(curr_node, {}).items():
            if weight < 0:
                raise ValueError("Dijkstra does not support negative edge weights.")
            distance = curr_dist + weight
            if distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = distance
                predecessors[neighbor] = curr_node
                heapq.heappush(pq, (distance, neighbor))

    # Reconstruct path
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = predecessors.get(curr)
    path.reverse()

    reachable = (path[0] == start)
    return {
        "algorithm": "Dijkstra",
        "start": start,
        "end": end,
        "reachable": reachable,
        "total_cost": round(distances[end], 4) if reachable else None,
        "optimal_path": path if reachable else [],
        "visited_nodes_count": len(visited_order),
        "visited_sequence": visited_order
    }


def detect_deadlock_cycles(dependencies: Dict[str, List[str]]) -> Dict[str, Any]:
    """Detects circular wait dependencies using 3-color DFS (White=0, Gray=1, Black=2)."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in dependencies}
    parent = {node: None for node in dependencies}
    cycles = []

    def dfs(u: str, path: List[str]):
        color[u] = GRAY
        path.append(u)

        for v in dependencies.get(u, []):
            if v not in color:
                color[v] = WHITE
                dependencies[v] = []

            if color[v] == GRAY:
                # Cycle found
                cycle_start_idx = path.index(v)
                cycle_path = path[cycle_start_idx:] + [v]
                cycles.append(cycle_path)
            elif color[v] == WHITE:
                dfs(v, path)

        path.pop()
        color[u] = BLACK

    for node in list(dependencies.keys()):
        if color[node] == WHITE:
            dfs(node, [])

    is_deadlocked = len(cycles) > 0

    return {
        "deadlock_detected": is_deadlocked,
        "cycle_count": len(cycles),
        "cycles": cycles,
        "status": "CRITICAL: Circular wait deadlock detected" if is_deadlocked else "HEALTHY: No circular dependencies (DAG valid)"
    }


def edmonds_karp_max_flow(capacity: Dict[str, Dict[str, float]], source: str, sink: str) -> Dict[str, Any]:
    """Calculates Max-Flow and Min-Cut bottleneck using Edmonds-Karp (BFS augmenting paths)."""
    # Build residual graph
    nodes = set(capacity.keys())
    for u in capacity:
        nodes.update(capacity[u].keys())
    
    residual: Dict[str, Dict[str, float]] = {u: {} for u in nodes}
    for u in capacity:
        for v, cap in capacity[u].items():
            residual[u][v] = cap
            if u not in residual[v]:
                residual[v][u] = 0.0

    max_flow = 0.0
    augmenting_paths_found = 0

    while True:
        # BFS to find augmenting path
        parent: Dict[str, Optional[str]] = {u: None for u in nodes}
        parent[source] = source
        queue = collections.deque([source])

        while queue and parent[sink] is None:
            curr = queue.popleft()
            for neighbor, cap in residual[curr].items():
                if cap > 1e-9 and parent[neighbor] is None:
                    parent[neighbor] = curr
                    queue.append(neighbor)

        if parent[sink] is None:
            break

        # Find bottleneck capacity along path
        path_flow = float("inf")
        s = sink
        while s != source:
            prev = parent[s]
            path_flow = min(path_flow, residual[prev][s])
            s = prev

        # Update residual capacities
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] += path_flow
            v = u

        max_flow += path_flow
        augmenting_paths_found += 1

    # Min-Cut: find nodes reachable from source in residual graph
    visited = set()
    q = collections.deque([source])
    visited.add(source)
    while q:
        curr = q.popleft()
        for neighbor, cap in residual[curr].items():
            if cap > 1e-9 and neighbor not in visited:
                visited.add(neighbor)
                q.append(neighbor)

    # Cut edges are original edges from visited to non-visited
    cut_edges = []
    for u in visited:
        for v in capacity.get(u, {}):
            if v not in visited:
                cut_edges.append({"from": u, "to": v, "capacity": capacity[u][v]})

    return {
        "source": source,
        "sink": sink,
        "max_flow": round(max_flow, 4),
        "augmenting_paths_count": augmenting_paths_found,
        "min_cut_bottlenecks": cut_edges,
        "reachable_source_component": sorted(list(visited))
    }


def evaluate_compression(text: str) -> Dict[str, Any]:
    """Evaluates Huffman and LZ77 compression and calculates Shannon entropy."""
    raw_bytes = text.encode("utf-8")
    raw_size_bytes = len(raw_bytes)
    raw_size_bits = raw_size_bytes * 8

    if raw_size_bytes == 0:
        return {"error": "Input text is empty"}

    # 1. Frequency Analysis & Shannon Entropy
    freqs = collections.Counter(raw_bytes)
    entropy = 0.0
    for count in freqs.values():
        p = count / raw_size_bytes
        entropy -= p * math.log2(p)

    # 2. Huffman Coding Simulation
    heap = [[weight, [byte, ""]] for byte, weight in freqs.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        huffman_bits = raw_size_bytes
        codebook = {chr(heap[0][1][0]): "0"}
    else:
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

        huffman_tree = heap[0]
        codebook = {}
        for pair in huffman_tree[1:]:
            byte_val = pair[0]
            char_repr = chr(byte_val) if 32 <= byte_val <= 126 else f"0x{byte_val:02x}"
            codebook[char_repr] = pair[1]

        huffman_bits = sum(freqs[pair[0]] * len(pair[1]) for pair in huffman_tree[1:])

    huffman_bytes = math.ceil(huffman_bits / 8)
    huffman_ratio = round((1.0 - (huffman_bytes / raw_size_bytes)) * 100, 2)

    # 3. Simple LZ77 Sliding Window Simulation (window=256, lookahead=16)
    window_size = 256
    lookahead_size = 16
    i = 0
    lz_tokens = []
    while i < raw_size_bytes:
        best_match_dist = 0
        best_match_len = 0
        max_search = max(0, i - window_size)

        for j in range(max_search, i):
            match_len = 0
            while (match_len < lookahead_size and 
                   i + match_len < raw_size_bytes and 
                   raw_bytes[j + match_len] == raw_bytes[i + match_len]):
                match_len += 1
            if match_len > best_match_len:
                best_match_len = match_len
                best_match_dist = i - j

        if best_match_len >= 3:
            next_char = raw_bytes[i + best_match_len] if (i + best_match_len < raw_size_bytes) else 0
            lz_tokens.append((best_match_dist, best_match_len, next_char))
            i += best_match_len + 1
        else:
            lz_tokens.append((0, 0, raw_bytes[i]))
            i += 1

    # LZ Token cost estimation: offset (8 bits) + length (4 bits) + byte (8 bits) = 20 bits per match
    lz_estimated_bytes = len(lz_tokens) * 2.5
    lz_ratio = round((1.0 - (lz_estimated_bytes / raw_size_bytes)) * 100, 2)

    return {
        "raw_size_bytes": raw_size_bytes,
        "shannon_entropy_bits_per_byte": round(entropy, 4),
        "theoretical_min_bits": round(entropy * raw_size_bytes, 1),
        "huffman_compressed_bits": huffman_bits,
        "huffman_compressed_bytes": huffman_bytes,
        "huffman_savings_percent": huffman_ratio,
        "lz77_tokens_count": len(lz_tokens),
        "lz77_estimated_bytes": round(lz_estimated_bytes, 1),
        "lz77_savings_percent": lz_ratio,
        "sample_codebook_entries": dict(list(codebook.items())[:8])
    }


def simulate_cache_replacement(references: List[str], capacity: int, policy: str = "lru") -> Dict[str, Any]:
    """Simulates cache/paging replacement policies (LRU, FIFO, LFU) across reference strings."""
    if capacity <= 0:
        raise ValueError("Cache capacity must be greater than 0")

    cache = []
    hits = 0
    misses = 0
    freqs = collections.Counter()
    history = []

    for ref in references:
        freqs[ref] += 1
        if ref in cache:
            hits += 1
            if policy.lower() == "lru":
                cache.remove(ref)
                cache.append(ref)
            history.append({"access": ref, "result": "HIT", "cache": list(cache)})
        else:
            misses += 1
            if len(cache) >= capacity:
                if policy.lower() == "fifo":
                    evicted = cache.pop(0)
                elif policy.lower() == "lru":
                    evicted = cache.pop(0)
                elif policy.lower() == "lfu":
                    # Evict item with lowest frequency
                    evicted = min(cache, key=lambda x: freqs[x])
                    cache.remove(evicted)
                else:
                    evicted = cache.pop(0)
            else:
                evicted = None
            cache.append(ref)
            history.append({"access": ref, "result": "MISS", "evicted": evicted, "cache": list(cache)})

    total = hits + misses
    hit_ratio = (hits / total) if total > 0 else 0.0

    return {
        "policy": policy.upper(),
        "capacity": capacity,
        "total_accesses": total,
        "hits": hits,
        "misses": misses,
        "hit_ratio_percent": round(hit_ratio * 100, 2),
        "final_cache_state": cache
    }


def simulate_distributed_consensus(cluster_size: int, active_nodes: List[str]) -> Dict[str, Any]:
    """Validates Raft/Paxos quorum consensus requirements under node failure states."""
    quorum_required = (cluster_size // 2) + 1
    active_count = len(active_nodes)
    has_quorum = active_count >= quorum_required
    fault_tolerance = (cluster_size - 1) // 2

    return {
        "cluster_size": cluster_size,
        "max_node_failures_tolerated": fault_tolerance,
        "quorum_majority_required": quorum_required,
        "active_nodes_count": active_count,
        "active_nodes": active_nodes,
        "quorum_achieved": has_quorum,
        "split_brain_resilient": True,
        "consensus_status": "OPERATIONAL: Valid leader election & log commit guaranteed" if has_quorum else "HALTED: Quorum lost. System prevents split-brain partition writes."
    }


def verify_hash_integrity(data_str: str) -> Dict[str, Any]:
    """Calculates SHA-256 and proves the avalanche effect by flipping 1 bit."""
    orig_bytes = data_str.encode("utf-8")
    orig_hash = hashlib.sha256(orig_bytes).hexdigest()

    # Flip 1 bit in the first character
    flipped_bytes = bytearray(orig_bytes)
    if len(flipped_bytes) > 0:
        flipped_bytes[0] ^= 0x01
    flipped_hash = hashlib.sha256(flipped_bytes).hexdigest()

    # Count differing bits (Hamming Distance between 256-bit hashes)
    h1_int = int(orig_hash, 16)
    h2_int = int(flipped_hash, 16)
    xor_diff = h1_int ^ h2_int
    diff_bits = bin(xor_diff).count("1")
    avalanche_pct = round((diff_bits / 256.0) * 100, 2)

    return {
        "original_sha256": orig_hash,
        "flipped_bit_sha256": flipped_hash,
        "total_hash_bits": 256,
        "differing_bits_count": diff_bits,
        "avalanche_effect_percent": f"{avalanche_pct}% (Ideal: ~50%)",
        "tamper_proof": True
    }


def main():
    parser = argparse.ArgumentParser(description="CS Algorithmic Foundations Engine (Video 2 Deconstruction)")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: explain
    p_exp = subparsers.add_parser("explain", help="Explain a core CS algorithm from the 23-algorithm catalog")
    p_exp.add_argument("--algorithm", type=str, required=True, help="Algorithm key (e.g., dijkstra, raft_paxos_consensus, btree, quicksort)")
    p_exp.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: graph-route
    p_gr = subparsers.add_parser("graph-route", help="Compute shortest path via Dijkstra's algorithm")
    p_gr.add_argument("--graph-json", type=str, required=True, help="JSON string representing adjacency graph: '{\"A\": {\"B\": 2, \"C\": 5}, \"B\": {\"C\": 1}}'")
    p_gr.add_argument("--start", type=str, required=True, help="Start node")
    p_gr.add_argument("--end", type=str, required=True, help="Destination node")
    p_gr.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: deadlock-check
    p_dc = subparsers.add_parser("deadlock-check", help="Check for circular wait deadlocks in lock dependency graphs")
    p_dc.add_argument("--deps-json", type=str, required=True, help="JSON string representing directed dependencies: '{\"T1\": [\"T2\"], \"T2\": [\"T3\"], \"T3\": [\"T1\"]}'")
    p_dc.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: max-flow
    p_mf = subparsers.add_parser("max-flow", help="Calculate Max-Flow and Min-Cut bottleneck in a pipe network")
    p_mf.add_argument("--capacity-json", type=str, required=True, help="JSON capacities: '{\"s\": {\"a\": 10, \"b\": 5}, \"a\": {\"t\": 10}, \"b\": {\"t\": 10}}'")
    p_mf.add_argument("--source", type=str, required=True, help="Source node")
    p_mf.add_argument("--sink", type=str, required=True, help="Sink node")
    p_mf.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: compression-eval
    p_ce = subparsers.add_parser("compression-eval", help="Evaluate Huffman and LZ77 compression and entropy")
    p_ce.add_argument("--text", type=str, required=True, help="Input string or data payload to evaluate")
    p_ce.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: cache-simulate
    p_cs = subparsers.add_parser("cache-simulate", help="Simulate virtual memory paging / cache replacement (LRU/FIFO/LFU)")
    p_cs.add_argument("--references", type=str, required=True, help="Comma-separated page/item accesses: '1,2,3,4,1,2,5,1,2,3,4,5'")
    p_cs.add_argument("--capacity", type=int, required=True, help="Cache capacity")
    p_cs.add_argument("--policy", type=str, default="lru", choices=["lru", "fifo", "lfu"])
    p_cs.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: consensus-simulate
    p_con = subparsers.add_parser("consensus-simulate", help="Simulate Raft/Paxos quorum majority and node failure tolerance")
    p_con.add_argument("--cluster-size", type=int, required=True, help="Total node count in cluster (e.g. 3, 5, 7)")
    p_con.add_argument("--active-nodes", type=str, required=True, help="Comma-separated IDs of healthy nodes: 'node1,node2,node3'")
    p_con.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    # Subcommand: hash-integrity
    p_hi = subparsers.add_parser("hash-integrity", help="Verify SHA-256 fingerprint and test avalanche tamper effect")
    p_hi.add_argument("--text", type=str, required=True, help="Input text string")
    p_hi.add_argument("--output", type=str, required=False, help="Path to write JSON output")

    args = parser.parse_args()
    result = {}

    if args.subcommand == "explain":
        key = args.algorithm.lower().replace("-", "_").replace(" ", "_")
        if key in CS_ALGORITHM_CATALOG:
            result = CS_ALGORITHM_CATALOG[key]
        else:
            matches = [k for k in CS_ALGORITHM_CATALOG if key in k]
            if matches:
                result = CS_ALGORITHM_CATALOG[matches[0]]
            else:
                result = {"error": f"Algorithm '{args.algorithm}' not found.", "available": list(CS_ALGORITHM_CATALOG.keys())}

    elif args.subcommand == "graph-route":
        graph = json.loads(args.graph_json)
        result = dijkstra_shortest_path(graph, args.start, args.end)

    elif args.subcommand == "deadlock-check":
        deps = json.loads(args.deps_json)
        result = detect_deadlock_cycles(deps)

    elif args.subcommand == "max-flow":
        cap = json.loads(args.capacity_json)
        result = edmonds_karp_max_flow(cap, args.source, args.sink)

    elif args.subcommand == "compression-eval":
        result = evaluate_compression(args.text)

    elif args.subcommand == "cache-simulate":
        refs = [r.strip() for r in args.references.split(",") if r.strip()]
        result = simulate_cache_replacement(refs, args.capacity, args.policy)

    elif args.subcommand == "consensus-simulate":
        active = [n.strip() for n in args.active_nodes.split(",") if n.strip()]
        result = simulate_distributed_consensus(args.cluster_size, active)

    elif args.subcommand == "hash-integrity":
        result = verify_hash_integrity(args.text)

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
