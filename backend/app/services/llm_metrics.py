from __future__ import annotations

import bisect
from collections import deque
from typing import Deque, Dict, List


class LLMMetrics:
    def __init__(self, latency_window: int = 512) -> None:
        self.calls_total: int = 0
        self.success_total: int = 0
        self.failure_total: int = 0
        self.cache_hit_total: int = 0
        self._latencies: Deque[int] = deque(maxlen=latency_window)

    def record_call(self, success: bool, latency_ms: int) -> None:
        self.calls_total += 1
        if success:
            self.success_total += 1
        else:
            self.failure_total += 1
        # append latency (non-negative)
        self._latencies.append(max(0, int(latency_ms)))

    def record_cache_hit(self) -> None:
        self.cache_hit_total += 1

    def _percentile(self, data: List[int], percentile: float) -> int:
        if not data:
            return 0
        k = (len(data) - 1) * percentile
        f = int(k)
        c = min(f + 1, len(data) - 1)
        if f == c:
            return data[f]
        d0 = data[f] * (c - k)
        d1 = data[c] * (k - f)
        return int(d0 + d1)

    def snapshot(self) -> Dict[str, int]:
        lat = list(self._latencies)
        lat.sort()
        p50 = self._percentile(lat, 0.50)
        p95 = self._percentile(lat, 0.95)
        last = lat[-1] if lat else 0
        return {
            "calls_total": self.calls_total,
            "success_total": self.success_total,
            "failure_total": self.failure_total,
            "cache_hit_total": self.cache_hit_total,
            "latency_p50_ms": p50,
            "latency_p95_ms": p95,
            "latency_last_ms": last,
        }


llm_metrics = LLMMetrics()


