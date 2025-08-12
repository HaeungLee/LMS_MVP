import json
import os
import random
from fastapi import APIRouter, HTTPException, Query
from ...models.question import Question

router = APIRouter()

@router.get("/questions/{subject}", response_model=list[Question])
def get_questions(
    subject: str, 
    shuffle: bool = Query(default=True, description="문제를 셔플할지 여부"),
    easy_count: int = Query(default=4, description="쉬운 문제 개수"),
    medium_count: int = Query(default=4, description="보통 문제 개수"), 
    hard_count: int = Query(default=2, description="어려운 문제 개수")
):
    # 데이터 파일 경로를 절대 경로로 수정
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "db.json")
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 주제별로 필터링
        all_questions = [question for question in data["questions"] if question["subject"] == subject]
        
        if not shuffle:
            return all_questions[:10]  # 셔플 안 할 경우 처음 10개만
        
        # 난이도별로 분류
        easy_questions = [q for q in all_questions if q.get("difficulty", "easy") == "easy"]
        medium_questions = [q for q in all_questions if q.get("difficulty", "easy") == "medium"]
        hard_questions = [q for q in all_questions if q.get("difficulty", "easy") == "hard"]
        
        # 각 난이도별로 랜덤 선택
        selected_questions = []
        
        # easy 문제 선택
        if len(easy_questions) >= easy_count:
            selected_questions.extend(random.sample(easy_questions, easy_count))
        else:
            selected_questions.extend(easy_questions)
            # 부족한 만큼 medium에서 보충
            remaining = easy_count - len(easy_questions)
            if len(medium_questions) >= remaining:
                selected_questions.extend(random.sample(medium_questions, remaining))
                medium_questions = [q for q in medium_questions if q not in selected_questions[-remaining:]]
        
        # medium 문제 선택
        available_medium = [q for q in medium_questions if q not in selected_questions]
        if len(available_medium) >= medium_count:
            selected_questions.extend(random.sample(available_medium, medium_count))
        else:
            selected_questions.extend(available_medium)
        
        # hard 문제 선택
        available_hard = [q for q in hard_questions if q not in selected_questions]
        if len(available_hard) >= hard_count:
            selected_questions.extend(random.sample(available_hard, hard_count))
        else:
            selected_questions.extend(available_hard)
        
        # 전체 순서 셔플
        random.shuffle(selected_questions)
        
        return selected_questions
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Database file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Database file is corrupted")
