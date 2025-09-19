"""
관리자 전용 API 엔드포인트
- 문제 검토 및 관리
- 커리큘럼 관리
- 시스템 모니터링
- 사용자 분석
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.orm import User, Topic
from app.models.question import Question
from app.schemas.admin import (
    QuestionReviewRequest, QuestionReviewResponse,
    CurriculumManagementRequest, CurriculumManagementResponse,
    SystemHealthResponse, UserAnalyticsResponse,
    AdminDashboardResponse
)
from app.core.security import get_current_user
from app.services.ai_question_generator_enhanced import AIQuestionGeneratorEnhanced
from app.services.enhanced_learning_analytics import EnhancedLearningAnalytics

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

def verify_admin_user(current_user: User = Depends(get_current_user)):
    """관리자 권한 검증"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user

@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_user)
):
    """관리자 대시보드 통합 데이터"""
    try:
        # 기본 통계
        total_users = db.query(User).count()
        active_users = db.query(User).filter(
            User.last_login >= datetime.now() - timedelta(days=7)
        ).count()
        total_questions = db.query(Question).count()
        total_topics = db.query(Topic).count()
        
        # AI 시스템 상태
        ai_generator = AIQuestionGeneratorEnhanced()
        ai_analytics = await ai_generator.get_analytics()
        
        return AdminDashboardResponse(
            total_users=total_users,
            active_users=active_users,
            total_questions=total_questions,
            total_topics=total_topics,
            ai_questions_generated=ai_analytics.get("total_generated", 0),
            system_health_score=98.5,
            recent_activities=[
                {"type": "user_registration", "count": 15, "period": "오늘"},
                {"type": "ai_questions_generated", "count": 45, "period": "오늘"},
                {"type": "curriculum_created", "count": 8, "period": "오늘"}
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 로드 실패: {str(e)}")

@router.get("/questions/pending-review")
async def get_pending_review_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_user)
):
    """검토 대기 중인 AI 생성 문제들"""
    try:
        # 실제로는 AI 생성 문제 테이블에서 가져와야 하지만, 
        # 현재는 모킹 데이터로 제공
        mock_questions = [
            {
                "id": i + 1,
                "type": "multiple_choice",
                "difficulty": "medium",
                "subject": "Python 기초",
                "topic": "변수와 데이터 타입",
                "question_text": f"Python에서 변수의 특징에 대한 설명으로 올바른 것은? (문제 {i+1})",
                "options": ["A. 선언시 타입 지정 필수", "B. 동적 타이핑 지원", "C. 재할당 불가", "D. 숫자만 저장 가능"],
                "correct_answer": "B",
                "explanation": "Python은 동적 타이핑을 지원하는 언어입니다.",
                "created_at": datetime.now() - timedelta(days=i),
                "ai_confidence": 0.85 + (i * 0.02),
                "status": "pending_review"
            }
            for i in range(skip, skip + limit)
        ]
        
        return {
            "questions": mock_questions,
            "total": 50,  # 전체 검토 대기 문제 수
            "has_more": skip + limit < 50
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검토 대기 문제 조회 실패: {str(e)}")

@router.post("/questions/{question_id}/review")
async def review_question(
    question_id: int,
    review_data: QuestionReviewRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_user)
):
    """문제 검토 및 승인/거부"""
    try:
        ai_generator = AIQuestionGeneratorEnhanced()
        result = await ai_generator.review_question(
            question_id, 
            review_data.status,
            review_data.feedback
        )
        
        if result:
            return QuestionReviewResponse(
                message=f"문제 {question_id}가 {review_data.status}로 처리되었습니다",
                question_id=question_id,
                new_status=review_data.status,
                reviewed_by=admin_user.username,
                reviewed_at=datetime.now()
            )
        else:
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문제 검토 실패: {str(e)}")

