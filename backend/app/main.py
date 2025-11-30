from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from .api.v1 import questions, submit, dashboard, student, auth, admin, results_guard, teacher_dashboard, taxonomy, teacher_groups, feedback, ai_learning, curriculum, personalization, monitoring, ai_features, beta_testing, subjects, stats, code_execution, unified_learning, dynamic_subjects_simple
# Phase 9 imports
from app.api.v1 import hybrid_ai, ai_curriculum, ai_teaching
# MVP imports
from app.api.v1 import mvp_learning, achievement, review_system, review_submit, payment, quotes, notes, pdf_export
# Phase B: Constitutional AI
from app.api.v1 import constitutional
# Phase C: Emotional Support
from app.api.v1 import emotional_support
# Phase 2: Metrics & Monitoring Enhancement
from app.api.v1 import metrics as prometheus_metrics
from .core.config import settings
from .core.exceptions import register_exception_handlers  # 전역 예외 핸들러
from sqlalchemy import create_engine
from .models.orm import Base
from .models.code_problem import CodeProblem, CodeTestCase, CodeSubmission, ProblemTag, ProblemTagAssociation  # 새 모델 import
import os
from .middleware.request_id import RequestIDMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.logging import StructuredLoggingMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
import json

# ============================================
# FastAPI 앱 설정 - 상세 API 문서화
# ============================================
app = FastAPI(
    title="LMS MVP API",
    description="""
## 🎓 AI 기반 코딩 학습 플랫폼 API

### 주요 기능
- **인증 (Auth)**: 회원가입, 로그인, JWT 토큰 관리
- **학습 (Learning)**: AI 커리큘럼, 일일 학습, 복습 시스템
- **문제 (Questions)**: 코딩 문제 조회 및 제출
- **대시보드 (Dashboard)**: 학습 통계 및 진도 관리
- **AI 기능**: 맞춤형 커리큘럼 생성, AI 튜터링

### 인증 방식
- **JWT Bearer Token**: `Authorization: Bearer <token>`
- **쿠키 인증**: `access_token`, `refresh_token`

### 응답 형식
모든 API는 JSON 형식으로 응답하며, 에러 시 표준화된 형식을 따릅니다:
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "에러 설명",
  "details": {}
}
```

### Rate Limiting
- 로그인: 10회/분
- 제출: 30회/분
- 피드백: 20회/분
    """,
    version="1.0.0",
    terms_of_service="https://lms-mvp.example.com/terms",
    contact={
        "name": "LMS MVP Support",
        "email": "support@lms-mvp.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "auth", "description": "🔐 인증 및 사용자 관리"},
        {"name": "health", "description": "💚 헬스체크 및 상태 확인"},
        {"name": "dashboard", "description": "📊 대시보드 및 통계"},
        {"name": "questions", "description": "📝 문제 조회 및 관리"},
        {"name": "submissions", "description": "✅ 답안 제출 및 채점"},
        {"name": "mvp", "description": "🚀 MVP 핵심 기능 (온보딩, 일일학습)"},
        {"name": "review", "description": "🔄 복습 시스템 (망각곡선 기반)"},
        {"name": "achievement", "description": "🏆 학습 달성 및 스트릭"},
        {"name": "ai-curriculum", "description": "🤖 AI 커리큘럼 생성"},
        {"name": "ai-teaching", "description": "👨‍🏫 AI 튜터링 세션"},
        {"name": "payment", "description": "💳 결제 및 구독 관리"},
        {"name": "subjects", "description": "📚 과목 및 토픽 관리"},
        {"name": "admin", "description": "⚙️ 관리자 기능"},
        {"name": "emotional-support", "description": "💝 감성적 학습 지원"},
    ],
)

# CORS origins 파싱 - 환경변수에서 JSON 배열로 읽어오기
cors_origins_str = os.getenv(
    "BACKEND_CORS_ORIGINS",
    '["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173","https://lms-mvp-psi.vercel.app","https://lms-1tddckc3w-eterialwinds-projects.vercel.app"]'
)
try:
    cors_origins = json.loads(cors_origins_str)
except json.JSONDecodeError:
    # 파싱 실패 시 기본값 사용 (Production 도메인 포함)
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://lms-mvp-psi.vercel.app",
        "https://lms-1tddckc3w-eterialwinds-projects.vercel.app"
    ]

print(f"✅ CORS Origins: {cors_origins}")  # 디버그용 로그

# CORS 미들웨어 추가 - 가장 먼저 등록
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
    expose_headers=["*"]  # 모든 응답 헤더 노출
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

# 전역 예외 핸들러 등록
register_exception_handlers(app)

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
app.include_router(quotes.router, tags=["quotes"])  # 명언 시스템
app.include_router(notes.router, tags=["notes"])  # 메모 시스템
app.include_router(pdf_export.router, tags=["pdf"])  # PDF 내보내기

# Phase B: Constitutional AI
app.include_router(constitutional.router, tags=["constitutional-ai"])  # Constitutional AI

# Phase C: Emotional Support
app.include_router(emotional_support.router, tags=["emotional-support"])  # 감성적 지원 시스템

# Phase 2: Prometheus 메트릭 엔드포인트
app.include_router(prometheus_metrics.router, prefix="/api/v1/metrics", tags=["monitoring"])

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

# Health check 엔드포인트 - GET과 HEAD 모두 지원
@app.get("/", tags=["health"])
@app.head("/", tags=["health"])
@app.get("/health", tags=["health"])
@app.head("/health", tags=["health"])
@app.get("/api/v1/health", tags=["health"])
@app.head("/api/v1/health", tags=["health"])
@app.get("/api/status", tags=["health"])
@app.get("/status", tags=["health"])
def health_check():
    return {"status": "ok", "service": "LMS MVP Backend"}

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
