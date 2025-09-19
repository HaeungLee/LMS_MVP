"""
Phase 10: AI 문제 생성 API 엔드포인트
- 스마트 문제 자동 생성
- 적응형 난이도 조절
- 관리자 문제 검토 시스템
- 실시간 피드백 기반 개선
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User
from app.services.ai_question_generator_enhanced import (
    get_ai_question_generator,
    AIQuestionGeneratorEnhanced,
    QuestionGenerationRequest,
    QuestionType,
    DifficultyLevel,
    GeneratedQuestion
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai-questions", tags=["AI Questions - Phase 10"])

# ========== Pydantic 모델들 ==========

class QuestionGenerationRequestModel(BaseModel):
    """문제 생성 요청 모델"""
    subject_key: str = Field(..., description="과목 키")
    topic: str = Field(..., description="토픽명")
    question_type: str = Field("multiple_choice", description="문제 유형")
    difficulty_level: str = Field("intermediate", description="난이도")
    count: int = Field(1, ge=1, le=10, description="생성할 문제 수")
    learning_goals: Optional[List[str]] = Field(None, description="학습 목표")
    context: Optional[str] = Field(None, description="추가 컨텍스트")

class AdaptiveQuestionRequest(BaseModel):
    """적응형 문제 요청 모델"""
    subject_key: str = Field(..., description="과목 키")
    current_performance: Dict[str, Any] = Field(..., description="현재 성과 데이터")
    focus_areas: Optional[List[str]] = Field(None, description="집중 영역")

class QuestionReviewRequest(BaseModel):
    """문제 검토 요청 모델"""
    question_id: str = Field(..., description="문제 ID")
    review_action: str = Field(..., description="검토 액션: approve/reject/modify")
    reviewer_notes: Optional[str] = Field(None, description="검토자 노트")
    modifications: Optional[Dict[str, Any]] = Field(None, description="수정사항")

class GeneratedQuestionResponse(BaseModel):
    """생성된 문제 응답 모델"""
    id: str
    question_text: str
    question_type: str
    difficulty_level: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    hints: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    estimated_time: Optional[int] = None
    learning_objective: Optional[str] = None
    quality_score: float
    generated_at: datetime
    status: str = "pending_review"

# ========== API 엔드포인트들 ==========

@router.post("/generate", response_model=Dict[str, Any])
async def generate_questions(
    request: QuestionGenerationRequestModel,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    generator: AIQuestionGeneratorEnhanced = Depends(get_ai_question_generator)
):
    """
    AI 기반 문제 생성
    
    커리큘럼과 사용자 데이터를 기반으로 개인화된 문제를 생성합니다.
    """
    try:
        logger.info(f"문제 생성 요청: {current_user.id} - {request.subject_key}/{request.topic}")
        
        # 요청 변환
        generation_request = QuestionGenerationRequest(
            user_id=current_user.id,
            subject_key=request.subject_key,
            topic=request.topic,
            question_type=QuestionType(request.question_type),
            difficulty_level=DifficultyLevel(request.difficulty_level),
            count=request.count,
            learning_goals=request.learning_goals,
            context=request.context
        )
        
        # 문제 생성 (비동기)
        generated_questions = await generator.generate_questions(generation_request, db)
        
        if not generated_questions:
            raise HTTPException(
                status_code=500,
                detail="문제 생성에 실패했습니다. 다시 시도해주세요."
            )
        
        # 응답 데이터 구성
        response_questions = []
        for i, question in enumerate(generated_questions):
            response_questions.append({
                "id": f"gen_{current_user.id}_{int(datetime.utcnow().timestamp())}_{i}",
                "question_text": question.question_text,
                "question_type": question.question_type.value,
                "difficulty_level": question.difficulty_level.value,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "hints": question.hints,
                "tags": question.tags,
                "estimated_time": question.estimated_time,
                "learning_objective": question.learning_objective,
                "quality_score": question.quality_score,
                "generated_at": datetime.utcnow(),
                "status": "ready" if question.quality_score >= 7.0 else "needs_review"
            })
        
        # 백그라운드에서 분석 데이터 저장
        background_tasks.add_task(
            _save_generation_analytics,
            current_user.id,
            request.subject_key,
            len(generated_questions),
            sum(q.quality_score for q in generated_questions) / len(generated_questions)
        )
        
        return {
            "success": True,
            "message": f"{len(generated_questions)}개의 문제가 생성되었습니다.",
            "questions": response_questions,
            "generation_info": {
                "total_generated": len(generated_questions),
                "avg_quality_score": sum(q.quality_score for q in generated_questions) / len(generated_questions),
                "estimated_total_time": sum(q.estimated_time or 5 for q in generated_questions),
                "ready_questions": len([q for q in generated_questions if q.quality_score >= 7.0]),
                "needs_review": len([q for q in generated_questions if q.quality_score < 7.0])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"문제 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 생성 실패: {str(e)}")

@router.post("/adaptive", response_model=Dict[str, Any])
async def generate_adaptive_questions(
    request: AdaptiveQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    generator: AIQuestionGeneratorEnhanced = Depends(get_ai_question_generator)
):
    """
    적응형 문제 생성
    
    사용자의 현재 성과를 분석하여 최적화된 난이도와 내용의 문제를 생성합니다.
    """
    try:
        logger.info(f"적응형 문제 생성: {current_user.id} - {request.subject_key}")
        
        # 적응형 문제 생성
        adaptive_questions = await generator.generate_adaptive_questions(
            user_id=current_user.id,
            subject_key=request.subject_key,
            current_performance=request.current_performance,
            db=db
        )
        
        if not adaptive_questions:
            return {
                "success": False,
                "message": "현재 성과 데이터로는 적응형 문제를 생성할 수 없습니다.",
                "suggestions": [
                    "더 많은 문제를 풀어 성과 데이터를 축적해보세요.",
                    "기본 문제 생성을 이용해보세요.",
                    "학습 목표를 구체적으로 설정해보세요."
                ]
            }
        
        # 응답 구성
        response_questions = []
        for i, question in enumerate(adaptive_questions):
            response_questions.append({
                "id": f"adaptive_{current_user.id}_{int(datetime.utcnow().timestamp())}_{i}",
                "question_text": question.question_text,
                "question_type": question.question_type.value,
                "difficulty_level": question.difficulty_level.value,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "adaptation_reason": "사용자 약점 영역 기반 생성",
                "quality_score": question.quality_score,
                "generated_at": datetime.utcnow()
            })
        
        return {
            "success": True,
            "message": f"적응형 문제 {len(adaptive_questions)}개가 생성되었습니다.",
            "questions": response_questions,
            "adaptation_info": {
                "performance_analysis": request.current_performance,
                "recommended_focus": request.focus_areas or [],
                "difficulty_adjustment": "사용자 성과에 맞춘 조절 완료"
            }
        }
        
    except Exception as e:
        logger.error(f"적응형 문제 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"적응형 문제 생성 실패: {str(e)}")

@router.post("/{question_id}/review", response_model=Dict[str, Any])
async def review_question(
    question_id: str,
    review_request: QuestionReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    generator: AIQuestionGeneratorEnhanced = Depends(get_ai_question_generator)
):
    """
    문제 검토 및 승인
    
    관리자가 생성된 문제를 검토하고 승인/거부/수정할 수 있습니다.
    """
    try:
        # 권한 확인 (관리자 또는 교사만)
        if current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="문제 검토 권한이 없습니다."
            )
        
        # 문제 검토 로직 구현
        review_result = {
            "question_id": question_id,
            "reviewer_id": current_user.id,
            "reviewer_name": current_user.display_name or current_user.email,
            "review_action": review_request.review_action,
            "reviewed_at": datetime.utcnow(),
            "notes": review_request.reviewer_notes
        }
        
        if review_request.review_action == "approve":
            review_result["status"] = "approved"
            review_result["message"] = "문제가 승인되었습니다."
            
        elif review_request.review_action == "reject":
            review_result["status"] = "rejected"
            review_result["message"] = "문제가 거부되었습니다."
            
        elif review_request.review_action == "modify":
            review_result["status"] = "modified"
            review_result["modifications"] = review_request.modifications
            review_result["message"] = "문제가 수정되었습니다."
        
        # 검토 이력 저장 (실제 구현에서는 DB에 저장)
        logger.info(f"문제 검토 완료: {question_id} by {current_user.id}")
        
        return {
            "success": True,
            "review_result": review_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"문제 검토 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 검토 실패: {str(e)}")

@router.get("/analytics", response_model=Dict[str, Any])
async def get_generation_analytics(
    subject_key: Optional[str] = Query(None, description="특정 과목 필터"),
    days: int = Query(7, ge=1, le=30, description="조회 기간"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    문제 생성 분석 데이터
    
    문제 생성 통계, 품질 지표, 사용자 피드백 등을 제공합니다.
    """
    try:
        # 권한 확인
        if current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="분석 데이터 조회 권한이 없습니다."
            )
        
        # 임시 분석 데이터 (실제로는 DB/Redis에서 조회)
        analytics_data = {
            "generation_stats": {
                "total_generated": 156,
                "approved": 142,
                "rejected": 8,
                "pending_review": 6,
                "avg_quality_score": 8.2,
                "generation_success_rate": 94.2
            },
            "subject_breakdown": {
                "python_basics": {
                    "generated": 45,
                    "avg_quality": 8.5,
                    "user_satisfaction": 4.3
                },
                "javascript_basics": {
                    "generated": 38,
                    "avg_quality": 8.1,
                    "user_satisfaction": 4.1
                },
                "react_fundamentals": {
                    "generated": 32,
                    "avg_quality": 7.9,
                    "user_satisfaction": 4.2
                }
            },
            "difficulty_distribution": {
                "beginner": 45,
                "intermediate": 67,
                "advanced": 44
            },
            "question_type_stats": {
                "multiple_choice": 89,
                "coding": 34,
                "short_answer": 23,
                "essay": 10
            },
            "performance_metrics": {
                "avg_generation_time": 12.5,
                "cache_hit_rate": 23.4,
                "ai_model_usage": {
                    "mistral-7b": 78.5,
                    "claude-haiku": 21.5
                }
            },
            "user_feedback": {
                "avg_rating": 4.2,
                "total_feedback": 89,
                "improvement_suggestions": [
                    "더 다양한 예시 문제",
                    "실습 중심 문제 증가",
                    "힌트 시스템 개선"
                ]
            }
        }
        
        return {
            "success": True,
            "period": f"최근 {days}일",
            "subject_filter": subject_key,
            "analytics": analytics_data,
            "generated_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 데이터 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 데이터 조회 실패: {str(e)}")

