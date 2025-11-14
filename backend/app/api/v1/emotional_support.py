# -*- coding: utf-8 -*-
"""
감성적 지원 API 엔드포인트

학습자의 감정, 동기, 컨텍스트를 관리하여
개인화된 학습 경험 제공
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.orm import User, LearningContext, MoodCheckIn, EncouragingMessage
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/api/v1/emotional")


# ============================================================
# Pydantic 스키마
# ============================================================

class LearningContextCreate(BaseModel):
    """학습 컨텍스트 생성"""
    session_id: Optional[str] = None
    track_id: Optional[int] = None
    module_id: Optional[int] = None
    
    # 감정 상태
    mood: Optional[str] = Field(None, description="great, good, okay, struggling, frustrated")
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    confidence_level: Optional[int] = Field(None, ge=1, le=10)
    
    # 학습 계획
    study_duration_minutes: Optional[int] = None
    daily_goal: Optional[str] = None
    motivation_level: Optional[int] = Field(None, ge=1, le=10)
    why_learning_today: Optional[str] = None
    
    # 어려움
    current_struggle: Optional[str] = None
    needs_encouragement: bool = False
    preferred_support_type: Optional[str] = Field(None, description="gentle, motivational, technical")


class MoodCheckInCreate(BaseModel):
    """기분 체크인 생성"""
    context_id: Optional[int] = None
    check_in_type: str = Field(..., description="before_learning, after_learning, during_break")
    
    mood: str = Field(..., description="great, good, okay, struggling, frustrated, exhausted")
    mood_emoji: Optional[str] = None
    energy_level: int = Field(..., ge=1, le=10)
    stress_level: int = Field(..., ge=1, le=10)
    
    # 선택적 설명
    feeling_description: Optional[str] = None
    what_went_well: Optional[str] = None
    what_was_hard: Optional[str] = None
    
    # 신체 상태
    is_tired: bool = False
    is_hungry: bool = False
    is_distracted: bool = False


class EncouragingMessageResponse(BaseModel):
    """격려 메시지 응답"""
    id: int
    message: str
    message_tone: str
    trigger_type: str
    sent_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# API 엔드포인트 - Learning Context
# ============================================================

@router.post("/context/start")
async def start_learning_session(
    context_data: LearningContextCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학습 세션 시작
    
    학습 시작 시 컨텍스트를 기록하고,
    필요한 경우 격려 메시지 생성
    """
    import uuid
    
    # 세션 ID 생성
    session_id = context_data.session_id or str(uuid.uuid4())
    
    # 마지막 컨텍스트 조회
    last_context = db.query(LearningContext).filter_by(
        user_id=user.id
    ).order_by(LearningContext.created_at.desc()).first()
    
    # 연속 학습 일수 계산
    yesterday = datetime.utcnow() - timedelta(days=1)
    had_session_yesterday = db.query(LearningContext).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= yesterday,
            LearningContext.created_at < datetime.utcnow().replace(hour=0, minute=0, second=0)
        )
    ).first() is not None
    
    # 연속 일수 결정
    if had_session_yesterday and last_context:
        consecutive_days_count = last_context.consecutive_days_count + 1
    else:
        consecutive_days_count = 1  # 새 시작 또는 연속 끊김
    
    # 현재 시간대 판단
    current_hour = datetime.utcnow().hour
    if 5 <= current_hour < 12:
        time_of_day = "morning"
    elif 12 <= current_hour < 17:
        time_of_day = "afternoon"
    elif 17 <= current_hour < 21:
        time_of_day = "evening"
    else:
        time_of_day = "night"
    
    # 컨텍스트 생성
    context = LearningContext(
        user_id=user.id,
        session_id=session_id,
        track_id=context_data.track_id,
        module_id=context_data.module_id,
        mood=context_data.mood,
        energy_level=context_data.energy_level,
        confidence_level=context_data.confidence_level,
        study_duration_minutes=context_data.study_duration_minutes,
        time_of_day=time_of_day,
        is_consecutive_day=had_session_yesterday,
        consecutive_days_count=consecutive_days_count,  # ✅ 수정됨!
        daily_goal=context_data.daily_goal,
        motivation_level=context_data.motivation_level,
        why_learning_today=context_data.why_learning_today,
        current_struggle=context_data.current_struggle,
        needs_encouragement=context_data.needs_encouragement,
        preferred_support_type=context_data.preferred_support_type
    )
    
    db.add(context)
    db.commit()
    db.refresh(context)
    
    # 격려 메시지 생성 로직
    encouraging_message = None
    if context_data.needs_encouragement or (context_data.confidence_level and context_data.confidence_level < 4):
        # 자신감이 낮거나 격려가 필요한 경우
        message = await _generate_encouraging_message(
            user=user,
            context=context,
            trigger_type="low_confidence",
            db=db
        )
        encouraging_message = message
    
    return {
        "session_id": session_id,
        "context_id": context.id,
        "consecutive_days": context.consecutive_days_count,
        "encouraging_message": encouraging_message
    }


