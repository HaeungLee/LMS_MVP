"""
Celery 애플리케이션 - Phase 3
- 비동기 작업 처리
- AI 피드백 생성
- 대용량 데이터 처리
- 백그라운드 분석 작업
"""

from celery import Celery
from celery.signals import worker_ready, worker_shutting_down
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

# Celery 앱 설정
celery_app = Celery(
    "lms_mvp",
    broker=f"redis://{getattr(settings, 'redis_host', 'localhost')}:{getattr(settings, 'redis_port', 6379)}/1",
    backend=f"redis://{getattr(settings, 'redis_host', 'localhost')}:{getattr(settings, 'redis_port', 6379)}/2",
    include=[
        'app.services.celery_tasks'
    ]
)

# Celery 설정
celery_app.conf.update(
    # 작업 설정
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    
    # 작업 라우팅
    task_routes={
        'app.services.celery_tasks.generate_ai_feedback': {'queue': 'ai_tasks'},
        'app.services.celery_tasks.process_bulk_submissions': {'queue': 'bulk_tasks'},
        'app.services.celery_tasks.update_user_analytics': {'queue': 'analytics_tasks'},
        'app.services.celery_tasks.send_notification': {'queue': 'notification_tasks'},
    },
    
    # 워커 설정
    worker_prefetch_multiplier=2,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # 작업 제한
    task_time_limit=300,  # 5분 최대 실행 시간
    task_soft_time_limit=240,  # 4분 소프트 제한
    
    # 재시도 설정
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # 결과 저장 설정
    result_expires=3600,  # 1시간 후 결과 삭제
    result_persistent=True,
    
    # 큐 설정
    task_default_queue='default',
    task_queues={
        'default': {
            'exchange': 'default',
            'exchange_type': 'direct',
            'routing_key': 'default',
        },
        'ai_tasks': {
            'exchange': 'ai_tasks',
            'exchange_type': 'direct',
            'routing_key': 'ai_tasks',
        },
        'bulk_tasks': {
            'exchange': 'bulk_tasks', 
            'exchange_type': 'direct',
            'routing_key': 'bulk_tasks',
        },
        'analytics_tasks': {
            'exchange': 'analytics_tasks',
            'exchange_type': 'direct',
            'routing_key': 'analytics_tasks',
        },
        'notification_tasks': {
            'exchange': 'notification_tasks',
            'exchange_type': 'direct',
            'routing_key': 'notification_tasks',
        }
    },
    
    # 모니터링
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # 보안
    worker_hijack_root_logger=False,
    worker_log_color=False,
)

@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """워커 시작 시 실행"""
    logger.info(f"Celery 워커 준비 완료: {sender}")

@worker_shutting_down.connect
def worker_shutting_down_handler(sender=None, **kwargs):
    """워커 종료 시 실행"""
    logger.info(f"Celery 워커 종료 중: {sender}")

# 헬스체크 작업
@celery_app.task(bind=True)
def health_check(self):
    """Celery 워커 상태 확인"""
    return {
        'status': 'healthy',
        'worker_id': self.request.id,
        'timestamp': datetime.utcnow().isoformat(),
        'hostname': self.request.hostname
    }

# 작업 상태 관리 클래스
class TaskManager:
    """Celery 작업 관리"""
    
    @staticmethod
    def get_task_result(task_id: str) -> Optional[Dict[str, Any]]:
        """작업 결과 조회"""
        try:
            result = celery_app.AsyncResult(task_id)
            return {
                'task_id': task_id,
                'status': result.status,
                'result': result.result,
                'date_done': result.date_done.isoformat() if result.date_done else None,
                'traceback': result.traceback
            }
        except Exception as e:
            logger.error(f"작업 결과 조회 실패 {task_id}: {str(e)}")
            return None
    
    @staticmethod
    def cancel_task(task_id: str) -> bool:
        """작업 취소"""
        try:
            celery_app.control.revoke(task_id, terminate=True)
            return True
        except Exception as e:
            logger.error(f"작업 취소 실패 {task_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_active_tasks() -> Dict[str, Any]:
        """활성 작업 목록 조회"""
        try:
            active_tasks = celery_app.control.inspect().active()
            return active_tasks or {}
        except Exception as e:
            logger.error(f"활성 작업 조회 실패: {str(e)}")
            return {}
    
    @staticmethod
    def get_worker_stats() -> Dict[str, Any]:
        """워커 통계 조회"""
        try:
            stats = celery_app.control.inspect().stats()
            return stats or {}
        except Exception as e:
            logger.error(f"워커 통계 조회 실패: {str(e)}")
            return {}
    
    @staticmethod
    def purge_queue(queue_name: str) -> int:
        """큐 비우기"""
        try:
            result = celery_app.control.purge()
            purged_count = sum(result.values()) if result else 0
            logger.info(f"큐 {queue_name}에서 {purged_count}개 작업 삭제")
            return purged_count
        except Exception as e:
            logger.error(f"큐 비우기 실패 {queue_name}: {str(e)}")
            return 0

# TaskManager 인스턴스
task_manager = TaskManager()

def get_celery_app() -> Celery:
    """Celery 앱 인스턴스 반환"""
    return celery_app

def get_task_manager() -> TaskManager:
    """작업 관리자 인스턴스 반환"""
    return task_manager
