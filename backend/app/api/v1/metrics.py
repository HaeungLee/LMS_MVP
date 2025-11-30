"""
Prometheus 메트릭 엔드포인트
- 시스템 메트릭 Prometheus 포맷 제공
- 커스텀 비즈니스 메트릭
- Grafana 대시보드 연동 지원
"""

from fastapi import APIRouter, Response
from typing import Dict, Any
from datetime import datetime, timezone
import os
import psutil

from app.middleware.logging import get_metrics_collector

router = APIRouter()


# ============================================
# Prometheus 포맷 헬퍼
# ============================================
def format_prometheus_metric(
    name: str, 
    value: float, 
    metric_type: str = "gauge",
    help_text: str = "",
    labels: Dict[str, str] = None
) -> str:
    """Prometheus 메트릭 포맷 생성"""
    lines = []
    
    # HELP 라인
    if help_text:
        lines.append(f"# HELP {name} {help_text}")
    
    # TYPE 라인
    lines.append(f"# TYPE {name} {metric_type}")
    
    # 값 라인
    if labels:
        label_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
        lines.append(f"{name}{{{label_str}}} {value}")
    else:
        lines.append(f"{name} {value}")
    
    return "\n".join(lines)


# ============================================
# 메트릭 수집 함수
# ============================================
def collect_system_metrics() -> str:
    """시스템 메트릭 수집"""
    metrics = []
    
    # CPU 사용률
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        metrics.append(format_prometheus_metric(
            "lms_system_cpu_usage_percent",
            cpu_percent,
            "gauge",
            "Current CPU usage percentage"
        ))
    except Exception:
        pass
    
    # 메모리 사용률
    try:
        memory = psutil.virtual_memory()
        metrics.append(format_prometheus_metric(
            "lms_system_memory_usage_percent",
            memory.percent,
            "gauge",
            "Current memory usage percentage"
        ))
        metrics.append(format_prometheus_metric(
            "lms_system_memory_available_bytes",
            memory.available,
            "gauge",
            "Available memory in bytes"
        ))
        metrics.append(format_prometheus_metric(
            "lms_system_memory_total_bytes",
            memory.total,
            "gauge",
            "Total memory in bytes"
        ))
    except Exception:
        pass
    
    # 디스크 사용률
    try:
        disk = psutil.disk_usage("/")
        metrics.append(format_prometheus_metric(
            "lms_system_disk_usage_percent",
            disk.percent,
            "gauge",
            "Current disk usage percentage"
        ))
    except Exception:
        pass
    
    # 프로세스 정보
    try:
        process = psutil.Process()
        metrics.append(format_prometheus_metric(
            "lms_process_memory_rss_bytes",
            process.memory_info().rss,
            "gauge",
            "Process resident memory size in bytes"
        ))
        metrics.append(format_prometheus_metric(
            "lms_process_cpu_percent",
            process.cpu_percent(),
            "gauge",
            "Process CPU usage percentage"
        ))
        metrics.append(format_prometheus_metric(
            "lms_process_threads_count",
            process.num_threads(),
            "gauge",
            "Number of process threads"
        ))
        metrics.append(format_prometheus_metric(
            "lms_process_open_files_count",
            len(process.open_files()),
            "gauge",
            "Number of open files"
        ))
    except Exception:
        pass
    
    return "\n\n".join(metrics)


def collect_api_metrics() -> str:
    """API 메트릭 수집"""
    metrics = []
    collector = get_metrics_collector()
    summary = collector.get_summary()
    
    # 총 요청 수
    total_requests = sum(m["total_requests"] for m in summary.values())
    metrics.append(format_prometheus_metric(
        "lms_http_requests_total",
        total_requests,
        "counter",
        "Total HTTP requests"
    ))
    
    # 엔드포인트별 메트릭
    for endpoint_key, data in summary.items():
        method, path = endpoint_key.split(":", 1) if ":" in endpoint_key else ("GET", endpoint_key)
        labels = {"method": method, "path": path}
        
        # 요청 수
        metrics.append(format_prometheus_metric(
            "lms_http_requests_by_endpoint_total",
            data["total_requests"],
            "counter",
            "HTTP requests by endpoint",
            labels
        ))
        
        # 평균 응답 시간
        metrics.append(format_prometheus_metric(
            "lms_http_request_duration_avg_ms",
            data["avg_duration_ms"],
            "gauge",
            "Average request duration in milliseconds",
            labels
        ))
        
        # 최대 응답 시간
        metrics.append(format_prometheus_metric(
            "lms_http_request_duration_max_ms",
            data["max_duration_ms"],
            "gauge",
            "Maximum request duration in milliseconds",
            labels
        ))
        
        # 에러율
        error_rate = float(data["error_rate"].replace("%", ""))
        metrics.append(format_prometheus_metric(
            "lms_http_request_error_rate_percent",
            error_rate,
            "gauge",
            "Request error rate percentage",
            labels
        ))
    
    return "\n\n".join(metrics)


