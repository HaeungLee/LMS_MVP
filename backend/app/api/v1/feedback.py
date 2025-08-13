from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.services.llm_metrics import llm_metrics

router = APIRouter()


@router.get("/feedback/providers/health")
async def feedback_providers_health() -> dict:
    """간단한 피드백 LLM 프로바이더 상태 확인.
    외부 네트워크 호출 없이 설정 기반 상태만 보고합니다.
    """
    data = {
        "enabled": settings.llm_enabled,
        "provider": settings.llm_provider,
        "model": settings.openrouter_model,
        "timeout_ms": settings.llm_timeout_ms,
        "max_retries": settings.llm_max_retries,
        "cache_ttl_seconds": settings.llm_cache_ttl_seconds,
        "max_rpm": settings.llm_max_rpm,
    }
    try:
        data.update(llm_metrics.snapshot())
    except Exception:
        pass
    return data


