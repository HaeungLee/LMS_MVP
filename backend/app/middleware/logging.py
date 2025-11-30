"""
Advanced Structured Logging Middleware - Phase 2 Enhanced
- 구조화된 JSON 로깅
- 로그 레벨 분리 (INFO, WARNING, ERROR)
- 에러 스택 트레이스 포함
- 성능 메트릭 수집
- 요청/응답 상세 정보
"""

import json
import time
import traceback
import sys
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Set
from starlette.types import ASGIApp, Receive, Scope, Send
import uuid


# ============================================
# JSON 로그 포매터
# ============================================
class JsonFormatter(logging.Formatter):
    """JSON 형식 로그 포매터"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # 추가 필드가 있으면 포함
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False, default=str)


def setup_logger(name: str = "lms_mvp") -> logging.Logger:
    """로거 초기화"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # 콘솔 핸들러 (JSON 형식)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)
        
    return logger


# 전역 로거 인스턴스
app_logger = setup_logger()


# ============================================
# 로그 유틸리티 함수
# ============================================
def log_info(message: str, request_id: Optional[str] = None, **kwargs):
    """INFO 레벨 로그"""
    _log(logging.INFO, message, request_id, **kwargs)


def log_warning(message: str, request_id: Optional[str] = None, **kwargs):
    """WARNING 레벨 로그"""
    _log(logging.WARNING, message, request_id, **kwargs)


def log_error(message: str, request_id: Optional[str] = None, exc_info: bool = False, **kwargs):
    """ERROR 레벨 로그"""
    _log(logging.ERROR, message, request_id, exc_info=exc_info, **kwargs)


def _log(level: int, message: str, request_id: Optional[str] = None, exc_info: bool = False, **kwargs):
    """내부 로그 함수"""
    record = app_logger.makeRecord(
        app_logger.name, level, "", 0, message, (), 
        sys.exc_info() if exc_info else None
    )
    if request_id:
        record.request_id = request_id
    record.extra_data = kwargs
    app_logger.handle(record)


