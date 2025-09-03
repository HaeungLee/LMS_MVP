from pydantic import BaseModel
from typing import List, Optional

class UserAnswer(BaseModel):
    question_id: int
    user_answer: str
    skipped: Optional[bool] = False

class Submission(BaseModel):
    user_answers: List[UserAnswer]

class QuestionResult(BaseModel):
    question_id: int
    user_answer: str
    correct_answer: str
    is_correct: bool
    score: float
    feedback: Optional[str] = None

class SubmissionResult(BaseModel):
    submission_id: str
    user_id: int
    total_score: float
    max_score: float
    percentage: float
    question_results: List[QuestionResult]
    ai_feedback: Optional[str] = None
    submitted_at: str

class FeedbackRequest(BaseModel):
    submission_id: str
    question_id: int
    feedback_type: str = "detailed"  # "detailed", "hint", "explanation"
    
class AIFeedbackResponse(BaseModel):
    feedback: str
    confidence: float
    suggestions: List[str] = []
