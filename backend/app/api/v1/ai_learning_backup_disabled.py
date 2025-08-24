from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.security import get_current_user
from app.models.orm import User
from app.services.ai_question_generator import ai_question_generator
# from app.services.curriculum_manager import curriculum_manager  # 임시 주석

router = APIRouter()


@router.get("/daily-plan", response_model=Dict[str, Any])
async def get_daily_learning_plan(
    subject: str = Query("python_basics", description="학습 과목"),
    current_user: User = Depends(get_current_user)
):
    """일일 맞춤 학습 계획 조회"""
    try:
        # TODO: curriculum_manager 기능 복구 후 활성화
        # daily_plan = await curriculum_manager.get_daily_learning_plan(
        #     user_id=current_user.id,
        #     subject=subject
        # )
        
        # 임시 응답
        daily_plan = {
            "date": datetime.now().isoformat(),
            "user_id": current_user.id,
            "subject": subject,
            "current_topic": "기초",
            "recommended_questions": 5,
            "note": "AI 학습 시스템이 곧 활성화됩니다."
        }
        
        return {
            "success": True,
            "daily_plan": daily_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"일일 계획 생성 실패: {str(e)}")


@router.post("/generate-questions")
async def generate_questions_for_topic(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """주제별 AI 문제 생성"""
    
    # 교사/관리자만 접근 가능
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    topic = request.get("topic")
    difficulty = request.get("difficulty", "easy")
    count = min(request.get("count", 5), 10)  # 최대 10개로 제한
    
    if not topic:
        raise HTTPException(status_code=400, detail="주제를 입력해주세요")
    
    try:
        questions = await ai_question_generator.generate_questions_for_daily_curriculum(
            subject=request.get("subject", "python_basics"),
            topic=topic,
            difficulty=difficulty,
            count=count
        )
        
        return {
            "success": True,
            "questions": questions,
            "topic": topic,
            "difficulty": difficulty,
            "generated_count": len(questions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문제 생성 실패: {str(e)}")


@router.post("/adaptive-questions")
async def generate_adaptive_questions(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """학습자 수준에 맞는 적응형 문제 생성"""
    
    subject = request.get("subject", "python_basics")
    recent_scores = request.get("recent_scores", [])
    preferred_difficulty = request.get("preferred_difficulty", "medium")
    
    try:
        # 최근 점수를 바탕으로 적절한 난이도 결정
        if recent_scores:
            avg_score = sum(recent_scores) / len(recent_scores)
            if avg_score >= 0.8:
                difficulty = "hard"
            elif avg_score >= 0.6:
                difficulty = "medium"
            else:
                difficulty = "easy"
        else:
            difficulty = preferred_difficulty
        
        # AI 문제 생성기를 사용하여 문제 생성
        questions = await ai_question_generator.generate_questions_for_daily_curriculum(
            subject=subject,
            topic=request.get("topic", "기초"),
            difficulty=difficulty,
            count=5
        )
        
        return {
            "success": True,
            "questions": questions,
            "determined_difficulty": difficulty,
            "average_recent_score": sum(recent_scores) / len(recent_scores) if recent_scores else 0,
            "adaptation_reason": f"최근 평균 점수를 바탕으로 {difficulty} 난이도를 선택했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"적응형 문제 생성 실패: {str(e)}")


@router.get("/class-overview", response_model=Dict[str, Any])
async def get_class_overview(
    subject: str = Query("python_basics", description="학습 과목"),
    current_user: User = Depends(get_current_user)
):
    """반 전체 학습 현황 개요"""
    
    # 교사/관리자만 접근 가능
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    try:
        # TODO: curriculum_manager 기능 복구 후 활성화
        # class_overview = await curriculum_manager.get_class_overview(
        #     teacher_id=current_user.id,
        #     subject=subject
        # )
        
        # 임시 응답
        class_overview = {
            "teacher_id": current_user.id,
            "subject": subject,
            "overview_date": datetime.now().isoformat(),
            "total_students": 25,
            "active_students": 20,
            "average_progress": 75.5,
            "note": "AI 학습 분석 시스템이 곧 활성화됩니다."
        }
        
        return {
            "success": True,
            "class_overview": class_overview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"반 현황 조회 실패: {str(e)}")


@router.post("/assign-learning")
async def assign_learning_to_student(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """학생에게 개별 학습 과제 배정"""
    
    # 교사/관리자만 접근 가능
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    
    student_id = request.get("student_id")
    subject = request.get("subject")
    topic = request.get("topic")
    target_date = request.get("target_date")
    
    if not all([student_id, subject, topic]):
        raise HTTPException(status_code=400, detail="학생 ID, 과목, 주제를 모두 입력해주세요")
    
    try:
        # TODO: curriculum_manager 기능 복구 후 활성화
        # success = await curriculum_manager.assign_learning_task(
        #     teacher_id=current_user.id,
        #     student_id=student_id,
        #     subject=subject,
        #     topic=topic,
        #     target_date=target_date
        # )
        
        # 임시 응답
        success = True
        
        return {
            "success": success,
            "message": "학습 과제가 성공적으로 배정되었습니다.",
            "assignment_details": {
                "student_id": student_id,
                "subject": subject,
                "topic": topic,
                "assigned_by": current_user.id,
                "assigned_at": datetime.now().isoformat(),
                "target_date": target_date
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"과제 배정 실패: {str(e)}")


@router.get("/learning-recommendations", response_model=Dict[str, Any])
async def get_learning_recommendations(
    subject: str = Query("python_basics", description="학습 과목"),
    current_user: User = Depends(get_current_user)
):
    """개인별 학습 추천"""
    try:
        # TODO: curriculum_manager 기능 복구 후 활성화
        # recommendations = await curriculum_manager.get_personalized_recommendations(
        #     user_id=current_user.id,
        #     subject=subject
        # )
        
        # 임시 응답
        recommendations = {
            "user_id": current_user.id,
            "subject": subject,
            "recommended_topics": ["변수와 자료형", "조건문"],
            "next_difficulty": "medium",
            "estimated_study_time": "30분",
            "note": "AI 추천 시스템이 곧 활성화됩니다."
        }
        
        return {
            "success": True,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 실패: {str(e)}")


@router.get("/weakness-analysis", response_model=Dict[str, Any])
async def analyze_student_weaknesses(
    subject: str = Query("python_basics", description="학습 과목"),
    current_user: User = Depends(get_current_user)
):
    """학습자 취약점 분석"""
    try:
        # TODO: AI 기반 취약점 분석 구현
        weaknesses = await ai_question_generator.analyze_student_weaknesses(
            user_id=current_user.id,
            subject=subject
        )
        
        return {
            "success": True,
            "weaknesses": weaknesses,
            "subject": subject,
            "analysis_date": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"취약점 분석 실패: {str(e)}")


@router.post("/question-quality-feedback")
async def submit_question_quality_feedback(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """AI 생성 문제 품질 피드백 수집"""
    
    question_id = request.get("question_id")
    quality_score = request.get("quality_score")  # 1-5점
    feedback_text = request.get("feedback_text", "")
    
    if not question_id or not quality_score:
        raise HTTPException(status_code=400, detail="문제 ID와 품질 점수를 입력해주세요")
    
    try:
        # 실제로는 피드백을 DB에 저장하여 AI 모델 개선에 활용
        feedback_data = {
            "question_id": question_id,
            "user_id": current_user.id,
            "quality_score": quality_score,
            "feedback_text": feedback_text,
            "submitted_at": datetime.now().isoformat()
        }
        
        # TODO: 피드백 데이터를 데이터베이스에 저장
        
        return {
            "success": True,
            "message": "피드백이 성공적으로 제출되었습니다",
            "feedback_id": f"fb_{question_id}_{current_user.id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 제출 실패: {str(e)}")
