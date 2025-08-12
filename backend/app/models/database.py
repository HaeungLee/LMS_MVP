from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    quiz_sessions = relationship("QuizSession", back_populates="user")
    recent_activities = relationship("RecentActivity", back_populates="user")

class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_type = Column(String(50), default="python_basics")  # 퀴즈 타입
    total_questions = Column(Integer)
    answered_questions = Column(Integer)
    skipped_questions = Column(Integer)
    total_score = Column(Float)
    time_taken = Column(Integer)  # 초 단위
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # 퀴즈 설정
    shuffle_enabled = Column(Boolean, default=True)
    easy_count = Column(Integer, default=4)
    medium_count = Column(Integer, default=4)
    hard_count = Column(Integer, default=2)
    
    # 관계
    user = relationship("User", back_populates="quiz_sessions")
    answers = relationship("QuizAnswer", back_populates="session")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"))
    question_id = Column(Integer)
    user_answer = Column(Text)
    correct_answer = Column(String(200))
    is_correct = Column(Boolean)
    is_skipped = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    session = relationship("QuizSession", back_populates="answers")

class RecentActivity(Base):
    __tablename__ = "recent_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_type = Column(String(50))  # "quiz_completed", "question_answered" 등
    activity_description = Column(String(200))
    score = Column(Float, nullable=True)
    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User", back_populates="recent_activities")
