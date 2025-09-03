"""
EduGPT 통합을 위한 하이브리드 AI API 엔드포인트
Phase 9: AI 제공자 테스트 및 모니터링
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

from app.services.hybrid_ai_provider import (
    get_hybrid_ai_provider,
    check_ai_availability,
    get_recommended_settings,
    generate_curriculum,
    generate_teaching_response,
    log_ai_usage
)

router = APIRouter(prefix="/api/v1/hybrid-ai", tags=["Hybrid AI"])

class CurriculumRequest(BaseModel):
    subject: str
    level: str
    weeks: int = 12

class TeachingRequest(BaseModel):
    context: str
    student_question: str

class AITestRequest(BaseModel):
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7

@router.get("/status", summary="AI 제공자 상태 확인")
async def get_ai_status() -> Dict[str, Any]:
    """
    현재 사용 중인 AI 제공자 상태와 설정 정보 확인
    """
    try:
        availability = check_ai_availability()
        settings = get_recommended_settings()
        
        if availability["available"]:
            provider = get_hybrid_ai_provider()
            provider_info = provider.get_provider_info()
            
            return {
                "status": "success",
                "ai_provider": {
                    "provider": provider_info["provider"],
                    "model": provider_info["model"],
                    "is_free": provider_info["is_free"],
                    "cost_optimized": provider_info["cost_optimization"]
                },
                "recommended_settings": settings,
                "availability": availability
            }
        else:
            return {
                "status": "error",
                "error": availability["error"],
                "availability": availability
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 상태 확인 실패: {str(e)}")

@router.post("/test", summary="AI 제공자 테스트")
async def test_ai_provider(request: AITestRequest) -> Dict[str, Any]:
    """
    현재 AI 제공자로 간단한 텍스트 생성 테스트
    """
    try:
        provider = get_hybrid_ai_provider()
        
        # AI 응답 생성
        response = provider.generate_text(
            request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 사용량 로깅
        log_ai_usage("test_generation", len(response.split()))
        
        provider_info = provider.get_provider_info()
        
        return {
            "status": "success",
            "response": response,
            "provider_info": provider_info,
            "request_params": {
                "prompt": request.prompt[:100] + "..." if len(request.prompt) > 100 else request.prompt,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 테스트 실패: {str(e)}")

@router.post("/curriculum", summary="커리큘럼 생성 (EduGPT 통합)")
async def create_curriculum(request: CurriculumRequest) -> Dict[str, Any]:
    """
    EduGPT 스타일 커리큘럼 생성
    """
    try:
        # 커리큘럼 생성
        curriculum = generate_curriculum(
            subject=request.subject,
            level=request.level,
            weeks=request.weeks
        )
        
        log_ai_usage("curriculum_generation", len(curriculum.split()))
        
        provider = get_hybrid_ai_provider()
        provider_info = provider.get_provider_info()
        
        return {
            "status": "success",
            "curriculum": curriculum,
            "subject": request.subject,
            "level": request.level,
            "weeks": request.weeks,
            "provider_info": provider_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커리큘럼 생성 실패: {str(e)}")

@router.post("/teaching", summary="교수 응답 생성 (EduGPT 티칭 에이전트)")
async def create_teaching_response(request: TeachingRequest) -> Dict[str, Any]:
    """
    EduGPT 티칭 에이전트 스타일 응답 생성
    """
    try:
        # 교수 응답 생성
        response = generate_teaching_response(
            context=request.context,
            student_question=request.student_question
        )
        
        log_ai_usage("teaching_response", len(response.split()))
        
        provider = get_hybrid_ai_provider()
        provider_info = provider.get_provider_info()
        
        return {
            "status": "success",
            "teaching_response": response,
            "context": request.context[:200] + "..." if len(request.context) > 200 else request.context,
            "student_question": request.student_question,
            "provider_info": provider_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교수 응답 생성 실패: {str(e)}")

@router.get("/cost-estimate", summary="AI 사용 비용 추정")
async def estimate_costs() -> Dict[str, Any]:
    """
    AI 제공자별 비용 추정 정보
    """
    try:
        provider = get_hybrid_ai_provider()
        provider_info = provider.get_provider_info()
        
        # 예시 토큰 사용량으로 비용 추정
        test_cases = [
            {"input_tokens": 100, "output_tokens": 500, "scenario": "간단한 질문-답변"},
            {"input_tokens": 500, "output_tokens": 1500, "scenario": "커리큘럼 생성"},
            {"input_tokens": 1000, "output_tokens": 2000, "scenario": "장문 교육 콘텐츠"}
        ]
        
        cost_estimates = []
        for case in test_cases:
            cost = provider.estimate_cost(case["input_tokens"], case["output_tokens"])
            cost_estimates.append({
                "scenario": case["scenario"],
                "input_tokens": case["input_tokens"],
                "output_tokens": case["output_tokens"],
                "estimated_cost_usd": cost,
                "estimated_cost_krw": cost * 1300  # 대략적인 환율
            })
        
        return {
            "status": "success",
            "provider_info": provider_info,
            "cost_estimates": cost_estimates,
            "notes": {
                "free_model": provider_info["is_free"],
                "cost_optimization": provider_info["cost_optimization"],
                "provider": provider_info["provider"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"비용 추정 실패: {str(e)}")

@router.get("/settings", summary="권장 설정 조회")
async def get_ai_settings() -> Dict[str, Any]:
    """
    현재 AI 제공자에 맞는 권장 설정 조회
    """
    try:
        settings = get_recommended_settings()
        provider = get_hybrid_ai_provider()
        provider_info = provider.get_provider_info()
        
        return {
            "status": "success",
            "provider_info": provider_info,
            "recommended_settings": settings,
            "usage_guidelines": {
                "curriculum_generation": "과목별 체계적인 커리큘럼 생성에 최적화",
                "teaching_agent": "학생 질문에 대한 교육적 응답에 최적화",
                "cost_optimization": "무료/저비용 모델 사용 시 토큰 제한 고려"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 조회 실패: {str(e)}")
