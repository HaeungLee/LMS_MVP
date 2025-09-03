import random
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from ...models.question import Question as QuestionModel
from ...core.database import get_db
from ...models.orm import Question as ORMQuestion

router = APIRouter()

@router.get("/questions/{subject}")
async def get_questions(
    subject: str,
    topic: str = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """과목별 문제 조회"""
    try:
        query = db.query(ORMQuestion).filter(ORMQuestion.subject == subject)
        
        if topic:
            query = query.filter(ORMQuestion.topic == topic)
        
        questions = query.limit(limit).all()
        
        return {
            "questions": [
                {
                    "id": q.id,
                    "subject": q.subject,
                    "topic": q.topic,
                    "question_type": q.question_type,
                    "code_snippet": q.code_snippet,
                    "difficulty": q.difficulty,
                    "taxonomy_level": q.taxonomy_level
                }
                for q in questions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/random/{subject}")
async def get_random_question(
    subject: str,
    topic: str = Query(None),
    difficulty: str = Query(None),
    db: Session = Depends(get_db)
):
    """랜덤 문제 조회"""
    try:
        query = db.query(ORMQuestion).filter(ORMQuestion.subject == subject)
        
        if topic:
            query = query.filter(ORMQuestion.topic == topic)
        if difficulty:
            query = query.filter(ORMQuestion.difficulty == difficulty)
        
        questions = query.all()
        
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found")
        
        question = random.choice(questions)
        
        return {
            "id": question.id,
            "subject": question.subject,
            "topic": question.topic,
            "question_type": question.question_type,
            "code_snippet": question.code_snippet,
            "correct_answer": question.correct_answer,
            "difficulty": question.difficulty,
            "taxonomy_level": question.taxonomy_level,
            "hint": question.hint,
            "explanation": question.explanation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/topics/{subject}")
async def get_topics_by_subject(
    subject: str,
    db: Session = Depends(get_db)
):
    """과목별 토픽 목록 조회"""
    try:
        topics = db.query(ORMQuestion.topic).filter(
            ORMQuestion.subject == subject
        ).distinct().all()
        
        return {
            "subject": subject,
            "topics": [topic[0] for topic in topics if topic[0]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
