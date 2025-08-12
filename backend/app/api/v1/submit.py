import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from ...models.submission import (
    Submission,
    SubmissionResult,
    QuestionResult,
    FeedbackRequest,
)
from ...services.scoring_service import scoring_service
from typing import Dict, List
import uuid
from ...core.database import SessionLocal
from ...core.security import get_current_user, require_csrf
from ...models.orm import User as OrmUser
from ...models.orm import Submission as OrmSubmission, SubmissionItem as OrmSubmissionItem

router = APIRouter()

# 피드백 저장소 (실제 환경에서는 DB 사용)
feedback_cache: Dict[str, str] = {}
submission_results_store: Dict[str, Dict] = {}

# 세션 팩토리 (Phase 1: 공용 SessionLocal 사용)

@router.post("/submit", response_model=SubmissionResult)
async def submit_answers(
    submission: Submission,
    request: Request,
    current_user: OrmUser = Depends(get_current_user),
):
    # CSRF 검증
    require_csrf(request)
    """답안 제출 및 즉시 채점"""
    try:
        results = []
        total_score = 0.0
        
        for user_answer in submission.user_answers:
            # 문제 정보 조회
            question = scoring_service.get_question_by_id(user_answer.question_id)
            if not question:
                raise HTTPException(status_code=404, detail=f"Question {user_answer.question_id} not found")
            
            # 채점
            score = scoring_service.score_answer(question, user_answer.user_answer)
            total_score += score
            
            result = QuestionResult(
                question_id=user_answer.question_id,
                user_answer=user_answer.user_answer,
                correct_answer=question["answer"],
                score=score,
                topic=question["topic"]
            )
            results.append(result)
        
        # 주제별 분석
        topic_analysis = scoring_service.analyze_by_topic([r.dict() for r in results])

        # 간단 요약/추천 생성 (Phase 0 템플릿)
        max_score = len(submission.user_answers)
        percent = round((total_score / max_score) * 100, 1) if max_score > 0 else 0
        weak_topics: List[str] = [t for t, s in topic_analysis.items() if s.get("percentage", 0) < 70]
        summary = f"총점 {total_score}/{max_score}점 ({percent}%). 개선 필요 영역: {', '.join(weak_topics) if weak_topics else '없음'}."
        recommendations = [f"'{t}' 관련 문제를 추가로 연습하세요" for t in weak_topics][:5]

        # submission_id 생성 및 메모리 저장 (Phase 1에서는 DB에도 영속화)
        submission_id = str(uuid.uuid4())
        submission_results_store[submission_id] = {
            "submission_id": submission_id,
            "total_score": total_score,
            "max_score": max_score,
            "results": [r.dict() for r in results],
            "topic_analysis": topic_analysis,
            "summary": summary,
            "recommendations": recommendations,
            "submitted_at": __import__("datetime").datetime.now().isoformat(),
        }

        # DB 저장 (익명 제출 금지: current_user.id 사용)
        try:
            db = SessionLocal()
            orm_sub = OrmSubmission(
                id=submission_id,
                user_id=current_user.id,
                subject=submission.subject,
                total_score=total_score,
                max_score=max_score,
                time_taken=submission.time_taken,
                summary=summary,
                recommendations_json=__import__("json").dumps(recommendations, ensure_ascii=False),
            )
            db.add(orm_sub)
            db.flush()

            for r in results:
                db.add(OrmSubmissionItem(
                    submission_id=submission_id,
                    question_id=r.question_id,
                    user_answer=r.user_answer,
                    skipped=False,
                    score=r.score,
                    correct_answer=r.correct_answer,
                    topic=r.topic,
                ))

            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        return SubmissionResult(
            submission_id=submission_id,
            total_score=total_score,
            max_score=max_score,
            results=results,
            topic_analysis=topic_analysis,
            summary=summary,
            recommendations=recommendations,
            submitted_at=submission_results_store[submission_id]["submitted_at"],
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@router.post("/feedback")
async def request_feedback(request: Request, body: FeedbackRequest, background_tasks: BackgroundTasks):
    require_csrf(request)
    """AI 피드백 요청 (비동기 처리)"""
    try:
        question = scoring_service.get_question_by_id(body.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # 채점
        score = scoring_service.score_answer(question, body.user_answer)
        
        # 캐시 키 생성
        cache_key = f"{body.question_id}_{hash(body.user_answer)}"
        
        # 백그라운드에서 피드백 생성
        background_tasks.add_task(generate_feedback_async, cache_key, question, body.user_answer, score)
        
        return {"message": "Feedback generation started", "cache_key": cache_key}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback request failed: {str(e)}")

@router.get("/feedback/{cache_key}")
async def get_feedback(cache_key: str):
    """생성된 피드백 조회"""
    if cache_key in feedback_cache:
        feedback = feedback_cache[cache_key]
        # 한번 조회하면 캐시에서 제거 (메모리 절약)
        del feedback_cache[cache_key]
        return {"feedback": feedback, "status": "ready"}
    else:
        return {"status": "processing"}

@router.get("/results/{submission_id}")
async def get_results(submission_id: str):
    """제출 결과 조회 (Phase 1: DB 우선, 없으면 메모리 폴백)"""
    # DB 조회
    try:
        db = SessionLocal()
        orm_sub = db.query(OrmSubmission).filter(OrmSubmission.id == submission_id).first()
        if orm_sub:
            items = db.query(OrmSubmissionItem).filter(OrmSubmissionItem.submission_id == submission_id).all()
            results: List[QuestionResult] = []
            for it in items:
                results.append(QuestionResult(
                    question_id=it.question_id,
                    user_answer=it.user_answer,
                    correct_answer=it.correct_answer,
                    score=it.score,
                    topic=it.topic,
                ))
            # 주제별 분석 재계산 (정합 보장)
            topic_analysis = scoring_service.analyze_by_topic([r.dict() for r in results])
            # DB 저장된 요약/추천 사용, 없으면 메모리 폴백
            mem = submission_results_store.get(submission_id, {})
            summary = orm_sub.summary or mem.get("summary")
            try:
                recommendations = __import__("json").loads(orm_sub.recommendations_json) if orm_sub.recommendations_json else mem.get("recommendations")
            except Exception:
                recommendations = mem.get("recommendations")
            submitted_at = orm_sub.submitted_at.isoformat() if orm_sub.submitted_at else mem.get("submitted_at")
            return SubmissionResult(
                submission_id=submission_id,
                total_score=orm_sub.total_score,
                max_score=orm_sub.max_score,
                results=results,
                topic_analysis=topic_analysis,
                summary=summary,
                recommendations=recommendations,
                submitted_at=submitted_at,
            )
    finally:
        try:
            db.close()
        except Exception:
            pass

    # 메모리 폴백
    data = submission_results_store.get(submission_id)
    if not data:
        raise HTTPException(status_code=404, detail="Submission not found")
    return data

async def generate_feedback_async(cache_key: str, question: Dict, user_answer: str, score: float):
    """백그라운드에서 AI 피드백 생성"""
    try:
        # 실제로는 시간이 걸리는 AI 호출이므로 딜레이 추가
        await asyncio.sleep(2)  # 2초 딜레이로 실제 AI 호출 시뮬레이션
        
        feedback = await scoring_service.generate_ai_feedback(question, user_answer, score)
        feedback_cache[cache_key] = feedback
        
    except Exception as e:
        feedback_cache[cache_key] = f"피드백 생성 중 오류가 발생했습니다: {str(e)}"
