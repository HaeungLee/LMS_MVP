"""
MVP API: 온보딩 & 일일 학습
Goal-based curriculum + Daily learning endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User
from app.services.goal_based_curriculum_service import (
    get_goal_based_curriculum_service,
    GoalBasedCurriculumService
)
from app.services.daily_learning_service import (
    get_daily_learning_service,
    DailyLearningService
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/mvp", tags=["MVP"])


# ============= Request/Response 모델 =============

class GoalSelectionRequest(BaseModel):
    """목표 선택 요청"""
    goal_key: str = Field(..., description="목표 키 (backend_developer, data_analyst, custom)")
    current_level: str = Field(default="Python 기초 완료", description="현재 수준")
    target_weeks: Optional[int] = Field(None, description="목표 주차 (None이면 기본값)")
    daily_study_minutes: int = Field(default=60, description="일일 학습 시간 (분)")
    custom_goal: Optional[str] = Field(None, description="직접 입력한 목표 (goal_key가 'custom'일 때)")


class CurriculumResponse(BaseModel):
    """커리큘럼 생성 응답"""
    curriculum_id: int
    goal: str
    description: str
    total_weeks: int
    daily_minutes: int
    core_technologies: List[str]
    weekly_themes: List[Dict[str, Any]]


class DailyLearningResponse(BaseModel):
    """일일 학습 응답"""
    date: str
    week: int
    day: int
    theme: str
    task: str
    deliverable: str
    learning_objectives: List[str]
    study_time_minutes: int
    status: str
    sections: Dict[str, Any]
    progress: Dict[str, Any]


class PracticeSubmitRequest(BaseModel):
    """실습 제출 요청"""
    curriculum_id: int
    problem_id: Optional[int] = None
    code: str


class QuizAnswerRequest(BaseModel):
    """퀴즈 답변 요청"""
    curriculum_id: int
    question_id: int
    answer: str


# ============= 온보딩 API =============

@router.get("/onboarding/goals")
async def get_available_goals() -> List[Dict[str, Any]]:
    """
    사용 가능한 목표 목록 조회
    
    온보딩 Step 2에서 사용 (인증 불필요)
    """
    try:
        # 하드코딩된 목표 목록 (언어 중립적, 다양한 직무)
        goals = [
            {
                "key": "backend_developer",
                "title": "백엔드 개발자",
                "description": "서버 개발 및 RESTful API 구축 전문가",
                "icon": "💻",
                "color": "from-blue-500 to-indigo-600",
                "defaultWeeks": 12,
                "technologies": ["서버 개발", "API 설계", "데이터베이스", "인증/보안"]
            },
            {
                "key": "frontend_developer",
                "title": "프론트엔드 개발자",
                "description": "웹 UI/UX 개발 및 사용자 인터랙션 구현",
                "icon": "🎨",
                "color": "from-pink-500 to-rose-600",
                "defaultWeeks": 12,
                "technologies": ["웹 개발", "UI 구현", "반응형 디자인", "상태 관리"]
            },
            {
                "key": "data_analyst",
                "title": "데이터 분석가",
                "description": "데이터 수집, 분석 및 인사이트 도출",
                "icon": "📊",
                "color": "from-green-500 to-emerald-600",
                "defaultWeeks": 10,
                "technologies": ["데이터 분석", "통계", "시각화", "SQL"]
            },
            {
                "key": "mobile_developer",
                "title": "모바일 개발자",
                "description": "iOS/Android 네이티브 및 크로스플랫폼 앱 개발",
                "icon": "📱",
                "color": "from-cyan-500 to-blue-600",
                "defaultWeeks": 14,
                "technologies": ["모바일 앱", "UI/UX", "네이티브 기능", "앱 배포"]
            },
            {
                "key": "devops_engineer",
                "title": "DevOps 엔지니어",
                "description": "CI/CD 파이프라인 구축 및 인프라 자동화",
                "icon": "⚙️",
                "color": "from-orange-500 to-amber-600",
                "defaultWeeks": 12,
                "technologies": ["CI/CD", "클라우드", "컨테이너", "모니터링"]
            },
            {
                "key": "ai_engineer",
                "title": "AI 엔지니어",
                "description": "머신러닝 모델 개발 및 프로덕션 배포",
                "icon": "🤖",
                "color": "from-purple-500 to-pink-600",
                "defaultWeeks": 16,
                "technologies": ["머신러닝", "딥러닝", "모델 배포", "MLOps"]
            }
        ]
        return goals
    except Exception as e:
        logger.error(f"목표 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"목표 목록을 불러올 수 없습니다: {str(e)}")


@router.post("/onboarding/generate-curriculum")
async def generate_curriculum(
    request: GoalSelectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GoalBasedCurriculumService = Depends(get_goal_based_curriculum_service)
) -> CurriculumResponse:
    """
    목표 기반 커리큘럼 생성
    
    온보딩 Step 3에서 사용
    AI가 2-Agent 협력으로 12주 커리큘럼 생성 (30초 소요)
    커스텀 목표 지원: goal_key가 'custom'이면 custom_goal 내용 사용
    """
    try:
        # 커스텀 목표 처리
        if request.goal_key == 'custom':
            if not request.custom_goal:
                raise HTTPException(
                    status_code=400, 
                    detail="커스텀 목표를 입력해주세요 (custom_goal 필드 필요)"
                )
            
            # 커스텀 목표를 goal_key로 변환 (임시)
            # 실제로는 LLM이 분석하여 적절한 커리큘럼 생성
            logger.info(f"커스텀 목표 요청: {request.custom_goal}")
            
            # 키워드 기반 매핑 (7개 목표 모두 지원)
            custom_goal_lower = request.custom_goal.lower()
            if 'backend' in custom_goal_lower or 'api' in custom_goal_lower or 'fastapi' in custom_goal_lower or '서버' in custom_goal_lower:
                actual_goal_key = 'backend_developer'
            elif 'frontend' in custom_goal_lower or 'react' in custom_goal_lower or 'vue' in custom_goal_lower or 'web' in custom_goal_lower or 'ui' in custom_goal_lower:
                actual_goal_key = 'frontend_developer'
            elif 'mobile' in custom_goal_lower or 'ios' in custom_goal_lower or 'android' in custom_goal_lower or '앱' in custom_goal_lower:
                actual_goal_key = 'mobile_developer'
            elif 'devops' in custom_goal_lower or 'docker' in custom_goal_lower or 'kubernetes' in custom_goal_lower or 'linux' in custom_goal_lower or '인프라' in custom_goal_lower:
                actual_goal_key = 'devops_engineer'
            elif 'ai' in custom_goal_lower or 'ml' in custom_goal_lower or 'machine learning' in custom_goal_lower or '머신러닝' in custom_goal_lower or '딥러닝' in custom_goal_lower:
                actual_goal_key = 'ai_engineer'
            elif 'data' in custom_goal_lower or '분석' in custom_goal_lower or 'pandas' in custom_goal_lower or 'sql' in custom_goal_lower:
                actual_goal_key = 'data_analyst'
            elif '자동화' in custom_goal_lower or 'automation' in custom_goal_lower or '크롤링' in custom_goal_lower or 'selenium' in custom_goal_lower:
                actual_goal_key = 'automation_engineer'
            else:
                # 기본값: 백엔드 개발자
                actual_goal_key = 'backend_developer'
            
            logger.info(f"커스텀 목표 '{request.custom_goal}' → '{actual_goal_key}'로 매핑")
        else:
            actual_goal_key = request.goal_key
        
        curriculum = await service.generate_goal_based_curriculum(
            user_id=current_user.id,
            goal_key=actual_goal_key,
            current_level=request.current_level,
            target_weeks=request.target_weeks,
            daily_study_minutes=request.daily_study_minutes,
            db=db
        )
        
        return CurriculumResponse(**curriculum)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/curricula/my")
async def get_my_curricula(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GoalBasedCurriculumService = Depends(get_goal_based_curriculum_service)
) -> List[Dict[str, Any]]:
    """
    내 커리큘럼 목록 조회
    """
    try:
        curricula = service.get_user_curricula(current_user.id, db)
        return curricula
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/curricula/{curriculum_id}")
async def get_curriculum(
    curriculum_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: GoalBasedCurriculumService = Depends(get_goal_based_curriculum_service)
) -> Dict[str, Any]:
    """
    특정 커리큘럼 조회
    """
    try:
        curriculum = service.get_curriculum_by_id(curriculum_id, db)
        if not curriculum:
            raise HTTPException(status_code=404, detail="커리큘럼을 찾을 수 없습니다")
        return curriculum
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= 일일 학습 API =============

@router.get("/daily-learning")
async def get_today_learning(
    curriculum_id: int,
    target_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: DailyLearningService = Depends(get_daily_learning_service)
) -> DailyLearningResponse:
    """
    오늘의 학습 조회
    
    대시보드에서 사용
    교과서 + 실습 + 퀴즈 3단계 제공
    """
    try:
        # 날짜 파싱
        date = None
        if target_date:
            date = datetime.fromisoformat(target_date)
        
        learning = await service.get_today_learning(
            user_id=current_user.id,
            curriculum_id=curriculum_id,
            target_date=date,
            db=db
        )
        
        return DailyLearningResponse(**learning)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/practice/submit")
async def submit_practice(
    request: PracticeSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: DailyLearningService = Depends(get_daily_learning_service)
) -> Dict[str, Any]:
    """
    실습 코드 제출
    
    학습 페이지 - 실습 탭에서 사용
    """
    try:
        result = await service.submit_practice(
            user_id=current_user.id,
            curriculum_id=request.curriculum_id,
            problem_id=request.problem_id,
            code=request.code,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quiz/submit")
async def submit_quiz_answer(
    request: QuizAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: DailyLearningService = Depends(get_daily_learning_service)
) -> Dict[str, Any]:
    """
    퀴즈 답변 제출
    
    학습 페이지 - 퀴즈 탭에서 사용
    """
    try:
        result = await service.submit_quiz_answer(
            user_id=current_user.id,
            curriculum_id=request.curriculum_id,
            question_id=request.question_id,
            answer=request.answer,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= 헬스 체크 =============

@router.get("/health")
async def health_check():
    """MVP API 상태 확인"""
    return {
        "status": "healthy",
        "service": "MVP Learning Platform",
        "version": "1.0.0",
        "endpoints": {
            "onboarding": "/api/v1/mvp/onboarding/goals",
            "curriculum": "/api/v1/mvp/onboarding/generate-curriculum",
            "daily_learning": "/api/v1/mvp/daily-learning"
        }
    }
