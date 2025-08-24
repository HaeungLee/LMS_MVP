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
        self._min_interval = 2.0  # 최소 2초 간격

    def allow(self) -> bool:
        now = time.time()
        cutoff = now - self._window_sec
        
        # 이전 요청들 중 시간 윈도우 밖의 것들 제거
        while self._events and self._events[0] < cutoff:
            self._events.popleft()
            
        # 최소 간격 체크 (마지막 요청 후 2초 경과 확인)
        if self._events and (now - self._events[-1]) < self._min_interval:
            return False
            
        # 분당 최대 요청 수 체크
        if len(self._events) < self._max:
            self._events.append(now)
            return True
        return False

    def wait_time(self) -> float:
        """다음 요청까지 대기해야 할 시간 반환"""
        if not self._events:
            return 0.0
            
        now = time.time()
        
        # 최소 간격 기준 대기 시간
        min_wait = max(0, self._min_interval - (now - self._events[-1]))
        
        # Rate limit 기준 대기 시간
        if len(self._events) >= self._max:
            oldest_in_window = self._events[0]
            rate_wait = max(0, self._window_sec - (now - oldest_in_window))
        else:
            rate_wait = 0.0
            
        return max(min_wait, rate_wait)


llm_rate_limiter = SlidingWindowRateLimiter(settings.llm_max_rpm)


