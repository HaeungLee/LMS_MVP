"""
Phase 9: AI 커리큘럼 생성 및 교육 세션 관련 모델
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Float, ForeignKey, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .orm import Base


class AIGeneratedCurriculum(Base):
    """AI로 생성된 커리큘럼 모델"""
    __tablename__ = "ai_generated_curricula"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)  # Phase 8 연동
    subject_key = Column(String(100), nullable=True, index=True)  # 동적 과목 키
    learning_goals = Column(ARRAY(Text), nullable=True)  # 학습 목표 리스트
    difficulty_level = Column(Integer, nullable=True)  # 1-10 난이도
    generated_syllabus = Column(JSON, nullable=True)  # 생성된 커리큘럼 JSON
    agent_conversation_log = Column(Text, nullable=True)  # 2-Agent 대화 로그
    generation_metadata = Column(JSON, nullable=True)  # AI 모델, 파라미터 등
    status = Column(String(20), nullable=False, default="generating", index=True)  # generating, completed, failed
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # 관계
    # user = relationship("User", back_populates="ai_curricula")  # 임시 비활성화
    # subject = relationship("Subject", back_populates="ai_curricula")  # 임시 비활성화
    teaching_sessions = relationship("AITeachingSession", back_populates="curriculum")


class AITeachingSession(Base):
    """AI 교육 세션 모델"""
    __tablename__ = "ai_teaching_sessions"

    id = Column(Integer, primary_key=True, index=True)
    curriculum_id = Column(Integer, ForeignKey("ai_generated_curricula.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_title = Column(String(200), nullable=True)
    conversation_history = Column(JSON, nullable=True)  # 대화 기록
    current_step = Column(Integer, nullable=False, default=1)  # 현재 단계
    total_steps = Column(Integer, nullable=True)  # 전체 단계 수
    completion_percentage = Column(Float, nullable=False, default=0.0)  # 완료율
    session_status = Column(String(20), nullable=False, default="active", index=True)  # active, paused, completed, abandoned
    teaching_metadata = Column(JSON, nullable=True)  # 세션 설정, AI 모델 등
    learning_progress = Column(JSON, nullable=True)  # 단계별 이해도, 점수 등
    started_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    last_activity_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)

    # 관계
    curriculum = relationship("AIGeneratedCurriculum", back_populates="teaching_sessions")
    # user = relationship("User", back_populates="ai_teaching_sessions")  # 임시 비활성화


class AIContentGenerationLog(Base):
    """AI 콘텐츠 생성 로그 (품질 관리 및 비용 추적용)"""
    __tablename__ = "ai_content_generation_logs"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # curriculum, teaching_response, problem
    content_id = Column(Integer, nullable=True)  # 관련 콘텐츠 ID
    ai_provider = Column(String(50), nullable=False, index=True)  # openai, openrouter
    model_name = Column(String(100), nullable=False)  # gpt-4, gpt-3.5-turbo 등
    prompt_template = Column(Text, nullable=True)  # 사용된 프롬프트 템플릿
    input_data = Column(JSON, nullable=True)  # 입력 데이터
    output_data = Column(JSON, nullable=True)  # 출력 데이터
    tokens_used = Column(Integer, nullable=True)  # 사용된 토큰 수
    generation_time_ms = Column(Integer, nullable=True)  # 생성 시간 (밀리초)
    cost_estimate = Column(Float, nullable=True)  # 추정 비용 (USD)
    quality_score = Column(Float, nullable=True)  # 품질 점수 (나중에 구현)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
