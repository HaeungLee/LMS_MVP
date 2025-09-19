"""
관리자 API용 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

class QuestionStatus(str, Enum):
    PENDING = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# 문제 검토 관련
class QuestionReviewRequest(BaseModel):
    status: QuestionStatus
    feedback: Optional[str] = None
    suggested_changes: Optional[str] = None

class QuestionReviewResponse(BaseModel):
    message: str
    question_id: int
    new_status: QuestionStatus
    reviewed_by: str
    reviewed_at: datetime

# 커리큘럼 관리 관련
class CurriculumTopicRequest(BaseModel):
    title: str
    description: str
    estimated_duration: str  # "2시간", "1주" 등
    prerequisites: List[str] = []
    learning_objectives: List[str] = []

class CurriculumManagementRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=100)
    difficulty_level: DifficultyLevel
    description: Optional[str] = None
    topics: List[CurriculumTopicRequest] = []
    estimated_total_duration: Optional[str] = None
    target_audience: Optional[str] = None
    tags: List[str] = []

class CurriculumManagementResponse(BaseModel):
    message: str
    template_id: int
    template: Dict[str, Any]

# 시스템 건강도 관련
class SystemComponentHealth(BaseModel):
    name: str
    status: str  # "healthy", "warning", "error"
    response_time: float  # milliseconds
    additional_info: Optional[Dict[str, Any]] = None

class SystemHealthResponse(BaseModel):
    overall_health: float  # 0-100 점수
    api_response_time: float  # milliseconds
    database_connections: int
    active_users: int
    memory_usage: float  # percentage
    cpu_usage: float  # percentage
    disk_usage: float  # percentage
    last_backup: datetime
    uptime: timedelta
    error_rate: float  # percentage
    components: List[SystemComponentHealth]

# 사용자 분석 관련
class UserGrowthData(BaseModel):
    date: str
    new_users: int
    active_users: int

class SubjectPopularityData(BaseModel):
    subject: str
    users: int
    completion_rate: float

class UserAnalyticsResponse(BaseModel):
    total_users: int
    new_users: int
    active_users: int
    retention_rate: float
    avg_session_duration: float  # minutes
    completion_rate: float  # percentage
    user_growth: List[UserGrowthData]
    subject_popularity: List[SubjectPopularityData]

# 관리자 대시보드 관련
class ActivitySummary(BaseModel):
    type: str
    count: int
    period: str

class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    total_questions: int
    total_topics: int
    ai_questions_generated: int
    system_health_score: float
    recent_activities: List[ActivitySummary]

# AI 모델 성능 관련
class AIModelPerformance(BaseModel):
    status: str  # "healthy", "warning", "error"
    success_rate: float  # percentage
    avg_response_time: float  # seconds
    requests_today: int
    last_training: str  # ISO datetime string

# 질문 리스트 응답
class QuestionListItem(BaseModel):
    id: int
    type: str
    difficulty: str
    subject: str
    topic: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    created_at: datetime
    ai_confidence: float
    status: QuestionStatus

class QuestionListResponse(BaseModel):
    questions: List[QuestionListItem]
    total: int
    has_more: bool

# 커리큘럼 템플릿 리스트
class CurriculumTemplateItem(BaseModel):
    id: int
    title: str
    subject: str
    difficulty_level: str
    total_topics: int
    estimated_duration: str
    usage_count: int
    rating: float
    created_by: str
    created_at: datetime
    last_modified: datetime
    is_active: bool
    tags: List[str]

class CurriculumTemplateListResponse(BaseModel):
    templates: List[CurriculumTemplateItem]
    total: int
    has_more: bool
