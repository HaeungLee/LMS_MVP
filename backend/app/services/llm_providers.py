from __future__ import annotations

import asyncio
import time
import json
from typing import Optional, Dict, Any

import httpx

from app.core.config import settings
from app.services.llm_rate_limiter import llm_rate_limiter
from app.services.llm_metrics import llm_metrics


class LLMProvider:
    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 160) -> Optional[str]:
        raise NotImplementedError


class OpenRouterProvider(LLMProvider):
    def __init__(self) -> None:
        self._api_key = settings.openrouter_api_key
        self._model = settings.openrouter_model
        self._timeout_sec = max(1, int(settings.llm_timeout_ms) / 1000)
        self._max_attempts = max(1, int(settings.llm_max_retries) + 1)

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 160) -> Optional[str]:
        if not self._api_key:
            return None
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        last_error: Optional[str] = None
        start = time.time()
        for attempt in range(self._max_attempts):
            try:
                # rate limit guard (best-effort)
                if not llm_rate_limiter.allow():
                    # soft-fail: don't call upstream
                    print(json.dumps({
                        "event": "llm_rate_limited",
                        "provider": "openrouter",
                        "model": self._model,
                        "attempt": attempt + 1,
                    }, ensure_ascii=False))
                    return None
                with httpx.Client(timeout=self._timeout_sec) as client:
                    resp = client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content")
                        if content:
                            latency_ms = int((time.time() - start) * 1000)
                            try:
                                llm_metrics.record_call(success=True, latency_ms=latency_ms)
                            except Exception:
                                pass
                            print(json.dumps({
                                "event": "llm_call",
                                "provider": "openrouter",
                                "model": self._model,
                                "success": True,
                                "status_code": 200,
                                "latency_ms": latency_ms,
                            }, ensure_ascii=False))
                            return content.strip()
                        return None
                    last_error = f"HTTP {resp.status_code}"
                    latency_ms = int((time.time() - start) * 1000)
                    try:
                        llm_metrics.record_call(success=False, latency_ms=latency_ms)
                    except Exception:
                        pass
                    print(json.dumps({
                        "event": "llm_call",
                        "provider": "openrouter",
                        "model": self._model,
                        "success": False,
                        "status_code": resp.status_code,
                        "latency_ms": latency_ms,
                    }, ensure_ascii=False))
                    
                    # 429 에러 (Rate Limiting)의 경우 더 긴 대기
                    if resp.status_code == 429:
                        wait_time = llm_rate_limiter.wait_time()
                        if wait_time > 0 and attempt < self._max_attempts - 1:
                            print(json.dumps({
                                "event": "llm_rate_limit_wait",
                                "provider": "openrouter", 
                                "wait_seconds": wait_time,
                                "attempt": attempt + 1
                            }, ensure_ascii=False))
                            await asyncio.sleep(wait_time)
                        continue
                        
            except Exception as e:  # noqa: BLE001
                last_error = str(e)
            if attempt < self._max_attempts - 1:
                # 일반 재시도는 짧은 대기
                await asyncio.sleep(0.5 * (attempt + 1))
        return None


def get_llm_provider() -> Optional[LLMProvider]:
    if not settings.llm_enabled:
        return None
    if settings.llm_provider.lower() == "openrouter":
        return OpenRouterProvider()
    return None


