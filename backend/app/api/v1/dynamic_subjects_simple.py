"""
Phase 8: 동적 과목 관리 API 엔드포인트 (간소화 버전)
기존 subjects, topics 테이블과 연동
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import engine
from app.models.orm import Subject, Topic  # 기존 ORM 모델 사용
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# 세션 생성
SessionLocal = sessionmaker(bind=engine)

router = APIRouter(tags=["Dynamic Subjects"])

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============= 기본 과목 관리 API =============

@router.get("/subjects", response_model=List[Dict[str, Any]])
async def get_subjects(
    active_only: bool = Query(True, description="활성 과목만 조회"),
    db: Session = Depends(get_db)
):
    """과목 목록 조회"""
    try:
        # 원시 SQL을 사용해서 확장된 subjects 테이블에서 조회
        query = """
            SELECT id, key, title as name, 
                   description, difficulty_level, estimated_duration,
                   icon_name, color_code, is_active, order_index, created_at
            FROM subjects 
        """
        
        if active_only:
            query += " WHERE is_active = true"
            
        query += " ORDER BY order_index"
        
        result = db.execute(text(query))
        subjects = result.fetchall()
        
        response = []
        for subject in subjects:
            # 과목별 토픽 수는 나중에 추가 (연결 관계 확인 필요)
            topic_count = 0
            
            response.append({
                "id": subject.id,
                "key": subject.key,
                "name": subject.name,
                "description": subject.description,
                "difficulty_level": subject.difficulty_level,
                "estimated_duration": subject.estimated_duration,
                "icon_name": subject.icon_name,
                "color_code": subject.color_code,
                "is_active": subject.is_active,
                "order_index": subject.order_index,
                "topic_count": topic_count,
                "created_at": subject.created_at.isoformat() if subject.created_at else None
            })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"과목 조회 실패: {str(e)}")


@router.get("/subjects/{subject_key}/topics", response_model=List[Dict[str, Any]])
async def get_subject_topics(
    subject_key: str,
    db: Session = Depends(get_db)
):
    """특정 과목의 토픽 목록 조회"""
    try:
        # 과목 존재 여부 확인
        subject = db.query(Subject).filter(Subject.key == subject_key).first()
        if not subject:
            raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다")
        
        # 토픽 조회
        topics = db.query(Topic).filter(Topic.subject_key == subject_key).all()
        
        result = []
        for topic in topics:
            result.append({
                "id": topic.id,
                "key": topic.key,
                "name": topic.name,
                "description": topic.description,
                "subject_key": topic.subject_key,
                "weight": topic.weight,
                "is_core": topic.is_core,
                "display_order": topic.display_order,
                "show_in_coverage": topic.show_in_coverage
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"토픽 조회 실패: {str(e)}")


@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_subject_categories(db: Session = Depends(get_db)):
    """과목 카테고리 목록 조회 (subject_categories 테이블에서)"""
    try:
        # 원시 SQL로 새로 생성된 subject_categories 테이블 조회
        result = db.execute(text("""
            SELECT id, key, name, description, color_code, order_index, created_at
            FROM subject_categories 
            ORDER BY order_index
        """))
        
        categories = []
        for row in result:
            categories.append({
                "id": row.id,
                "key": row.key,
                "name": row.name,
                "description": row.description,
                "color_code": row.color_code,
                "order_index": row.order_index,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리 조회 실패: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_dynamic_subjects_stats(db: Session = Depends(get_db)):
    """동적 과목 관리 통계"""
    try:
        # 기본 통계 (원시 SQL 사용)
        total_subjects = db.execute(text("SELECT COUNT(*) FROM subjects")).scalar()
        active_subjects = db.execute(text("SELECT COUNT(*) FROM subjects WHERE is_active = true")).scalar()
        total_topics = db.query(Topic).count()
        
        # 카테고리별 과목 수 (subject_categories와 연결된 과목이 있다면)
        category_stats = db.execute(text("""
            SELECT c.name, COUNT(s.id) as subject_count
            FROM subject_categories c
            LEFT JOIN subjects s ON s.category = c.key
            GROUP BY c.id, c.name
            ORDER BY c.order_index
        """)).fetchall()
        
        return {
            "total_subjects": total_subjects,
            "active_subjects": active_subjects,
            "total_topics": total_topics,
            "category_breakdown": [
                {"category": row.name, "subject_count": row.subject_count}
                for row in category_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """동적 과목 관리 API 상태 확인"""
    return {
        "status": "healthy",
        "service": "dynamic_subjects",
        "timestamp": datetime.utcnow().isoformat()
    }
