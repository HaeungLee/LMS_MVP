"""
Celery 작업 정의 - Phase 3
- AI 피드백 생성 작업
- 대용량 제출 처리
- 사용자 분석 업데이트
- 알림 발송
"""

import asyncio
from celery import current_task
from celery.exceptions import Retry
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import hashlib
import json

from app.services.celery_app import celery_app
from app.services.redis_service import get_redis_service
from app.services.personalized_feedback_service import get_personalized_feedback_service
from app.services.advanced_recommendation_engine import get_recommendation_engine
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_ai_feedback(
    self,
    user_id: int,
    submission_item_id: int,
    user_answer: str,
    correct_answer: str,
    is_correct: bool,
    topic: str,
    question_context: Optional[Dict[str, Any]] = None
):
    """AI 피드백 생성 작업"""
    
    try:
        # 작업 시작 로깅
        logger.info(f"AI 피드백 생성 시작: user={user_id}, submission={submission_item_id}")
        
        # 진행률 업데이트
        current_task.update_state(
            state='PROGRESS',
            meta={'message': 'AI 피드백 생성 중...', 'progress': 20}
        )
        
        # 데이터베이스 세션 생성
        db = SessionLocal()
        
        try:
            # 개인화 피드백 서비스 초기화
            feedback_service = get_personalized_feedback_service(db)
            
            # 진행률 업데이트
            current_task.update_state(
                state='PROGRESS',
                meta={'message': '사용자 프로필 분석 중...', 'progress': 40}
            )
            
            # 비동기 함수를 동기적으로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 개인화 피드백 생성
                feedback_result = loop.run_until_complete(
                    feedback_service.generate_personalized_feedback(
                        user_id=user_id,
                        submission_item_id=submission_item_id,
                        user_answer=user_answer,
                        correct_answer=correct_answer,
                        is_correct=is_correct,
                        topic=topic,
                        question_context=question_context
                    )
                )
                
                # 진행률 업데이트
                current_task.update_state(
                    state='PROGRESS',
                    meta={'message': '피드백 생성 완료', 'progress': 80}
                )
                
            finally:
                loop.close()
            
            # Redis에 결과 캐싱
            redis_service = get_redis_service()
            cache_key = f"feedback:{submission_item_id}"
            redis_service.set_cache(cache_key, feedback_result, 86400)  # 24시간
            
            # 작업 완료
            result = {
                'success': True,
                'feedback': feedback_result,
                'cached_key': cache_key,
                'generated_at': datetime.utcnow().isoformat(),
                'processing_time_seconds': (datetime.utcnow() - datetime.fromisoformat(
                    current_task.request.eta or datetime.utcnow().isoformat()
                )).total_seconds() if current_task.request.eta else None
            }
            
            logger.info(f"AI 피드백 생성 완료: user={user_id}, submission={submission_item_id}")
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"AI 피드백 생성 실패: {str(e)}")
        
        # 재시도 가능한 오류인지 확인
        if "rate limit" in str(e).lower() or "timeout" in str(e).lower():
            # 재시도
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
        # 치명적 오류 - 재시도 없이 실패 처리
        return {
            'success': False,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def process_bulk_submissions(self, submission_ids: List[int], batch_size: int = 10):
    """대용량 제출 처리 작업"""
    
    try:
        logger.info(f"대량 제출 처리 시작: {len(submission_ids)}개 항목")
        
        db = SessionLocal()
        processed_count = 0
        failed_count = 0
        results = []
        
        try:
            # 배치 단위로 처리
            for i in range(0, len(submission_ids), batch_size):
                batch = submission_ids[i:i + batch_size]
                
                # 진행률 업데이트
                progress = int((i / len(submission_ids)) * 100)
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'message': f'배치 {i//batch_size + 1} 처리 중...',
                        'progress': progress,
                        'processed': processed_count,
                        'failed': failed_count
                    }
                )
                
                # 배치 처리
                for submission_id in batch:
                    try:
                        # 제출 데이터 처리 로직
                        # (실제 구현에서는 제출 데이터를 조회하고 처리)
                        
                        processed_count += 1
                        results.append({
                            'submission_id': submission_id,
                            'status': 'processed',
                            'processed_at': datetime.utcnow().isoformat()
                        })
                        
                    except Exception as e:
                        failed_count += 1
                        results.append({
                            'submission_id': submission_id,
                            'status': 'failed',
                            'error': str(e),
                            'failed_at': datetime.utcnow().isoformat()
                        })
                        logger.error(f"제출 처리 실패 {submission_id}: {str(e)}")
                
                # 배치 간 잠시 대기 (시스템 부하 방지)
                import time
                time.sleep(0.1)
            
            return {
                'success': True,
                'total_submissions': len(submission_ids),
                'processed_count': processed_count,
                'failed_count': failed_count,
                'results': results,
                'completed_at': datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"대량 제출 처리 실패: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def update_user_analytics(self, user_id: int, analytics_type: str = "comprehensive"):
    """사용자 분석 데이터 업데이트"""
    
    try:
        logger.info(f"사용자 분석 업데이트 시작: user={user_id}, type={analytics_type}")
        
        # 진행률 업데이트
        current_task.update_state(
            state='PROGRESS',
            meta={'message': '분석 데이터 수집 중...', 'progress': 25}
        )
        
        db = SessionLocal()
        
        try:
            # 분석 데이터 계산
            analytics_data = {
                'user_id': user_id,
                'analytics_type': analytics_type,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            if analytics_type == "comprehensive":
                # 종합 분석
                current_task.update_state(
                    state='PROGRESS',
                    meta={'message': '학습 패턴 분석 중...', 'progress': 50}
                )
                
                # 학습 패턴 분석 로직
                analytics_data['learning_pattern'] = 'steady_learner'  # 예시
                analytics_data['learning_velocity'] = 1.2
                
                current_task.update_state(
                    state='PROGRESS',
                    meta={'message': '약점 분석 중...', 'progress': 75}
                )
                
                # 약점 분석 로직
                analytics_data['weaknesses_count'] = 3  # 예시
                analytics_data['improvement_areas'] = ['debugging', 'algorithms']
                
            elif analytics_type == "progress_only":
                # 진도만 분석
                analytics_data['completion_rate'] = 67.5  # 예시
                analytics_data['modules_completed'] = 8
            
            # Redis에 분석 결과 캐싱
            redis_service = get_redis_service()
            cache_key = f"analytics:{user_id}:{analytics_type}"
            redis_service.set_cache(cache_key, analytics_data, 1800)  # 30분
            
            return {
                'success': True,
                'analytics_data': analytics_data,
                'cache_key': cache_key
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"사용자 분석 업데이트 실패: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True, max_retries=3)
def generate_personalized_recommendations(self, user_id: int, recommendation_type: str = "next_module"):
    """개인화 추천 생성 작업"""
    
    try:
        logger.info(f"개인화 추천 생성 시작: user={user_id}, type={recommendation_type}")
        
        # 진행률 업데이트
        current_task.update_state(
            state='PROGRESS',
            meta={'message': '사용자 프로필 분석 중...', 'progress': 30}
        )
        
        db = SessionLocal()
        
        try:
            # 추천 엔진 초기화
            recommendation_engine = get_recommendation_engine(db)
            
            # 진행률 업데이트
            current_task.update_state(
                state='PROGRESS',
                meta={'message': '추천 알고리즘 실행 중...', 'progress': 60}
            )
            
            # 비동기 함수를 동기적으로 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                recommendations = loop.run_until_complete(
                    recommendation_engine.get_personalized_recommendations(
                        user_id=user_id,
                        recommendation_type=recommendation_type,
                        limit=5
                    )
                )
            finally:
                loop.close()
            
            # 진행률 업데이트
            current_task.update_state(
                state='PROGRESS',
                meta={'message': '추천 결과 캐싱 중...', 'progress': 90}
            )
            
            # Redis에 추천 결과 캐싱
            redis_service = get_redis_service()
            cache_key = f"recommendations:{user_id}:{recommendation_type}"
            redis_service.set_recommendation_cache(user_id, recommendation_type, recommendations, 1800)
            
            return {
                'success': True,
                'recommendations': recommendations,
                'recommendation_count': len(recommendations),
                'cache_key': cache_key,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"개인화 추천 생성 실패: {str(e)}")
        
        # 재시도 로직
        if "database" in str(e).lower() or "connection" in str(e).lower():
            raise self.retry(exc=e, countdown=30 * (self.request.retries + 1))
        
        return {
            'success': False,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def send_notification(self, user_id: int, notification_type: str, content: Dict[str, Any]):
    """알림 발송 작업"""
    
    try:
        logger.info(f"알림 발송 시작: user={user_id}, type={notification_type}")
        
        # 알림 데이터 준비
        notification_data = {
            'user_id': user_id,
            'type': notification_type,
            'content': content,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        
        # 진행률 업데이트
        current_task.update_state(
            state='PROGRESS',
            meta={'message': '알림 전송 중...', 'progress': 50}
        )
        
        # 실제 알림 발송 로직 (이메일, 푸시 등)
        # 여기서는 Redis에 알림 큐 저장으로 시뮬레이션
        redis_service = get_redis_service()
        notification_key = f"notification:{user_id}:{datetime.utcnow().timestamp()}"
        redis_service.set_cache(notification_key, notification_data, 86400)
        
        notification_data['status'] = 'sent'
        
        return {
            'success': True,
            'notification_data': notification_data
        }
        
    except Exception as e:
        logger.error(f"알림 발송 실패: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def cleanup_expired_cache(self):
    """만료된 캐시 데이터 정리 작업"""
    
    try:
        logger.info("캐시 정리 작업 시작")
        
        redis_service = get_redis_service()
        
        # 진행률 업데이트
        current_task.update_state(
            state='PROGRESS',
            meta={'message': '만료된 캐시 검색 중...', 'progress': 30}
        )
        
        # 캐시 통계 조회
        cache_stats_before = redis_service.get_cache_stats()
        
        # 실제 정리 작업은 Redis의 자동 만료 기능에 의존
        # 여기서는 통계 정보만 수집
        
        current_task.update_state(
            state='PROGRESS',
            meta={'message': '정리 작업 완료', 'progress': 100}
        )
        
        cache_stats_after = redis_service.get_cache_stats()
        
        return {
            'success': True,
            'cache_stats_before': cache_stats_before,
            'cache_stats_after': cache_stats_after,
            'cleaned_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"캐시 정리 실패: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }

# 주기적 작업 스케줄링을 위한 설정
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-expired-cache': {
        'task': 'app.services.celery_tasks.cleanup_expired_cache',
        'schedule': crontab(minute=0, hour='*/6'),  # 6시간마다
    },
}

celery_app.conf.timezone = 'Asia/Seoul'
