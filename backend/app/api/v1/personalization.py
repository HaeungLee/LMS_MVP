"""
개인화 학습 API 엔드포인트 (Phase 2)
- 개인화된 커리큘럼 추천
- 학습 진도 추적
- 약점 분석 및 개선 제안
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import (
    User, UserProgress, UserWeakness, UserTrackProgress, LearningGoal,
    PersonalizedRecommendation, LearningModule, LearningTrack
)
from app.services.advanced_recommendation_engine import get_recommendation_engine

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/recommendations/{user_id}")
async def get_personalized_recommendations(
    user_id: int,
    recommendation_type: str = Query("next_module", description="Type: next_module, skill_reinforcement, career_path"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 맞춤 학습 추천"""
    
    # 권한 확인 (본인 또는 관리자)
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # 추천 엔진 생성
        engine = get_recommendation_engine(db)
        
        # 개인화 추천 생성
        recommendations = await engine.get_personalized_recommendations(
            user_id=user_id,
            recommendation_type=recommendation_type,
            limit=limit
        )
        
        # 응답 형식 조정
        formatted_recommendations = []
        for rec in recommendations:
            formatted_rec = {
                "module_id": rec["module_id"],
                "module_name": rec["module"].name,
                "module_display_name": rec["module"].display_name,
                "track_name": rec["track"].name,
                "track_display_name": rec["track"].display_name,
                "confidence_score": round(rec["confidence_score"], 3),
                "reasoning": rec["reasoning"],
                "estimated_completion_time": rec.get("estimated_completion_time", 0),
                "difficulty_level": rec["module"].difficulty_level,
                "module_type": rec["module"].module_type,
                "tags": rec["module"].tags or [],
                "industry_focus": rec["module"].industry_focus
            }
            
            # 추천 타입별 추가 정보
            if recommendation_type == "skill_reinforcement":
                if "weakness_addressed" in rec:
                    formatted_rec["weakness_info"] = {
                        "topic": rec["weakness_addressed"].topic,
                        "weakness_type": rec["weakness_addressed"].weakness_type,
                        "current_accuracy": rec["weakness_addressed"].accuracy_rate
                    }
                
                if "estimated_improvement" in rec:
                    formatted_rec["improvement_prediction"] = rec["estimated_improvement"]
            
            elif recommendation_type == "career_path":
                if "career_goal" in rec:
                    formatted_rec["career_goal"] = {
                        "title": rec["career_goal"].title,
                        "target_completion_date": rec["career_goal"].target_completion_date.isoformat() if rec["career_goal"].target_completion_date else None
                    }
                
                if "business_impact" in rec:
                    formatted_rec["business_impact"] = rec["business_impact"]
            
            formatted_recommendations.append(formatted_rec)
        
        return {
            "success": True,
            "user_id": user_id,
            "recommendation_type": recommendation_type,
            "total_recommendations": len(formatted_recommendations),
            "recommendations": formatted_recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/progress/{user_id}")
async def get_user_progress_overview(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 학습 진도 종합 조회"""
    
    # 권한 확인
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # 트랙별 진도 현황
        track_progress = db.query(UserTrackProgress).filter(
            UserTrackProgress.user_id == user_id
        ).all()
        
        # 모듈별 진도 현황
        module_progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
        
        # 전체 통계 계산
        total_tracks_enrolled = len(track_progress)
        completed_tracks = len([tp for tp in track_progress if tp.status == "completed"])
        
        total_modules_attempted = len(module_progress)
        completed_modules = len([mp for mp in module_progress if mp.status == "completed"])
        
        # 평균 정확도 계산
        total_attempts = sum(mp.total_attempts for mp in module_progress)
        successful_attempts = sum(mp.successful_attempts for mp in module_progress)
        overall_accuracy = (successful_attempts / total_attempts) if total_attempts > 0 else 0
        
        # 학습 시간 계산
        total_time_spent = sum(mp.time_spent_minutes for mp in module_progress)
        
        # 트랙별 상세 진도
        track_details = []
        for tp in track_progress:
            track = db.query(LearningTrack).filter(LearningTrack.id == tp.track_id).first()
            if track:
                track_modules = db.query(UserProgress).filter(
                    and_(
                        UserProgress.user_id == user_id,
                        UserProgress.track_id == tp.track_id
                    )
                ).all()
                
                track_detail = {
                    "track_id": tp.track_id,
                    "track_name": track.name,
                    "track_display_name": track.display_name,
                    "status": tp.status,
                    "enrollment_date": tp.enrollment_date.isoformat(),
                    "modules_completed": tp.modules_completed,
                    "total_modules": tp.total_modules,
                    "completion_percentage": (tp.modules_completed / tp.total_modules * 100) if tp.total_modules > 0 else 0,
                    "overall_accuracy": tp.overall_accuracy,
                    "time_spent_minutes": tp.total_time_spent,
                    "preferred_difficulty": tp.preferred_difficulty,
                    "learning_pace": tp.learning_pace,
                    "industry_preference": tp.industry_preference
                }
                
                if tp.estimated_completion_date:
                    track_detail["estimated_completion_date"] = tp.estimated_completion_date.isoformat()
                if tp.actual_completion_date:
                    track_detail["actual_completion_date"] = tp.actual_completion_date.isoformat()
                
                track_details.append(track_detail)
        
        return {
            "success": True,
            "user_id": user_id,
            "overview": {
                "total_tracks_enrolled": total_tracks_enrolled,
                "completed_tracks": completed_tracks,
                "total_modules_attempted": total_modules_attempted,
                "completed_modules": completed_modules,
                "overall_accuracy": round(overall_accuracy, 3),
                "total_time_spent_hours": round(total_time_spent / 60, 1),
                "completion_rate": round((completed_modules / total_modules_attempted * 100), 1) if total_modules_attempted > 0 else 0
            },
            "track_progress": track_details,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching progress for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch progress: {str(e)}")

@router.get("/weaknesses/{user_id}")
async def get_user_weaknesses(
    user_id: int,
    only_unresolved: bool = Query(True, description="Only show unresolved weaknesses"),
    weakness_type: Optional[str] = Query(None, description="Filter by weakness type: critical, moderate, minor"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 약점 분석 결과"""
    
    # 권한 확인
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # 약점 조회 쿼리 구성
        query = db.query(UserWeakness).filter(UserWeakness.user_id == user_id)
        
        if only_unresolved:
            query = query.filter(UserWeakness.is_resolved == False)
        
        if weakness_type:
            query = query.filter(UserWeakness.weakness_type == weakness_type)
        
        weaknesses = query.order_by(
            desc(UserWeakness.weakness_type == 'critical'),
            desc(UserWeakness.error_count),
            UserWeakness.last_updated_at
        ).all()
        
        # 약점별 상세 정보
        weakness_details = []
        for weakness in weaknesses:
            weakness_detail = {
                "id": weakness.id,
                "category": weakness.category,
                "subcategory": weakness.subcategory,
                "topic": weakness.topic,
                "weakness_type": weakness.weakness_type,
                "error_count": weakness.error_count,
                "accuracy_rate": round(weakness.accuracy_rate, 3),
                "avg_time_taken_seconds": round(weakness.avg_time_taken, 1),
                "suggested_practice": weakness.suggested_practice,
                "improvement_trend": weakness.improvement_trend,
                "first_detected_at": weakness.first_detected_at.isoformat(),
                "last_updated_at": weakness.last_updated_at.isoformat(),
                "is_resolved": weakness.is_resolved
            }
            
            if weakness.resolved_at:
                weakness_detail["resolved_at"] = weakness.resolved_at.isoformat()
            
            weakness_details.append(weakness_detail)
        
        # 약점 타입별 통계
        type_counts = {
            'critical': len([w for w in weaknesses if w.weakness_type == 'critical']),
            'moderate': len([w for w in weaknesses if w.weakness_type == 'moderate']),
            'minor': len([w for w in weaknesses if w.weakness_type == 'minor'])
        }
        
        # 카테고리별 통계
        category_counts = {}
        for weakness in weaknesses:
            category = weakness.category
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
        
        return {
            "success": True,
            "user_id": user_id,
            "summary": {
                "total_weaknesses": len(weaknesses),
                "by_type": type_counts,
                "by_category": category_counts,
                "avg_accuracy_rate": round(
                    sum(w.accuracy_rate for w in weaknesses) / len(weaknesses), 3
                ) if weaknesses else 0
            },
            "weaknesses": weakness_details,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching weaknesses for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weaknesses: {str(e)}")

@router.post("/progress/{user_id}/update")
async def update_user_progress(
    user_id: int,
    module_id: int,
    progress_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 진도 업데이트"""
    
    # 권한 확인
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # 모듈 확인
        module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # 기존 진도 조회 또는 새로 생성
        progress = db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.module_id == module_id
            )
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                track_id=module.track_id,
                module_id=module_id
            )
            db.add(progress)
        
        # 진도 데이터 업데이트
        if "status" in progress_data:
            progress.status = progress_data["status"]
            
            if progress_data["status"] == "in_progress" and not progress.started_at:
                progress.started_at = datetime.utcnow()
            elif progress_data["status"] == "completed" and not progress.completed_at:
                progress.completed_at = datetime.utcnow()
        
        if "completion_percentage" in progress_data:
            progress.completion_percentage = max(0, min(100, progress_data["completion_percentage"]))
        
        if "time_spent_minutes" in progress_data:
            progress.time_spent_minutes += progress_data["time_spent_minutes"]
        
        if "attempts" in progress_data:
            progress.total_attempts += 1
            if progress_data.get("success", False):
                progress.successful_attempts += 1
        
        progress.last_accessed_at = datetime.utcnow()
        progress.updated_at = datetime.utcnow()
        
        # 트랙 진도도 업데이트
        track_progress = db.query(UserTrackProgress).filter(
            and_(
                UserTrackProgress.user_id == user_id,
                UserTrackProgress.track_id == module.track_id
            )
        ).first()
        
        if track_progress:
            # 완료된 모듈 수 업데이트
            completed_modules = db.query(UserProgress).filter(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.track_id == module.track_id,
                    UserProgress.status == "completed"
                )
            ).count()
            
            track_progress.modules_completed = completed_modules
            track_progress.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Progress updated successfully",
            "progress": {
                "module_id": module_id,
                "status": progress.status,
                "completion_percentage": progress.completion_percentage,
                "total_attempts": progress.total_attempts,
                "successful_attempts": progress.successful_attempts,
                "time_spent_minutes": progress.time_spent_minutes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating progress for user {user_id}, module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")

@router.get("/goals/{user_id}")
async def get_user_learning_goals(
    user_id: int,
    status: Optional[str] = Query(None, description="Filter by status: active, completed, paused, cancelled"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자 학습 목표 조회"""
    
    # 권한 확인
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # 목표 조회
        query = db.query(LearningGoal).filter(LearningGoal.user_id == user_id)
        
        if status:
            query = query.filter(LearningGoal.status == status)
        
        goals = query.order_by(
            desc(LearningGoal.priority_level),
            LearningGoal.target_completion_date,
            LearningGoal.created_at
        ).all()
        
        # 목표별 상세 정보
        goal_details = []
        for goal in goals:
            goal_detail = {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "goal_type": goal.goal_type,
                "priority_level": goal.priority_level,
                "status": goal.status,
                "progress_percentage": goal.progress_percentage,
                "target_tracks": goal.target_tracks,
                "success_criteria": goal.success_criteria,
                "milestones_achieved": goal.milestones_achieved,
                "created_at": goal.created_at.isoformat(),
                "updated_at": goal.updated_at.isoformat()
            }
            
            if goal.target_completion_date:
                goal_detail["target_completion_date"] = goal.target_completion_date.isoformat()
            if goal.completed_at:
                goal_detail["completed_at"] = goal.completed_at.isoformat()
            
            goal_details.append(goal_detail)
        
        # 목표 달성 통계
        total_goals = len(goals)
        completed_goals = len([g for g in goals if g.status == "completed"])
        active_goals = len([g for g in goals if g.status == "active"])
        
        return {
            "success": True,
            "user_id": user_id,
            "summary": {
                "total_goals": total_goals,
                "completed_goals": completed_goals,
                "active_goals": active_goals,
                "completion_rate": round((completed_goals / total_goals * 100), 1) if total_goals > 0 else 0
            },
            "goals": goal_details,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching goals for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch goals: {str(e)}")

@router.get("/analytics/{user_id}")
async def get_learning_analytics(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """학습 분석 데이터"""
    
    # 권한 확인
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 기간 내 학습 활동
        recent_progress = db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.last_accessed_at >= start_date
            )
        ).all()
        
        # 학습 패턴 분석
        daily_activity = {}
        for progress in recent_progress:
            date_key = progress.last_accessed_at.date().isoformat()
            if date_key not in daily_activity:
                daily_activity[date_key] = {
                    "modules_studied": 0,
                    "time_spent": 0,
                    "attempts": 0,
                    "successes": 0
                }
            
            daily_activity[date_key]["modules_studied"] += 1
            daily_activity[date_key]["time_spent"] += progress.time_spent_minutes
            daily_activity[date_key]["attempts"] += progress.total_attempts
            daily_activity[date_key]["successes"] += progress.successful_attempts
        
        # 학습 속도 및 효율성
        total_time = sum(p.time_spent_minutes for p in recent_progress)
        total_attempts = sum(p.total_attempts for p in recent_progress)
        total_successes = sum(p.successful_attempts for p in recent_progress)
        
        accuracy_rate = (total_successes / total_attempts) if total_attempts > 0 else 0
        avg_daily_time = total_time / days if days > 0 else 0
        
        # 최근 추천 효과성
        recent_recommendations = db.query(PersonalizedRecommendation).filter(
            and_(
                PersonalizedRecommendation.user_id == user_id,
                PersonalizedRecommendation.created_at >= start_date
            )
        ).all()
        
        recommendation_stats = {
            "total_received": len(recent_recommendations),
            "accepted": len([r for r in recent_recommendations if r.user_action == "accepted"]),
            "declined": len([r for r in recent_recommendations if r.user_action == "declined"]),
            "avg_confidence": round(
                sum(r.confidence_score for r in recent_recommendations) / len(recent_recommendations), 3
            ) if recent_recommendations else 0
        }
        
        return {
            "success": True,
            "user_id": user_id,
            "analysis_period_days": days,
            "learning_metrics": {
                "total_time_minutes": total_time,
                "avg_daily_time_minutes": round(avg_daily_time, 1),
                "total_attempts": total_attempts,
                "accuracy_rate": round(accuracy_rate, 3),
                "modules_studied": len(recent_progress),
                "active_days": len(daily_activity)
            },
            "daily_activity": daily_activity,
            "recommendation_effectiveness": recommendation_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating analytics for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")

@router.get("/health")
async def personalization_health_check():
    """개인화 API 상태 확인"""
    return {
        "status": "healthy",
        "message": "Personalization API is operational",
        "version": "2.0.0-phase2",
        "features": [
            "personalized_recommendations",
            "progress_tracking", 
            "weakness_analysis",
            "learning_analytics"
        ]
    }
