from pydantic import BaseModel
from typing import Optional, Dict, Any
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
    question_data: Optional[Dict[str, Any]] = None
    question_metadata: Optional[Dict[str, Any]] = None
    ai_generated: bool = False

class Question(QuestionBase):
    id: int
    created_at: datetime
    is_active: bool = True
    question_data: Optional[Dict[str, Any]] = None
    question_metadata: Optional[Dict[str, Any]] = None
    ai_generated: bool = False

    class Config:
        from_attributes = True