@router.put("/context/{session_id}/end")
async def end_learning_session(
    session_id: str,
    actual_duration_minutes: int,
    interruptions_count: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """학습 세션 종료 및 실제 학습 시간 기록"""
    
    context = db.query(LearningContext).filter(
        and_(
            LearningContext.session_id == session_id,
            LearningContext.user_id == user.id
        )
    ).first()
    
    if not context:
        raise HTTPException(status_code=404, detail="학습 세션을 찾을 수 없습니다")
    
    context.actual_duration_minutes = actual_duration_minutes
    context.interruptions_count = interruptions_count
    
    db.commit()
    
    return {
        "message": "학습 세션이 종료되었습니다",
        "planned_duration": context.study_duration_minutes,
        "actual_duration": actual_duration_minutes,
        "completion_rate": (actual_duration_minutes / context.study_duration_minutes * 100) if context.study_duration_minutes else 0
    }


# ============================================================
# API 엔드포인트 - Mood Check-in
# ============================================================

@router.post("/mood/check-in")
async def create_mood_check_in(
    mood_data: MoodCheckInCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    기분 체크인
    
    학습 전후의 감정 상태를 기록
    """
    
    # context_id 자동 연결 (없으면 최근 학습 세션 찾기)
    context_id = mood_data.context_id
    if not context_id:
        # 최근 24시간 이내의 학습 세션 찾기
        recent_time = datetime.utcnow() - timedelta(hours=24)
        recent_context = db.query(LearningContext).filter(
            and_(
                LearningContext.user_id == user.id,
                LearningContext.created_at >= recent_time
            )
        ).order_by(LearningContext.created_at.desc()).first()
        
        if recent_context:
            context_id = recent_context.id
    
    check_in = MoodCheckIn(
        user_id=user.id,
        context_id=context_id,  # ✅ 자동 연결됨
        check_in_type=mood_data.check_in_type,
        mood=mood_data.mood,
        mood_emoji=mood_data.mood_emoji,
        energy_level=mood_data.energy_level,
        stress_level=mood_data.stress_level,
        feeling_description=mood_data.feeling_description,
        what_went_well=mood_data.what_went_well,
        what_was_hard=mood_data.what_was_hard,
        is_tired=mood_data.is_tired,
        is_hungry=mood_data.is_hungry,
        is_distracted=mood_data.is_distracted
    )
    
    db.add(check_in)
    db.commit()
    db.refresh(check_in)
    
    return {
        "id": check_in.id,
        "message": "기분 체크인이 기록되었습니다",
        "mood": check_in.mood,
        "checked_in_at": check_in.checked_in_at,
        "linked_to_session": context_id is not None
    }


@router.get("/mood/history")
async def get_mood_history(
    days: int = Query(7, ge=1, le=90, description="조회 기간 (일)"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    기분 히스토리 조회
    
    지난 N일간의 기분 변화 추이
    """
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    check_ins = db.query(MoodCheckIn).filter(
        and_(
            MoodCheckIn.user_id == user.id,
            MoodCheckIn.checked_in_at >= since_date
        )
    ).order_by(MoodCheckIn.checked_in_at.desc()).all()
    
    # 통계 계산
    mood_counts = {}
    avg_energy = 0
    avg_stress = 0
    
    if check_ins:
        for check_in in check_ins:
            mood_counts[check_in.mood] = mood_counts.get(check_in.mood, 0) + 1
        
        avg_energy = sum(c.energy_level for c in check_ins) / len(check_ins)
        avg_stress = sum(c.stress_level for c in check_ins) / len(check_ins)
    
    return {
        "total_check_ins": len(check_ins),
        "mood_distribution": mood_counts,
        "average_energy_level": round(avg_energy, 1),
        "average_stress_level": round(avg_stress, 1),
        "check_ins": [
            {
                "id": c.id,
                "mood": c.mood,
                "mood_emoji": c.mood_emoji,
                "energy_level": c.energy_level,
                "stress_level": c.stress_level,
                "check_in_type": c.check_in_type,
                "checked_in_at": c.checked_in_at
            }
            for c in check_ins
        ]
    }


# ============================================================
# API 엔드포인트 - Encouraging Messages
# ============================================================

@router.get("/encouragement", response_model=List[EncouragingMessageResponse])
async def get_encouraging_messages(
    unread_only: bool = Query(False, description="읽지 않은 메시지만 조회"),
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """격려 메시지 조회"""
    
    query = db.query(EncouragingMessage).filter_by(user_id=user.id)
    
    if unread_only:
        query = query.filter(EncouragingMessage.read_at.is_(None))
    
    messages = query.order_by(EncouragingMessage.sent_at.desc()).limit(limit).all()
    
    return messages


@router.put("/encouragement/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    was_helpful: Optional[bool] = None,
    feedback: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """격려 메시지 읽음 처리 및 피드백"""
    
    message = db.query(EncouragingMessage).filter(
        and_(
            EncouragingMessage.id == message_id,
            EncouragingMessage.user_id == user.id
        )
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다")
    
    message.read_at = datetime.utcnow()
    
    if was_helpful is not None:
        message.was_helpful = was_helpful
    
    if feedback:
        message.user_feedback = feedback
    
    db.commit()
    
    return {"message": "피드백이 기록되었습니다"}


# ============================================================
# API 엔드포인트 - 자기 대비 대시보드
# ============================================================

@router.get("/dashboard/self-comparison")
async def get_self_comparison_dashboard(
    compare_days: int = Query(30, description="비교 기간 (일)"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    자기 대비 대시보드
    
    과거의 나와 비교하여 성장 추적
    """
    
    # 현재 기간 (최근 N일)
    current_end = datetime.utcnow()
    current_start = current_end - timedelta(days=compare_days)
    
    # 비교 기간 (그 이전 N일)
    past_end = current_start
    past_start = past_end - timedelta(days=compare_days)
    
    # 학습 세션 수
    current_sessions = db.query(func.count(LearningContext.id)).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= current_start,
            LearningContext.created_at < current_end
        )
    ).scalar() or 0
    
    past_sessions = db.query(func.count(LearningContext.id)).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= past_start,
            LearningContext.created_at < past_end
        )
    ).scalar() or 0
    
    # 평균 자신감 레벨
    current_confidence = db.query(func.avg(LearningContext.confidence_level)).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= current_start,
            LearningContext.confidence_level.isnot(None)
        )
    ).scalar() or 0
    
    past_confidence = db.query(func.avg(LearningContext.confidence_level)).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= past_start,
            LearningContext.created_at < past_end,
            LearningContext.confidence_level.isnot(None)
        )
    ).scalar() or 0
    
    # 평균 학습 시간
    current_avg_duration = db.query(func.avg(LearningContext.actual_duration_minutes)).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= current_start,
            LearningContext.actual_duration_minutes.isnot(None)
        )
    ).scalar() or 0
    
    past_avg_duration = db.query(func.avg(LearningContext.actual_duration_minutes)).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= past_start,
            LearningContext.created_at < past_end,
            LearningContext.actual_duration_minutes.isnot(None)
        )
    ).scalar() or 0
    
    # 연속 학습 일수
    recent_contexts = db.query(LearningContext.consecutive_days_count).filter(
        LearningContext.user_id == user.id
    ).order_by(LearningContext.created_at.desc()).first()
    
    current_streak = recent_contexts.consecutive_days_count if recent_contexts else 0
    
    return {
        "comparison_period_days": compare_days,
        "learning_sessions": {
            "current": current_sessions,
            "past": past_sessions,
            "change": current_sessions - past_sessions,
            "change_percentage": ((current_sessions - past_sessions) / past_sessions * 100) if past_sessions > 0 else 0
        },
        "confidence_level": {
            "current": round(current_confidence, 1),
            "past": round(past_confidence, 1),
            "change": round(current_confidence - past_confidence, 1)
        },
        "average_study_time": {
            "current_minutes": round(current_avg_duration, 1),
            "past_minutes": round(past_avg_duration, 1),
            "change_minutes": round(current_avg_duration - past_avg_duration, 1)
        },
        "current_streak_days": current_streak,
        "insights": _generate_insights(
            current_sessions, past_sessions,
            current_confidence, past_confidence,
            current_streak
        )
    }


# ============================================================
# API 엔드포인트 - 적응형 학습 목표
# ============================================================

@router.get("/adaptive-goal")
async def get_adaptive_learning_goal(
    track_id: Optional[int] = Query(None, description="학습 트랙 ID"),
    module_id: Optional[int] = Query(None, description="모듈 ID"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    적응형 학습 목표 추천
    
    현재 학습자의 상태(에너지, 자신감, 스트레스)에 따라
    최적의 학습 목표와 난이도를 추천
    """
    
    # 최근 컨텍스트 조회 (최근 7일)
    recent_date = datetime.utcnow() - timedelta(days=7)
    recent_contexts = db.query(LearningContext).filter(
        and_(
            LearningContext.user_id == user.id,
            LearningContext.created_at >= recent_date
        )
    ).order_by(LearningContext.created_at.desc()).limit(5).all()
    
    # 최근 기분 체크인 조회
    recent_mood = db.query(MoodCheckIn).filter(
        and_(
            MoodCheckIn.user_id == user.id,
            MoodCheckIn.checked_in_at >= recent_date
        )
    ).order_by(MoodCheckIn.checked_in_at.desc()).first()
    
    # 기본값
    avg_energy = 5
    avg_confidence = 5
    avg_stress = 5
    
    # 평균 계산
    if recent_contexts:
        energy_levels = [c.energy_level for c in recent_contexts if c.energy_level]
        confidence_levels = [c.confidence_level for c in recent_contexts if c.confidence_level]
        
        if energy_levels:
            avg_energy = sum(energy_levels) / len(energy_levels)
        if confidence_levels:
            avg_confidence = sum(confidence_levels) / len(confidence_levels)
    
    if recent_mood:
        avg_stress = recent_mood.stress_level
    
    # 적응형 난이도 결정
    recommended_difficulty = _calculate_adaptive_difficulty(
        energy=avg_energy,
        confidence=avg_confidence,
        stress=avg_stress
    )
    
    # 권장 학습 시간 (분)
    recommended_duration = _calculate_recommended_duration(
        energy=avg_energy,
        stress=avg_stress
    )
    
    # 맞춤형 조언
    advice = _generate_adaptive_advice(
        difficulty=recommended_difficulty,
        energy=avg_energy,
        confidence=avg_confidence,
        stress=avg_stress
    )
    
    return {
        "current_state": {
            "average_energy": round(avg_energy, 1),
            "average_confidence": round(avg_confidence, 1),
            "average_stress": round(avg_stress, 1)
        },
        "recommended_difficulty": recommended_difficulty,
        "recommended_duration_minutes": recommended_duration,
        "advice": advice,
        "motivational_message": _get_motivational_message_by_state(
            energy=avg_energy,
            confidence=avg_confidence
        )
    }


@router.post("/adaptive-session/start")
async def start_adaptive_learning_session(
    context_data: LearningContextCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    적응형 학습 세션 시작
    
    현재 상태에 기반한 맞춤형 학습 세션 시작
    """
    
    # 적응형 목표 가져오기
    adaptive_goal = await get_adaptive_learning_goal(
        track_id=context_data.track_id,
        module_id=context_data.module_id,
        user=user,
        db=db
    )
    
    # 컨텍스트 데이터에 추천 시간 적용
    if not context_data.study_duration_minutes:
        context_data.study_duration_minutes = adaptive_goal["recommended_duration_minutes"]
    
    # 세션 시작 (기존 로직 재사용)
    session = await start_learning_session(context_data, user, db)
    
    # 적응형 정보 추가
    session["adaptive_recommendations"] = {
        "difficulty": adaptive_goal["recommended_difficulty"],
        "duration": adaptive_goal["recommended_duration_minutes"],
        "advice": adaptive_goal["advice"]
    }
    
    return session


# ============================================================
# Helper Functions
# ============================================================

async def _generate_encouraging_message(
    user: User,
    context: LearningContext,
    trigger_type: str,
    db: Session
) -> dict:
    """격려 메시지 생성"""
    
    # 사전 정의된 메시지 (추후 Claude로 개인화 가능)
    messages = {
        "low_confidence": [
            "괜찮아요! 모든 전문가도 처음에는 초보자였어요. 한 걸음씩 나아가면 됩니다. 💪",
            "어려움은 성장의 신호입니다. 지금 느끼는 어려움이 곧 당신을 더 강하게 만들 거예요. 🌱",
            "완벽할 필요는 없어요. 어제의 나보다 조금 나아지면 충분합니다. 화이팅! ✨"
        ],
        "consecutive_learning": [
            f"와! {context.consecutive_days_count}일 연속 학습 중이시네요! 정말 대단해요! 🔥",
            "꾸준함이 재능을 이긴다고 했죠. 당신은 이미 승리하고 있어요! 🏆"
        ],
        "comeback": [
            "다시 돌아오신 걸 환영해요! 쉬는 것도 학습의 일부랍니다. 💙",
            "오늘부터 다시 시작이에요. 과거는 중요하지 않아요. 지금 이 순간이 중요합니다! 🚀"
        ]
    }
    
    import random
    message_text = random.choice(messages.get(trigger_type, ["화이팅! 💪"]))
    
    message = EncouragingMessage(
        user_id=user.id,
        trigger_type=trigger_type,
        message=message_text,
        message_tone=context.preferred_support_type or "gentle",
        is_ai_generated=False,
        context_data={"mood": context.mood, "confidence": context.confidence_level}
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.id,
        "message": message.message,
        "tone": message.message_tone
    }


def _generate_insights(
    current_sessions: int,
    past_sessions: int,
    current_confidence: float,
    past_confidence: float,
    current_streak: int
) -> List[str]:
    """성장 인사이트 생성"""
    
    insights = []
    
    # 학습 세션 비교
    if current_sessions > past_sessions:
        increase = current_sessions - past_sessions
        insights.append(f"🎉 이전보다 {increase}개 더 많은 학습 세션을 진행했어요!")
    elif current_sessions < past_sessions and past_sessions > 0:
        insights.append("💪 학습 빈도가 줄었네요. 작은 목표부터 다시 시작해볼까요?")
    
    # 자신감 비교
    if current_confidence > past_confidence:
        insights.append(f"✨ 자신감이 {round(current_confidence - past_confidence, 1)}점 상승했어요!")
    
    # 연속 학습
    if current_streak >= 7:
        insights.append(f"🔥 {current_streak}일 연속 학습 중! 정말 대단해요!")
    elif current_streak >= 3:
        insights.append(f"👏 {current_streak}일 연속 학습! 이대로만 계속하세요!")
    
    # 기본 메시지
    if not insights:
        insights.append("💙 당신의 학습 여정을 응원합니다. 꾸준히 나아가세요!")
    
    return insights


def _calculate_adaptive_difficulty(energy: float, confidence: float, stress: float) -> str:
    """
    적응형 난이도 계산
    
    에너지, 자신감, 스트레스를 종합하여 최적의 난이도 결정
    """
    
    # 종합 점수 계산 (1-10 scale)
    # 에너지 40%, 자신감 40%, 스트레스(역) 20%
    overall_score = (energy * 0.4) + (confidence * 0.4) + ((11 - stress) * 0.2)
    
    if overall_score >= 8:
        return "challenging"  # 도전적
    elif overall_score >= 6:
        return "moderate"  # 보통
    elif overall_score >= 4:
        return "easy"  # 쉬움
    else:
        return "very_easy"  # 매우 쉬움
    

def _calculate_recommended_duration(energy: float, stress: float) -> int:
    """
    권장 학습 시간 계산 (분)
    
    에너지와 스트레스에 따라 최적 학습 시간 추천
    """
    
    # 기본 시간: 45분
    base_duration = 45
    
    # 에너지가 높으면 +15분, 낮으면 -15분
    energy_adjustment = (energy - 5) * 3  # -15 ~ +15
    
    # 스트레스가 높으면 -10분
    stress_adjustment = -(max(0, stress - 5) * 2)  # -10 ~ 0
    
    total = base_duration + energy_adjustment + stress_adjustment
    
    # 최소 15분, 최대 90분
    return max(15, min(90, int(total)))


def _generate_adaptive_advice(
    difficulty: str,
    energy: float,
    confidence: float,
    stress: float
) -> List[str]:
    """맞춤형 학습 조언 생성"""
    
    advice = []
    
    # 난이도 기반 조언
    difficulty_advice = {
        "challenging": "지금 컨디션이 좋으니 도전적인 내용을 학습하기 좋은 시기예요! 💪",
        "moderate": "적당한 난이도의 학습으로 꾸준히 발전해나가세요. 👍",
        "easy": "오늘은 쉬운 내용으로 부담 없이 시작해보세요. 🌱",
        "very_easy": "무리하지 마세요. 가벼운 복습이나 개념 정리가 좋겠어요. 💙"
    }
    advice.append(difficulty_advice[difficulty])
    
    # 에너지 기반 조언
    if energy < 4:
        advice.append("⚡ 에너지가 낮네요. 짧은 학습 시간을 권장합니다. 휴식도 학습의 일부예요!")
    elif energy > 7:
        advice.append("🔥 활기가 넘치네요! 집중 학습에 좋은 타이밍입니다!")
    
    # 자신감 기반 조언
    if confidence < 4:
        advice.append("💙 자신감이 낮을 때는 이미 잘 아는 내용을 복습하면서 성취감을 쌓아보세요.")
    elif confidence > 7:
        advice.append("✨ 자신감이 높네요! 새로운 도전을 시도해보는 건 어떨까요?")
    
    # 스트레스 기반 조언
    if stress > 7:
        advice.append("😌 스트레스가 높네요. 학습 전에 5분 정도 심호흡이나 스트레칭을 해보세요.")
    
    return advice


def _get_motivational_message_by_state(energy: float, confidence: float) -> str:
    """상태에 따른 동기부여 메시지"""
    
    if energy < 4 and confidence < 4:
        return "오늘은 힘든 하루네요. 그래도 여기까지 온 당신이 대단해요. 💙 작은 것부터 시작해봐요."
    elif energy < 4:
        return "피곤하지만 학습하려는 당신의 의지가 멋져요! 🌙 오늘은 짧게라도 괜찮아요."
    elif confidence < 4:
        return "자신감이 없을 때도 있어요. 괜찮아요. 💛 한 걸음씩 나아가다 보면 달라질 거예요."
    elif energy > 7 and confidence > 7:
        return "최고의 컨디션이네요! 🔥 오늘은 정말 많은 것을 배울 수 있을 거예요!"
    else:
        return "좋은 컨디션이에요! 💪 오늘도 꾸준히 나아가봐요!"

