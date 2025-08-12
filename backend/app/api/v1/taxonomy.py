from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.orm import SubjectTopic


router = APIRouter()


@router.get("/taxonomy/topics")
def get_topics(subject: str = Query(...), db: Session = Depends(get_db), _=Depends(require_role(["teacher", "admin"])) ) -> Dict[str, Any]:
    rows: List[SubjectTopic] = (
        db.query(SubjectTopic)
        .filter(SubjectTopic.subject_key == subject)
        .order_by(SubjectTopic.display_order.asc())
        .all()
    )
    return {"items": [{"topic_key": r.topic_key, "is_core": r.is_core, "display_order": r.display_order} for r in rows]}


