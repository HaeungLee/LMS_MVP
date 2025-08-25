"""
커리큘럼 관련 API 엔드포인트
Phase 1: 기본 추천 및 조회 기능
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import (
    User, CurriculumCategory, LearningTrack, LearningModule, LearningResource
)

router = APIRouter()

@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_curriculum_categories(
    db: Session = Depends(get_db)
):
    """커리큘럼 카테고리 목록 조회"""
    try:
        categories = db.query(CurriculumCategory).all()
        
        result = []
        for category in categories:
            tracks_count = db.query(LearningTrack).filter(
                LearningTrack.curriculum_category_id == category.id
            ).count()
            
            result.append({
                "id": category.id,
                "name": category.name,
                "display_name": category.display_name,
                "description": category.description,
                "target_audience": category.target_audience,
                "estimated_total_months": category.estimated_total_months,
                "tracks_count": tracks_count,
                "created_at": category.created_at.isoformat()
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

@router.get("/categories/{category_id}/tracks", response_model=List[Dict[str, Any]])
async def get_category_tracks(
    category_id: int,
    db: Session = Depends(get_db)
):
    """특정 카테고리의 학습 트랙 조회"""
    try:
        # 카테고리 존재 확인
        category = db.query(CurriculumCategory).filter(
            CurriculumCategory.id == category_id
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        tracks = db.query(LearningTrack).filter(
            LearningTrack.curriculum_category_id == category_id
        ).order_by(LearningTrack.difficulty_level, LearningTrack.created_at).all()
        
        result = []
        for track in tracks:
            modules_count = db.query(LearningModule).filter(
                LearningModule.track_id == track.id
            ).count()
            
            result.append({
                "id": track.id,
                "name": track.name,
                "display_name": track.display_name,
                "category": track.category,
                "specialization_level": track.specialization_level,
                "prerequisite_tracks": track.prerequisite_tracks or [],
                "difficulty_level": track.difficulty_level,
                "estimated_hours": track.estimated_hours,
                "description": track.description,
                "modules_count": modules_count,
                "created_at": track.created_at.isoformat()
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tracks: {str(e)}")

@router.get("/tracks/{track_id}/modules", response_model=List[Dict[str, Any]])
async def get_track_modules(
    track_id: int,
    db: Session = Depends(get_db)
):
    """특정 트랙의 모듈 조회"""
    try:
        # 트랙 존재 확인
        track = db.query(LearningTrack).filter(
            LearningTrack.id == track_id
        ).first()
        
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        modules = db.query(LearningModule).filter(
            LearningModule.track_id == track_id
        ).order_by(LearningModule.difficulty_level, LearningModule.created_at).all()
        
        result = []
        for module in modules:
            resources_count = db.query(LearningResource).filter(
                LearningResource.module_id == module.id
            ).count()
            
            result.append({
                "id": module.id,
                "name": module.name,
                "display_name": module.display_name,
                "module_type": module.module_type,
                "estimated_hours": module.estimated_hours,
                "difficulty_level": module.difficulty_level,
                "prerequisites": module.prerequisites or [],
                "tags": module.tags or [],
                "industry_focus": module.industry_focus,
                "resources_count": resources_count,
                "created_at": module.created_at.isoformat()
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch modules: {str(e)}")

@router.get("/modules/{module_id}/resources", response_model=List[Dict[str, Any]])
async def get_module_resources(
    module_id: int,
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    difficulty_level: Optional[int] = Query(None, description="Filter by difficulty level"),
    db: Session = Depends(get_db)
):
    """특정 모듈의 학습 자료 조회"""
    try:
        # 모듈 존재 확인
        module = db.query(LearningModule).filter(
            LearningModule.id == module_id
        ).first()
        
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # 필터 조건 구성
        query = db.query(LearningResource).filter(
            LearningResource.module_id == module_id
        )
        
        if resource_type:
            query = query.filter(LearningResource.resource_type == resource_type)
        
        if difficulty_level:
            query = query.filter(LearningResource.difficulty_level == difficulty_level)
        
        resources = query.order_by(
            LearningResource.difficulty_level, 
            LearningResource.created_at
        ).all()
        
        result = []
        for resource in resources:
            result.append({
                "id": resource.id,
                "sub_topic": resource.sub_topic,
                "resource_type": resource.resource_type,
                "title": resource.title,
                "url": resource.url,
                "description": resource.description,
                "difficulty_level": resource.difficulty_level,
                "industry_focus": resource.industry_focus,
                "created_at": resource.created_at.isoformat()
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch resources: {str(e)}")

@router.get("/recommend-path")
async def recommend_learning_path(
    career_goal: str = Query(..., description="Career goal (saas_development, react_specialist, data_engineering_advanced)"),
    current_level: str = Query("beginner", description="Current level (beginner, intermediate, advanced)"),
    industry: str = Query("general", description="Industry focus (general, fintech, ecommerce, enterprise)"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """기본 학습 경로 추천 (규칙 기반)"""
    try:
        # 카테고리 조회
        category = db.query(CurriculumCategory).filter(
            CurriculumCategory.name == career_goal
        ).first()
        
        if not category:
            raise HTTPException(status_code=404, detail=f"Career goal '{career_goal}' not found")
        
        # 해당 카테고리의 트랙들 조회
        tracks = db.query(LearningTrack).filter(
            LearningTrack.curriculum_category_id == category.id
        ).order_by(LearningTrack.difficulty_level, LearningTrack.created_at).all()
        
        # 현재 레벨에 따른 추천 로직
        level_mapping = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3
        }
        
        max_difficulty = level_mapping.get(current_level, 1)
        
        # 추천 경로 생성
        recommended_tracks = []
        for track in tracks:
            # 난이도 필터링
            if track.difficulty_level <= max_difficulty + 1:  # 약간의 도전 허용
                
                # 트랙의 모듈들 조회
                modules = db.query(LearningModule).filter(
                    LearningModule.track_id == track.id
                ).order_by(LearningModule.difficulty_level).all()
                
                # 업계별 특화 모듈 우선순위
                filtered_modules = []
                for module in modules:
                    if industry != "general" and module.industry_focus == industry:
                        # 업계 특화 모듈 우선
                        filtered_modules.insert(0, {
                            "id": module.id,
                            "name": module.name,
                            "display_name": module.display_name,
                            "estimated_hours": module.estimated_hours,
                            "difficulty_level": module.difficulty_level,
                            "tags": module.tags or [],
                            "industry_focus": module.industry_focus,
                            "is_specialized": True
                        })
                    elif module.industry_focus == "general" or module.industry_focus == industry:
                        filtered_modules.append({
                            "id": module.id,
                            "name": module.name,
                            "display_name": module.display_name,
                            "estimated_hours": module.estimated_hours,
                            "difficulty_level": module.difficulty_level,
                            "tags": module.tags or [],
                            "industry_focus": module.industry_focus,
                            "is_specialized": False
                        })
                
                recommended_tracks.append({
                    "id": track.id,
                    "name": track.name,
                    "display_name": track.display_name,
                    "category": track.category,
                    "difficulty_level": track.difficulty_level,
                    "estimated_hours": track.estimated_hours,
                    "description": track.description,
                    "modules": filtered_modules[:5],  # 처음 5개 모듈만
                    "is_recommended": track.difficulty_level <= max_difficulty
                })
        
        # 총 예상 시간 계산
        total_hours = sum(track["estimated_hours"] or 0 for track in recommended_tracks)
        estimated_months = round(total_hours / 40)  # 주당 10시간 기준
        
        return {
            "success": True,
            "career_goal": career_goal,
            "current_level": current_level,
            "industry": industry,
            "category": {
                "id": category.id,
                "name": category.name,
                "display_name": category.display_name,
                "description": category.description
            },
            "recommended_tracks": recommended_tracks,
            "total_estimated_hours": total_hours,
            "estimated_completion_months": estimated_months,
            "next_steps": recommended_tracks[:3],  # 다음 3단계
            "rationale": f"{current_level} 레벨 학습자를 위한 {category.display_name} 경로 추천"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendation: {str(e)}")

@router.get("/tracks", response_model=List[Dict[str, Any]])
async def get_all_tracks(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty_level: Optional[int] = Query(None, description="Filter by difficulty level"),
    specialization_level: Optional[str] = Query(None, description="Filter by specialization level"),
    db: Session = Depends(get_db)
):
    """모든 학습 트랙 조회 (필터링 지원)"""
    try:
        query = db.query(LearningTrack)
        
        # 필터 적용
        if category:
            query = query.filter(LearningTrack.category == category)
        
        if difficulty_level:
            query = query.filter(LearningTrack.difficulty_level == difficulty_level)
        
        if specialization_level:
            query = query.filter(LearningTrack.specialization_level == specialization_level)
        
        tracks = query.order_by(
            LearningTrack.difficulty_level, 
            LearningTrack.created_at
        ).all()
        
        result = []
        for track in tracks:
            # 카테고리 정보 조회
            category_info = None
            if track.curriculum_category_id:
                category_obj = db.query(CurriculumCategory).filter(
                    CurriculumCategory.id == track.curriculum_category_id
                ).first()
                if category_obj:
                    category_info = {
                        "id": category_obj.id,
                        "name": category_obj.name,
                        "display_name": category_obj.display_name
                    }
            
            modules_count = db.query(LearningModule).filter(
                LearningModule.track_id == track.id
            ).count()
            
            result.append({
                "id": track.id,
                "name": track.name,
                "display_name": track.display_name,
                "category": track.category,
                "curriculum_category": category_info,
                "specialization_level": track.specialization_level,
                "prerequisite_tracks": track.prerequisite_tracks or [],
                "difficulty_level": track.difficulty_level,
                "estimated_hours": track.estimated_hours,
                "description": track.description,
                "modules_count": modules_count,
                "created_at": track.created_at.isoformat()
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tracks: {str(e)}")

@router.get("/health")
async def curriculum_health_check():
    """커리큘럼 API 상태 확인"""
    return {
        "status": "healthy",
        "message": "Curriculum API is operational",
        "version": "1.0.0-phase1"
    }
