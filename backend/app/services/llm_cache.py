from __future__ import annotations

import hashlib
import time
from typing import Optional, Dict, Tuple

from app.core.config import settings
from app.services.llm_metrics import llm_metrics


class InMemoryTTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._store: Dict[str, Tuple[float, str]] = {}

    def get(self, key: str) -> Optional[str]:
        now = time.time()
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < now:
            self._store.pop(key, None)
            return None
        try:
            llm_metrics.record_cache_hit()
        except Exception:
            pass
        return value

    def set(self, key: str, value: str) -> None:
        self._store[key] = (time.time() + self._ttl, value)


def make_feedback_cache_key(question_id: int, rubric_version: str, normalized_answer: str, user_id: Optional[int] = None) -> str:
    user_segment = f"u{user_id}" if user_id is not None else "anon"
    base = f"feedback:{user_segment}:{question_id}:{rubric_version}:{normalized_answer}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


feedback_cache = InMemoryTTLCache(settings.llm_cache_ttl_seconds)


