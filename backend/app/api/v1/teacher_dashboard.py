from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case

from app.core.database import SessionLocal
from app.core.security import require_role
from app.models.orm import Question, Submission, SubmissionItem


router = APIRouter()


@router.get("/teacher/dashboard/stats")
async def get_teacher_dashboard_stats(subject: str | None = Query(default=None), _=Depends(require_role(["teacher", "admin"])) ) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        # 주제별 문제 수
        topic_counts: Dict[str, int] = {}
        topic_q = db.query(Question.topic, func.count(Question.id))
        if subject:
            topic_q = topic_q.filter(Question.subject == subject)
        for topic, count in topic_q.group_by(Question.topic).all():
            topic_counts[topic] = int(count)

        # 난이도별 문제 수
        difficulty_counts: Dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}
        diff_q = db.query(Question.difficulty, func.count(Question.id))
        if subject:
            diff_q = diff_q.filter(Question.subject == subject)
        for difficulty, count in diff_q.group_by(Question.difficulty).all():
            difficulty_counts[difficulty] = int(count)

        # 최근 제출 10건(학생 전역)
        recent_submissions = []
        subs_q = db.query(Submission)
        if subject:
            subs_q = subs_q.filter(Submission.subject == subject)
        for s in subs_q.order_by(Submission.submitted_at.desc()).limit(10).all():
            percentage = 0
            try:
                percentage = round((s.total_score / s.max_score) * 100)
            except Exception:
                percentage = 0
            recent_submissions.append({
                "submission_id": s.id,
                "user_id": s.user_id,
                "subject": s.subject,
                "submitted_at": (s.submitted_at.isoformat() if s.submitted_at else None),
                "score_pct": percentage,
            })

        # 주제별 정답률
        topic_accuracy: Dict[str, Dict[str, float]] = {}
        acc_q = db.query(
            SubmissionItem.topic.label("topic"),
            func.count(SubmissionItem.id).label("total"),
            func.sum(case((SubmissionItem.score >= 0.5, 1), else_=0)).label("correct"),
        ).join(Submission, Submission.id == SubmissionItem.submission_id)
        if subject:
            acc_q = acc_q.filter(Submission.subject == subject)
        for row in acc_q.group_by(SubmissionItem.topic).all():
            total = int(row.total or 0)
            correct = int(row.correct or 0)
            pct = round((correct / total) * 100, 1) if total > 0 else 0.0
            topic_accuracy[row.topic] = {"correct": correct, "total": total, "percentage": pct}

        total_questions_q = db.query(func.count(Question.id))
        if subject:
            total_questions_q = total_questions_q.filter(Question.subject == subject)
        total_questions = int(total_questions_q.scalar() or 0)

        return {
            "topics": topic_counts,
            "difficulties": difficulty_counts,
            "total_questions": total_questions,
            "recent_submissions": recent_submissions,
            "topic_accuracy": topic_accuracy,
        }
    finally:
        try:
            db.close()
        except Exception:
            pass


