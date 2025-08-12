from pydantic import BaseModel
from typing import List, Optional

class UserAnswer(BaseModel):
    question_id: int
    user_answer: str
    skipped: Optional[bool] = False

class Submission(BaseModel):
    user_answers: List[UserAnswer]
    subject: str
    time_taken: Optional[int] = None

class FeedbackRequest(BaseModel):
    question_id: int
    user_answer: str

class QuestionResult(BaseModel):
    question_id: int
    user_answer: str
    correct_answer: str
    score: float  # 0, 0.5, 1
    topic: str

class SubmissionResult(BaseModel):
    submission_id: Optional[str] = None
    total_score: float
    max_score: int
    results: List[QuestionResult]
    topic_analysis: dict  # 주제별 정답률
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    submitted_at: Optional[str] = None
