"""
이메일 자동화를 위한 Celery 작업들
"""

from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.email_service import get_email_service
from app.models.user import User
from app.models.subscription import Subscription
import logging

logger = logging.getLogger(__name__)


def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@shared_task(name="send_welcome_email")
def send_welcome_email_task(user_id: int, user_email: str, user_name: str):
    """
    환영 이메일 전송 작업
    
    Args:
        user_id: 사용자 ID
        user_email: 사용자 이메일
        user_name: 사용자 이름
    """
    try:
        email_service = get_email_service()
        success = email_service.send_welcome_email(
            to_email=user_email,
            user_name=user_name,
            user_id=user_id
        )
        
        if success:
            logger.info(f"✅ 환영 이메일 전송 성공: user_id={user_id}")
        else:
            logger.error(f"❌ 환영 이메일 전송 실패: user_id={user_id}")
            
        return success
        
    except Exception as e:
        logger.error(f"환영 이메일 작업 실패: user_id={user_id}, error={str(e)}")
        return False


@shared_task(name="send_trial_reminders")
def send_trial_reminders_task():
    """
    무료 체험 리마인더 이메일 전송 (일일 작업)
    
    - 무료 체험 종료 2일 전 사용자에게 알림
    - 아직 프리미엄 구독하지 않은 사용자만
    """
    try:
        db = next(get_db())
        email_service = get_email_service()
        
        # 무료 체험 종료 2일 전 날짜 계산
        target_date = datetime.now() - timedelta(days=5)  # 7일 체험 - 2일 = 5일 전 가입자
        
        # 무료 체험 사용자 조회 (프리미엄 구독 없음)
        users = db.query(User).filter(
            User.created_at >= target_date,
            User.created_at < target_date + timedelta(days=1),
            User.is_active == True,
            ~User.id.in_(
                db.query(Subscription.user_id).filter(
                    Subscription.status == 'active'
                )
            )
        ).all()
        
        success_count = 0
        fail_count = 0
        
        for user in users:
            try:
                # 사용자 학습 통계 조회 (예시)
                stats = {
                    'problems_solved': 0,
                    'study_hours': 0,
                    'accuracy': 0
                }
                
                # TODO: 실제 통계 조회 로직 추가
                
                success = email_service.send_trial_reminder_email(
                    to_email=user.email,
                    user_name=user.full_name or user.email.split('@')[0],
                    days_left=2,
                    stats=stats
                )
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"사용자 {user.id} 리마인더 전송 실패: {str(e)}")
                fail_count += 1
        
        logger.info(f"📧 무료 체험 리마인더 전송 완료: 성공={success_count}, 실패={fail_count}")
        return {'success': success_count, 'failed': fail_count}
        
    except Exception as e:
        logger.error(f"무료 체험 리마인더 작업 실패: {str(e)}")
        return {'success': 0, 'failed': 0}
    finally:
        db.close()


@shared_task(name="send_re_engagement_emails")
def send_re_engagement_emails_task():
    """
    재참여 유도 이메일 전송 (일일 작업)
    
    - 7일 동안 로그인하지 않은 사용자에게 알림
    """
    try:
        db = next(get_db())
        email_service = get_email_service()
        
        # 7일 전 날짜 계산
        inactive_date = datetime.now() - timedelta(days=7)
        
        # 7일 이상 비활성 사용자 조회
        users = db.query(User).filter(
            User.last_login < inactive_date,
            User.is_active == True
        ).all()
        
        success_count = 0
        fail_count = 0
        
        for user in users:
            try:
                # 마지막 로그인 후 경과 일수 계산
                last_login_days = (datetime.now() - user.last_login).days
                
                # 사용자 학습 진행 상황 조회 (예시)
                progress = {
                    'completion_rate': 0,
                    'completed_problems': 0,
                    'total_problems': 0
                }
                
                # TODO: 실제 진행 상황 조회 로직 추가
                
                success = email_service.send_re_engagement_email(
                    to_email=user.email,
                    user_name=user.full_name or user.email.split('@')[0],
                    last_login_days=last_login_days,
                    progress=progress
                )
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"사용자 {user.id} 재참여 이메일 전송 실패: {str(e)}")
                fail_count += 1
        
        logger.info(f"📧 재참여 이메일 전송 완료: 성공={success_count}, 실패={fail_count}")
        return {'success': success_count, 'failed': fail_count}
        
    except Exception as e:
        logger.error(f"재참여 이메일 작업 실패: {str(e)}")
        return {'success': 0, 'failed': 0}
    finally:
        db.close()


@shared_task(name="send_payment_success_email")
def send_payment_success_email_task(
    user_id: int,
    user_email: str,
    user_name: str,
    plan_name: str,
    amount: int,
    next_billing_date: str
):
    """
    결제 성공 확인 이메일 전송 작업
    
    Args:
        user_id: 사용자 ID
        user_email: 사용자 이메일
        user_name: 사용자 이름
        plan_name: 플랜 이름
        amount: 결제 금액
        next_billing_date: 다음 결제일 (ISO format)
    """
    try:
        email_service = get_email_service()
        
        # 날짜 파싱
        next_billing = datetime.fromisoformat(next_billing_date.replace('Z', '+00:00'))
        
        success = email_service.send_payment_success_email(
            to_email=user_email,
            user_name=user_name,
            plan_name=plan_name,
            amount=amount,
            next_billing_date=next_billing
        )
        
        if success:
            logger.info(f"✅ 결제 성공 이메일 전송 성공: user_id={user_id}")
        else:
            logger.error(f"❌ 결제 성공 이메일 전송 실패: user_id={user_id}")
            
        return success
        
    except Exception as e:
        logger.error(f"결제 성공 이메일 작업 실패: user_id={user_id}, error={str(e)}")
        return False
