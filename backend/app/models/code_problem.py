"""
Code Problem Database Models
코딩테스트 문제 관련 데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.orm import Base

class CodeProblem(Base):
    """코딩테스트 문제 모델"""
    __tablename__ = "code_problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    difficulty = Column(String(50), nullable=False, index=True)  # easy, medium, hard
    category = Column(String(100), nullable=False, index=True)   # Python 기초, 알고리즘 등
    
    # 문제 상세 정보
    examples = Column(JSON, nullable=False)  # [{"input": "...", "output": "...", "explanation": "..."}]
    constraints = Column(JSON, nullable=False)  # ["constraint1", "constraint2", ...]
    hints = Column(JSON, nullable=False)  # ["hint1", "hint2", ...]
    template = Column(Text)  # 초기 코드 템플릿
    
    # 제한 사항
    time_limit_ms = Column(Integer, default=10000)  # 10초
    memory_limit_mb = Column(Integer, default=128)  # 128MB
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    
    # 통계 정보
    total_submissions = Column(Integer, default=0)
    accepted_submissions = Column(Integer, default=0)
    acceptance_rate = Column(Float, default=0.0)
    
    # 관계
    test_cases = relationship("CodeTestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("CodeSubmission", back_populates="problem")
    created_by = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self):
        return f"<CodeProblem(id={self.id}, title='{self.title}', difficulty='{self.difficulty}')>"

class CodeTestCase(Base):
    """코딩테스트 문제의 테스트 케이스"""
    __tablename__ = "code_test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("code_problems.id"), nullable=False)
    
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    description = Column(String(500))  # 테스트 케이스 설명
    
    is_hidden = Column(Boolean, default=True)  # 공개 여부 (예제는 False, 검증용은 True)
    is_sample = Column(Boolean, default=False)  # 예제 테스트 케이스 여부
    weight = Column(Float, default=1.0)  # 가중치 (일부 테스트 케이스가 더 중요할 수 있음)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    problem = relationship("CodeProblem", back_populates="test_cases")

    def __repr__(self):
        return f"<CodeTestCase(id={self.id}, problem_id={self.problem_id}, is_hidden={self.is_hidden})>"

class CodeSubmission(Base):
    """코드 제출 기록"""
    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("code_problems.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 제출 정보
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False, default="python")
    
    # 실행 결과
    status = Column(String(50), nullable=False)  # accepted, wrong_answer, time_limit_exceeded, runtime_error 등
    execution_time_ms = Column(Integer)
    memory_usage_mb = Column(Float)
    
    # 테스트 결과
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    test_results = Column(JSON)  # 상세 테스트 결과
    
    # 메타데이터
    submitted_at = Column(DateTime, default=datetime.utcnow)
    judged_at = Column(DateTime)
    
    # 관계
    problem = relationship("CodeProblem", back_populates="submissions")
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<CodeSubmission(id={self.id}, problem_id={self.problem_id}, status='{self.status}')>"

class ProblemTag(Base):
    """문제 태그 시스템"""
    __tablename__ = "problem_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    color = Column(String(20), default="#3B82F6")  # 태그 색상
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ProblemTagAssociation(Base):
    """문제-태그 연결 테이블"""
    __tablename__ = "problem_tag_associations"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("code_problems.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("problem_tags.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
