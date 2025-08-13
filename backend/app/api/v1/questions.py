import random
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from ...models.question import Question as QuestionModel
from ...core.database import get_db
from ...models.orm import Question as ORMQuestion

router = APIRouter()

@router.get("/questions/{subject}", response_model=list[QuestionModel])
def get_questions(
    subject: str,
    shuffle: bool = Query(default=True, description="문제를 셔플할지 여부"),
    easy_count: int = Query(default=4, description="쉬운 문제 개수"),
    medium_count: int = Query(default=4, description="보통 문제 개수"),
    hard_count: int = Query(default=2, description="어려운 문제 개수"),
    db: Session = Depends(get_db),
):
    try:
        # DB에서 과목별 문제 조회
        rows = db.query(ORMQuestion).filter(ORMQuestion.subject == subject, ORMQuestion.is_active == True).all()
        if not rows:
            return []

        # 난이도별 분류
        easy = [r for r in rows if (r.difficulty or '').lower() == 'easy']
        medium = [r for r in rows if (r.difficulty or '').lower() == 'medium']
        hard = [r for r in rows if (r.difficulty or '').lower() == 'hard']

        def pick(source, n):
            if n <= 0:
                return []
            if len(source) <= n:
                return list(source)
            return random.sample(source, n)

        selected = []
        selected.extend(pick(easy, easy_count))
        # 남은 medium에서
        remaining_medium = medium[:]
        selected.extend(pick(remaining_medium, medium_count))
        # hard
        remaining_hard = hard[:]
        selected.extend(pick(remaining_hard, hard_count))

        if shuffle:
            random.shuffle(selected)

        # 응답 모델에 맞춰 직렬화
        return [
            {
                "id": r.id,
                "subject": r.subject,
                "topic": r.topic,
                "question_type": r.question_type,
                "code_snippet": r.code_snippet,
                "answer": r.correct_answer,
                "difficulty": r.difficulty,
                "rubric": r.rubric or "",
            }
            for r in selected
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load questions: {e}")
