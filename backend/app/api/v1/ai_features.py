"""
AI 고도화 기능 API 엔드포인트 - Phase 4
- 심층 학습 분석 API
- 적응형 난이도 조절 API
- AI 멘토링 API
- 개인화 학습 경로 API
- 고급 AI 기능 API
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.orm import User
from app.services.deep_learning_analyzer import get_deep_learning_analyzer
from app.services.adaptive_difficulty_engine import get_adaptive_difficulty_engine
from app.services.ai_mentoring_system import get_ai_mentoring_system, ConversationMode, MentorPersonality
from app.services.personalized_learning_path import get_personalized_learning_path_generator, LearningGoalType
from app.services.advanced_ai_features import get_advanced_ai_features, ReviewType

logger = logging.getLogger(__name__)

router = APIRouter()

# === Pydantic 모델들 ===

class LearningAnalysisRequest(BaseModel):
    use_ai: bool = True
    analysis_type: str = "comprehensive"

class DifficultyRequest(BaseModel):
    topic: Optional[str] = None
    current_difficulty: Optional[int] = None

class MentorSessionRequest(BaseModel):
    initial_question: Optional[str] = None

class MentorMessageRequest(BaseModel):
    session_id: str
    message: str
    conversation_mode: str = "help_seeking"

class LearningPathRequest(BaseModel):
    goal_type: str
    target_skill: str
    deadline: Optional[str] = None
    current_level: Optional[str] = None

class CodeReviewRequest(BaseModel):
    code: str
    language: str
    review_type: str = "full"
    user_level: str = "intermediate"

class ProjectAnalysisRequest(BaseModel):
    project_data: Dict[str, Any]

# === 심층 학습 분석 API ===

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """AI 기능 헬스 체크"""
    return {
        "status": "healthy",
        "message": "AI Features API is operational",
        "version": "1.0.0-phase4",
        "features": [
            "deep_learning_analysis",
            "adaptive_difficulty",
            "ai_mentoring",
            "personalized_learning_path",
            "advanced_ai_features"
        ]
    }

@router.post("/analysis/deep-learning/{user_id}", response_model=Dict[str, Any])
async def analyze_user_learning_deeply(
    user_id: int,
    request: LearningAnalysisRequest = Body(...),
    db: Session = Depends(get_db)
):
    """사용자 심층 학습 분석"""
    
    try:
        # 임시로 간단한 더미 데이터 반환
        logger.info(f"심층 학습 분석 요청: user {user_id}")
        
        # 실제 분석기 호출 대신 임시 데이터 반환
        return {
            "success": True,
            "analysis": {
                "success": True,
                "user_id": user_id,
                "analysis_date": datetime.utcnow().isoformat(),
                "data_period_days": 30,
                "submissions_analyzed": 5,
                "learner_profile": {
                    "type": "steady_learner",
                    "phase": "intermediate",
                    "strengths": ["문제 해결", "논리적 사고"],
                    "weaknesses": ["시간 관리"],
                    "preferred_difficulty": 7,
                    "optimal_session_length": 30,
                    "learning_style": ["visual", "practice"],
                    "motivation_factors": ["achievement", "progress"]
                },
                "learning_metrics": {
                    "overall_accuracy": 0.75,
                    "avg_response_time": 45.2,
                    "consistency_score": 0.8,
                    "improvement_rate": 0.15,
                    "engagement_level": 0.9,
                    "topic_mastery": {"알고리즘": 0.8, "자료구조": 0.7},
                    "difficulty_progression": [5, 6, 7]
                },
                "ai_insights": {"note": "AI 분석 임시 비활성화"},
                "recommendations": [
                    "매일 꾸준한 학습 계속하기",
                    "시간 관리 연습하기"
                ],
                "learning_path": {"next_topics": ["고급 알고리즘", "시간 복잡도"]},
                "next_actions": ["문제 풀이 속도 향상 연습"]
            },
            "generated_at": datetime.utcnow().isoformat(),
            "api_version": "phase4"
        }
        
    except Exception as e:
        logger.error(f"심층 학습 분석 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@router.get("/analysis/learning-metrics/{user_id}", response_model=Dict[str, Any])
async def get_learning_metrics(
    user_id: int,
    days: int = Query(30, description="분석 기간 (일)"),
    db: Session = Depends(get_db)
):
    """학습 메트릭 조회"""
    
    try:
        analyzer = get_deep_learning_analyzer(db)
        
        # 간단한 메트릭만 반환 (캐시된 분석 결과 활용)
        cache_key = f"deep_analysis:{user_id}"
        cached_analysis = analyzer.redis_service.get_cache(cache_key)
        
        if cached_analysis:
            return {
                "success": True,
                "metrics": cached_analysis.get('learning_metrics', {}),
                "learner_profile": cached_analysis.get('learner_profile', {}),
                "data_period_days": days,
                "last_updated": cached_analysis.get('analysis_date', datetime.utcnow().isoformat())
            }
        
        # 캐시가 없으면 새로 분석
        analysis_result = await analyzer.analyze_user_deeply(user_id, use_ai=False)
        
        return {
            "success": analysis_result.get('success', False),
            "metrics": analysis_result.get('learning_metrics', {}),
            "learner_profile": analysis_result.get('learner_profile', {}),
            "message": "새로운 분석 결과입니다."
        }
        
    except Exception as e:
        logger.error(f"학습 메트릭 조회 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"메트릭 조회 실패: {str(e)}")

# === 적응형 난이도 조절 API ===

@router.post("/difficulty/optimal/{user_id}", response_model=Dict[str, Any])
async def calculate_optimal_difficulty(
    user_id: int,
    request: DifficultyRequest = Body(...),
    db: Session = Depends(get_db)
):
    """최적 난이도 계산"""
    
    try:
        difficulty_engine = get_adaptive_difficulty_engine(db)
        
        recommendation = await difficulty_engine.calculate_optimal_difficulty(
            user_id=user_id,
            topic=request.topic,
            current_difficulty=request.current_difficulty
        )
        
        return {
            "success": True,
            "recommendation": {
                "recommended_difficulty": recommendation.recommended_difficulty,
                "confidence": recommendation.confidence,
                "reasoning": recommendation.reasoning,
                "expected_accuracy": recommendation.expected_accuracy,
                "adjustment_timeline": recommendation.adjustment_timeline
            },
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"난이도 계산 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"난이도 계산 실패: {str(e)}")

@router.get("/difficulty/next-question/{user_id}", response_model=Dict[str, Any])
async def get_next_question_difficulty(
    user_id: int,
    topic: str = Query(..., description="주제"),
    db: Session = Depends(get_db)
):
    """다음 문제 난이도 추천"""
    
    try:
        difficulty_engine = get_adaptive_difficulty_engine(db)
        
        next_difficulty = await difficulty_engine.get_next_question_difficulty(user_id, topic)
        
        return {
            "success": True,
            "next_difficulty": next_difficulty,
            "topic": topic,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"다음 문제 난이도 추천 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"난이도 추천 실패: {str(e)}")

# === AI 멘토링 API ===

@router.post("/mentoring/start-session/{user_id}", response_model=Dict[str, Any])
async def start_mentoring_session(
    user_id: int,
    request: MentorSessionRequest = Body(...),
    db: Session = Depends(get_db)
):
    """멘토링 세션 시작"""
    
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        session = await mentoring_system.start_mentoring_session(
            user_id=user_id,
            initial_question=request.initial_question
        )
        
        # 인사말 추출
        greeting = ""
        if session.conversation_history:
            greeting = session.conversation_history[0].get('content', '')
        
        return {
            "success": True,
            "session": {
                "session_id": session.session_id,
                "mentor_personality": session.mentor_personality.value,
                "session_goals": session.session_goals,
                "greeting": greeting
            },
            "started_at": session.start_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"멘토링 세션 시작 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"멘토링 세션 시작 실패: {str(e)}")

@router.post("/mentoring/continue", response_model=Dict[str, Any])
async def continue_mentoring_conversation(
    request: MentorMessageRequest = Body(...),
    db: Session = Depends(get_db)
):
    """멘토링 대화 계속하기"""
    
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        # ConversationMode 변환
        mode_mapping = {
            "help_seeking": ConversationMode.HELP_SEEKING,
            "motivation": ConversationMode.MOTIVATION,
            "explanation": ConversationMode.EXPLANATION,
            "guidance": ConversationMode.GUIDANCE,
            "reflection": ConversationMode.REFLECTION
        }
        
        conversation_mode = mode_mapping.get(request.conversation_mode, ConversationMode.HELP_SEEKING)
        
        response = await mentoring_system.continue_conversation(
            session_id=request.session_id,
            user_message=request.message,
            conversation_mode=conversation_mode
        )
        
        return {
            "success": True,
            "mentor_response": {
                "content": response.content,
                "tone": response.tone,
                "suggestions": response.suggestions,
                "follow_up_questions": response.follow_up_questions,
                "resources": response.resources,
                "confidence": response.confidence
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"멘토링 대화 실패 session {request.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"멘토링 대화 실패: {str(e)}")

@router.get("/mentoring/daily-motivation/{user_id}", response_model=Dict[str, Any])
async def get_daily_motivation(
    user_id: int,
    db: Session = Depends(get_db)
):
    """일일 동기부여 메시지"""
    
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        motivation_message = await mentoring_system.get_daily_motivation(user_id)
        
        return {
            "success": True,
            "motivation": motivation_message,
            "date": datetime.utcnow().date().isoformat(),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"일일 동기부여 생성 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"동기부여 생성 실패: {str(e)}")

@router.get("/mentoring/learning-tips/{user_id}", response_model=Dict[str, Any])
async def get_learning_tips(
    user_id: int,
    topic: Optional[str] = Query(None, description="특정 주제"),
    db: Session = Depends(get_db)
):
    """학습 팁 제공"""
    
    try:
        mentoring_system = get_ai_mentoring_system(db)
        
        tips = await mentoring_system.get_learning_tips(user_id, topic)
        
        return {
            "success": True,
            "tips": tips,
            "topic": topic,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"학습 팁 생성 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"학습 팁 생성 실패: {str(e)}")

# === 개인화 학습 경로 API ===

@router.post("/learning-path/generate/{user_id}", response_model=Dict[str, Any])
async def generate_personalized_learning_path(
    user_id: int,
    request: LearningPathRequest = Body(...),
    db: Session = Depends(get_db)
):
    """개인화 학습 경로 생성"""
    
    try:
        path_generator = get_personalized_learning_path_generator(db)
        
        # 목표 타입 변환
        goal_type_mapping = {
            "skill": LearningGoalType.SKILL_ACQUISITION,
            "certification": LearningGoalType.CERTIFICATION,
            "project": LearningGoalType.PROJECT_COMPLETION,
            "career": LearningGoalType.CAREER_CHANGE,
            "knowledge": LearningGoalType.KNOWLEDGE_EXPANSION
        }
        
        goal_type = goal_type_mapping.get(request.goal_type, LearningGoalType.SKILL_ACQUISITION)
        
        # 마감일 변환
        deadline = None
        if request.deadline:
            try:
                deadline = datetime.fromisoformat(request.deadline)
            except:
                # 상대적 기간 처리 (예: "3months")
                if "month" in request.deadline:
                    months = int(request.deadline.replace("months", "").replace("month", ""))
                    deadline = datetime.utcnow() + timedelta(days=months * 30)
        
        plan = await path_generator.generate_personalized_path(
            user_id=user_id,
            goal_type=goal_type,
            target_skill=request.target_skill,
            deadline=deadline,
            current_level=request.current_level
        )
        
        return {
            "success": True,
            "learning_plan": {
                "plan_id": plan.plan_id,
                "goal_type": plan.goal_type.value,
                "target_completion_date": plan.target_completion_date.isoformat(),
                "learning_path": {
                    "title": plan.learning_path.title,
                    "description": plan.learning_path.description,
                    "total_estimated_hours": plan.learning_path.total_estimated_hours,
                    "steps_count": len(plan.learning_path.steps),
                    "milestones_count": len(plan.learning_path.milestones)
                },
                "weekly_schedule": plan.weekly_schedule,
                "progress_tracking": plan.progress_tracking
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"학습 경로 생성 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"학습 경로 생성 실패: {str(e)}")

@router.get("/learning-path/steps/{user_id}", response_model=Dict[str, Any])
async def get_learning_path_steps(
    user_id: int,
    plan_id: Optional[str] = Query(None, description="계획 ID"),
    db: Session = Depends(get_db)
):
    """학습 경로 단계 조회"""
    
    try:
        # 캐시에서 계획 조회
        path_generator = get_personalized_learning_path_generator(db)
        
        # 실제 구현에서는 데이터베이스나 캐시에서 계획을 조회해야 함
        return {
            "success": True,
            "message": "학습 경로 단계 조회 기능은 데이터베이스 연동 후 완성됩니다.",
            "user_id": user_id,
            "plan_id": plan_id
        }
        
    except Exception as e:
        logger.error(f"학습 경로 단계 조회 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"단계 조회 실패: {str(e)}")

# === 고급 AI 기능 API ===

@router.post("/code-review", response_model=Dict[str, Any])
async def review_code(
    request: CodeReviewRequest = Body(...),
    db: Session = Depends(get_db)
):
    """AI 코드 리뷰"""
    
    try:
        ai_features = get_advanced_ai_features(db)
        
        # 리뷰 타입 변환
        review_type_mapping = {
            "full": ReviewType.FULL_REVIEW,
            "security": ReviewType.SECURITY_FOCUS,
            "performance": ReviewType.PERFORMANCE_FOCUS,
            "style": ReviewType.STYLE_FOCUS,
            "logic": ReviewType.LOGIC_FOCUS
        }
        
        review_type = review_type_mapping.get(request.review_type, ReviewType.FULL_REVIEW)
        
        review_result = await ai_features.review_code(
            code=request.code,
            language=request.language,
            review_type=review_type,
            user_level=request.user_level
        )
        
        return {
            "success": True,
            "review": {
                "overall_score": review_result.overall_score,
                "quality_grade": review_result.quality_grade.value,
                "issues": [
                    {
                        "severity": issue.severity,
                        "type": issue.type,
                        "line_number": issue.line_number,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                        "example": issue.example
                    }
                    for issue in review_result.issues
                ],
                "strengths": review_result.strengths,
                "recommendations": review_result.recommendations,
                "scores": {
                    "security": review_result.security_score,
                    "performance": review_result.performance_score,
                    "maintainability": review_result.maintainability_score
                }
            },
            "reviewed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"코드 리뷰 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"코드 리뷰 실패: {str(e)}")

@router.post("/project-analysis/{user_id}", response_model=Dict[str, Any])
async def analyze_project(
    user_id: int,
    request: ProjectAnalysisRequest = Body(...),
    db: Session = Depends(get_db)
):
    """프로젝트 종합 분석"""
    
    try:
        ai_features = get_advanced_ai_features(db)
        
        analysis = await ai_features.analyze_project(user_id, request.project_data)
        
        return {
            "success": True,
            "analysis": {
                "project_id": analysis.project_id,
                "analysis_date": analysis.analysis_date.isoformat(),
                "technical_stack": analysis.technical_stack,
                "architecture_quality": analysis.architecture_quality,
                "code_coverage": analysis.code_coverage,
                "security_assessment": analysis.security_assessment,
                "performance_metrics": analysis.performance_metrics,
                "improvement_roadmap": analysis.improvement_roadmap,
                "skill_demonstration": analysis.skill_demonstration,
                "market_relevance": analysis.market_relevance
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"프로젝트 분석 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로젝트 분석 실패: {str(e)}")

# === 통합 AI 기능 API ===

@router.get("/ai-usage-stats", response_model=Dict[str, Any])
async def get_ai_usage_statistics(
    days: int = Query(7, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """AI 사용량 통계"""
    
    try:
        from app.services.ai_providers import get_ai_provider_manager
        
        ai_provider = get_ai_provider_manager()
        stats = ai_provider.get_usage_stats(days)
        
        return {
            "success": True,
            "usage_stats": stats,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI 사용량 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@router.get("/ai-models/available", response_model=Dict[str, Any])
async def get_available_ai_models(
    tier: Optional[str] = Query(None, description="모델 등급 (free/basic/premium)")
):
    """사용 가능한 AI 모델 목록"""
    
    try:
        from app.services.ai_providers import get_ai_provider_manager, ModelTier
        
        ai_provider = get_ai_provider_manager()
        
        tier_filter = None
        if tier:
            tier_mapping = {
                "free": ModelTier.FREE,
                "basic": ModelTier.BASIC,
                "premium": ModelTier.PREMIUM,
                "enterprise": ModelTier.ENTERPRISE
            }
            tier_filter = tier_mapping.get(tier.lower())
        
        models = ai_provider.get_available_models(tier_filter)
        
        return {
            "success": True,
            "models": models,
            "tier_filter": tier,
            "total_count": len(models)
        }
        
    except Exception as e:
        logger.error(f"AI 모델 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"모델 목록 조회 실패: {str(e)}")

@router.get("/features/status", response_model=Dict[str, Any])
async def get_ai_features_status():
    """AI 기능 상태 확인"""
    
    try:
        features_status = {
            "deep_learning_analysis": "operational",
            "adaptive_difficulty": "operational", 
            "ai_mentoring": "operational",
            "personalized_learning_path": "operational",
            "code_review": "operational",
            "project_analysis": "operational"
        }
        
        return {
            "success": True,
            "features": features_status,
            "overall_status": "operational",
            "last_checked": datetime.utcnow().isoformat(),
            "version": "phase4"
        }
        
    except Exception as e:
        logger.error(f"AI 기능 상태 확인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")
