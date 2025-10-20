from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import questions, submit, dashboard, student, auth, admin, results_guard, teacher_dashboard, taxonomy, teacher_groups, feedback, ai_learning, curriculum, personalization, monitoring, ai_features, beta_testing, subjects, stats, code_execution, unified_learning, dynamic_subjects_simple
# Phase 9 imports
from app.api.v1 import hybrid_ai, ai_curriculum, ai_teaching
# MVP imports
from app.api.v1 import mvp_learning, achievement, review_system, review_submit, payment
from .core.config import settings
from sqlalchemy import create_engine
from .models.orm import Base
from .models.code_problem import CodeProblem, CodeTestCase, CodeSubmission, ProblemTag, ProblemTagAssociation  # 새 모델 import
import os
from .middleware.request_id import RequestIDMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import StructuredLoggingMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware

app = FastAPI(
    title="LMS MVP API",
    description="AI 기반 코딩 학습 플랫폼 API",
    version="1.0.0"
)

# CORS 미들웨어 추가 - 가장 먼저 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5174"],  # 특정 도메인 허용
    allow_credentials=True,  # credentials 허용
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],  # 모든 헤더 허용
)

# Request ID
app.add_middleware(RequestIDMiddleware)

# Rate limit (basic quotas)
app.add_middleware(
    RateLimitMiddleware,
    limits={
        "/api/v1/auth/login": (10, 60),
        "/api/v1/submit": (30, 60),
        "/api/v1/feedback": (20, 60),
        "/api/v1/admin/questions": (60, 60),
    }
)

# Structured logging
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# 초기 테이블 생성 (개발 편의용; 운영은 Alembic 사용)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lms_user:1234@localhost:15432/lms_mvp_db")
try:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
except Exception:
    # DB가 아직 준비되지 않은 개발 초기 단계에서도 앱이 기동되도록 무시
    pass

# 라우터 등록
app.include_router(questions.router, prefix="/api/v1", tags=["questions"])
app.include_router(submit.router, prefix="/api/v1", tags=["submissions"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(student.router, prefix="/api/v1", tags=["student"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(results_guard.router, prefix="/api/v1", tags=["results_guard"])
app.include_router(teacher_dashboard.router, prefix="/api/v1", tags=["teacher"])
app.include_router(taxonomy.router, prefix="/api/v1", tags=["taxonomy"])
app.include_router(teacher_groups.router, prefix="/api/v1", tags=["teacher_groups"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
app.include_router(ai_learning.router, prefix="/api/v1/ai-learning", tags=["ai-learning"])
app.include_router(curriculum.router, prefix="/api/v1/curriculum", tags=["curriculum"])
app.include_router(personalization.router, prefix="/api/v1/personalization", tags=["personalization"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(ai_features.router, prefix="/api/v1/ai-features", tags=["ai-features"])
app.include_router(beta_testing.router, prefix="/api/v1/beta", tags=["beta-testing"])
app.include_router(subjects.router, prefix="/api/v1", tags=["subjects"])
app.include_router(dynamic_subjects_simple.router, prefix="/api/v1/dynamic-subjects", tags=["dynamic-subjects"])  # Phase 8 - 재활성화
# app.include_router(simple_topics.router, prefix="/api/v1", tags=["simple-topics"])  # 파일 없음 - 주석 처리
app.include_router(unified_learning.router, prefix="/api/v1", tags=["unified-learning"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(code_execution.router, prefix="/api/v1", tags=["code-execution"])
# app.include_router(hybrid_ai.router, tags=["hybrid-ai"])  # Phase 9: EduGPT 통합용 하이브리드 AI - 임시 비활성화
app.include_router(ai_curriculum.router, tags=["ai-curriculum"])  # Phase 9: AI 커리큘럼 생성 및 교육 세션 (prefix 이미 설정됨)
app.include_router(ai_teaching.router, tags=["ai-teaching"])  # Phase 9: 실라버스 기반 개별화 교육 (prefix 이미 설정됨)

# Phase 10: 고급 AI 기능들
from app.api.v1 import ai_questions, ai_counseling
app.include_router(ai_questions.router, tags=["ai-questions-phase10"])  # Phase 10: 스마트 문제 생성 (prefix 이미 설정됨)
app.include_router(ai_counseling.router, tags=["ai-counseling"])  # AI 학습 상담 시스템 (기존 멘토링 시스템 활용)

# MVP: 온보딩 & 일일 학습
app.include_router(mvp_learning.router, tags=["mvp"])  # MVP 온보딩 + 일일 학습
app.include_router(achievement.router, prefix="/api/v1/achievement", tags=["achievement"])  # 학습 달성 통계
app.include_router(review_system.router, prefix="/api/v1/review", tags=["review"])  # 복습 시스템
app.include_router(review_submit.router, prefix="/api/v1/review", tags=["review"])  # 복습 제출
app.include_router(payment.router, prefix="/api/v1/payment", tags=["payment"])  # 결제 시스템

@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "LMS MVP API Server is running!",
        "version": "1.0.0",
        "endpoints": {
            "questions": "/api/v1/questions/{subject}",
            "submit": "/api/v1/submit",
            "feedback": "/api/v1/feedback",
            "results": "/api/v1/results/{submission_id}"
        }
    }

@app.get("/api/v1", tags=["api"])
@app.get("/api/v1/", tags=["api"])
@app.post("/api/v1", tags=["api"])
@app.post("/api/v1/", tags=["api"])
def api_root():
    return {
        "message": "LMS MVP API v1",
        "version": "1.0.0",
        "available_endpoints": [
            "/api/v1/questions/{subject}",
            "/api/v1/submit",
            "/api/v1/feedback",
            "/api/v1/dashboard/stats",
            "/api/v1/auth/me",
            "/api/v1/health"
        ]
    }

@app.get("/api/status", tags=["health"])
@app.get("/status", tags=["health"])
def health_check():
    return {"status": "healthy", "service": "LMS MVP Backend"}

# OPTIONS 요청 처리를 위한 글로벌 핸들러
from fastapi import Request, Response

@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    """모든 경로에 대한 OPTIONS 요청 처리"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": request.headers.get("Origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
            "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRF-Token, X-Request-ID, Origin, Referer, User-Agent",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
    )
