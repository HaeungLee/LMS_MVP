from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from sqlalchemy import func, case
from app.core.database import SessionLocal
from app.models.orm import Question, Submission, SubmissionItem

router = APIRouter()

# 간단 캐시 (30초)
_CACHE: Dict[str, Any] = {"data": None, "ts": 0}
_CACHE_TTL = 30

@router.get("/dashboard/stats")
async def get_dashboard_stats(subject: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """대시보드용 통계 데이터를 반환합니다 (DB 기반)."""
    import time
    now = int(time.time())
    cache_key = f"stats::{subject or 'all'}"
    if _CACHE.get(cache_key) and now - _CACHE.get(f"ts::{cache_key}", 0) < _CACHE_TTL:
        return _CACHE[cache_key]

    try:
        db = SessionLocal()

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

        tq_q = db.query(func.count(Question.id))
        if subject:
            tq_q = tq_q.filter(Question.subject == subject)
        total_questions = int(tq_q.scalar() or 0)

        # 최근 활동: 최근 제출 3건
        recent_activity = []
        subs_q = db.query(Submission)
        if subject:
            subs_q = subs_q.filter(Submission.subject == subject)
        subs = subs_q.order_by(Submission.submitted_at.desc()).limit(3).all()
        for s in subs:
            percentage = 0
            try:
                percentage = round((s.total_score / s.max_score) * 100)
            except Exception:
                percentage = 0
            recent_activity.append({
                "submission_id": s.id,
                "date": (s.submitted_at.isoformat() if s.submitted_at else ""),
                "activity": f"{s.subject} 퀴즈 완료",
                "score": percentage,
            })

        # 진행률(임시 값 유지)
        progress_data = {
            "overall_progress": 65,
            "today_goal": "Python 자료구조",
            "completed_quizzes": len(subs),
            "total_quizzes": total_questions // 10 if total_questions else 0,
            "weak_points": ["집합(Set)", "리스트 컴프리헨션"],
            "strong_points": ["딕셔너리", "문자열"],
        }

        # 주제별 정답률(0.5 이상을 정답으로 간주)
        topic_accuracy: Dict[str, Dict[str, float]] = {}
        acc_q = db.query(
            SubmissionItem.topic.label("topic"),
            func.count(SubmissionItem.id).label("total"),
            func.sum(case((SubmissionItem.score >= 0.5, 1), else_=0)).label("correct"),
        ).join(Submission, Submission.id == SubmissionItem.submission_id)
        if subject:
            acc_q = acc_q.filter(Submission.subject == subject)
        acc_rows = acc_q.group_by(SubmissionItem.topic).all()
        for row in acc_rows:
            total = int(row.total or 0)
            correct = int(row.correct or 0)
            percentage = round((correct / total) * 100, 1) if total > 0 else 0.0
            topic_accuracy[row.topic] = {
                "correct": correct,
                "total": total,
                "percentage": percentage,
            }

        data = {
            "topics": topic_counts,
            "difficulties": difficulty_counts,
            "total_questions": total_questions,
            "progress": progress_data,
            "recent_activity": recent_activity,
            "topic_accuracy": topic_accuracy,
        }
        _CACHE[cache_key] = data
        _CACHE[f"ts::{cache_key}"] = now
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard data: {str(e)}")
    finally:
        try:
            db.close()
        except Exception:
            pass
