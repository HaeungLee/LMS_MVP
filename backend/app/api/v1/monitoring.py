"""
모니터링 API 엔드포인트 - Phase 3
- 시스템 성능 조회
- 메트릭 대시보드
- 알림 관리
- 확장성 상태 확인
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.orm import User
from app.services.performance_monitor import get_performance_monitor, APIMetrics
from app.services.redis_service import get_redis_service
from app.services.celery_app import get_task_manager
from app.services.advanced_llm_optimizer import get_llm_optimizer, LLMProvider
from app.middleware.advanced_rate_limit import advanced_rate_limiter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def monitoring_health_check():
    """모니터링 API 상태 확인"""
    return {
        "status": "healthy",
        "message": "Monitoring API is operational",
        "version": "3.0.0-phase3",
        "features": [
            "real_time_monitoring",
            "performance_metrics",
            "system_health",
            "scalability_tracking"
        ]
    }

@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(get_current_user)
):
    """시스템 전반적인 건강 상태"""
    
    # 관리자만 접근 가능
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        performance_monitor = get_performance_monitor()
        health_status = await performance_monitor.get_system_health()
        
        # Redis 상태 확인
        redis_service = get_redis_service()
        redis_stats = redis_service.get_cache_stats()
        
        # Celery 상태 확인
        task_manager = get_task_manager()
        worker_stats = task_manager.get_worker_stats()
        active_tasks = task_manager.get_active_tasks()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": health_status,
            "components": {
                "redis": {
                    "status": "healthy" if redis_stats.get('connected') else "unhealthy",
                    "stats": redis_stats
                },
                "celery": {
                    "status": "healthy" if worker_stats else "unhealthy",
                    "worker_count": len(worker_stats) if worker_stats else 0,
                    "active_tasks": len(active_tasks) if active_tasks else 0
                },
                "database": {
                    "status": "healthy",  # DB 연결이 되었으므로
                    "connection": "active"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"시스템 건강 상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

@router.get("/metrics/system")
async def get_system_metrics(
    hours: int = Query(1, ge=1, le=24, description="Hours of metrics to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """시스템 메트릭 조회"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        redis_service = get_redis_service()
        
        # 지정된 시간 범위의 메트릭 조회
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        metrics_data = []
        current_time = start_time
        
        # 10분 간격으로 메트릭 조회
        while current_time <= end_time:
            timestamp_key = int(current_time.timestamp())
            
            # 해당 시간대의 메트릭 찾기 (±5분 범위)
            for offset in range(-5, 6):
                key = f"system_metrics:{timestamp_key + offset * 60}"
                data = redis_service.get_cache(key)
                if data:
                    metrics_data.append(data)
                    break
            
            current_time += timedelta(minutes=10)
        
        return {
            "success": True,
            "period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "hours": hours
            },
            "metrics_count": len(metrics_data),
            "metrics": metrics_data
        }
        
    except Exception as e:
        logger.error(f"시스템 메트릭 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

@router.get("/metrics/api")
async def get_api_performance_metrics(
    endpoint: Optional[str] = Query(None, description="Specific endpoint to analyze"),
    hours: int = Query(1, ge=1, le=24, description="Hours of metrics to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """API 성능 메트릭 조회"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        redis_service = get_redis_service()
        
        if endpoint:
            # 특정 엔드포인트 통계
            endpoint_key = f"endpoint_stats:{endpoint}"
            endpoint_stats = redis_service.get_cache(endpoint_key)
            
            if not endpoint_stats:
                return {
                    "success": True,
                    "endpoint": endpoint,
                    "message": "No data found for this endpoint"
                }
            
            # 평균 응답 시간 계산
            avg_response_time = (
                endpoint_stats['total_response_time'] / endpoint_stats['count']
                if endpoint_stats['count'] > 0 else 0
            )
            
            # 에러율 계산
            error_rate = (
                endpoint_stats['error_count'] / endpoint_stats['count']
                if endpoint_stats['count'] > 0 else 0
            )
            
            return {
                "success": True,
                "endpoint": endpoint,
                "statistics": {
                    "total_requests": endpoint_stats['count'],
                    "error_count": endpoint_stats['error_count'],
                    "error_rate": f"{error_rate:.2%}",
                    "avg_response_time": f"{avg_response_time:.3f}s",
                    "last_updated": endpoint_stats['last_updated']
                }
            }
        
        else:
            # 전체 API 성능 개요
            all_endpoints = []
            
            # Redis에서 모든 endpoint_stats 키 찾기
            if redis_service._is_connected():
                pattern = "endpoint_stats:*"
                keys = redis_service.redis_client.keys(pattern)
                
                for key in keys:
                    stats = redis_service.get_cache(key)
                    if stats:
                        endpoint_name = key.replace("endpoint_stats:", "")
                        avg_response_time = (
                            stats['total_response_time'] / stats['count']
                            if stats['count'] > 0 else 0
                        )
                        error_rate = (
                            stats['error_count'] / stats['count']
                            if stats['count'] > 0 else 0
                        )
                        
                        all_endpoints.append({
                            "endpoint": endpoint_name,
                            "total_requests": stats['count'],
                            "error_count": stats['error_count'],
                            "error_rate": f"{error_rate:.2%}",
                            "avg_response_time": f"{avg_response_time:.3f}s",
                            "last_updated": stats['last_updated']
                        })
            
            # 요청 수 기준으로 정렬
            all_endpoints.sort(key=lambda x: x['total_requests'], reverse=True)
            
            return {
                "success": True,
                "total_endpoints": len(all_endpoints),
                "endpoints": all_endpoints
            }
        
    except Exception as e:
        logger.error(f"API 메트릭 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get API metrics: {str(e)}")

@router.get("/metrics/llm")
async def get_llm_performance_metrics(
    provider: Optional[str] = Query(None, description="LLM provider (openrouter, openai, anthropic)"),
    current_user: User = Depends(get_current_user)
):
    """LLM 성능 메트릭 조회"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        llm_optimizer = get_llm_optimizer()
        
        if provider:
            # 특정 프로바이더 통계
            try:
                llm_provider_enum = LLMProvider(provider.lower())
                provider_stats = llm_optimizer.get_provider_stats(llm_provider_enum)
                cache_stats = await llm_optimizer.get_cache_stats(llm_provider_enum)
                
                return {
                    "success": True,
                    "provider": provider,
                    "performance": provider_stats,
                    "cache": cache_stats
                }
                
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        else:
            # 모든 프로바이더 통계
            all_providers = {}
            
            for llm_provider in LLMProvider:
                provider_stats = llm_optimizer.get_provider_stats(llm_provider)
                cache_stats = await llm_optimizer.get_cache_stats(llm_provider)
                
                all_providers[llm_provider.value] = {
                    "performance": provider_stats,
                    "cache": cache_stats
                }
            
            return {
                "success": True,
                "providers": all_providers
            }
        
    except Exception as e:
        logger.error(f"LLM 메트릭 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get LLM metrics: {str(e)}")

@router.get("/scalability/status")
async def get_scalability_status(
    current_user: User = Depends(get_current_user)
):
    """확장성 상태 확인"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # 동시 사용자 추정
        redis_service = get_redis_service()
        redis_stats = redis_service.get_cache_stats()
        
        # 활성 세션 수 (추정)
        active_sessions = 0
        if redis_service._is_connected():
            session_keys = redis_service.redis_client.keys("session:user:*")
            active_sessions = len(session_keys) if session_keys else 0
        
        # Celery 작업 부하
        task_manager = get_task_manager()
        active_tasks = task_manager.get_active_tasks()
        total_active_tasks = sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0
        
        # 시스템 리소스 활용도
        performance_monitor = get_performance_monitor()
        system_health = await performance_monitor.get_system_health()
        
        # 확장성 점수 계산 (0-100)
        scalability_score = 100
        
        # 활성 세션이 20명 이상이면 점수 감소
        if active_sessions >= 20:
            scalability_score -= min(50, (active_sessions - 20) * 2)
        
        # 시스템 리소스가 높으면 점수 감소
        if system_health.get('overall_status') == 'critical':
            scalability_score -= 30
        elif system_health.get('overall_status') == 'warning':
            scalability_score -= 15
        
        # 백그라운드 작업 부하가 높으면 점수 감소
        if total_active_tasks > 10:
            scalability_score -= min(20, (total_active_tasks - 10))
        
        scalability_score = max(0, scalability_score)
        
        # 상태 결정
        if scalability_score >= 80:
            status = "excellent"
        elif scalability_score >= 60:
            status = "good"
        elif scalability_score >= 40:
            status = "moderate"
        else:
            status = "poor"
        
        return {
            "success": True,
            "scalability": {
                "status": status,
                "score": scalability_score,
                "max_concurrent_users": 20,
                "current_active_users": active_sessions,
                "utilization_percentage": (active_sessions / 20) * 100,
                "remaining_capacity": max(0, 20 - active_sessions)
            },
            "resource_usage": {
                "system_health": system_health.get('overall_status'),
                "active_background_tasks": total_active_tasks,
                "redis_status": redis_stats.get('connected', False)
            },
            "recommendations": await self._generate_scalability_recommendations(
                active_sessions, total_active_tasks, system_health
            )
        }
        
    except Exception as e:
        logger.error(f"확장성 상태 확인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get scalability status: {str(e)}")

async def _generate_scalability_recommendations(
    active_sessions: int,
    active_tasks: int,
    system_health: Dict[str, Any]
) -> List[str]:
    """확장성 개선 권장사항 생성"""
    
    recommendations = []
    
    if active_sessions >= 18:
        recommendations.append("동시 사용자 수가 임계치에 근접했습니다. 추가 서버 인스턴스 고려가 필요합니다.")
    
    if active_tasks > 15:
        recommendations.append("백그라운드 작업 부하가 높습니다. Celery 워커 증설을 고려하세요.")
    
    if system_health.get('overall_status') == 'critical':
        recommendations.append("시스템 리소스가 부족합니다. 메모리 또는 CPU 업그레이드가 필요합니다.")
    
    if system_health.get('overall_status') == 'warning':
        recommendations.append("시스템 리소스 사용량을 모니터링하고 최적화를 고려하세요.")
    
    if not recommendations:
        recommendations.append("현재 시스템은 안정적으로 운영되고 있습니다.")
    
    return recommendations

@router.post("/metrics/api/record")
async def record_api_metric(
    request: Request,
    endpoint: str,
    method: str,
    response_time: float,
    status_code: int,
    user_id: Optional[int] = None,
    error_message: Optional[str] = None
):
    """API 메트릭 수동 기록 (내부 API)"""
    
    try:
        # 성능 모니터에 메트릭 기록
        performance_monitor = get_performance_monitor()
        
        api_metrics = APIMetrics(
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            error_message=error_message
        )
        
        await performance_monitor.record_api_metrics(api_metrics)
        
        return {
            "success": True,
            "message": "API metric recorded successfully"
        }
        
    except Exception as e:
        logger.error(f"API 메트릭 기록 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to record API metric: {str(e)}")

@router.get("/alerts/recent")
async def get_recent_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours of alerts to retrieve"),
    level: Optional[str] = Query(None, description="Alert level filter (info, warning, critical)"),
    current_user: User = Depends(get_current_user)
):
    """최근 알림 조회"""
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        redis_service = get_redis_service()
        
        # 지정된 시간 범위의 알림 조회
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        alerts = []
        
        if redis_service._is_connected():
            # 알림 기록 키 패턴으로 검색
            pattern = "alert_record:*"
            keys = redis_service.redis_client.keys(pattern)
            
            for key in keys:
                alert_data = redis_service.get_cache(key)
                if alert_data:
                    alert_timestamp = datetime.fromisoformat(alert_data['timestamp'])
                    
                    # 시간 범위 필터
                    if start_time <= alert_timestamp <= end_time:
                        # 레벨 필터
                        if not level or alert_data.get('level', {}).get('value') == level:
                            alerts.append(alert_data)
        
        # 시간순 정렬 (최신 순)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            "success": True,
            "period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "hours": hours
            },
            "filter": {
                "level": level
            },
            "alerts_count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"최근 알림 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent alerts: {str(e)}")

@router.get("/status/concurrency")
async def get_concurrency_status():
    """동시 접속 상태 확인 (인증 불필요)"""
    
    try:
        redis_service = get_redis_service()
        
        # 활성 세션 수
        active_sessions = 0
        if redis_service._is_connected():
            session_keys = redis_service.redis_client.keys("session:user:*")
            active_sessions = len(session_keys) if session_keys else 0
        
        # 용량 상태
        max_capacity = 20
        usage_percentage = (active_sessions / max_capacity) * 100
        
        status = "available"
        if usage_percentage >= 95:
            status = "full"
        elif usage_percentage >= 80:
            status = "high"
        elif usage_percentage >= 60:
            status = "moderate"
        
        return {
            "success": True,
            "concurrency": {
                "status": status,
                "current_users": active_sessions,
                "max_capacity": max_capacity,
                "usage_percentage": round(usage_percentage, 1),
                "available_slots": max(0, max_capacity - active_sessions)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"동시 접속 상태 확인 실패: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "concurrency": {
                "status": "unknown",
                "current_users": 0,
                "max_capacity": 20,
                "usage_percentage": 0,
                "available_slots": 20
            }
        }
