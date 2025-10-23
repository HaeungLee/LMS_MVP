"""
MVP 학습 통계 API

사용자의 학습 통계 및 달성 정보 제공
- 연속 학습일 (streak)
- 주간/월간 목표 달성률
- 총 학습일 및 학습 시간
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User, QuizSession
from app.models.code_problem import CodeSubmission
from app.models.ai_curriculum import AITeachingSession

logger = logging.getLogger(__name__)
router = APIRouter()


# ============= Response Models =============

class AchievementStats(BaseModel):
    """학습 달성 통계"""
    streak: int  # 연속 학습일
    today_completed: bool  # 오늘 학습 완료 여부
    weekly_progress: int  # 주간 목표 달성률 (0-100)
    total_days_learned: int  # 총 학습일
    total_study_hours: float  # 총 학습 시간 (시간 단위)
    this_week_days: int  # 이번 주 학습일
    this_month_days: int  # 이번 달 학습일
    longest_streak: int  # 최장 연속 학습일


# ============= API Endpoints =============

@router.get("/stats", response_model=AchievementStats)
async def get_achievement_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학습 달성 통계 조회 (AI Teaching Session 기반)
    
    - 연속 학습일 계산 (오늘부터 역산)
    - 주간/월간 학습일 계산
    - 총 학습 시간 합산 (세션 활동 기준)
    """
    
    # MVP 시스템: AITeachingSession (교재) + QuizSession (퀴즈) + CodeSubmission (실습) 통합 추적
    study_dates_set = set()
    
    # 1. AITeachingSession (교재 읽기)
    teaching_dates = db.query(
        func.date(AITeachingSession.last_activity_at).label('study_date')
    ).filter(
        AITeachingSession.user_id == current_user.id,
        AITeachingSession.last_activity_at.isnot(None)
    ).group_by(
        func.date(AITeachingSession.last_activity_at)
    ).all()
    
    for record in teaching_dates:
        study_dates_set.add(record.study_date)
    
    # 2. QuizSession (퀴즈 제출)
    quiz_dates = db.query(
        func.date(QuizSession.completed_at).label('study_date')
    ).filter(
        QuizSession.user_id == current_user.id,
        QuizSession.completed_at.isnot(None)
    ).group_by(
        func.date(QuizSession.completed_at)
    ).all()
    
    for record in quiz_dates:
        study_dates_set.add(record.study_date)
    
    # 3. CodeSubmission (실습 제출)
    code_dates = db.query(
        func.date(CodeSubmission.judged_at).label('study_date')
    ).filter(
        CodeSubmission.user_id == current_user.id,
        CodeSubmission.judged_at.isnot(None)
    ).group_by(
        func.date(CodeSubmission.judged_at)
    ).all()
    
    for record in code_dates:
        study_dates_set.add(record.study_date)
    
    # 학습한 날짜들 (오늘부터 역순 정렬)
    study_dates = sorted(list(study_dates_set), reverse=True)
    
    logger.info(f"[Achievement] user_id={current_user.id}")
    logger.info(f"[Achievement] Teaching dates: {len(teaching_dates)}")
    logger.info(f"[Achievement] Quiz dates: {len(quiz_dates)}")
    logger.info(f"[Achievement] Code dates: {len(code_dates)}")
    logger.info(f"[Achievement] Total unique study dates: {len(study_dates)}")
    logger.info(f"[Achievement] Study dates: {study_dates[:5] if len(study_dates) > 5 else study_dates}")
    
    # 1. 연속 학습일 계산
    streak = calculate_streak(study_dates)
    
    # 2. 오늘 학습 완료 여부
    today = datetime.now().date()
    today_completed = today in study_dates
    
    # 3. 주간 목표 달성률 (주 5일 학습 목표)
    week_start = today - timedelta(days=today.weekday())  # 이번 주 월요일
    this_week_days = sum(1 for d in study_dates if d >= week_start)
    weekly_progress = min(int((this_week_days / 5) * 100), 100)  # 최대 100%
    
    # 4. 총 학습일
    total_days_learned = len(study_dates)
    
    # 5. 총 학습 시간 추정 (MVP: AITeachingSession + QuizSession 시간 합산)
    total_minutes = 0
    
    # Teaching Session 시간
    total_sessions = db.query(AITeachingSession).filter(
        AITeachingSession.user_id == current_user.id,
        AITeachingSession.session_status.in_(['active', 'completed'])
    ).all()
    
    for session in total_sessions:
        if session.started_at and session.last_activity_at:
            duration = (session.last_activity_at - session.started_at).total_seconds() / 60
            duration = max(1, min(duration, 180))  # 1~180분 제한
            total_minutes += duration
    
    # Quiz Session 시간 (time_taken은 초 단위)
    quiz_times = db.query(func.sum(QuizSession.time_taken)).filter(
        QuizSession.user_id == current_user.id,
        QuizSession.time_taken.isnot(None)
    ).scalar()
    
    if quiz_times:
        total_minutes += quiz_times / 60  # 초 → 분
    
    total_study_hours = round(total_minutes / 60, 1)
    
    # 6. 이번 달 학습일
    month_start = today.replace(day=1)
    this_month_days = sum(1 for d in study_dates if d >= month_start)
    
    # 7. 최장 연속 학습일
    longest_streak = calculate_longest_streak(study_dates)
    
    return AchievementStats(
        streak=streak,
        today_completed=today_completed,
        weekly_progress=weekly_progress,
        total_days_learned=total_days_learned,
        total_study_hours=total_study_hours,
        this_week_days=this_week_days,
        this_month_days=this_month_days,
        longest_streak=longest_streak
    )


# ============= Helper Functions =============

def calculate_streak(study_dates: list) -> int:
    """
    연속 학습일 계산 (오늘부터 역산)
    
    예:
    - 오늘, 어제, 그제 학습 → streak = 3
    - 오늘 학습 안 함, 어제 학습 → streak = 1
    - 오늘, 어제 학습 안 함 → streak = 0
    """
    if not study_dates:
        return 0
    
    today = datetime.now().date()
    streak = 0
    
    # 오늘부터 역순으로 확인
    check_date = today
    
    for _ in range(365):  # 최대 365일까지
        if check_date in study_dates:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            # 연속 끊김
            break
    
    return streak


def calculate_longest_streak(study_dates: list) -> int:
    """
    역대 최장 연속 학습일 계산
    """
    if not study_dates:
        return 0
    
    # 날짜 정렬 (오래된 순)
    sorted_dates = sorted(study_dates)
    
    max_streak = 1
    current_streak = 1
    
    for i in range(1, len(sorted_dates)):
        # 이전 날짜와 1일 차이인지 확인
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
    
    return max_streak