def collect_application_metrics() -> str:
    """애플리케이션 메트릭 수집"""
    metrics = []
    
    # 앱 정보
    metrics.append(format_prometheus_metric(
        "lms_app_info",
        1,
        "gauge",
        "Application information",
        {
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "python_version": os.sys.version.split()[0]
        }
    ))
    
    # 앱 시작 시간 (업타임 계산용)
    metrics.append(format_prometheus_metric(
        "lms_app_start_time_seconds",
        datetime.now(timezone.utc).timestamp(),
        "gauge",
        "Application start time in Unix timestamp"
    ))
    
    return "\n\n".join(metrics)


# ============================================
# API 엔드포인트
# ============================================
@router.get("/prometheus", tags=["monitoring"])
async def prometheus_metrics():
    """
    Prometheus 형식의 메트릭 제공
    
    Prometheus나 Grafana에서 스크래핑하여 사용
    """
    metrics_output = []
    
    # 시스템 메트릭
    system_metrics = collect_system_metrics()
    if system_metrics:
        metrics_output.append(system_metrics)
    
    # API 메트릭
    api_metrics = collect_api_metrics()
    if api_metrics:
        metrics_output.append(api_metrics)
    
    # 애플리케이션 메트릭
    app_metrics = collect_application_metrics()
    if app_metrics:
        metrics_output.append(app_metrics)
    
    content = "\n\n".join(metrics_output) + "\n"
    
    return Response(
        content=content,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )


@router.get("/json", tags=["monitoring"])
async def json_metrics():
    """
    JSON 형식의 메트릭 제공
    
    디버깅 및 대시보드용
    """
    collector = get_metrics_collector()
    
    # 시스템 메트릭
    system = {}
    try:
        system["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        system["memory_percent"] = memory.percent
        system["memory_available_mb"] = memory.available / (1024 * 1024)
        system["memory_total_mb"] = memory.total / (1024 * 1024)
        disk = psutil.disk_usage("/")
        system["disk_percent"] = disk.percent
    except Exception as e:
        system["error"] = str(e)
    
    # 프로세스 메트릭
    process = {}
    try:
        proc = psutil.Process()
        process["memory_rss_mb"] = proc.memory_info().rss / (1024 * 1024)
        process["cpu_percent"] = proc.cpu_percent()
        process["threads"] = proc.num_threads()
    except Exception as e:
        process["error"] = str(e)
    
    return {
        "success": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": system,
        "process": process,
        "api_endpoints": collector.get_summary(),
        "app": {
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
    }


@router.get("/health/detailed", tags=["health"])
async def detailed_health_check():
    """
    상세 헬스체크
    
    각 컴포넌트별 상태 확인
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {}
    }
    
    # 시스템 체크
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        if cpu > 90 or memory.percent > 90:
            health["components"]["system"] = {
                "status": "degraded",
                "cpu_percent": cpu,
                "memory_percent": memory.percent
            }
            health["status"] = "degraded"
        else:
            health["components"]["system"] = {
                "status": "healthy",
                "cpu_percent": cpu,
                "memory_percent": memory.percent
            }
    except Exception as e:
        health["components"]["system"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # 디스크 체크
    try:
        disk = psutil.disk_usage("/")
        if disk.percent > 90:
            health["components"]["disk"] = {
                "status": "degraded",
                "usage_percent": disk.percent
            }
            health["status"] = "degraded"
        else:
            health["components"]["disk"] = {
                "status": "healthy",
                "usage_percent": disk.percent
            }
    except Exception as e:
        health["components"]["disk"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # API 메트릭 체크
    try:
        collector = get_metrics_collector()
        summary = collector.get_summary()
        
        # 에러율이 높은 엔드포인트 확인
        high_error_endpoints = [
            k for k, v in summary.items() 
            if float(v["error_rate"].replace("%", "")) > 10
        ]
        
        if high_error_endpoints:
            health["components"]["api"] = {
                "status": "degraded",
                "high_error_endpoints": high_error_endpoints
            }
            health["status"] = "degraded"
        else:
            health["components"]["api"] = {
                "status": "healthy",
                "monitored_endpoints": len(summary)
            }
    except Exception as e:
        health["components"]["api"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    return health