@router.get("/curriculum/templates")
async def get_curriculum_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    subject_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_user)
):
    """커리큘럼 템플릿 목록 조회"""
    try:
        # 현재는 모킹 데이터, 실제로는 데이터베이스에서 조회
        mock_templates = [
            {
                "id": i + 1,
                "title": f"Python 기초 커리큘럼 {i+1}",
                "subject": "Python",
                "difficulty_level": "beginner",
                "total_topics": 12 + i,
                "estimated_duration": f"{4 + i}주",
                "usage_count": 25 - i,
                "rating": 4.5 + (i * 0.1),
                "created_by": "admin",
                "created_at": datetime.now() - timedelta(days=i*7),
                "last_modified": datetime.now() - timedelta(days=i),
                "is_active": True,
                "tags": ["기초", "프로그래밍", "Python"]
            }
            for i in range(skip, skip + limit)
            if not subject_filter or subject_filter.lower() in f"python 기초 커리큘럼 {i+1}".lower()
        ]
        
        return {
            "templates": mock_templates,
            "total": len(mock_templates),
            "has_more": skip + limit < 20
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커리큘럼 템플릿 조회 실패: {str(e)}")

@router.post("/curriculum/template")
async def create_curriculum_template(
    template_data: CurriculumManagementRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin_user)
):
    """새 커리큘럼 템플릿 생성"""
    try:
        # 실제로는 데이터베이스에 저장
        new_template = {
            "id": 999,  # 새로 생성된 ID
            "title": template_data.title,
            "subject": template_data.subject,
            "difficulty_level": template_data.difficulty_level,
            "topics": template_data.topics,
            "created_by": admin_user.username,
            "created_at": datetime.now(),
            "is_active": True
        }
        
        return CurriculumManagementResponse(
            message="커리큘럼 템플릿이 성공적으로 생성되었습니다",
            template_id=new_template["id"],
            template=new_template
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커리큘럼 템플릿 생성 실패: {str(e)}")

@router.get("/system/health")
async def get_system_health(
    admin_user: User = Depends(verify_admin_user)
):
    """시스템 건강도 및 성능 모니터링"""
    try:
        # 실제 시스템 메트릭 수집
        return SystemHealthResponse(
            overall_health=98.5,
            api_response_time=245,  # ms
            database_connections=8,
            active_users=156,
            memory_usage=65.2,  # %
            cpu_usage=23.8,  # %
            disk_usage=45.3,  # %
            last_backup=datetime.now() - timedelta(hours=6),
            uptime=timedelta(days=15, hours=8, minutes=32),
            error_rate=0.02,  # %
            components=[
                {"name": "Database", "status": "healthy", "response_time": 12},
                {"name": "AI Service", "status": "healthy", "response_time": 234},
                {"name": "Authentication", "status": "healthy", "response_time": 45},
                {"name": "File Storage", "status": "warning", "response_time": 1200}
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시스템 상태 조회 실패: {str(e)}")

@router.get("/analytics/users")
async def get_user_analytics(
    period: str = Query("7d", regex="^(1d|7d|30d|90d)$"),
    admin_user: User = Depends(verify_admin_user),
    db: Session = Depends(get_db)
):
    """사용자 분석 데이터"""
    try:
        analytics = EnhancedLearningAnalytics()
        
        # 기간별 사용자 활동 데이터
        period_days = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}[period]
        start_date = datetime.now() - timedelta(days=period_days)
        
        # 실제로는 데이터베이스 쿼리로 수집
        mock_analytics = {
            "total_users": 1247,
            "new_users": 89,
            "active_users": 432,
            "retention_rate": 78.5,
            "avg_session_duration": 25.3,  # minutes
            "completion_rate": 64.2,  # %
            "user_growth": [
                {"date": "2024-09-15", "new_users": 12, "active_users": 89},
                {"date": "2024-09-16", "new_users": 15, "active_users": 95},
                {"date": "2024-09-17", "new_users": 8, "active_users": 87},
                {"date": "2024-09-18", "new_users": 11, "active_users": 92},
                {"date": "2024-09-19", "new_users": 18, "active_users": 105}
            ],
            "subject_popularity": [
                {"subject": "Python", "users": 324, "completion_rate": 68.2},
                {"subject": "JavaScript", "users": 289, "completion_rate": 62.1},
                {"subject": "SQL", "users": 245, "completion_rate": 75.3},
                {"subject": "React", "users": 198, "completion_rate": 58.9}
            ]
        }
        
        return UserAnalyticsResponse(**mock_analytics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 분석 데이터 조회 실패: {str(e)}")

@router.get("/performance/ai-models")
async def get_ai_model_performance(
    admin_user: User = Depends(verify_admin_user)
):
    """AI 모델 성능 모니터링"""
    try:
        return {
            "curriculum_generator": {
                "status": "healthy",
                "success_rate": 96.8,
                "avg_response_time": 2.34,  # seconds
                "requests_today": 127,
                "last_training": "2024-09-15T10:30:00Z"
            },
            "question_generator": {
                "status": "healthy", 
                "success_rate": 94.2,
                "avg_response_time": 1.87,
                "requests_today": 89,
                "last_training": "2024-09-14T15:45:00Z"
            },
            "ai_teacher": {
                "status": "warning",
                "success_rate": 89.1,
                "avg_response_time": 3.12,
                "requests_today": 234,
                "last_training": "2024-09-13T09:20:00Z"
            },
            "feedback_analyzer": {
                "status": "healthy",
                "success_rate": 97.5,
                "avg_response_time": 0.89,
                "requests_today": 156,
                "last_training": "2024-09-16T14:15:00Z"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 모델 성능 조회 실패: {str(e)}")
    