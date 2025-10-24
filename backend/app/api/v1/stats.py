"""
사용자 통계 API 엔드포인트
- 일일 학습 통계
- 과목별 진도
- 성과 분석
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User, Submission, SubmissionItem, Question, QuizSession
from app.models.ai_curriculum import AITeachingSession
from app.models.code_problem import CodeSubmission

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/user/{user_id}/daily", response_model=Dict[str, Any])
async def get_user_daily_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """사용자 일일 학습 통계"""
    
    try:
        # 오늘 날짜 기준
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # 오늘 제출된 답안들
        today_submissions = db.query(SubmissionItem).join(Submission).filter(
            Submission.user_id == user_id,
            Submission.submitted_at >= today_start,
            Submission.submitted_at <= today_end
        ).all()
        
        # 통계 계산
        total_questions = len(today_submissions)
        correct_answers = sum(1 for item in today_submissions if item.is_correct)
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # 학습 시간 계산 (세션 기반 추정)
        sessions = db.query(Submission).filter(
            Submission.user_id == user_id,
            Submission.submitted_at >= today_start,
            Submission.submitted_at <= today_end
        ).order_by(Submission.submitted_at).all()
        
        study_minutes = 0
        if sessions:
            # 세션 간격 기반으로 학습 시간 추정
            for i, session in enumerate(sessions):
                if i == 0:
                    study_minutes += 5  # 첫 세션 기본 5분
                else:
                    time_diff = (session.submitted_at - sessions[i-1].submitted_at).total_seconds() / 60
                    if time_diff <= 30:  # 30분 이내면 연속 학습으로 간주
                        study_minutes += min(time_diff, 15)  # 최대 15분까지
                    else:
                        study_minutes += 5  # 새 세션으로 간주
        
        # 현재 레벨 결정 (정답률 기반)
        if accuracy >= 90:
            current_level = "고급"
        elif accuracy >= 70:
            current_level = "중급"
        elif accuracy >= 50:
            current_level = "초급"
        else:
            current_level = "입문"
        
        # 학습 시간 포맷
        if study_minutes >= 60:
            study_time = f"{int(study_minutes // 60)}시간 {int(study_minutes % 60)}분"
        else:
            study_time = f"{int(study_minutes)}분"
        
        return {
            "success": True,
            "todayStudyTime": study_time,
            "completedQuestions": total_questions,
            "currentLevel": current_level,
            "todayAccuracy": round(accuracy, 1),
            "correctAnswers": correct_answers,
            "date": today.isoformat()
        }
        
    except Exception as e:
        logger.error(f"사용자 일일 통계 조회 실패 {user_id}: {str(e)}")
        # 폴백 데이터
        return {
            "success": False,
            "todayStudyTime": "30분",
            "completedQuestions": 15,
            "currentLevel": "중급",
            "todayAccuracy": 75.0,
            "correctAnswers": 11,
            "error": "실시간 데이터 로딩 실패"
        }

@router.get("/user/{user_id}/weekly", response_model=Dict[str, Any])
async def get_user_weekly_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """사용자 주간 학습 통계"""
    
    try:
        # 지난 7일간 데이터
        week_start = datetime.utcnow() - timedelta(days=7)
        
        # 일별 제출 통계
        daily_stats = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_start = datetime.combine(day.date(), datetime.min.time())
            day_end = datetime.combine(day.date(), datetime.max.time())
            
            day_submissions = db.query(SubmissionItem).join(Submission).filter(
                Submission.user_id == user_id,
                Submission.submitted_at >= day_start,
                Submission.submitted_at <= day_end
            ).all()
            
            total = len(day_submissions)
            correct = sum(1 for item in day_submissions if item.is_correct)
            accuracy = (correct / total * 100) if total > 0 else 0
            
            daily_stats.append({
                "date": day.date().isoformat(),
                "questions": total,
                "accuracy": round(accuracy, 1),
                "correct": correct
            })
        
        return {
            "success": True,
            "weeklyStats": daily_stats,
            "week_start": week_start.date().isoformat()
        }
        
    except Exception as e:
        logger.error(f"주간 통계 조회 실패 {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"주간 통계 조회 실패: {str(e)}")

@router.get("/user/{user_id}/progress", response_model=Dict[str, Any])
async def get_user_progress(
    user_id: int,
    subject: Optional[str] = Query(None, description="과목"),
    db: Session = Depends(get_db)
):
    """사용자 학습 진도"""
    
    try:
        # 전체 또는 과목별 제출 데이터
        query = db.query(SubmissionItem).join(Submission).join(Question).filter(
            Submission.user_id == user_id
        )
        
        if subject:
            query = query.filter(Question.subject == subject)
        
        submissions = query.all()
        
        if not submissions:
            return {
                "success": True,
                "progress": {
                    "totalQuestions": 0,
                    "completedQuestions": 0,
                    "correctAnswers": 0,
                    "accuracy": 0,
                    "progressPercentage": 0
                }
            }
        
        # 진도 계산
        total_questions = len(submissions)
        correct_answers = sum(1 for item in submissions if item.is_correct)
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # 전체 문제 수 (해당 과목의)
        if subject:
            total_available = db.query(Question).filter(Question.subject == subject).count()
        else:
            total_available = db.query(Question).count()
        
        progress_percentage = (total_questions / total_available * 100) if total_available > 0 else 0
        
        return {
            "success": True,
            "progress": {
                "totalAvailable": total_available,
                "completedQuestions": total_questions,
                "correctAnswers": correct_answers,
                "accuracy": round(accuracy, 1),
                "progressPercentage": round(progress_percentage, 1),
                "subject": subject or "전체"
            }
        }
        
    except Exception as e:
        logger.error(f"학습 진도 조회 실패 {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"학습 진도 조회 실패: {str(e)}")

@router.get("/subjects", response_model=Dict[str, Any])
async def get_available_subjects(db: Session = Depends(get_db)):
    """사용 가능한 과목 목록"""
    
    try:
        subjects = db.query(Question.subject, func.count(Question.id).label('count')).group_by(Question.subject).all()
        
        subject_list = []
        for subject, count in subjects:
            subject_list.append({
                "id": subject,
                "name": subject,
                "questionCount": count
            })
        
        return {
            "success": True,
            "subjects": subject_list
        }
        
    except Exception as e:
        logger.error(f"과목 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"과목 목록 조회 실패: {str(e)}")


@router.get("/learning", response_model=Dict[str, Any])
async def get_learning_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    통합 학습 통계 (일일/주간/월간)
    
    프론트엔드 StatsCard 컴포넌트용
    MVP 시스템: AITeachingSession + QuizSession + CodeSubmission 기반
    """
    
    try:
        user_id = current_user.id
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # === 오늘 통계 (MVP 테이블 기반) ===
        
        # 1. 오늘 퀴즈 제출
        today_quiz = db.query(QuizSession).filter(
            QuizSession.user_id == user_id,
            QuizSession.completed_at >= today_start,
            QuizSession.completed_at <= today_end
        ).all()
        
        # 2. 오늘 코드 제출
        today_code = db.query(CodeSubmission).filter(
            CodeSubmission.user_id == user_id,
            CodeSubmission.judged_at >= today_start,
            CodeSubmission.judged_at <= today_end
        ).all()
        
        # 문제 수와 정확도 계산
        daily_problems = len(today_quiz) + len(today_code)
        
        # 퀴즈: total_score 기반 정확도 (각 퀴즈의 총점/문항수)
        quiz_correct = 0
        for q in today_quiz:
            if q.total_score is not None and q.total_questions and q.total_questions > 0:
                quiz_correct += 1 if (q.total_score / q.total_questions) >= 0.6 else 0  # 60% 이상이면 정답
        
        # 코드: accepted 상태만 정답
        code_correct = sum(1 for c in today_code if c.status == 'accepted')
        
        daily_correct = quiz_correct + code_correct
        daily_accuracy = round((daily_correct / daily_problems * 100), 1) if daily_problems > 0 else 0
        
        # 3. 오늘 학습 시간 (Teaching Session 기반)
        daily_teaching = db.query(AITeachingSession).filter(
            AITeachingSession.user_id == user_id,
            AITeachingSession.last_activity_at >= today_start,
            AITeachingSession.last_activity_at <= today_end
        ).all()
        
        daily_minutes = 0
        for session in daily_teaching:
            if session.started_at and session.last_activity_at:
                duration = (session.last_activity_at - session.started_at).total_seconds() / 60
                daily_minutes += max(1, min(duration, 180))  # 1~180분 제한
        
        # 퀴즈 시간 추가 (초 단위)
        quiz_times = sum(q.time_taken or 0 for q in today_quiz)
        daily_minutes += quiz_times / 60
        
        # === 주간 통계 (이번 주 월요일부터) ===
        week_start = today - timedelta(days=today.weekday())  # 이번 주 월요일
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        
        # 1. 주간 퀴즈 제출
        weekly_quiz = db.query(QuizSession).filter(
            QuizSession.user_id == user_id,
            QuizSession.completed_at >= week_start_dt
        ).all()
        
        # 2. 주간 코드 제출
        weekly_code = db.query(CodeSubmission).filter(
            CodeSubmission.user_id == user_id,
            CodeSubmission.judged_at >= week_start_dt
        ).all()
        
        weekly_problems = len(weekly_quiz) + len(weekly_code)
        
        # 퀴즈 정확도
        weekly_quiz_correct = 0
        for q in weekly_quiz:
            if q.total_score is not None and q.total_questions and q.total_questions > 0:
                weekly_quiz_correct += 1 if (q.total_score / q.total_questions) >= 0.6 else 0
        
        weekly_code_correct = sum(1 for c in weekly_code if c.status == 'accepted')
        weekly_correct = weekly_quiz_correct + weekly_code_correct
        weekly_accuracy = round((weekly_correct / weekly_problems * 100), 1) if weekly_problems > 0 else 0
        
        # 3. 주간 학습 시간
        weekly_teaching = db.query(AITeachingSession).filter(
            AITeachingSession.user_id == user_id,
            AITeachingSession.last_activity_at >= week_start_dt
        ).all()
        
        weekly_minutes = 0
        for session in weekly_teaching:
            if session.started_at and session.last_activity_at:
                duration = (session.last_activity_at - session.started_at).total_seconds() / 60
                weekly_minutes += max(1, min(duration, 180))
        
        quiz_times = sum(q.time_taken or 0 for q in weekly_quiz)
        weekly_minutes += quiz_times / 60
        
        if weekly_minutes <= 30:
                        pass  # 이미 추가됨
        
        weekly_hours = round(weekly_minutes / 60, 1)
        
        # 4. 주간 연속 학습일 (이번 주 내에서만 계산)
        weekly_dates = set()
        
        for session in weekly_teaching:
            if session.last_activity_at:
                weekly_dates.add(session.last_activity_at.date())
        
        for quiz in weekly_quiz:
            if quiz.completed_at:
                weekly_dates.add(quiz.completed_at.date())
        
        for code in weekly_code:
            if code.judged_at:
                weekly_dates.add(code.judged_at.date())
        
        streak_days = len(weekly_dates)  # 이번 주에 학습한 날 수
        
        # === 월간 통계 (이번 달 1일부터) ===
        month_start = today.replace(day=1)
        month_start_dt = datetime.combine(month_start, datetime.min.time())
        
        # 1. 월간 퀴즈 제출
        monthly_quiz = db.query(QuizSession).filter(
            QuizSession.user_id == user_id,
            QuizSession.completed_at >= month_start_dt
        ).all()
        
        # 2. 월간 코드 제출
        monthly_code = db.query(CodeSubmission).filter(
            CodeSubmission.user_id == user_id,
            CodeSubmission.judged_at >= month_start_dt
        ).all()
        
        monthly_problems = len(monthly_quiz) + len(monthly_code)
        
        # 퀴즈 정확도
        monthly_quiz_correct = 0
        for q in monthly_quiz:
            if q.total_score is not None and q.total_questions and q.total_questions > 0:
                monthly_quiz_correct += 1 if (q.total_score / q.total_questions) >= 0.6 else 0
        
        monthly_code_correct = sum(1 for c in monthly_code if c.status == 'accepted')
        monthly_correct = monthly_quiz_correct + monthly_code_correct
        monthly_accuracy = round((monthly_correct / monthly_problems * 100), 1) if monthly_problems > 0 else 0
        
        # 3. 월간 학습 시간
        monthly_teaching = db.query(AITeachingSession).filter(
            AITeachingSession.user_id == user_id,
            AITeachingSession.last_activity_at >= month_start_dt
        ).all()
        
        monthly_minutes = 0
        for session in monthly_teaching:
            if session.started_at and session.last_activity_at:
                duration = (session.last_activity_at - session.started_at).total_seconds() / 60
                monthly_minutes += max(1, min(duration, 180))
        
        quiz_times = sum(q.time_taken or 0 for q in monthly_quiz)
        monthly_minutes += quiz_times / 60
        
        monthly_hours = round(monthly_minutes / 60, 1)
        
        # 4. 월간 학습일
        monthly_dates = set()
        
        for session in monthly_teaching:
            if session.last_activity_at:
                monthly_dates.add(session.last_activity_at.date())
        
        for quiz in monthly_quiz:
            if quiz.completed_at:
                monthly_dates.add(quiz.completed_at.date())
        
        for code in monthly_code:
            if code.judged_at:
                monthly_dates.add(code.judged_at.date())
        
        completed_days = len(monthly_dates)
        
        # === 개선도 계산 (이번 주 vs 지난 주) ===
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start
        last_week_start_dt = datetime.combine(last_week_start, datetime.min.time())
        last_week_end_dt = datetime.combine(last_week_end, datetime.min.time())
        
        # 지난주 퀴즈/코드
        last_week_quiz = db.query(QuizSession).filter(
            QuizSession.user_id == user_id,
            QuizSession.completed_at >= last_week_start_dt,
            QuizSession.completed_at < last_week_end_dt
        ).all()
        
        last_week_code = db.query(CodeSubmission).filter(
            CodeSubmission.user_id == user_id,
            CodeSubmission.judged_at >= last_week_start_dt,
            CodeSubmission.judged_at < last_week_end_dt
        ).all()
        
        last_week_problems = len(last_week_quiz) + len(last_week_code)
        
        # 퀴즈 정확도
        last_week_quiz_correct = 0
        for q in last_week_quiz:
            if q.total_score is not None and q.total_questions and q.total_questions > 0:
                last_week_quiz_correct += 1 if (q.total_score / q.total_questions) >= 0.6 else 0
        
        last_week_code_correct = sum(1 for c in last_week_code if c.status == 'accepted')
        last_week_correct = last_week_quiz_correct + last_week_code_correct
        last_week_accuracy = (last_week_correct / last_week_problems * 100) if last_week_problems > 0 else 0
        
        accuracy_change = round(weekly_accuracy - last_week_accuracy, 1)
        
        # 속도 개선 (문제당 평균 시간)
        current_avg_time = (weekly_minutes / weekly_problems) if weekly_problems > 0 else 0
        last_avg_time = (weekly_minutes / last_week_problems) if last_week_problems > 0 else 1
        speed_change = round(((last_avg_time - current_avg_time) / last_avg_time * 100), 1) if last_avg_time > 0 else 0
        
        return {
            "daily": {
                "problems_solved": daily_problems,
                "accuracy": daily_accuracy,
                "study_minutes": int(daily_minutes)
            },
            "weekly": {
                "problems_solved": weekly_problems,
                "accuracy": weekly_accuracy,
                "study_hours": weekly_hours,
                "streak_days": streak_days
            },
            "monthly": {
                "problems_solved": monthly_problems,
                "accuracy": monthly_accuracy,
                "study_hours": monthly_hours,
                "completed_days": completed_days
            },
            "improvement": {
                "accuracy_change": accuracy_change,
                "speed_change": speed_change
            }
        }
        
    except Exception as e:
        logger.error(f"학습 통계 조회 실패 {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"학습 통계 조회 실패: {str(e)}")
