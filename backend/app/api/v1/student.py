from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, case
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.orm import Submission, SubmissionItem, Subject, SubjectTopic, SubjectSettings, StudentAssignment


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

        # Assign 스코프 필터(초안): 해당 과목에 대해 학생 할당이 존재하면 그 토픽만 표기
        # (현재는 사용자 인증 컨텍스트 미도입으로 과목 단위 스코핑으로 제한)
        assigned_topics = set()
        try:
            assigns = (
                db.query(StudentAssignment)
                .filter(StudentAssignment.subject == subject)
                .all()
            )
            for a in assigns:
                if a.topic_key:
                    assigned_topics.add(a.topic_key)
        except Exception:
            assigned_topics = set()

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
            if assigned_topics and (m.topic_key not in assigned_topics):
                continue
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

        # streak/최근7일 시도수/평균 세션 시간(분)
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)

        recent7dAttempts = (
            db.query(func.count(Submission.id))
            .filter(Submission.subject == subject)
            .filter(Submission.submitted_at >= seven_days_ago)
            .scalar()
            or 0
        )
        # 간단 streak: 최근 7일 중 시도한 날의 최대 연속 카운트(간소화)
        days = (
            db.query(func.date_trunc('day', Submission.submitted_at))
            .filter(Submission.subject == subject)
            .filter(Submission.submitted_at >= seven_days_ago)
            .group_by(func.date_trunc('day', Submission.submitted_at))
            .all()
        )
        day_set = {d[0].date() for d in days if d and d[0]}
        streak = 0
        cur = 0
        for i in range(7):
            day = (now.date() - timedelta(days=i))
            if day in day_set:
                cur += 1
                streak = max(streak, cur)
            else:
                cur = 0

        # 평균 세션 시간(최근 14일, time_taken 초 단위 가정)
        avgSessionMin = (
            db.query(func.avg(Submission.time_taken))
            .filter(Submission.subject == subject)
            .filter(Submission.submitted_at >= fourteen_days_ago)
            .scalar()
        )
        avgSessionMin = float(avgSessionMin or 0) / 60.0

        # 최근 N회 성과(기본 5회)
        recentScores: List[Dict[str, Any]] = []
        recent_subs = (
            db.query(Submission)
            .filter(Submission.subject == subject)
            .order_by(Submission.submitted_at.desc())
            .limit(5)
            .all()
        )
        for s in recent_subs:
            pct = 0
            try:
                pct = round((s.total_score / s.max_score) * 100)
            except Exception:
                pct = 0
            recentScores.append({
                "date": s.submitted_at.isoformat() if s.submitted_at else None,
                "score_pct": pct,
                "submission_id": s.id,
            })

        # 강/중/약 버킷(도넛 대안): strong ≥0.8, medium 0.5~0.79, weak <0.5
        strong = sum(1 for _, st in accuracy_by_topic.items() if st >= 0.8)
        medium = sum(1 for _, st in accuracy_by_topic.items() if 0.5 <= st < 0.8)
        weak = sum(1 for _, st in accuracy_by_topic.items() if st < 0.5)
        strengthBuckets = {"strong": strong, "medium": medium, "weak": weak}

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
            "avgSessionMin": round(avgSessionMin, 1),
            "recentScores": recentScores,
            "strengthBuckets": strengthBuckets,
            "assign": {
                "subject": subject,
                "topic_keys": sorted(list(assigned_topics)) if assigned_topics else None,
            },
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


@router.get("/student/insights")
async def get_student_insights(subject: str = Query(...)) -> Dict[str, Any]:
    """오늘의 인사이트 v1: 요약/추천/델타(서버 계산값 기반, LLM 폴백 가능)"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)

        # 최근 7일 평균 점수 vs 직전 7일(간단 Δ)
        def avg_pct(start, end):
            subs = (
                db.query(Submission)
                .filter(Submission.subject == subject)
                .filter(Submission.submitted_at >= start)
                .filter(Submission.submitted_at < end)
                .all()
            )
            vals = []
            for s in subs:
                try:
                    vals.append((s.total_score / s.max_score) * 100.0)
                except Exception:
                    pass
            return (sum(vals) / len(vals)) if vals else 0.0

        avg_recent = avg_pct(seven_days_ago, now)
        avg_prev = avg_pct(seven_days_ago - timedelta(days=7), seven_days_ago)
        delta = round(avg_recent - avg_prev, 1)

        # streak/최근7일 시도
        recent_count = (
            db.query(func.count(Submission.id))
            .filter(Submission.subject == subject)
            .filter(Submission.submitted_at >= seven_days_ago)
            .scalar()
        ) or 0

        # 간단 요약/추천(템플릿)
        trend = "상승" if delta > 0 else ("유지" if delta == 0 else "하락")
        summary = f"최근 7일 평균 점수가 전 주 대비 {abs(delta)}pt {trend}했어요. 일관된 학습으로 streak를 이어가보세요."
        suggestions = [
            "최근 약점 토픽에서 1문제만 더 풀기",
            "학습 시간을 10분 늘려 복습 세션 추가",
        ]

        return {
            "summary": summary,
            "suggestions": suggestions,
            "deltas": {
                "score_7d_pct": round(avg_recent, 1),
                "delta_vs_prev_7d": delta,
                "recent7dAttempts": int(recent_count),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load insights: {str(e)}")
    finally:
        try:
            db.close()
        except Exception:
            pass