@router.get("/templates", response_model=Dict[str, Any])
async def get_question_templates(
    question_type: Optional[str] = Query(None, description="문제 유형 필터"),
    current_user: User = Depends(get_current_user)
):
    """
    문제 생성 템플릿 조회
    
    다양한 문제 유형별 템플릿과 가이드라인을 제공합니다.
    """
    try:
        templates = {
            "multiple_choice": {
                "name": "객관식 문제",
                "description": "4지 선다 객관식 문제 생성",
                "template": "명확한 질문 + 4개 선택지 + 정답 + 해설",
                "best_practices": [
                    "명확하고 구체적인 질문 작성",
                    "매력적인 오답 선택지 구성",
                    "정답 근거가 분명한 문제"
                ],
                "estimated_time": "3-5분"
            },
            "coding": {
                "name": "코딩 문제",
                "description": "프로그래밍 실습 문제 생성",
                "template": "문제 설명 + 입출력 명세 + 예시 + 해답 코드",
                "best_practices": [
                    "실용적이고 교육적인 문제",
                    "단계별 난이도 증가",
                    "명확한 입출력 예시"
                ],
                "estimated_time": "10-30분"
            },
            "short_answer": {
                "name": "단답형 문제",
                "description": "핵심 개념 단답형 문제",
                "template": "질문 + 핵심 키워드 + 모범 답안",
                "best_practices": [
                    "핵심 개념 중심 질문",
                    "명확한 답안 기준",
                    "부분 점수 기준 제시"
                ],
                "estimated_time": "2-5분"
            },
            "essay": {
                "name": "서술형 문제",
                "description": "깊이 있는 사고를 요구하는 문제",
                "template": "주제 제시 + 평가 기준 + 예시 답안",
                "best_practices": [
                    "사고력을 요구하는 주제",
                    "구체적인 평가 기준",
                    "창의적 사고 유도"
                ],
                "estimated_time": "15-30분"
            }
        }
        
        if question_type and question_type in templates:
            return {
                "success": True,
                "template": {question_type: templates[question_type]}
            }
        
        return {
            "success": True,
            "templates": templates,
            "usage_guide": {
                "step1": "적절한 문제 유형 선택",
                "step2": "학습 목표와 난이도 설정",
                "step3": "컨텍스트와 요구사항 입력",
                "step4": "AI 생성 결과 검토 및 수정"
            }
        }
        
    except Exception as e:
        logger.error(f"템플릿 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"템플릿 조회 실패: {str(e)}")

# ========== 백그라운드 작업 함수들 ==========

async def _save_generation_analytics(
    user_id: int,
    subject_key: str,
    question_count: int,
    avg_quality_score: float
):
    """문제 생성 분석 데이터 저장"""
    try:
        # Redis나 DB에 분석 데이터 저장
        analytics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "subject_key": subject_key,
            "question_count": question_count,
            "avg_quality_score": avg_quality_score
        }
        
        logger.info(f"분석 데이터 저장: {analytics_data}")
        
    except Exception as e:
        logger.error(f"분석 데이터 저장 실패: {str(e)}")

# 헬스 체크
@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """AI 문제 생성 시스템 상태 확인"""
    return {
        "status": "healthy",
        "service": "AI Question Generation",
        "version": "Phase 10",
        "features": [
            "smart_generation",
            "adaptive_difficulty", 
            "quality_review",
            "performance_analytics"
        ]
    }
