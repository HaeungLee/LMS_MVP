from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, JSON, Float
)
from sqlalchemy.orm import relationship
from .orm import Base


class SubjectCategory(Base):
    """과목 카테고리 테이블"""
    __tablename__ = "subject_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color_code = Column(String(10), nullable=True)  # 예: #3B82F6
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    subjects = relationship("SubjectExtended", back_populates="category")


class SubjectExtended(Base):
    """확장된 과목 메타데이터 테이블"""
    __tablename__ = "subjects_extended"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("subject_categories.id"), nullable=False)
    difficulty_level = Column(String(20), default='beginner')  # beginner, intermediate, advanced
    estimated_duration = Column(String(50), nullable=True)  # 예: "4주", "20시간"
    icon_name = Column(String(50), nullable=True)  # 예: "🐍", "📊"
    color_code = Column(String(10), nullable=True)  # 예: #10B981
    is_active = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    
    # 통계 정보
    total_problems = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    average_completion_rate = Column(Float, default=0.0)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    category = relationship("SubjectCategory", back_populates="subjects")
    topics = relationship("SubjectTopic", back_populates="subject")
    prerequisites = relationship(
        "SubjectPrerequisite", 
        foreign_keys="SubjectPrerequisite.subject_id",
        back_populates="subject"
    )


class SubjectTopic(Base):
    """과목 토픽 구조 테이블"""
    __tablename__ = "subject_topics_extended"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects_extended.id", ondelete="CASCADE"), nullable=False)
    topic_key = Column(String(100), nullable=False, index=True)
    topic_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    parent_topic_id = Column(Integer, ForeignKey("subject_topics_extended.id"), nullable=True)
    
    # 학습 정보
    learning_objectives = Column(JSON, default=list)  # 학습 목표 리스트
    estimated_duration = Column(String(50), nullable=True)  # 예상 소요 시간
    difficulty_level = Column(String(20), default='beginner')
    
    # 통계
    problem_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    subject = relationship("app.models.subject.SubjectExtended", back_populates="topics")
    parent_topic = relationship("app.models.subject.SubjectTopic", remote_side=[id])


class SubjectPrerequisite(Base):
    """과목 전제조건 테이블"""
    __tablename__ = "subject_prerequisites_extended"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects_extended.id", ondelete="CASCADE"), nullable=False)
    prerequisite_subject_id = Column(Integer, ForeignKey("subjects_extended.id"), nullable=False)
    is_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    subject = relationship("SubjectExtended", foreign_keys=[subject_id], back_populates="prerequisites")
    prerequisite_subject = relationship("SubjectExtended", foreign_keys=[prerequisite_subject_id])


class UserSubjectProgress(Base):
    """사용자별 과목 진도 테이블"""
    __tablename__ = "user_subject_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects_extended.id"), nullable=False)
    
    # 진도 정보
    current_topic_id = Column(Integer, ForeignKey("subject_topics_extended.id"), nullable=True)
    completed_topics = Column(JSON, default=list)  # 완료한 토픽 ID 리스트
    progress_percentage = Column(Float, default=0.0)
    
    # 학습 통계
    total_study_time = Column(Integer, default=0)  # 분 단위
    problems_solved = Column(Integer, default=0)
    problems_correct = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    
    # 타임스탬프
    started_at = Column(DateTime, default=datetime.utcnow)
    last_studied_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    subject = relationship("app.models.subject.SubjectExtended")
    current_topic = relationship("app.models.subject.SubjectTopic")
