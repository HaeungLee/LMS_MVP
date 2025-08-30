from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionBase(BaseModel):
    subject: str
    topic: str
    question_type: str
    code_snippet: str
    correct_answer: str
    difficulty: str
    rubric: Optional[str] = None

class QuestionCreate(QuestionBase):
    created_by: Optional[str] = None
    is_active: bool = True

class Question(QuestionBase):
    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True
