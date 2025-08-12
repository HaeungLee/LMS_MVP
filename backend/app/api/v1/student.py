from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, case
from app.core.database import SessionLocal
from app.models.orm import Submission, SubmissionItem, Subject, SubjectTopic, SubjectSettings


router = APIRouter()


@router.get("/student/learning-status")
async def get_learning_status(subject: str = Query(...)) -> Dict[str, Any]:
    """학생 학습 지표: 커버리지/약점/토픽 진행/연속학습/최근7일 시도수"""
    db = SessionLocal()
    try:
        # 설정/매핑 로드
        subj = db.query(Subject).filter(Subject.key == subject).first()
        if not subj:
            raise HTTPException(status_code=400, detail="Unknown subject")

        settings = db.query(SubjectSettings).filter(SubjectSettings.subject_key == subject).first()
        min_attempts = int(getattr(settings, "min_attempts", 3))
        min_accuracy = float(getattr(settings, "min_accuracy", 0.6))

        mappings = (
            db.query(SubjectTopic)
            .filter(SubjectTopic.subject_key == subject)
            .order_by(SubjectTopic.display_order.asc())
            .all()
        )
        total_core_weight = sum((m.weight or 1.0) for m in mappings if m.is_core and m.show_in_coverage)

        # 토픽별 집계
        acc_q = (
            db.query(
                SubmissionItem.topic.label("topic"),
                func.count(SubmissionItem.id).label("attempts"),
                func.sum(case((SubmissionItem.score >= 0.5, 1), else_=0)).label("correct"),
            )
            .join(Submission, Submission.id == SubmissionItem.submission_id)
        )
        if subject:
            acc_q = acc_q.filter(Submission.subject == subject)
        acc_rows = acc_q.group_by(SubmissionItem.topic).all()

        attempts_by_topic = {r.topic: int(r.attempts or 0) for r in acc_rows}
        accuracy_by_topic: Dict[str, float] = {}
        for r in acc_rows:
            a = int(r.attempts or 0)
            c = int(r.correct or 0)
            accuracy_by_topic[r.topic] = (c / a) if a > 0 else 0.0

        # 커버리지/약점 계산
        covered_weight = 0.0
        topic_progress = []
        weaknesses = []
        for m in mappings:
            attempts = attempts_by_topic.get(m.topic_key, 0)
            acc = accuracy_by_topic.get(m.topic_key, 0.0)
            topic_progress.append(
                {
                    "topic_key": m.topic_key,
                    "title": m.topic_key,
                    "attempts": attempts,
                    "accuracy": round(acc, 4),
                    "display_order": m.display_order,
                }
            )
            if m.is_core and m.show_in_coverage:
                completed = (attempts >= min_attempts) or (acc >= min_accuracy)
                if completed:
                    covered_weight += (m.weight or 1.0)
            if attempts >= min_attempts:
                weaknesses.append(
                    {
                        "topic_key": m.topic_key,
                        "title": m.topic_key,
                        "accuracy": round(acc, 4),
                        "attempts": attempts,
                    }
                )

        weaknesses.sort(key=lambda x: (x["accuracy"], -x["attempts"]))
        weaknesses = weaknesses[:3]

        # streak/최근7일 시도수(간단 집계)
        recent7dAttempts = (
            db.query(func.count(Submission.id)).filter(Submission.subject == subject).scalar() or 0
        )
        streak = 0  # 상세 로직은 후속(캘린더 기반)

        return {
            "coverage": {
                "value": (covered_weight / total_core_weight) if total_core_weight > 0 else 0,
                "covered_weight": covered_weight,
                "total_core_weight": total_core_weight,
                "min_attempts": min_attempts,
                "min_accuracy": min_accuracy,
                "subject_version": subj.version or "v1",
            },
            "weaknesses": weaknesses,
            "topic_progress": sorted(topic_progress, key=lambda x: x["display_order"]),
            "streak": int(streak),
            "recent7dAttempts": int(recent7dAttempts),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load learning status: {str(e)}")
    finally:
        try:
            db.close()
        except Exception:
            pass


