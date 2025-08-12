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