# ============================================
# 구조화된 로깅 미들웨어
# ============================================
class StructuredLoggingMiddleware:
    """
    고도화된 구조화된 로깅 미들웨어 (ASGI 호환)
    
    기능:
    - 모든 요청/응답 자동 로깅
    - 요청 ID 기반 추적
    - 성능 메트릭 (응답 시간)
    - 에러 상세 정보 및 스택 트레이스
    - 로그 레벨 자동 분류 (INFO, WARNING, ERROR)
    """
    
    # 로깅에서 제외할 경로
    EXCLUDE_PATHS: Set[str] = {"/health", "/api/health", "/favicon.ico", "/docs", "/openapi.json", "/redoc"}
    
    # 민감한 헤더 (로그에서 마스킹)
    SENSITIVE_HEADERS: Set[str] = {"authorization", "cookie", "x-api-key", "api-key"}

    def __init__(self, app: ASGIApp, log_slow_threshold_ms: int = 2000):
        self.app = app
        self.log_slow_threshold_ms = log_slow_threshold_ms

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 제외 경로 체크
        path = scope.get("path", "")
        if path in self.EXCLUDE_PATHS:
            await self.app(scope, receive, send)
            return

        started = time.time()
        method = scope.get("method")
        client = scope.get("client")
        ip = client[0] if client else "unknown"
        
        # 헤더에서 정보 추출
        headers = dict(scope.get("headers", []))
        user_agent = headers.get(b"user-agent", b"").decode("utf-8", errors="ignore")[:200]
        content_type = headers.get(b"content-type", b"").decode("utf-8", errors="ignore")
        x_forwarded_for = headers.get(b"x-forwarded-for", b"").decode("utf-8", errors="ignore")
        
        # 프록시 IP 처리
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        
        # 요청 ID 처리
        state = scope.setdefault("state", {})
        request_id: Optional[str] = state.get("request_id") or str(uuid.uuid4())[:8]
        state["request_id"] = request_id
        
        # 쿼리 파라미터
        query_string = scope.get("query_string", b"").decode("utf-8", errors="ignore")
        
        status_code_holder = {"value": None}
        error_holder = {"exception": None, "traceback": None}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code_holder["value"] = message.get("status")
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            error_holder["exception"] = type(e).__name__
            error_holder["traceback"] = traceback.format_exc()
            raise
        finally:
            duration_ms = int((time.time() - started) * 1000)
            status_code = status_code_holder["value"] or 500
            
            # 기본 로그 데이터
            log_data = {
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_string": query_string if query_string else None,
                "status": status_code,
                "duration_ms": duration_ms,
                "ip": ip,
                "user_agent": user_agent[:100] if user_agent else None,
                "content_type": content_type if content_type else None,
            }
            
            # 성능 분류
            if duration_ms < 100:
                log_data["performance"] = "fast"
            elif duration_ms < 500:
                log_data["performance"] = "normal"
            elif duration_ms < self.log_slow_threshold_ms:
                log_data["performance"] = "slow"
            else:
                log_data["performance"] = "very_slow"
            
            # 에러 정보 추가
            if error_holder["exception"]:
                log_data["error"] = {
                    "type": error_holder["exception"],
                    "traceback": error_holder["traceback"]
                }
            
            # 로그 레벨 결정 및 출력
            if error_holder["exception"] or status_code >= 500:
                log_data["level"] = "error"
                log_data["message"] = f"Request failed: {method} {path}"
                log_error(
                    log_data["message"],
                    request_id=request_id,
                    **{k: v for k, v in log_data.items() if k not in ("message", "request_id")}
                )
            elif status_code >= 400:
                log_data["level"] = "warning"
                log_data["message"] = f"Client error: {method} {path}"
                log_warning(
                    log_data["message"],
                    request_id=request_id,
                    **{k: v for k, v in log_data.items() if k not in ("message", "request_id")}
                )
            elif duration_ms >= self.log_slow_threshold_ms:
                log_data["level"] = "warning"
                log_data["message"] = f"Slow request: {method} {path} ({duration_ms}ms)"
                log_warning(
                    log_data["message"],
                    request_id=request_id,
                    **{k: v for k, v in log_data.items() if k not in ("message", "request_id")}
                )
            else:
                log_data["level"] = "info"
                log_data["message"] = f"Request completed: {method} {path}"
                log_info(
                    log_data["message"],
                    request_id=request_id,
                    **{k: v for k, v in log_data.items() if k not in ("message", "request_id")}
                )


# ============================================
# 성능 메트릭 수집기
# ============================================
class PerformanceMetricsCollector:
    """API 성능 메트릭 수집기 (인메모리)"""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def record(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """메트릭 기록"""
        key = f"{method}:{endpoint}"
        
        if key not in self.metrics:
            self.metrics[key] = {
                "count": 0,
                "total_duration_ms": 0,
                "error_count": 0,
                "min_duration_ms": float("inf"),
                "max_duration_ms": 0,
                "last_updated": None,
            }
        
        metric = self.metrics[key]
        metric["count"] += 1
        metric["total_duration_ms"] += duration_ms
        metric["min_duration_ms"] = min(metric["min_duration_ms"], duration_ms)
        metric["max_duration_ms"] = max(metric["max_duration_ms"], duration_ms)
        metric["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        if status_code >= 400:
            metric["error_count"] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """메트릭 요약"""
        summary = {}
        for key, metric in self.metrics.items():
            avg_duration = metric["total_duration_ms"] / metric["count"] if metric["count"] > 0 else 0
            error_rate = (metric["error_count"] / metric["count"] * 100) if metric["count"] > 0 else 0
            
            summary[key] = {
                "total_requests": metric["count"],
                "avg_duration_ms": round(avg_duration, 2),
                "min_duration_ms": round(metric["min_duration_ms"], 2) if metric["min_duration_ms"] != float("inf") else 0,
                "max_duration_ms": round(metric["max_duration_ms"], 2),
                "error_rate": f"{error_rate:.1f}%",
                "last_updated": metric["last_updated"],
            }
        
        return summary
    
    def reset(self):
        """메트릭 초기화"""
        self.metrics = {}


# 전역 메트릭 수집기 인스턴스
_metrics_collector: Optional[PerformanceMetricsCollector] = None


def get_metrics_collector() -> PerformanceMetricsCollector:
    """메트릭 수집기 인스턴스 반환"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = PerformanceMetricsCollector()
    return _metrics_collector
