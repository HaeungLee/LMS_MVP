import random
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from ...models.question import Question as QuestionModel
from ...core.database import get_db
from ...models.orm import Question as ORMQuestion

router = APIRouter()

@router.get("/questions/{subject}")
def get_questions(
    subject: str,
    shuffle: bool = Query(default=True, description="문제를 셔플할지 여부"),
    easy_count: int = Query(default=4, description="쉬운 문제 개수"),
    medium_count: int = Query(default=4, description="보통 문제 개수"),
    hard_count: int = Query(default=2, description="어려운 문제 개수"),
    db: Session = Depends(get_db),
):
    try:
        print(f"🔍 Questions API 호출: subject={subject}, easy_count={easy_count}, medium_count={medium_count}, hard_count={hard_count}")

        # DB에서 과목별 문제 조회
        rows = db.query(ORMQuestion).filter(ORMQuestion.subject == subject, ORMQuestion.is_active == True).all()
        print(f"📊 DB에서 조회된 문제 개수: {len(rows)}")

        if not rows:
            print("⚠️ 해당 과목의 문제가 없습니다")
            return []

        # 난이도별 분류
        easy = [r for r in rows if (r.difficulty or '').lower() == 'easy']
        medium = [r for r in rows if (r.difficulty or '').lower() == 'medium']
        hard = [r for r in rows if (r.difficulty or '').lower() == 'hard']

        print(f"📊 난이도별 분류: Easy={len(easy)}, Medium={len(medium)}, Hard={len(hard)}")

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

        print(f"📊 선택된 문제 개수: {len(selected)}")

        if shuffle:
            random.shuffle(selected)

        # 프론트엔드에서 기대하는 형식으로 변환
        result = []
        for r in selected:
            try:
                question_data = {
                    "id": r.id,
                    "subject": r.subject,
                    "topic": r.topic,
                    "question_type": r.question_type,
                    "code_snippet": r.code_snippet,
                    "answer": r.correct_answer,  # 프론트엔드 호환성을 위해 answer로 매핑
                    "difficulty": r.difficulty,
                    "rubric": r.rubric or "",
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "is_active": r.is_active
                }
                result.append(question_data)
            except Exception as item_error:
                print(f"❌ 문제 {r.id} 변환 실패: {item_error}")
                continue

        print(f"✅ 최종 반환 문제 개수: {len(result)}")
        return result

    except Exception as e:
        print(f"❌ Questions API 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to load questions: {str(e)}")
