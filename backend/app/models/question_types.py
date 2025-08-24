from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    CODE_COMPLETION = "code_completion"
    DEBUG_CODE = "debug_code"
    TRUE_FALSE = "true_false"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BaseQuestion(BaseModel):
    """모든 문제 유형의 기본 구조"""
    id: Optional[str] = None
    type: QuestionType
    question: str
    topic: str
    difficulty: DifficultyLevel
    estimated_time: int = Field(default=300, description="예상 소요 시간 (초)")
    learning_objectives: List[str] = []
    created_at: Optional[datetime] = None
    ai_generated: bool = True
    language: str = "python"


class MultipleChoiceQuestion(BaseQuestion):
    """객관식 문제"""
    type: Literal[QuestionType.MULTIPLE_CHOICE] = QuestionType.MULTIPLE_CHOICE
    options: List[str] = Field(..., min_items=4, max_items=4, description="A, B, C, D 4개 선택지")
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str
    distractor_analysis: Dict[str, str] = Field(default_factory=dict, description="오답 선택지별 설명")


class ShortAnswerQuestion(BaseQuestion):
    """주관식 문제"""
    type: Literal[QuestionType.SHORT_ANSWER] = QuestionType.SHORT_ANSWER
    expected_keywords: List[str] = Field(..., min_items=3, description="핵심 키워드 3-5개")
    sample_answer: str = Field(..., min_length=50, max_length=500)
    scoring_criteria: Dict[str, float] = Field(
        default={"keyword_match": 0.4, "semantic_similarity": 0.6},
        description="채점 기준 가중치"
    )
    min_length: int = 50
    max_length: int = 300


class CodeCompletionQuestion(BaseQuestion):
    """코드 완성 문제"""
    type: Literal[QuestionType.CODE_COMPLETION] = QuestionType.CODE_COMPLETION
    code_template: str = Field(..., description="빈칸이 포함된 코드 템플릿")
    blanks: List[str] = Field(..., min_items=1, description="정답 목록")
    blank_hints: List[str] = Field(default_factory=list, description="힌트 목록")
    test_cases: List[Dict[str, Any]] = Field(default_factory=list, description="테스트 케이스")


class DebugCodeQuestion(BaseQuestion):
    """디버깅 문제"""
    type: Literal[QuestionType.DEBUG_CODE] = QuestionType.DEBUG_CODE
    buggy_code: str = Field(..., description="버그가 있는 코드")
    errors: List[Dict[str, Any]] = Field(..., min_items=1, description="오류 정보")
    corrected_code: str = Field(..., description="수정된 코드")
    bug_types: List[str] = Field(default_factory=list, description="버그 유형")


class TrueFalseQuestion(BaseQuestion):
    """참/거짓 문제"""
    type: Literal[QuestionType.TRUE_FALSE] = QuestionType.TRUE_FALSE
    statement: str = Field(..., description="판단할 문장")
    correct_answer: bool
    explanation: str
    common_misconception: str = Field(default="", description="자주 틀리는 이유")


# 문제 유형별 Union 타입
QuestionUnion = Union[
    MultipleChoiceQuestion,
    ShortAnswerQuestion, 
    CodeCompletionQuestion,
    DebugCodeQuestion,
    TrueFalseQuestion
]


class QuestionGenerationRequest(BaseModel):
    """문제 생성 요청 모델"""
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    question_type: Optional[QuestionType] = None
    count: int = Field(default=1, ge=1, le=10)
    context: Optional[Dict[str, Any]] = None


class MixedQuestionRequest(BaseModel):
    """혼합 문제 생성 요청 모델"""
    topic: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    question_types: Dict[QuestionType, int] = Field(
        default={
            QuestionType.MULTIPLE_CHOICE: 2,
            QuestionType.SHORT_ANSWER: 1,
            QuestionType.CODE_COMPLETION: 1,
            QuestionType.TRUE_FALSE: 1
        }
    )
    context: Optional[Dict[str, Any]] = None


class QuestionGenerationResponse(BaseModel):
    """문제 생성 응답 모델"""
    success: bool
    questions: List[QuestionUnion]
    topic: str
    difficulty: DifficultyLevel
    total_count: int
    type_distribution: Optional[Dict[str, int]] = None
    generation_time: Optional[float] = None
    ai_model_used: Optional[str] = None


class ScoringResult(BaseModel):
    """채점 결과 모델"""
    score: float = Field(..., ge=0.0, le=1.0)
    feedback: str
    is_correct: Optional[bool] = None
    detailed_analysis: Optional[Dict[str, Any]] = None
    scoring_method: str
    ai_generated_feedback: bool = True
