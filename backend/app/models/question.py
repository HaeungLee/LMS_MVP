from pydantic import BaseModel

class Question(BaseModel):
    id: int
    subject: str
    topic: str
    question_type: str
    code_snippet: str
    answer: str
    difficulty: str
    rubric: str
