from __future__ import annotations

import time
from typing import Deque
from collections import deque

from app.core.config import settings


class SlidingWindowRateLimiter:
    def __init__(self, max_requests_per_minute: int) -> None:
        self._max = max_requests_per_minute
        self._window_sec = 60
        self._events: Deque[float] = deque()

    def allow(self) -> bool:
        now = time.time()
        cutoff = now - self._window_sec
        while self._events and self._events[0] < cutoff:
            self._events.popleft()
        if len(self._events) < self._max:
            self._events.append(now)
            return True
        return False


llm_rate_limiter = SlidingWindowRateLimiter(settings.llm_max_rpm)


