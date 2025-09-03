"""
Phase 8B: 통합 학습 API
Mock 데이터 없이 실제 데이터만 사용하는 새로운 엔드포인트
Phase 8의 동적 과목 시스템과 연동
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.services.unified_learning_service import get_unified_learning_service, UnifiedLearningService
from app.models.orm import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/unified-learning", tags=["Unified Learning - No Mock Data"])

@router.get("/analytics/{user_id}", response_model=Dict[str, Any])
async def get_user_learning_analytics(
    user_id: int,
    unified_service: UnifiedLearningService = Depends(get_unified_learning_service),
    db: Session = Depends(get_db)
):
    """
    사용자 통합 학습 분석 - Mock 데이터 없이 실제 데이터만 사용
    Phase 8의 동적 과목 시스템과 연동
    """
    try:
        logger.info(f"통합 학습 분석 요청: user {user_id}")
        
        # 사용자 존재 확인
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # 통합 분석 실행
        analytics_result = await unified_service.get_user_learning_analytics(user_id)
        
        if not analytics_result.get("success"):
            return {
                "success": False,
                "message": analytics_result.get("message"),
                "data_needed": analytics_result.get("data_needed"),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "data": analytics_result["analytics"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"통합 학습 분석 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

@router.get("/dashboard/{user_id}", response_model=Dict[str, Any])
async def get_unified_dashboard(
    user_id: int,
    unified_service: UnifiedLearningService = Depends(get_unified_learning_service),
    db: Session = Depends(get_db)
):
    """
    통합 대시보드 데이터 - Mock 데이터 없이 실제 데이터만 사용
    DashboardPage에서 사용할 실제 데이터
    """
    try:
        logger.info(f"통합 대시보드 요청: user {user_id}")
        
        # 사용자 존재 확인
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # 기본 분석 데이터 가져오기
        analytics_result = await unified_service.get_user_learning_analytics(user_id)
        
        if not analytics_result.get("success"):
            # 데이터가 없는 경우 빈 대시보드 반환
            return {
                "success": True,
                "dashboard": {
                    "has_data": False,
                    "message": analytics_result.get("message"),
                    "suggestions": analytics_result.get("data_needed", {}).get("suggestion"),
                    "progress": {"value": 0, "total": 100},
                    "topics": {},
                    "recent_activity": [],
                    "total_questions": 0,
                    "topic_accuracy": {},
                    "learning": {
                        "coverage": {"value": 0},
                        "consistency": {"value": 0},
                        "improvement": {"value": 0}
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        analytics = analytics_result["analytics"]
        
        # 대시보드 형식으로 데이터 변환
        dashboard_data = {
            "has_data": True,
            "progress": {
                "value": _calculate_overall_progress(analytics["subject_performance"]),
                "total": 100
            },
            "topics": _transform_to_topics_format(analytics["subject_performance"]),
            "recent_activity": _generate_recent_activity(analytics),
            "total_questions": analytics["user_profile"]["total_submissions"],
            "topic_accuracy": _calculate_topic_accuracy(analytics["subject_performance"]),
            "learning": {
                "coverage": {
                    "value": analytics["learning_patterns"].get("overall_accuracy", 0)
                },
                "consistency": {
                    "value": analytics["learning_patterns"].get("consistency_score", 0)
                },
                "improvement": {
                    "value": max(0, analytics["learning_patterns"].get("improvement_rate", 0))
                }
            },
            "user_profile": analytics["user_profile"],
            "recommendations": analytics["recommendations"]
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"통합 대시보드 생성 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"대시보드 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/recommendations/{user_id}", response_model=Dict[str, Any])
async def get_personalized_recommendations(
    user_id: int,
    unified_service: UnifiedLearningService = Depends(get_unified_learning_service),
    db: Session = Depends(get_db)
):
    """개인화 추천 시스템 - Phase 8 과목 시스템 기반"""
    try:
        logger.info(f"개인화 추천 요청: user {user_id}")
        
        analytics_result = await unified_service.get_user_learning_analytics(user_id)
        
        if not analytics_result.get("success"):
            return {
                "success": False,
                "message": analytics_result.get("message"),
                "recommendations": [
                    {
                        "title": "학습 시작하기",
                        "description": "과목을 등록하고 문제를 풀어 개인화된 추천을 받아보세요",
                        "priority": "high",
                        "action_type": "get_started"
                    }
                ]
            }
        
        recommendations = analytics_result["analytics"]["recommendations"]
        
        return {
            "success": True,
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"개인화 추천 생성 실패 user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류가 발생했습니다: {str(e)}")

# === 헬퍼 함수들 ===

def _calculate_overall_progress(subject_performance: Dict[str, Any]) -> float:
    """전체 진행률 계산"""
    if not subject_performance:
        return 0.0
    
    total_progress = sum(
        data.get("progress_percentage", 0) 
        for data in subject_performance.values()
    )
    return total_progress / len(subject_performance) if subject_performance else 0.0

def _transform_to_topics_format(subject_performance: Dict[str, Any]) -> Dict[str, int]:
    """과목 성과를 토픽 형식으로 변환"""
    topics = {}
    for subject_name, data in subject_performance.items():
        topics[subject_name] = data.get("total_submissions", 0)
    return topics

def _calculate_topic_accuracy(subject_performance: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    """토픽별 정확도 계산"""
    accuracy = {}
    for subject_name, data in subject_performance.items():
        accuracy[subject_name] = {
            "percentage": data.get("accuracy", 0) * 100
        }
    return accuracy

def _generate_recent_activity(analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """최근 활동 생성"""
    activities = []
    
    # 과목별 최근 활동 생성
    for subject_name, data in analytics["subject_performance"].items():
        if data.get("total_submissions", 0) > 0:
            activities.append({
                "date": data.get("last_activity", datetime.utcnow().isoformat()),
                "topic": subject_name,
                "question_count": data.get("total_submissions", 0),
                "score": int(data.get("accuracy", 0) * 100)
            })
    
    # 날짜순 정렬 (최신순)
    activities.sort(key=lambda x: x["date"], reverse=True)
    return activities[:10]  # 최근 10개만
