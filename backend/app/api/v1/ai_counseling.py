"""
AI 학습 상담 API - 기존 AI 멘토링 시스템 활용
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User
from app.services.ai_mentoring_system import (
    get_ai_mentoring_system, 
    AIMentoringSystem, 
    ConversationMode,
    MentorPersonality
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai-counseling", tags=["AI Counseling"])

# ========== Pydantic 모델들 ==========

class CounselingRequest(BaseModel):
    """상담 요청 모델"""
    message: str = Field(..., description="상담 내용")
    type: str = Field(..., description="상담 유형: motivation, guidance, goal_setting, habit_building")
    mood_score: Optional[int] = Field(None, ge=1, le=10, description="기분 점수 (1-10)")
    context: Optional[Dict[str, Any]] = Field(None, description="추가 컨텍스트")

class CounselingResponse(BaseModel):
    """상담 응답 모델"""
    session_id: str
    ai_response: str
    mentor_personality: str
    suggestions: List[str]
    follow_up_questions: List[str]
    confidence: float
    timestamp: datetime

class MotivationRequest(BaseModel):
    """일일 동기부여 요청"""
    user_context: Optional[Dict[str, Any]] = Field(None, description="사용자 컨텍스트")

class LearningTipsRequest(BaseModel):
    """학습 팁 요청"""
    topic: Optional[str] = Field(None, description="특정 주제")
    learning_context: Optional[Dict[str, Any]] = Field(None, description="학습 컨텍스트")

# ========== API 엔드포인트들 ==========

@router.post("/start-session", response_model=Dict[str, Any])
async def start_counseling_session(
    initial_question: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """상담 세션 시작"""
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        # 멘토링 세션 시작
        session = await mentoring_system.start_mentoring_session(
            user_id=current_user.id,
            initial_question=initial_question
        )
        
        return {
            "success": True,
            "session_id": session.session_id,
            "mentor_personality": session.mentor_personality.value,
            "welcome_message": session.conversation_history[-1]['content'] if session.conversation_history else "안녕하세요! AI 학습 상담사입니다.",
            "session_goals": session.session_goals,
            "current_mood": session.current_mood
        }
        
    except Exception as e:
        logger.error(f"상담 세션 시작 실패 user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상담 세션 시작 실패: {str(e)}")

@router.post("/message", response_model=CounselingResponse)
async def send_counseling_message(
    request: CounselingRequest,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """상담 메시지 전송"""
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        # 세션이 없으면 새로 시작
        if not session_id:
            session = await mentoring_system.start_mentoring_session(
                user_id=current_user.id,
                initial_question=request.message
            )
            actual_session_id = session.session_id
        else:
            actual_session_id = session_id
        
        # 상담 유형에 따른 대화 모드 설정
        conversation_mode_mapping = {
            'motivation': ConversationMode.MOTIVATION,
            'guidance': ConversationMode.GUIDANCE,
            'goal_setting': ConversationMode.GUIDANCE,
            'habit_building': ConversationMode.GUIDANCE,
            'explanation': ConversationMode.EXPLANATION,
            'help': ConversationMode.HELP_SEEKING
        }
        
        conversation_mode = conversation_mode_mapping.get(
            request.type, 
            ConversationMode.HELP_SEEKING
        )
        
        # AI 멘토와 대화 진행
        mentor_response = await mentoring_system.continue_conversation(
            session_id=actual_session_id,
            user_message=request.message,
            conversation_mode=conversation_mode
        )
        
        return CounselingResponse(
            session_id=actual_session_id,
            ai_response=mentor_response.content,
            mentor_personality=mentor_response.tone,
            suggestions=mentor_response.suggestions,
            follow_up_questions=mentor_response.follow_up_questions,
            confidence=mentor_response.confidence,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"상담 메시지 처리 실패 user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상담 메시지 처리 실패: {str(e)}")

@router.get("/daily-motivation", response_model=Dict[str, Any])
async def get_daily_motivation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """일일 동기부여 메시지"""
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        motivation_message = await mentoring_system.get_daily_motivation(current_user.id)
        
        return {
            "success": True,
            "motivation_message": motivation_message,
            "user_id": current_user.id,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"일일 동기부여 생성 실패 user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"동기부여 메시지 생성 실패: {str(e)}")

@router.get("/learning-tips", response_model=Dict[str, Any])
async def get_learning_tips(
    topic: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """개인화된 학습 팁"""
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        learning_tips = await mentoring_system.get_learning_tips(
            user_id=current_user.id,
            topic=topic
        )
        
        return {
            "success": True,
            "tips": learning_tips,
            "topic": topic or "general",
            "user_id": current_user.id,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"학습 팁 생성 실패 user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"학습 팁 생성 실패: {str(e)}")

@router.get("/session-history/{session_id}", response_model=Dict[str, Any])
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """세션 기록 조회"""
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        # 세션 조회 (내부 메서드 사용)
        session = await mentoring_system._get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
        
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="세션 접근 권한이 없습니다")
        
        return {
            "success": True,
            "session_id": session.session_id,
            "conversation_history": session.conversation_history,
            "mentor_personality": session.mentor_personality.value,
            "session_goals": session.session_goals,
            "start_time": session.start_time,
            "current_mood": session.current_mood
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 기록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"세션 기록 조회 실패: {str(e)}")

@router.get("/user-insights", response_model=Dict[str, Any])
async def get_user_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 학습 인사이트"""
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        # 사용자 기분 상태 및 학습 팁 조합
        user_mood = await mentoring_system._assess_user_mood(current_user.id)
        motivation_message = await mentoring_system.get_daily_motivation(current_user.id)
        learning_tips = await mentoring_system.get_learning_tips(current_user.id)
        
        # 인사이트 구성
        insights = []
        
        # 기분 기반 인사이트
        if user_mood == 'confident':
            insights.append({
                "type": "achievement",
                "title": "훌륭한 성과를 보이고 있어요!",
                "message": "최근 학습 성과가 매우 좋습니다. 이 기세를 유지해보세요!",
                "icon": "🎉"
            })
        elif user_mood == 'struggling':
            insights.append({
                "type": "encouragement",
                "title": "포기하지 마세요",
                "message": "어려운 시기지만 꾸준히 노력하고 계십니다. 조금씩 나아지고 있어요.",
                "icon": "💪"
            })
        else:
            insights.append({
                "type": "progress",
                "title": "꾸준한 성장 중이에요",
                "message": "안정적인 학습 패턴을 보이고 있습니다. 계속 진행해보세요!",
                "icon": "📈"
            })
        
        # 학습 팁 기반 인사이트
        if learning_tips:
            insights.append({
                "type": "challenge",
                "title": "새로운 도전 제안",
                "message": f"다음 단계: {learning_tips[0] if learning_tips else '꾸준한 학습 지속'}",
                "icon": "🚀"
            })
        
        return {
            "success": True,
            "insights": insights,
            "motivation_message": motivation_message,
            "learning_tips": learning_tips,
            "user_mood": user_mood,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"사용자 인사이트 생성 실패 user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"인사이트 생성 실패: {str(e)}")

# 헬스 체크
@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """AI 상담 시스템 상태 확인"""
    return {
        "status": "healthy",
        "service": "AI Counseling System",
        "version": "1.0",
        "integration": "AI Mentoring System"
    }
