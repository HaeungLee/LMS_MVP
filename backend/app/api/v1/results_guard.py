from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import Submission, User


router = APIRouter()


@router.get("/results/secure/{submission_id}")
def get_results_secure(submission_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # 소유권 확인
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if sub.user_id != user.id and user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"ok": True}


