from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    ARRAY,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, index=True)  # UUID 문자열
    user_id = Column(Integer, nullable=True, index=True)
    subject = Column(String(100), nullable=False, index=True)
    total_score = Column(Float, nullable=False)
    max_score = Column(Integer, nullable=False)
    time_taken = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    items = relationship("SubmissionItem", back_populates="submission", cascade="all, delete-orphan")


class SubmissionItem(Base):
    __tablename__ = "submission_items"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, nullable=False)
    user_answer = Column(Text, nullable=False)
    skipped = Column(Boolean, default=False, nullable=False)
    score = Column(Float, nullable=False)
    correct_answer = Column(String(200), nullable=False)
    topic = Column(String(100), nullable=False, index=True)

    submission = relationship("Submission", back_populates="items")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    submission_item_id = Column(Integer, ForeignKey("submission_items.id", ondelete="CASCADE"), nullable=False, index=True)
    feedback_text = Column(Text, nullable=False)
    ai_generated = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    question_type = Column(String(50), nullable=False)
    code_snippet = Column(Text, nullable=False)
    correct_answer = Column(String(200), nullable=False)
    difficulty = Column(String(20), nullable=False)
    rubric = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(64), nullable=False)
    role = Column(String(20), nullable=False, default="student", index=True)
    display_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(64), primary_key=True, index=True)  # token id
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    parent_topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)


class SubjectTopic(Base):
    __tablename__ = "subject_topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_key = Column(String(100), ForeignKey("subjects.key", ondelete="CASCADE"), nullable=False, index=True)
    topic_key = Column(String(100), ForeignKey("topics.key", ondelete="CASCADE"), nullable=False, index=True)
    weight = Column(Float, default=1.0, nullable=False)
    is_core = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    show_in_coverage = Column(Boolean, default=True, nullable=False)


class SubjectSettings(Base):
    __tablename__ = "subject_settings"

    id = Column(Integer, primary_key=True, index=True)
    subject_key = Column(String(100), ForeignKey("subjects.key", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    min_attempts = Column(Integer, default=3, nullable=False)
    min_accuracy = Column(Float, default=0.6, nullable=False)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)


class TeacherGroup(Base):
    __tablename__ = "teacher_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)


class StudentAssignment(Base):
    __tablename__ = "student_assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(100), nullable=False, index=True)
    topic_key = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


# Phase 1: 확장 가능한 커리큘럼 아키텍처 모델들

class CurriculumCategory(Base):
    """커리큘럼 카테고리 (최상위 레벨)"""
    __tablename__ = "curriculum_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # 'saas_development'
    display_name = Column(String(100), nullable=False)  # 'SaaS 개발자 종합과정'
    description = Column(Text, nullable=True)
    target_audience = Column(String(100), nullable=True)  # 'beginner_to_professional'
    estimated_total_months = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 관계 설정
    tracks = relationship("LearningTrack", back_populates="curriculum_category")


class LearningTrack(Base):
    """학습 트랙 (중간 레벨) - 새로 생성"""
    __tablename__ = "learning_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)  # 'python_basics'
    display_name = Column(String(100), nullable=False)  # 'Python 기초'
    category = Column(String(50), nullable=False)  # 'foundation', 'development', 'specialization'
    curriculum_category_id = Column(Integer, ForeignKey("curriculum_categories.id"), nullable=True)
    specialization_level = Column(String(50), default='general')  # 'general', 'specialist', 'expert', 'master'
    prerequisite_tracks = Column(ARRAY(Text), default=[])  # 선수 트랙들
    difficulty_level = Column(Integer, default=1)  # 1-5
    estimated_hours = Column(Integer, default=20)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 관계 설정
    curriculum_category = relationship("CurriculumCategory", back_populates="tracks")
    modules = relationship("LearningModule", back_populates="track")


class LearningModule(Base):
    """학습 모듈 (최하위 레벨)"""
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    name = Column(String(100), nullable=False)  # 'react_hooks'
    display_name = Column(String(100), nullable=False)  # 'React Hooks 마스터'
    module_type = Column(String(50), default='core')  # 'core', 'elective', 'project', 'certification'
    estimated_hours = Column(Integer, default=8)
    difficulty_level = Column(Integer, default=1)  # 1-5
    prerequisites = Column(ARRAY(Text), default=[])  # 다른 모듈 이름들
    tags = Column(ARRAY(Text), default=[])  # ['frontend', 'state-management', 'hooks']
    industry_focus = Column(String(100), default='general')  # 'fintech', 'ecommerce', 'enterprise'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 관계 설정
    track = relationship("LearningTrack", back_populates="modules")
    resources = relationship("LearningResource", back_populates="module")


class LearningResource(Base):
    """AI 참고자료 시스템"""
    __tablename__ = "learning_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=True)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    sub_topic = Column(String(100), nullable=True)
    resource_type = Column(String(50), nullable=False)  # 'documentation', 'tutorial', 'video', 'project'
    title = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(Integer, default=1)
    industry_focus = Column(String(100), default='general')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 관계 설정
    module = relationship("LearningModule", back_populates="resources")

