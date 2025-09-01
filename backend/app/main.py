from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import questions, submit, dashboard, student, auth, admin, results_guard, teacher_dashboard, taxonomy, teacher_groups, feedback, ai_learning, curriculum, personalization, monitoring, ai_features, beta_testing, subjects, stats, code_execution
from .core.config import settings
from sqlalchemy import create_engine
from .models.orm import Base
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
# CORS 미들웨어 추가 - 등록은 다른 커스텀 미들웨어보다 먼저 해야 함
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://192.168.0.104:5174",  # 네트워크 인터페이스 추가
        "http://172.25.64.1:5174",
        "http://172.31.80.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # 24시간
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
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(code_execution.router, prefix="/api/v1", tags=["code-execution"])

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

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy", "service": "LMS MVP Backend"}
