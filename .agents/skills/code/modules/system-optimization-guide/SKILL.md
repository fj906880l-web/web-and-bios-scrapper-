---
name: system-optimization-guide
description: Playbook for System Efficiency & Performance Engineering covering WAL mode, connection pooling, Parquet caching, indicator profiling, and prioritized roadmap.
---

# System Efficiency Optimization & Performance Playbook

This skill defines the architecture standards, implementation steps, and prioritized roadmap for optimizing Regime Trader 2.0 system efficiency.

---

## 1. Prioritized 4-Phase Implementation Roadmap

| Priority | Strategy | Risk | Effort | Core Objective |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | **SQLite WAL Mode & Telemetry Pruning** | Very Low | Very Low | Fixes actual DB lock failures (`PRAGMA journal_mode=WAL;`) and prunes telemetry logs. |
| **Phase 2** | **Persistent Connection Pooling (`aiohttp`)** | Low | Low | Eliminates 100-250ms TLS handshake latency via shared `ClientSession`. |
| **Phase 3** | **Parquet Caching with TTL Invalidation** | Low-Med | Medium | Local columnar cache for market bars with TTL freshness policy. |
| **Phase 4** | **Indicator Audit → Selective Vectorization** | Medium | Med-High | Target `.apply()` bottlenecks specifically before attempting Polars/NumPy rewrites. |

---

## 2. Phase 1 Implementation Guide: SQLite WAL Mode

```python
import sqlite3

def get_db_connection(db_path: str = "trading_bot.db"):
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn
```

---

## 3. Phase 2 Implementation Guide: Shared HTTP Connection Pool

```python
import aiohttp

class HTTPPoolManager:
    _session: aiohttp.ClientSession = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None or cls._session.closed:
            connector = aiohttp.TCPConnector(limit=100, keepalive_timeout=60.0)
            cls._session = aiohttp.ClientSession(connector=connector)
        return cls._session

    @classmethod
    async def close(cls):
        if cls._session and not cls._session.closed:
            await cls._session.close()
```

---

## 4. Realistic Latency Budget Target

Target **sub-10ms local processing overhead** rather than claiming end-to-end sub-millisecond execution, as broker REST/WebSocket latency dominates total round-trip duration.
