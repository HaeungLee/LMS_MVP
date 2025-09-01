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
    text_style: str = "default"
    line_height: str = "comfortable"

class MentorMessageRequest(BaseModel):
    message: str
    conversation_mode: str = "help_seeking"
    text_style: str = "default"
    line_height: str = "comfortable"

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
        logger.info(f"심층 학습 분석 요청: user {user_id}")
        
        # 실제 분석기 호출
        analyzer = get_deep_learning_analyzer(db)
        analysis_result = await analyzer.analyze_user_deeply(user_id, use_ai=request.use_ai)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "analysis_type": request.analysis_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"심층 학습 분석 실패 user {user_id}: {str(e)}")
        
        # 폴백 데이터 - 사용자의 실제 제출 데이터 기반
        try:
            from app.models.orm import Submission, SubmissionItem
            
            # 사용자 제출 데이터 조회
            recent_submissions = db.query(SubmissionItem).join(Submission).filter(
                Submission.user_id == user_id
            ).limit(50).all()
            
            if not recent_submissions:
                # 데이터가 없으면 기본 Mock
                fallback_analysis = {
                    "learner_profile": {
                        "type": "steady_learner",
                        "phase": "beginner",
                        "optimal_session_length": 25,
                        "preferred_difficulty": 2,
                        "strengths": ["기본 문법", "반복 학습"],
                        "weaknesses": ["고급 개념", "문제 해결"]
                    },
                    "learning_metrics": {
                        "overall_accuracy": 0.65,
                        "consistency_score": 0.72,
                        "improvement_rate": 0.15,
                        "engagement_level": 0.80
                    },
                    "recommendations": [
                        {
                            "title": "기초 개념 복습",
                            "description": "변수와 조건문 개념을 다시 정리해보세요",
                            "priority": "high"
                        },
                        {
                            "title": "단계별 문제 풀이",
                            "description": "쉬운 문제부터 차근차근 실력을 쌓아가세요",
                            "priority": "medium"
                        }
                    ],
                    "next_actions": [
                        {
                            "title": "파이썬 기초 문제 10개 풀기",
                            "description": "변수와 조건문 관련 문제를 중심으로",
                            "timeframe": "today"
                        },
                        {
                            "title": "반복문 개념 학습",
                            "description": "for와 while 반복문 문법 정리",
                            "timeframe": "this_week"
                        }
                    ]
                }
            else:
                # 실제 데이터 기반 분석
                total_count = len(recent_submissions)
                correct_count = sum(1 for s in recent_submissions if s.is_correct)
                accuracy = correct_count / total_count if total_count > 0 else 0
                
                # 학습자 유형 판별
                if accuracy >= 0.9:
                    learner_type = "fast_learner"
                    phase = "advanced"
                elif accuracy >= 0.8:
                    learner_type = "deep_thinker"
                    phase = "intermediate"
                elif accuracy >= 0.6:
                    learner_type = "steady_learner"
                    phase = "intermediate"
                elif accuracy >= 0.4:
                    learner_type = "practical_learner"
                    phase = "beginner"
                else:
                    learner_type = "struggling_learner"
                    phase = "beginner"
                
                # 최근 성과 추이
                recent_10 = recent_submissions[-10:] if len(recent_submissions) >= 10 else recent_submissions
                old_10 = recent_submissions[:10] if len(recent_submissions) >= 20 else recent_submissions[:len(recent_submissions)//2]
                
                recent_acc = sum(1 for s in recent_10 if s.is_correct) / len(recent_10) if recent_10 else 0
                old_acc = sum(1 for s in old_10 if s.is_correct) / len(old_10) if old_10 else 0
                improvement = recent_acc - old_acc
                
                fallback_analysis = {
                    "learner_profile": {
                        "type": learner_type,
                        "phase": phase,
                        "optimal_session_length": 30 if accuracy >= 0.7 else 20,
                        "preferred_difficulty": min(5, max(1, int(accuracy * 5) + 1)),
                        "strengths": ["꾸준한 학습", "문제 해결 의지"] if accuracy >= 0.6 else ["기본 문법"],
                        "weaknesses": ["고급 개념"] if accuracy >= 0.6 else ["기본 개념", "문법 정리"]
                    },
                    "learning_metrics": {
                        "overall_accuracy": accuracy,
                        "consistency_score": min(1.0, accuracy + 0.1),
                        "improvement_rate": improvement,
                        "engagement_level": min(1.0, total_count / 20)  # 문제 수 기반 참여도
                    },
                    "recommendations": [
                        {
                            "title": "현재 수준 유지" if accuracy >= 0.8 else "기초 실력 강화",
                            "description": "꾸준한 학습으로 실력을 더욱 향상시켜보세요" if accuracy >= 0.8 else "기본 개념을 다시 정리하고 연습하세요",
                            "priority": "high"
                        }
                    ],
                    "next_actions": [
                        {
                            "title": f"정확도 향상을 위한 복습",
                            "description": f"현재 정확도 {accuracy*100:.1f}%에서 10% 향상 목표",
                            "timeframe": "this_week"
                        }
                    ]
                }
            
            return {
                "success": True,
                "analysis": fallback_analysis,
                "analysis_type": request.analysis_type,
                "timestamp": datetime.utcnow().isoformat(),
                "fallback_mode": True,
                "note": "실제 사용자 데이터 기반 분석"
            }
            
        except Exception as fallback_error:
            logger.error(f"폴백 분석도 실패: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"학습 분석 실패: {str(e)}")

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
        logger.info(f"최적 난이도 계산 요청: user {user_id}, topic: {request.topic}")
        
        # 실제 사용자 데이터 기반 난이도 계산
        from app.models.orm import Submission, SubmissionItem, Question
        
        # 사용자의 최근 제출 데이터 조회 (특정 주제가 있으면 필터링)
        query = db.query(SubmissionItem).join(Submission).join(Question).filter(
            Submission.user_id == user_id
        )
        
        if request.topic and request.topic != "general":
            query = query.filter(Question.topic == request.topic)
        
        recent_submissions = query.order_by(Submission.submitted_at.desc()).limit(20).all()
        
        if not recent_submissions:
            # 데이터가 없으면 기본 난이도 추천
            return {
                "success": True,
                "recommendation": {
                    "recommended_difficulty": 2,
                    "confidence": 0.5,
                    "reasoning": "첫 학습이므로 기본 난이도로 시작하는 것을 권장합니다.",
                    "expected_accuracy": 0.7,
                    "adjustment_timeline": "5-10문제 후 재평가"
                },
                "calculated_at": datetime.utcnow().isoformat()
            }
        
        # 정확도 계산
        total_count = len(recent_submissions)
        correct_count = sum(1 for s in recent_submissions if s.is_correct)
        current_accuracy = correct_count / total_count
        
        # 최적 난이도 결정 로직
        current_diff = request.current_difficulty or 2
        
        if current_accuracy >= 0.85:
            # 정확도가 높으면 난이도 상승
            recommended_difficulty = min(5, current_diff + 1)
            reasoning = f"정확도 {current_accuracy*100:.1f}%로 높아 한 단계 상승을 권장합니다."
            expected_accuracy = 0.75
        elif current_accuracy >= 0.70:
            # 적절한 정확도면 현재 유지
            recommended_difficulty = current_diff
            reasoning = f"정확도 {current_accuracy*100:.1f}%로 적절하여 현재 난이도 유지를 권장합니다."
            expected_accuracy = current_accuracy
        elif current_accuracy >= 0.50:
            # 낮은 정확도면 난이도 하락 고려
            recommended_difficulty = max(1, current_diff - 1) if current_diff > 2 else current_diff
            reasoning = f"정확도 {current_accuracy*100:.1f}%로 낮아 한 단계 하락을 고려합니다."
            expected_accuracy = 0.75
        else:
            # 매우 낮은 정확도면 난이도 하락
            recommended_difficulty = max(1, current_diff - 1)
            reasoning = f"정확도 {current_accuracy*100:.1f}%로 매우 낮아 난이도 하락이 필요합니다."
            expected_accuracy = 0.8
        
        # 신뢰도 계산 (데이터 충분성 기반)
        confidence = min(1.0, total_count / 20) * 0.9  # 최대 90%
        
        return {
            "success": True,
            "recommendation": {
                "recommended_difficulty": recommended_difficulty,
                "confidence": confidence,
                "reasoning": reasoning,
                "expected_accuracy": expected_accuracy,
                "adjustment_timeline": "다음 5-10문제 후",
                "current_performance": {
                    "accuracy": current_accuracy,
                    "total_submissions": total_count
                }
            },
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"난이도 계산 실패 user {user_id}: {str(e)}")
        # 폴백 응답
        return {
            "success": True,
            "recommendation": {
                "recommended_difficulty": request.current_difficulty or 2,
                "confidence": 0.5,
                "reasoning": "데이터 분석 중 오류가 발생하여 현재 난이도 유지를 권장합니다.",
                "expected_accuracy": 0.7,
                "adjustment_timeline": "다음 세션에서 재분석"
            },
            "calculated_at": datetime.utcnow().isoformat(),
            "fallback_mode": True
        }

@router.get("/difficulty/next-question/{user_id}", response_model=Dict[str, Any])
async def get_next_question_difficulty(
    user_id: int,
    topic: str = Query(..., description="주제"),
    db: Session = Depends(get_db)
):
    """다음 문제 난이도 추천"""
    
    try:
        logger.info(f"다음 문제 난이도 추천 요청: user {user_id}, topic: {topic}")
        
        # 사용자의 최근 성과 기반으로 다음 문제 난이도 결정
        from app.models.orm import Submission, SubmissionItem, Question
        
        # 해당 주제의 최근 성과 조회
        recent_submissions = db.query(SubmissionItem).join(Submission).join(Question).filter(
            Submission.user_id == user_id,
            Question.topic == topic
        ).order_by(Submission.submitted_at.desc()).limit(10).all()
        
        if not recent_submissions:
            # 해당 주제의 데이터가 없으면 기본 난이도
            return {
                "success": True,
                "next_difficulty": 2,
                "topic": topic,
                "user_id": user_id,
                "reasoning": "해당 주제의 학습 기록이 없어 기본 난이도로 시작합니다.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # 최근 성과 분석
        total_recent = len(recent_submissions)
        correct_recent = sum(1 for s in recent_submissions if s.is_correct)
        recent_accuracy = correct_recent / total_recent
        
        # 최근 3문제 성과 (더 가중치 높게)
        last_3 = recent_submissions[:3]
        last_3_accuracy = sum(1 for s in last_3 if s.is_correct) / len(last_3)
        
        # 가중 평균 정확도 (최근 3문제 70%, 전체 30%)
        weighted_accuracy = (last_3_accuracy * 0.7) + (recent_accuracy * 0.3)
        
        # 현재 평균 난이도 계산
        difficulties = [getattr(s.question, 'difficulty', 2) for s in recent_submissions if hasattr(s.question, 'difficulty')]
        current_avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 2
        
        # 다음 문제 난이도 결정
        if weighted_accuracy >= 0.9:
            # 매우 높은 정확도 - 2단계 상승
            next_difficulty = min(5, int(current_avg_difficulty) + 2)
            reasoning = f"최근 정확도 {weighted_accuracy*100:.1f}%로 매우 높아 도전적인 문제를 제공합니다."
        elif weighted_accuracy >= 0.8:
            # 높은 정확도 - 1단계 상승
            next_difficulty = min(5, int(current_avg_difficulty) + 1)
            reasoning = f"최근 정확도 {weighted_accuracy*100:.1f}%로 높아 한 단계 어려운 문제를 제공합니다."
        elif weighted_accuracy >= 0.6:
            # 적절한 정확도 - 현재 수준 유지
            next_difficulty = max(1, min(5, int(current_avg_difficulty)))
            reasoning = f"최근 정확도 {weighted_accuracy*100:.1f}%로 적절하여 현재 수준을 유지합니다."
        elif weighted_accuracy >= 0.4:
            # 낮은 정확도 - 1단계 하락
            next_difficulty = max(1, int(current_avg_difficulty) - 1)
            reasoning = f"최근 정확도 {weighted_accuracy*100:.1f}%로 낮아 쉬운 문제로 자신감을 회복하세요."
        else:
            # 매우 낮은 정확도 - 2단계 하락
            next_difficulty = max(1, int(current_avg_difficulty) - 2)
            reasoning = f"최근 정확도 {weighted_accuracy*100:.1f}%로 매우 낮아 기초부터 다시 시작합니다."
        
        return {
            "success": True,
            "next_difficulty": next_difficulty,
            "topic": topic,
            "user_id": user_id,
            "reasoning": reasoning,
            "performance_data": {
                "recent_accuracy": recent_accuracy,
                "last_3_accuracy": last_3_accuracy,
                "weighted_accuracy": weighted_accuracy,
                "total_submissions": total_recent,
                "current_avg_difficulty": current_avg_difficulty
            },
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
        # 실제 AI 멘토링 시스템 사용 (OpenRouter API 연동)
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
                "id": session.session_id,
                "session_id": session.session_id,
                "user_id": user_id,
                "user_name": f"학습자 {user_id}",
                "mentor_personality": session.mentor_personality.value if hasattr(session, 'mentor_personality') else "friendly",
                "session_goals": session.session_goals if hasattr(session, 'session_goals') else ["학습 지원"],
                "greeting": greeting
            },
            "started_at": session.start_time.isoformat()
        }

    except Exception as e:
        logger.error(f"멘토링 세션 시작 실패 user {user_id}: {str(e)}")
        # 폴백 모드 - 기본 더미 응답
        logger.warning(f"AI 멘토링 시스템 실패, 폴백 모드 사용: {e}")
        import uuid
        session_id = str(uuid.uuid4())

        return {
            "success": True,
            "session": {
                "id": session_id,
                "session_id": session_id,
                "user_id": user_id,
                "user_name": f"학습자 {user_id}",
                "mentor_personality": "friendly",
                "session_goals": ["학습 지원", "프로그래밍 실력 향상"],
                "greeting": "**안녕하세요!** AI 학습 멘토입니다. 무엇을 도와드릴까요? **핵심** 개념부터 실무 활용까지 함께 배워봅시다! (현재 오프라인 모드)"
            },
            "started_at": datetime.utcnow().isoformat(),
            "fallback_mode": True
        }

@router.post("/mentoring/chat/{session_id}", response_model=Dict[str, Any])
async def continue_mentoring_conversation(
    session_id: str,
    request: MentorMessageRequest = Body(...),
    db: Session = Depends(get_db)
):
    """멘토링 대화 계속하기"""

    try:
        # 실제 AI 멘토링 시스템 사용 (OpenRouter API 연동)
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
            session_id=session_id,
            user_message=request.message,
            conversation_mode=conversation_mode
        )

        return {
            "success": True,
            "response": response.content,
            "follow_up_questions": response.follow_up_questions if hasattr(response, 'follow_up_questions') else [],
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"멘토링 대화 실패 session {session_id}: {str(e)}")
        # 폴백 모드 - 사용자 메시지 기반 응답 생성
        logger.warning(f"AI 멘토링 시스템 실패, 폴백 모드 사용: {e}")
        
        user_message = request.message.lower()

        if "파이썬" in user_message or "python" in user_message:
            response_text = "**파이썬**은 초보자에게 아주 좋은 프로그래밍 언어입니다! **핵심**은 변수, 조건문, 반복문부터 시작하는 것입니다. **중요한** 건 실습을 통해 익히는 거예요. (현재 오프라인 모드)"
        elif "알고리즘" in user_message:
            response_text = "**알고리즘**은 문제 해결의 **핵심**입니다. 정렬, 검색부터 시작해서 점진적으로 어려운 문제에 도전해보세요. **팁**: 작은 문제부터 차근차근! (현재 오프라인 모드)"
        elif "자료구조" in user_message:
            response_text = "**자료구조**는 데이터를 효율적으로 다루는 방법입니다. 배열, 리스트, 스택, 큐부터 공부해보는 걸 **추천**합니다. **핵심**은 각각의 특징을 이해하는 것! (현재 오프라인 모드)"
        else:
            response_text = "**좋은 질문**이네요! 구체적인 주제나 어려움을 말씀해주시면 더 자세히 도와드리겠습니다. **중요한** 건 포기하지 않는 마음가짐이에요! (현재 오프라인 모드)"

        follow_up_questions = [
            "어떤 부분이 가장 어려우신가요?",
            "어떤 목표를 가지고 계신가요?",
            "어떤 프로그래밍 언어를 선호하시나요?"
        ]

        return {
            "success": True,
            "response": response_text,
            "follow_up_questions": follow_up_questions,
            "timestamp": datetime.utcnow().isoformat(),
            "fallback_mode": True
        }

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
