"""
성능 모니터링 시스템 - Phase 3
- 실시간 성능 메트릭
- 시스템 리소스 모니터링
- API 응답 시간 추적
- 알림 및 임계값 관리
"""

import psutil
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from app.services.redis_service import get_redis_service
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """알림 레벨"""
    INFO = "info"
    WARNING = "warning" 
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """시스템 메트릭"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    active_connections: int
    load_average: Optional[List[float]] = None

@dataclass
class APIMetrics:
    """API 메트릭"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: datetime
    user_id: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class DatabaseMetrics:
    """데이터베이스 메트릭"""
    timestamp: datetime
    active_connections: int
    slow_queries: int
    cache_hit_ratio: float
    avg_query_time: float

class PerformanceMonitor:
    """성능 모니터링 시스템"""
    
    def __init__(self):
        self.redis_service = get_redis_service()
        self.monitoring_active = False
        self.metrics_buffer = []
        self.buffer_size = 100
        
        # 임계값 설정
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 85.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'disk_warning': 80.0,
            'disk_critical': 95.0,
            'response_time_warning': 2.0,
            'response_time_critical': 5.0,
            'error_rate_warning': 0.05,  # 5%
            'error_rate_critical': 0.10  # 10%
        }
        
        # 메트릭 수집 간격 (초)
        self.collection_intervals = {
            'system_metrics': 10,
            'api_metrics': 1,  # 실시간
            'database_metrics': 30
        }
    
    async def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        logger.info("성능 모니터링 시작")
        
        # 백그라운드 작업들 시작
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._collect_database_metrics())
        asyncio.create_task(self._process_metrics_buffer())
        asyncio.create_task(self._check_alerts())
    
    async def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        logger.info("성능 모니터링 중지")
    
    async def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        while self.monitoring_active:
            try:
                # CPU 사용률
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # 메모리 정보
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_available_gb = memory.available / (1024**3)
                
                # 디스크 사용률
                disk = psutil.disk_usage('/')
                disk_usage_percent = disk.percent
                
                # 네트워크 I/O
                network_io = psutil.net_io_counters()._asdict()
                
                # 활성 연결 수 (추정)
                active_connections = len(psutil.net_connections())
                
                # 로드 평균 (Linux/Unix만)
                load_average = None
                try:
                    load_average = list(psutil.getloadavg())
                except (AttributeError, OSError):
                    pass
                
                # 메트릭 객체 생성
                metrics = SystemMetrics(
                    timestamp=datetime.utcnow(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    memory_available_gb=memory_available_gb,
                    disk_usage_percent=disk_usage_percent,
                    network_io=network_io,
                    active_connections=active_connections,
                    load_average=load_average
                )
                
                # Redis에 저장
                await self._store_system_metrics(metrics)
                
                # 임계값 확인
                await self._check_system_thresholds(metrics)
                
            except Exception as e:
                logger.error(f"시스템 메트릭 수집 실패: {str(e)}")
            
            await asyncio.sleep(self.collection_intervals['system_metrics'])
    
    async def _collect_database_metrics(self):
        """데이터베이스 메트릭 수집"""
        while self.monitoring_active:
            try:
                db = SessionLocal()
                
                try:
                    # 활성 연결 수 조회
                    active_connections_result = db.execute(
                        "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                    ).scalar()
                    
                    # 느린 쿼리 수 (예시)
                    slow_queries = 0  # 실제 구현 필요
                    
                    # 캐시 히트율 (PostgreSQL 버퍼 캐시)
                    cache_stats = db.execute("""
                        SELECT 
                            sum(heap_blks_hit) as hits,
                            sum(heap_blks_read) as reads
                        FROM pg_statio_user_tables
                    """).fetchone()
                    
                    if cache_stats and (cache_stats[0] + cache_stats[1]) > 0:
                        cache_hit_ratio = cache_stats[0] / (cache_stats[0] + cache_stats[1])
                    else:
                        cache_hit_ratio = 0.0
                    
                    # 평균 쿼리 시간 (예시)
                    avg_query_time = 0.1  # 실제 구현 필요
                    
                    metrics = DatabaseMetrics(
                        timestamp=datetime.utcnow(),
                        active_connections=active_connections_result or 0,
                        slow_queries=slow_queries,
                        cache_hit_ratio=cache_hit_ratio,
                        avg_query_time=avg_query_time
                    )
                    
                    # Redis에 저장
                    await self._store_database_metrics(metrics)
                    
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"데이터베이스 메트릭 수집 실패: {str(e)}")
            
            await asyncio.sleep(self.collection_intervals['database_metrics'])
    
    async def record_api_metrics(self, metrics: APIMetrics):
        """API 메트릭 기록"""
        try:
            # 버퍼에 추가
            self.metrics_buffer.append(metrics)
            
            # 버퍼 크기 제한
            if len(self.metrics_buffer) > self.buffer_size:
                self.metrics_buffer.pop(0)
            
            # 즉시 Redis에 저장 (중요한 메트릭)
            if metrics.status_code >= 500 or metrics.response_time > self.thresholds['response_time_critical']:
                await self._store_api_metrics(metrics)
                
        except Exception as e:
            logger.error(f"API 메트릭 기록 실패: {str(e)}")
    
    async def _process_metrics_buffer(self):
        """메트릭 버퍼 처리"""
        while self.monitoring_active:
            try:
                if self.metrics_buffer:
                    # 버퍼의 메트릭들을 배치로 처리
                    batch = self.metrics_buffer.copy()
                    self.metrics_buffer.clear()
                    
                    for metrics in batch:
                        await self._store_api_metrics(metrics)
                    
                    # API 성능 분석
                    await self._analyze_api_performance(batch)
                    
            except Exception as e:
                logger.error(f"메트릭 버퍼 처리 실패: {str(e)}")
            
            await asyncio.sleep(5)  # 5초마다 처리
    
    async def _store_system_metrics(self, metrics: SystemMetrics):
        """시스템 메트릭 저장"""
        try:
            key = f"system_metrics:{int(metrics.timestamp.timestamp())}"
            self.redis_service.set_cache(key, asdict(metrics), 3600)  # 1시간
            
            # 최근 메트릭 목록 업데이트
            recent_key = "recent_system_metrics"
            recent_metrics = self.redis_service.get_cache(recent_key) or []
            recent_metrics.append(key)
            
            # 최근 100개만 유지
            if len(recent_metrics) > 100:
                # 오래된 메트릭 삭제
                old_key = recent_metrics.pop(0)
                self.redis_service.delete_cache(old_key)
            
            self.redis_service.set_cache(recent_key, recent_metrics, 7200)  # 2시간
            
        except Exception as e:
            logger.error(f"시스템 메트릭 저장 실패: {str(e)}")
    
    async def _store_api_metrics(self, metrics: APIMetrics):
        """API 메트릭 저장"""
        try:
            timestamp_key = int(metrics.timestamp.timestamp())
            
            # 개별 메트릭 저장
            key = f"api_metrics:{timestamp_key}:{id(metrics)}"
            self.redis_service.set_cache(key, asdict(metrics), 1800)  # 30분
            
            # 엔드포인트별 집계
            endpoint_key = f"endpoint_stats:{metrics.endpoint}:{metrics.method}"
            endpoint_stats = self.redis_service.get_cache(endpoint_key) or {
                'count': 0,
                'total_response_time': 0,
                'error_count': 0,
                'last_updated': None
            }
            
            endpoint_stats['count'] += 1
            endpoint_stats['total_response_time'] += metrics.response_time
            if metrics.status_code >= 400:
                endpoint_stats['error_count'] += 1
            endpoint_stats['last_updated'] = metrics.timestamp.isoformat()
            
            self.redis_service.set_cache(endpoint_key, endpoint_stats, 3600)  # 1시간
            
        except Exception as e:
            logger.error(f"API 메트릭 저장 실패: {str(e)}")
    
    async def _store_database_metrics(self, metrics: DatabaseMetrics):
        """데이터베이스 메트릭 저장"""
        try:
            key = f"db_metrics:{int(metrics.timestamp.timestamp())}"
            self.redis_service.set_cache(key, asdict(metrics), 3600)  # 1시간
            
        except Exception as e:
            logger.error(f"데이터베이스 메트릭 저장 실패: {str(e)}")
    
    async def _check_system_thresholds(self, metrics: SystemMetrics):
        """시스템 임계값 확인"""
        alerts = []
        
        # CPU 확인
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append({
                'level': AlertLevel.CRITICAL,
                'metric': 'cpu',
                'value': metrics.cpu_percent,
                'threshold': self.thresholds['cpu_critical'],
                'message': f"CPU 사용률이 임계치를 초과했습니다: {metrics.cpu_percent:.1f}%"
            })
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append({
                'level': AlertLevel.WARNING,
                'metric': 'cpu',
                'value': metrics.cpu_percent,
                'threshold': self.thresholds['cpu_warning'],
                'message': f"CPU 사용률이 경고 수준입니다: {metrics.cpu_percent:.1f}%"
            })
        
        # 메모리 확인
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            alerts.append({
                'level': AlertLevel.CRITICAL,
                'metric': 'memory',
                'value': metrics.memory_percent,
                'threshold': self.thresholds['memory_critical'],
                'message': f"메모리 사용률이 임계치를 초과했습니다: {metrics.memory_percent:.1f}%"
            })
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            alerts.append({
                'level': AlertLevel.WARNING,
                'metric': 'memory',
                'value': metrics.memory_percent,
                'threshold': self.thresholds['memory_warning'],
                'message': f"메모리 사용률이 경고 수준입니다: {metrics.memory_percent:.1f}%"
            })
        
        # 디스크 확인
        if metrics.disk_usage_percent >= self.thresholds['disk_critical']:
            alerts.append({
                'level': AlertLevel.CRITICAL,
                'metric': 'disk',
                'value': metrics.disk_usage_percent,
                'threshold': self.thresholds['disk_critical'],
                'message': f"디스크 사용률이 임계치를 초과했습니다: {metrics.disk_usage_percent:.1f}%"
            })
        elif metrics.disk_usage_percent >= self.thresholds['disk_warning']:
            alerts.append({
                'level': AlertLevel.WARNING,
                'metric': 'disk',
                'value': metrics.disk_usage_percent,
                'threshold': self.thresholds['disk_warning'],
                'message': f"디스크 사용률이 경고 수준입니다: {metrics.disk_usage_percent:.1f}%"
            })
        
        # 알림 발송
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _analyze_api_performance(self, metrics_batch: List[APIMetrics]):
        """API 성능 분석"""
        if not metrics_batch:
            return
        
        # 엔드포인트별 그룹화
        endpoint_groups = {}
        for metrics in metrics_batch:
            key = f"{metrics.endpoint}:{metrics.method}"
            if key not in endpoint_groups:
                endpoint_groups[key] = []
            endpoint_groups[key].append(metrics)
        
        # 각 엔드포인트 분석
        for endpoint_key, endpoint_metrics in endpoint_groups.items():
            total_requests = len(endpoint_metrics)
            error_requests = sum(1 for m in endpoint_metrics if m.status_code >= 400)
            avg_response_time = sum(m.response_time for m in endpoint_metrics) / total_requests
            
            error_rate = error_requests / total_requests
            
            alerts = []
            
            # 응답 시간 확인
            if avg_response_time >= self.thresholds['response_time_critical']:
                alerts.append({
                    'level': AlertLevel.CRITICAL,
                    'metric': 'response_time',
                    'endpoint': endpoint_key,
                    'value': avg_response_time,
                    'message': f"평균 응답 시간이 임계치를 초과했습니다: {avg_response_time:.2f}초"
                })
            elif avg_response_time >= self.thresholds['response_time_warning']:
                alerts.append({
                    'level': AlertLevel.WARNING,
                    'metric': 'response_time',
                    'endpoint': endpoint_key,
                    'value': avg_response_time,
                    'message': f"평균 응답 시간이 경고 수준입니다: {avg_response_time:.2f}초"
                })
            
            # 에러율 확인
            if error_rate >= self.thresholds['error_rate_critical']:
                alerts.append({
                    'level': AlertLevel.CRITICAL,
                    'metric': 'error_rate',
                    'endpoint': endpoint_key,
                    'value': error_rate,
                    'message': f"에러율이 임계치를 초과했습니다: {error_rate:.1%}"
                })
            elif error_rate >= self.thresholds['error_rate_warning']:
                alerts.append({
                    'level': AlertLevel.WARNING,
                    'metric': 'error_rate',
                    'endpoint': endpoint_key,
                    'value': error_rate,
                    'message': f"에러율이 경고 수준입니다: {error_rate:.1%}"
                })
            
            # 알림 발송
            for alert in alerts:
                await self._send_alert(alert)
    
    async def _check_alerts(self):
        """주기적 알림 확인"""
        while self.monitoring_active:
            try:
                # 시스템 전반적인 건강 상태 확인
                health_status = await self.get_system_health()
                
                if health_status['overall_status'] == 'critical':
                    await self._send_alert({
                        'level': AlertLevel.CRITICAL,
                        'metric': 'system_health',
                        'message': "시스템 전반적인 상태가 위험합니다",
                        'details': health_status
                    })
                
            except Exception as e:
                logger.error(f"알림 확인 실패: {str(e)}")
            
            await asyncio.sleep(60)  # 1분마다 확인
    
    async def _send_alert(self, alert: Dict[str, Any]):
        """알림 발송"""
        try:
            # 알림 중복 방지
            alert_key = f"alert:{alert.get('metric')}:{alert.get('endpoint', 'system')}"
            
            if self.redis_service.get_cache(alert_key):
                return  # 최근에 같은 알림이 발송됨
            
            # 알림 기록
            alert['timestamp'] = datetime.utcnow().isoformat()
            alert_record_key = f"alert_record:{int(time.time())}"
            self.redis_service.set_cache(alert_record_key, alert, 86400)  # 24시간
            
            # 중복 방지 플래그 설정 (5분)
            self.redis_service.set_cache(alert_key, True, 300)
            
            logger.warning(f"[{alert['level'].value.upper()}] {alert['message']}")
            
            # 실제 알림 발송 (이메일, 슬랙 등) - 여기서는 로깅만
            
        except Exception as e:
            logger.error(f"알림 발송 실패: {str(e)}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """시스템 건강 상태 조회"""
        try:
            # 최근 시스템 메트릭 조회
            recent_metrics_keys = self.redis_service.get_cache("recent_system_metrics") or []
            
            if not recent_metrics_keys:
                return {'overall_status': 'unknown', 'message': '메트릭 데이터 없음'}
            
            # 최근 5개 메트릭 평균
            recent_data = []
            for key in recent_metrics_keys[-5:]:
                data = self.redis_service.get_cache(key)
                if data:
                    recent_data.append(data)
            
            if not recent_data:
                return {'overall_status': 'unknown', 'message': '최근 메트릭 데이터 없음'}
            
            # 평균 계산
            avg_cpu = sum(d['cpu_percent'] for d in recent_data) / len(recent_data)
            avg_memory = sum(d['memory_percent'] for d in recent_data) / len(recent_data)
            avg_disk = sum(d['disk_usage_percent'] for d in recent_data) / len(recent_data)
            
            # 상태 판정
            critical_count = 0
            warning_count = 0
            
            if avg_cpu >= self.thresholds['cpu_critical']:
                critical_count += 1
            elif avg_cpu >= self.thresholds['cpu_warning']:
                warning_count += 1
            
            if avg_memory >= self.thresholds['memory_critical']:
                critical_count += 1
            elif avg_memory >= self.thresholds['memory_warning']:
                warning_count += 1
            
            if avg_disk >= self.thresholds['disk_critical']:
                critical_count += 1
            elif avg_disk >= self.thresholds['disk_warning']:
                warning_count += 1
            
            # 전체 상태 결정
            if critical_count > 0:
                overall_status = 'critical'
            elif warning_count > 0:
                overall_status = 'warning'
            else:
                overall_status = 'healthy'
            
            return {
                'overall_status': overall_status,
                'metrics': {
                    'avg_cpu_percent': round(avg_cpu, 1),
                    'avg_memory_percent': round(avg_memory, 1),
                    'avg_disk_percent': round(avg_disk, 1)
                },
                'alerts': {
                    'critical_count': critical_count,
                    'warning_count': warning_count
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"시스템 건강 상태 조회 실패: {str(e)}")
            return {'overall_status': 'error', 'error': str(e)}

# 전역 인스턴스
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """성능 모니터 인스턴스 반환"""
    return performance_monitor
