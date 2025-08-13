from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import case, asc, desc

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
    sort_by: Optional[str] = Query(default="latest"),
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

    # sorting
    s = (sort_by or "latest").strip().lower()
    if s == "difficulty_asc":
        diff_order = case(
            (
                (Question.difficulty == "easy", 1),
                (Question.difficulty == "medium", 2),
                (Question.difficulty == "hard", 3),
            ),
            else_=4,
        )
        qry = qry.order_by(asc(diff_order), desc(Question.id))
    elif s == "difficulty_desc":
        diff_order = case(
            (
                (Question.difficulty == "hard", 1),
                (Question.difficulty == "medium", 2),
                (Question.difficulty == "easy", 3),
            ),
            else_=4,
        )
        qry = qry.order_by(asc(diff_order), desc(Question.id))
    elif s == "topic_asc":
        qry = qry.order_by(asc(Question.topic), desc(Question.id))
    else:
        qry = qry.order_by(desc(Question.id))  # latest

    rows: List[Question] = qry.offset(offset).limit(limit).all()
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


@router.post("/admin/questions/import")
async def import_questions(
    request: Request,
    file: UploadFile = File(...),
    dry_run: bool = Query(default=False),
    db: Session = Depends(get_db),
    _=Depends(require_role(["teacher", "admin"]))
) -> Dict:
    """Bulk import questions from JSON or CSV. JSON expects list of records.
    Required fields per record: subject, topic, question_type, code_snippet, correct_answer, difficulty
    """
    require_csrf(request)
    content = await file.read()
    name = (file.filename or '').lower()
    text = content.decode('utf-8', errors='ignore')

    records = []
    errors: list[str] = []

    try:
        if name.endswith('.json') or file.content_type == 'application/json':
            import json as _json
            data = _json.loads(text)
            if isinstance(data, dict):
                # accept { items: [...] }
                data = data.get('items', [])
            if not isinstance(data, list):
                raise ValueError('JSON must be a list of records')
            records = data
        else:
            # assume CSV
            import csv
            from io import StringIO
            reader = csv.DictReader(StringIO(text))
            records = list(reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    required = [
        'subject', 'topic', 'question_type', 'code_snippet', 'correct_answer', 'difficulty'
    ]
    inserted = 0
    for idx, rec in enumerate(records, start=1):
        # normalize keys
        r = { (k.strip() if isinstance(k, str) else k): (v.strip() if isinstance(v, str) else v) for k, v in rec.items() }
        missing = [k for k in required if not r.get(k)]
        if missing:
            errors.append(f"row {idx}: missing fields {missing}")
            continue
        if dry_run:
            continue
        try:
            q = Question(
                subject=r['subject'],
                topic=r['topic'],
                question_type=r['question_type'],
                code_snippet=r['code_snippet'],
                correct_answer=r['correct_answer'],
                difficulty=r['difficulty'],
                rubric=r.get('rubric'),
                created_by=r.get('created_by'),
                is_active=True,
            )
            db.add(q)
            inserted += 1
        except Exception as e:
            errors.append(f"row {idx}: {e}")
    if not dry_run:
        db.commit()
    return {"ok": True, "total": len(records), "inserted": (0 if dry_run else inserted), "dry_run": dry_run, "errors": errors[:100]}


@router.delete("/admin/questions/{qid}")
def delete_question(qid: int, request: Request, db: Session = Depends(get_db), _=Depends(require_role(["teacher", "admin"]))):
    require_csrf(request)
    rec: Question = db.query(Question).filter(Question.id == qid).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(rec)
    db.commit()
    return {"ok": True}


