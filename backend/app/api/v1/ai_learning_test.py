from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.security import get_current_user
from app.models.orm import User

router = APIRouter()

@router.get("/daily-plan", response_model=Dict[str, Any])
async def get_daily_learning_plan(
    subject: str = Query("python_basics", description="학습 과목"),
    current_user: User = Depends(get_current_user)
):
    """일일 맞춤 학습 계획 조회"""
    # 🔥🔥🔥 FORCE TEST - 강제 테스트
    print("=" * 50)
    print("🔥🔥🔥 AI_LEARNING_TEST.PY 파일이 실행되었습니다!!!")
    print("🔥🔥🔥 DAILY PLAN API 호출됨!")
    print(f"🔥🔥🔥 User: {current_user.id}, Subject: {subject}")
    print("=" * 50)
    
    # 응답을 명확하게 수정해서 어떤 파일이 실행되는지 확인
    return {
        "success": True,
        "message": "🔥 AI_LEARNING_TEST.PY 파일이 실행되었습니다!",
        "daily_plan": {
            "date": "2025-08-24T15:00:00",
            "user_id": current_user.id,
            "subject": subject,
            "current_topic": "🔥 TEST: 이 메시지가 보이면 ai_learning_test.py가 실행된 것입니다",
            "problem_count": 999,  # 명확한 테스트 값
            "estimated_time": 1234,  # 명확한 테스트 값  
            "target_accuracy": 0.99,  # 명확한 테스트 값
            "note": "🔥 MODIFIED ai_learning_test.py 실행됨!"
        }
    }

@router.get("/learning-recommendations", response_model=Dict[str, Any])
async def get_learning_recommendations(
    subject: str = Query("python_basics", description="학습 과목"),
    current_user: User = Depends(get_current_user)
):
    """AI 학습 추천 조회"""
    print("🔥🔥🔥 LEARNING RECOMMENDATIONS 호출됨!")
    
    return {
        "success": True,
        "recommendations": [
            "🔥 TEST: 변수 선언 연습하기",
            "🔥 TEST: 반복문 활용하기",
            "🔥 TEST: 함수 작성 연습하기"
        ],
        "next_topic": "🔥 TEST 다음 주제",
        "estimated_time": 900
    }

@router.get("/weakness-analysis", response_model=Dict[str, Any])
async def get_weakness_analysis(
    subject: str = Query("python_basics", description="학습 과목"),
    current_user: User = Depends(get_current_user)
):
    """학습 약점 분석 조회"""
    print("🔥🔥🔥 WEAKNESS ANALYSIS 호출됨!")
    
    return {
        "success": True,
        "weaknesses": [
            "🔥 TEST: 메서드 사용법", 
            "🔥 TEST: 변수명 규칙"
        ]
    }
