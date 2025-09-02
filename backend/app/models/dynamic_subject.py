"""
Phase 8: 동적 과목 관리 시스템을 위한 독립적인 모델
기존 모델과 분리하여 새로운 테이블 구조 정의
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, JSON, Float, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# 새로운 Base 생성 (기존과 분리)
DynamicSubjectBase = declarative_base()


class SubjectCategory(DynamicSubjectBase):
    """과목 카테고리 테이블"""
    __tablename__ = "dynamic_subject_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color_code = Column(String(10), nullable=True)  # 예: #3B82F6
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    subjects = relationship("DynamicSubject", back_populates="category")


class DynamicSubject(DynamicSubjectBase):
    """동적 과목 메타데이터 테이블"""
    __tablename__ = "dynamic_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("dynamic_subject_categories.id"), nullable=False)
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
    topics = relationship("DynamicSubjectTopic", back_populates="subject")
    prerequisites = relationship(
        "DynamicSubjectPrerequisite", 
        foreign_keys="DynamicSubjectPrerequisite.subject_id",
        back_populates="subject"
    )


class DynamicSubjectTopic(DynamicSubjectBase):
    """동적 과목 토픽 구조 테이블"""
    __tablename__ = "dynamic_subject_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("dynamic_subjects.id", ondelete="CASCADE"), nullable=False)
    topic_key = Column(String(100), nullable=False, index=True)
    topic_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    parent_topic_id = Column(Integer, ForeignKey("dynamic_subject_topics.id"), nullable=True)
    
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
    subject = relationship("DynamicSubject", back_populates="topics")
    parent_topic = relationship("DynamicSubjectTopic", remote_side=[id])


class DynamicSubjectPrerequisite(DynamicSubjectBase):
    """동적 과목 전제조건 테이블"""
    __tablename__ = "dynamic_subject_prerequisites"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("dynamic_subjects.id", ondelete="CASCADE"), nullable=False)
    prerequisite_subject_id = Column(Integer, ForeignKey("dynamic_subjects.id"), nullable=False)
    is_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    subject = relationship("DynamicSubject", foreign_keys=[subject_id], back_populates="prerequisites")
    prerequisite_subject = relationship("DynamicSubject", foreign_keys=[prerequisite_subject_id])


# class DynamicUserSubjectProgress(DynamicSubjectBase):
#     """사용자별 동적 과목 진도 테이블"""
#     __tablename__ = "user_progress_dynamic"  # 삭제된 테이블과 이름 구분
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, nullable=False, index=True)
#     subject_id = Column(Integer, ForeignKey("dynamic_subjects.id"), nullable=False)
    
#     # 진도 정보
#     current_topic_id = Column(Integer, ForeignKey("dynamic_subject_topics.id"), nullable=True)
#     completed_topics = Column(JSON, default=list)  # 완료한 토픽 ID 리스트
#     progress_percentage = Column(Float, default=0.0)
    
#     # 학습 통계
#     total_study_time = Column(Integer, default=0)  # 분 단위
#     problems_solved = Column(Integer, default=0)
#     problems_correct = Column(Integer, default=0)
#     current_streak = Column(Integer, default=0)
#     best_streak = Column(Integer, default=0)
    
#     # 타임스탬프
#     started_at = Column(DateTime, default=datetime.utcnow)
#     last_studied_at = Column(DateTime, nullable=True)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # 관계
#     subject = relationship("DynamicSubject")
#     current_topic = relationship("DynamicSubjectTopic")
