"""
베타 테스트 데이터 수집 및 관리 API
- 베타 테스터 등록 및 프로필 관리
- 사용자 행동 데이터 수집
- 피드백 수집 및 분석
- 베타 테스트 진행 상황 모니터링
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.orm import User
from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)

router = APIRouter()

# === Pydantic 모델들 ===

class BetaUserProfile(BaseModel):
    name: str
    email: str
    experience_level: str
    interests: List[str]
    goals: List[str]
    beta_feedback_consent: bool
    ai_features_interest: List[str]

class UserAction(BaseModel):
    action_type: str
    action_data: Dict[str, Any]
    session_id: Optional[str] = None
    timestamp: Optional[str] = None

class FeedbackSubmission(BaseModel):
    feedback_type: str  # bug, feature_request, general, improvement
    title: str
    description: str
    rating: Optional[int] = None  # 1-5
    category: Optional[str] = None
    severity: Optional[str] = None  # low, medium, high, critical

class BetaMetrics(BaseModel):
    feature_used: str
    usage_duration: int
    success: bool
    error_encountered: Optional[str] = None
    user_satisfaction: Optional[int] = None

# === 베타 테스터 관리 ===

@router.post("/register", response_model=Dict[str, Any])
async def register_beta_tester(
    profile: BetaUserProfile = Body(...),
    db: Session = Depends(get_db)
):
    """베타 테스터 등록"""
    
    try:
        redis_service = get_redis_service()
        
        # 베타 테스터 정보 저장
        beta_tester_data = {
            "profile": profile.dict(),
            "registered_at": datetime.utcnow().isoformat(),
            "status": "active",
            "session_count": 0,
            "feedback_count": 0,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        # Redis에 베타 테스터 정보 저장
        beta_key = f"beta_tester:{profile.email}"
        redis_service.set_cache(beta_key, beta_tester_data, 86400 * 30)  # 30일
        
        # 베타 테스터 목록에 추가
        beta_list = redis_service.get_cache("beta_testers_list") or []
        if profile.email not in beta_list:
            beta_list.append(profile.email)
            redis_service.set_cache("beta_testers_list", beta_list, 86400 * 30)
        
        # 베타 테스터 ID 생성
        beta_tester_id = f"BETA_{len(beta_list):04d}"
        beta_tester_data["beta_id"] = beta_tester_id
        redis_service.set_cache(beta_key, beta_tester_data, 86400 * 30)
        
        logger.info(f"베타 테스터 등록: {profile.email} (ID: {beta_tester_id})")
        
        return {
            "success": True,
            "beta_tester_id": beta_tester_id,
            "message": "베타 테스터 등록이 완료되었습니다",
            "access_features": profile.ai_features_interest,
            "registered_at": beta_tester_data["registered_at"]
        }
        
    except Exception as e:
        logger.error(f"베타 테스터 등록 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"등록 실패: {str(e)}")

@router.get("/profile/{email}", response_model=Dict[str, Any])
async def get_beta_tester_profile(
    email: str,
    db: Session = Depends(get_db)
):
    """베타 테스터 프로필 조회"""
    
    try:
        redis_service = get_redis_service()
        
        beta_key = f"beta_tester:{email}"
        beta_data = redis_service.get_cache(beta_key)
        
        if not beta_data:
            raise HTTPException(status_code=404, detail="베타 테스터를 찾을 수 없습니다")
        
        return {
            "success": True,
            "profile": beta_data,
            "access_level": "beta",
            "features_available": [
                "deep_learning_analysis",
                "ai_mentoring", 
                "adaptive_difficulty",
                "code_review",
                "personalized_learning_path"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"베타 테스터 프로필 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

# === 사용자 행동 데이터 수집 ===

@router.post("/track-action", response_model=Dict[str, str])
async def track_user_action(
    email: str,
    action: UserAction = Body(...),
    db: Session = Depends(get_db)
):
    """사용자 행동 추적"""
    
    try:
        redis_service = get_redis_service()
        
        # 베타 테스터 확인
        beta_key = f"beta_tester:{email}"
        beta_data = redis_service.get_cache(beta_key)
        
        if not beta_data:
            raise HTTPException(status_code=404, detail="베타 테스터를 찾을 수 없습니다")
        
        # 행동 데이터 저장
        action_data = {
            "beta_id": beta_data.get("beta_id"),
            "email": email,
            "action_type": action.action_type,
            "action_data": action.action_data,
            "session_id": action.session_id,
            "timestamp": action.timestamp or datetime.utcnow().isoformat(),
            "user_agent": "beta_test_app"
        }
        
        # 일별 행동 데이터에 추가
        date_key = datetime.utcnow().strftime("%Y-%m-%d")
        daily_actions_key = f"beta_actions:{date_key}"
        
        daily_actions = redis_service.get_cache(daily_actions_key) or []
        daily_actions.append(action_data)
        
        # 최대 1000개 액션만 유지
        if len(daily_actions) > 1000:
            daily_actions = daily_actions[-1000:]
        
        redis_service.set_cache(daily_actions_key, daily_actions, 86400 * 7)  # 7일간 보관
        
        # 베타 테스터 활동 업데이트
        beta_data["last_activity"] = datetime.utcnow().isoformat()
        beta_data["session_count"] = beta_data.get("session_count", 0) + 1
        redis_service.set_cache(beta_key, beta_data, 86400 * 30)
        
        return {
            "success": True,
            "message": "행동 데이터가 기록되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"행동 추적 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"추적 실패: {str(e)}")

# === 피드백 수집 ===

@router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(
    email: str,
    feedback: FeedbackSubmission = Body(...),
    db: Session = Depends(get_db)
):
    """피드백 제출"""
    
    try:
        redis_service = get_redis_service()
        
        # 베타 테스터 확인
        beta_key = f"beta_tester:{email}"
        beta_data = redis_service.get_cache(beta_key)
        
        if not beta_data:
            raise HTTPException(status_code=404, detail="베타 테스터를 찾을 수 없습니다")
        
        # 피드백 데이터 생성
        feedback_id = f"FB_{int(datetime.utcnow().timestamp())}"
        feedback_data = {
            "feedback_id": feedback_id,
            "beta_id": beta_data.get("beta_id"),
            "email": email,
            "feedback_type": feedback.feedback_type,
            "title": feedback.title,
            "description": feedback.description,
            "rating": feedback.rating,
            "category": feedback.category,
            "severity": feedback.severity,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "new"
        }
        
        # 피드백 저장
        feedback_key = f"feedback:{feedback_id}"
        redis_service.set_cache(feedback_key, feedback_data, 86400 * 30)
        
        # 피드백 목록에 추가
        feedback_list = redis_service.get_cache("beta_feedback_list") or []
        feedback_list.append(feedback_id)
        redis_service.set_cache("beta_feedback_list", feedback_list, 86400 * 30)
        
        # 베타 테스터 피드백 카운트 업데이트
        beta_data["feedback_count"] = beta_data.get("feedback_count", 0) + 1
        redis_service.set_cache(beta_key, beta_data, 86400 * 30)
        
        logger.info(f"피드백 접수: {feedback_id} from {email}")
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "소중한 피드백을 주셔서 감사합니다",
            "estimated_response_time": "24-48시간"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"피드백 제출 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제출 실패: {str(e)}")

@router.get("/feedback/list", response_model=Dict[str, Any])
async def get_feedback_list(
    status: Optional[str] = Query(None, description="피드백 상태 필터"),
    feedback_type: Optional[str] = Query(None, description="피드백 유형 필터"),
    limit: int = Query(50, description="조회할 피드백 수"),
    db: Session = Depends(get_db)
):
    """피드백 목록 조회 (관리자용)"""
    
    try:
        redis_service = get_redis_service()
        
        feedback_list = redis_service.get_cache("beta_feedback_list") or []
        feedbacks = []
        
        for feedback_id in feedback_list[-limit:]:  # 최근 feedback부터
            feedback_data = redis_service.get_cache(f"feedback:{feedback_id}")
            if feedback_data:
                # 필터링
                if status and feedback_data.get("status") != status:
                    continue
                if feedback_type and feedback_data.get("feedback_type") != feedback_type:
                    continue
                
                feedbacks.append(feedback_data)
        
        # 최신순 정렬
        feedbacks.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
        
        return {
            "success": True,
            "feedbacks": feedbacks,
            "total_count": len(feedbacks),
            "filters_applied": {
                "status": status,
                "feedback_type": feedback_type
            }
        }
        
    except Exception as e:
        logger.error(f"피드백 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

# === 베타 메트릭 수집 ===

@router.post("/metrics", response_model=Dict[str, str])
async def record_beta_metrics(
    email: str,
    metrics: BetaMetrics = Body(...),
    db: Session = Depends(get_db)
):
    """베타 테스트 메트릭 기록"""
    
    try:
        redis_service = get_redis_service()
        
        # 베타 테스터 확인
        beta_key = f"beta_tester:{email}"
        beta_data = redis_service.get_cache(beta_key)
        
        if not beta_data:
            raise HTTPException(status_code=404, detail="베타 테스터를 찾을 수 없습니다")
        
        # 메트릭 데이터 생성
        metric_data = {
            "beta_id": beta_data.get("beta_id"),
            "email": email,
            "feature_used": metrics.feature_used,
            "usage_duration": metrics.usage_duration,
            "success": metrics.success,
            "error_encountered": metrics.error_encountered,
            "user_satisfaction": metrics.user_satisfaction,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 일별 메트릭에 추가
        date_key = datetime.utcnow().strftime("%Y-%m-%d")
        metrics_key = f"beta_metrics:{date_key}"
        
        daily_metrics = redis_service.get_cache(metrics_key) or []
        daily_metrics.append(metric_data)
        
        # 최대 500개 메트릭만 유지
        if len(daily_metrics) > 500:
            daily_metrics = daily_metrics[-500:]
        
        redis_service.set_cache(metrics_key, daily_metrics, 86400 * 7)  # 7일간 보관
        
        return {
            "success": True,
            "message": "메트릭이 기록되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메트릭 기록 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"기록 실패: {str(e)}")

# === 베타 테스트 현황 조회 ===

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_beta_dashboard():
    """베타 테스트 대시보드 데이터"""
    
    try:
        redis_service = get_redis_service()
        
        # 베타 테스터 목록
        beta_testers = redis_service.get_cache("beta_testers_list") or []
        
        # 활성 베타 테스터 통계
        active_testers = 0
        total_sessions = 0
        total_feedback = 0
        
        for email in beta_testers:
            beta_data = redis_service.get_cache(f"beta_tester:{email}")
            if beta_data:
                # 최근 7일 내 활동한 사용자
                last_activity = beta_data.get("last_activity")
                if last_activity:
                    last_activity_date = datetime.fromisoformat(last_activity)
                    if (datetime.utcnow() - last_activity_date).days <= 7:
                        active_testers += 1
                
                total_sessions += beta_data.get("session_count", 0)
                total_feedback += beta_data.get("feedback_count", 0)
        
        # 일별 활동 통계 (최근 7일)
        daily_activity = {}
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            actions = redis_service.get_cache(f"beta_actions:{date}") or []
            daily_activity[date] = len(actions)
        
        # 피드백 유형별 통계
        feedback_list = redis_service.get_cache("beta_feedback_list") or []
        feedback_by_type = {}
        
        for feedback_id in feedback_list:
            feedback_data = redis_service.get_cache(f"feedback:{feedback_id}")
            if feedback_data:
                fb_type = feedback_data.get("feedback_type", "unknown")
                feedback_by_type[fb_type] = feedback_by_type.get(fb_type, 0) + 1
        
        # AI 기능 사용 통계
        feature_usage = {}
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            metrics = redis_service.get_cache(f"beta_metrics:{date}") or []
            
            for metric in metrics:
                feature = metric.get("feature_used", "unknown")
                feature_usage[feature] = feature_usage.get(feature, 0) + 1
        
        return {
            "success": True,
            "overview": {
                "total_beta_testers": len(beta_testers),
                "active_testers_7d": active_testers,
                "total_sessions": total_sessions,
                "total_feedback": total_feedback,
                "avg_sessions_per_user": round(total_sessions / max(1, len(beta_testers)), 1)
            },
            "daily_activity": daily_activity,
            "feedback_by_type": feedback_by_type,
            "feature_usage": feature_usage,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"베타 대시보드 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

@router.get("/testers/list", response_model=Dict[str, Any])
async def get_beta_testers_list(
    active_only: bool = Query(False, description="활성 사용자만 조회"),
    db: Session = Depends(get_db)
):
    """베타 테스터 목록 조회"""
    
    try:
        redis_service = get_redis_service()
        
        beta_testers = redis_service.get_cache("beta_testers_list") or []
        testers_data = []
        
        for email in beta_testers:
            beta_data = redis_service.get_cache(f"beta_tester:{email}")
            if beta_data:
                # 활성 사용자 필터
                if active_only:
                    last_activity = beta_data.get("last_activity")
                    if last_activity:
                        last_activity_date = datetime.fromisoformat(last_activity)
                        if (datetime.utcnow() - last_activity_date).days > 7:
                            continue
                
                # 민감 정보 제거
                safe_data = {
                    "beta_id": beta_data.get("beta_id"),
                    "email": email,
                    "experience_level": beta_data.get("profile", {}).get("experience_level"),
                    "interests": beta_data.get("profile", {}).get("interests", []),
                    "registered_at": beta_data.get("registered_at"),
                    "last_activity": beta_data.get("last_activity"),
                    "session_count": beta_data.get("session_count", 0),
                    "feedback_count": beta_data.get("feedback_count", 0),
                    "status": beta_data.get("status", "active")
                }
                testers_data.append(safe_data)
        
        # 최근 활동순 정렬
        testers_data.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        
        return {
            "success": True,
            "testers": testers_data,
            "total_count": len(testers_data),
            "active_filter": active_only
        }
        
    except Exception as e:
        logger.error(f"베타 테스터 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"조회 실패: {str(e)}")

# === 베타 테스트 상태 확인 ===

@router.get("/health", response_model=Dict[str, Any])
async def beta_testing_health():
    """베타 테스트 시스템 상태 확인"""
    
    try:
        redis_service = get_redis_service()
        
        # Redis 연결 확인
        redis_status = "connected"
        try:
            redis_service.get_cache("test_key")
        except:
            redis_status = "disconnected"
        
        # 베타 테스터 수 확인
        beta_testers = redis_service.get_cache("beta_testers_list") or []
        
        # 최근 활동 확인
        recent_activity = 0
        for i in range(3):  # 최근 3일
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            actions = redis_service.get_cache(f"beta_actions:{date}") or []
            recent_activity += len(actions)
        
        status = "healthy"
        if redis_status == "disconnected":
            status = "unhealthy"
        elif len(beta_testers) == 0:
            status = "no_testers"
        elif recent_activity == 0:
            status = "inactive"
        
        return {
            "status": status,
            "redis_connection": redis_status,
            "beta_testers_count": len(beta_testers),
            "recent_activity_3d": recent_activity,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "beta-1.0"
        }
        
    except Exception as e:
        logger.error(f"베타 테스트 헬스 체크 실패: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
