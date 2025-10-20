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

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User, UserProgress

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
    학습 달성 통계 조회
    
    - 연속 학습일 계산 (오늘부터 역산)
    - 주간/월간 학습일 계산
    - 총 학습 시간 합산
    """
    
    # 사용자의 모든 학습 기록 조회 (날짜별 그룹화)
    progress_records = db.query(
        func.date(UserProgress.last_accessed_at).label('study_date'),
        func.count(UserProgress.id).label('activities')
    ).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.last_accessed_at.isnot(None)
    ).group_by(
        func.date(UserProgress.last_accessed_at)
    ).order_by(
        desc('study_date')
    ).all()
    
    # 학습한 날짜들 (오늘부터 역순)
    study_dates = [record.study_date for record in progress_records]
    
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
    
    # 5. 총 학습 시간 (분 → 시간)
    total_minutes = db.query(
        func.sum(UserProgress.time_spent_minutes)
    ).filter(
        UserProgress.user_id == current_user.id
    ).scalar() or 0
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
