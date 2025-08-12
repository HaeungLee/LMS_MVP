from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role, require_csrf
from app.models.orm import Question


router = APIRouter()


class QuestionCreateDto(BaseModel):
    subject: str
    topic: str
    question_type: str
    code_snippet: str
    correct_answer: str
    difficulty: str = "easy"
    rubric: Optional[str] = None
    created_by: Optional[str] = None
    is_active: bool = True


class QuestionUpdateDto(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    question_type: Optional[str] = None
    code_snippet: Optional[str] = None
    correct_answer: Optional[str] = None
    difficulty: Optional[str] = None
    rubric: Optional[str] = None
    created_by: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/admin/questions")
def list_questions(
    subject: Optional[str] = Query(default=None),
    topic: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(require_role(["teacher", "admin"]))
) -> Dict:
    qry = db.query(Question)
    if subject:
        qry = qry.filter(Question.subject == subject)
    if topic:
        qry = qry.filter(Question.topic == topic)
    if q is not None and len(q.strip()) > 0:
        term = f"%{q.strip()}%"
        qry = qry.filter(
            (Question.code_snippet.ilike(term)) | (Question.correct_answer.ilike(term)) | (Question.topic.ilike(term))
        )
    total = qry.count()
    rows: List[Question] = qry.order_by(Question.id.desc()).offset(offset).limit(limit).all()
    data = [
        {
            "id": r.id,
            "subject": r.subject,
            "topic": r.topic,
            "question_type": r.question_type,
            "code_snippet": r.code_snippet,
            "correct_answer": r.correct_answer,
            "difficulty": r.difficulty,
            "rubric": r.rubric,
            "created_by": r.created_by,
            "created_at": (r.created_at.isoformat() if r.created_at else None),
            "is_active": r.is_active,
        }
        for r in rows
    ]
    return {"total": total, "items": data}


@router.post("/admin/questions")
def create_question(request: Request, body: QuestionCreateDto, db: Session = Depends(get_db), _=Depends(require_role(["teacher", "admin"]))):
    require_csrf(request)
    rec = Question(
        subject=body.subject,
        topic=body.topic,
        question_type=body.question_type,
        code_snippet=body.code_snippet,
        correct_answer=body.correct_answer,
        difficulty=body.difficulty,
        rubric=body.rubric,
        created_by=body.created_by,
        is_active=body.is_active,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {"id": rec.id}


@router.put("/admin/questions/{qid}")
def update_question(qid: int, request: Request, body: QuestionUpdateDto, db: Session = Depends(get_db), _=Depends(require_role(["teacher", "admin"]))):
    require_csrf(request)
    rec: Question = db.query(Question).filter(Question.id == qid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Question not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(rec, field, value)
    db.commit()
    return {"ok": True}


@router.delete("/admin/questions/{qid}")
def delete_question(qid: int, request: Request, db: Session = Depends(get_db), _=Depends(require_role(["teacher", "admin"]))):
    require_csrf(request)
    rec: Question = db.query(Question).filter(Question.id == qid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(rec)
    db.commit()
    return {"ok": True}


