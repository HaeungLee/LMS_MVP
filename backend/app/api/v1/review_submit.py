"""
복습 제출 API

사용자가 복습 세션에서 문제를 풀고 제출
- 답안 검증
- 결과 저장
- 다음 복습 날짜 계산
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User, Submission
from app.api.v1.review_system import calculate_next_review_date

router = APIRouter()


# ============= Models =============

class ReviewSubmitRequest(BaseModel):
    """복습 제출 요청"""
    session_id: str
    problem_id: int
    user_answer: str
    time_spent: int  # 초 단위
    

class ReviewSubmitResponse(BaseModel):
    """복습 제출 응답"""
    is_correct: bool
    feedback: str
    next_review_date: Optional[datetime]
    current_streak: int  # 이 문제의 연속 정답 횟수
    

# ============= API Endpoints =============

@router.post("/submit", response_model=ReviewSubmitResponse)
async def submit_review_answer(
    request: ReviewSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    복습 답안 제출
    
    - 답안 검증
    - 결과 DB 저장
    - 다음 복습 날짜 계산 (간격 반복 학습)
    """
    
    # 임시: 간단한 정답 검증 (실제로는 Question 테이블에서 정답 가져와서 비교)
    # 지금은 "5" 또는 "fibonacci" 포함하면 정답으로 처리
    user_answer_lower = request.user_answer.lower().strip()
    is_correct = "5" in user_answer_lower or "fibonacci" in user_answer_lower
    
    # 제출 기록 저장
    submission = Submission(
        user_id=current_user.id,
        problem_id=request.problem_id,
        user_code=request.user_answer,
        is_correct=is_correct,
        submitted_at=datetime.now()
    )
    db.add(submission)
    db.commit()
    
    # 이 문제의 이전 시도 횟수 계산
    previous_attempts = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.problem_id == request.problem_id
    ).count()
    
    # 연속 정답 횟수 계산
    recent_submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.problem_id == request.problem_id
    ).order_by(Submission.submitted_at.desc()).limit(5).all()
    
    current_streak = 0
    for sub in recent_submissions:
        if sub.is_correct:
            current_streak += 1
        else:
            break
    
    # 다음 복습 날짜 계산
    next_review_date = calculate_next_review_date(
        last_attempt=datetime.now(),
        attempt_count=current_streak,
        was_correct=is_correct
    )
    
    # 피드백 메시지
    if is_correct:
        if current_streak == 1:
            feedback = "정답입니다! 🎉 다음 복습: 1일 후"
        elif current_streak == 2:
            feedback = "연속 정답! 💪 다음 복습: 3일 후"
        elif current_streak >= 3:
            feedback = f"{current_streak}연속 정답! 🔥 완벽해요! 다음 복습: {7 if current_streak == 3 else 14 if current_streak == 4 else 30}일 후"
        else:
            feedback = "정답입니다! ✅"
    else:
        feedback = "아쉽지만 틀렸습니다. 💡 1일 후 다시 복습해봅시다!"
    
    return ReviewSubmitResponse(
        is_correct=is_correct,
        feedback=feedback,
        next_review_date=next_review_date,
        current_streak=current_streak
    )
