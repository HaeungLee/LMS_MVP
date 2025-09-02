"""
Phase 8: 동적 과목 관리 API 엔드포인트
카테고리, 과목, 토픽 관리를 위한 REST API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import engine
from app.models.orm import Subject, Topic  # 기존 ORM 모델 사용
from sqlalchemy.orm import sessionmaker

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


# ============= 카테고리 관리 API =============

@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_subject_categories(
    active_only: bool = Query(True, description="활성 카테고리만 조회"),
    db: Session = Depends(get_db)
):
    """과목 카테고리 목록 조회"""
    try:
        query = db.query(SubjectCategory).order_by(SubjectCategory.order_index)
        
        categories = query.all()
        
        result = []
        for category in categories:
            # 카테고리별 과목 수 계산
            subject_count = db.query(SubjectExtended).filter(
                SubjectExtended.category_id == category.id,
                SubjectExtended.is_active == True if active_only else True
            ).count()
            
            result.append({
                "id": category.id,
                "key": category.key,
                "name": category.name,
                "description": category.description,
                "color_code": category.color_code,
                "order_index": category.order_index,
                "subject_count": subject_count,
                "created_at": category.created_at.isoformat() if category.created_at else None
            })
        
        return {"success": True, "categories": result}
        
    except Exception as e:
        print(f"❌ 카테고리 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"카테고리 조회 실패: {str(e)}")


@router.post("/categories", response_model=Dict[str, Any])
async def create_subject_category(
    category_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """새 과목 카테고리 생성 (관리자만)"""
    try:
        # 이미 존재하는 키인지 확인
        existing = db.query(SubjectCategory).filter(
            SubjectCategory.key == category_data.get('key')
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="이미 존재하는 카테고리 키입니다.")
        
        # 새 카테고리 생성
        category = SubjectCategory(
            key=category_data['key'],
            name=category_data['name'],
            description=category_data.get('description'),
            color_code=category_data.get('color_code', '#3B82F6'),
            order_index=category_data.get('order_index', 0)
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        return {
            "success": True,
            "message": "카테고리가 성공적으로 생성되었습니다.",
            "category": {
                "id": category.id,
                "key": category.key,
                "name": category.name,
                "description": category.description,
                "color_code": category.color_code,
                "order_index": category.order_index
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 카테고리 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"카테고리 생성 실패: {str(e)}")


# ============= 과목 관리 API =============

@router.get("/subjects", response_model=Dict[str, Any])
async def get_subjects(
    category_key: Optional[str] = Query(None, description="카테고리 키로 필터링"),
    active_only: bool = Query(True, description="활성 과목만 조회"),
    include_stats: bool = Query(False, description="통계 정보 포함"),
    db: Session = Depends(get_db)
):
    """과목 목록 조회 (카테고리별 필터링)"""
    try:
        query = db.query(SubjectExtended).join(SubjectCategory)
        
        # 카테고리 필터링
        if category_key:
            query = query.filter(SubjectCategory.key == category_key)
        
        # 활성 과목만 필터링
        if active_only:
            query = query.filter(SubjectExtended.is_active == True)
        
        # 정렬
        query = query.order_by(SubjectCategory.order_index, SubjectExtended.order_index)
        
        subjects = query.all()
        
        result = []
        for subject in subjects:
            subject_data = {
                "id": subject.id,
                "key": subject.key,
                "name": subject.name,
                "description": subject.description,
                "category": {
                    "id": subject.category.id,
                    "key": subject.category.key,
                    "name": subject.category.name,
                    "color_code": subject.category.color_code
                },
                "difficulty_level": subject.difficulty_level,
                "estimated_duration": subject.estimated_duration,
                "icon_name": subject.icon_name,
                "color_code": subject.color_code,
                "is_active": subject.is_active,
                "order_index": subject.order_index,
                "created_at": subject.created_at.isoformat() if subject.created_at else None,
                "updated_at": subject.updated_at.isoformat() if subject.updated_at else None
            }
            
            # 통계 정보 포함
            if include_stats:
                # 토픽 수
                topic_count = db.query(SubjectTopic).filter(
                    SubjectTopic.subject_id == subject.id
                ).count()
                
                # 학습자 수  
                learner_count = db.query(UserSubjectProgress).filter(
                    UserSubjectProgress.subject_id == subject.id
                ).count()
                
                subject_data.update({
                    "stats": {
                        "topic_count": topic_count,
                        "learner_count": learner_count,
                        "total_problems": subject.total_problems or 0,
                        "average_completion_rate": subject.average_completion_rate or 0.0
                    }
                })
            
            result.append(subject_data)
        
        return {"success": True, "subjects": result}
        
    except Exception as e:
        print(f"❌ 과목 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"과목 조회 실패: {str(e)}")


@router.get("/subjects/{subject_id}", response_model=Dict[str, Any])
async def get_subject_detail(
    subject_id: int,
    include_topics: bool = Query(False, description="토픽 정보 포함"),
    include_prerequisites: bool = Query(False, description="전제조건 포함"),
    db: Session = Depends(get_db)
):
    """과목 상세 정보 조회"""
    try:
        subject = db.query(SubjectExtended).filter(SubjectExtended.id == subject_id).first()
        
        if not subject:
            raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")
        
        result = {
            "id": subject.id,
            "key": subject.key,
            "name": subject.name,
            "description": subject.description,
            "category": {
                "id": subject.category.id,
                "key": subject.category.key,
                "name": subject.category.name,
                "color_code": subject.category.color_code
            },
            "difficulty_level": subject.difficulty_level,
            "estimated_duration": subject.estimated_duration,
            "icon_name": subject.icon_name,
            "color_code": subject.color_code,
            "is_active": subject.is_active,
            "order_index": subject.order_index,
            "total_problems": subject.total_problems or 0,
            "total_students": subject.total_students or 0,
            "average_completion_rate": subject.average_completion_rate or 0.0,
            "created_at": subject.created_at.isoformat() if subject.created_at else None,
            "updated_at": subject.updated_at.isoformat() if subject.updated_at else None
        }
        
        # 토픽 정보 포함
        if include_topics:
            topics = db.query(SubjectTopic).filter(
                SubjectTopic.subject_id == subject_id
            ).order_by(SubjectTopic.order_index).all()
            
            result["topics"] = [
                {
                    "id": topic.id,
                    "topic_key": topic.topic_key,
                    "topic_name": topic.topic_name,
                    "description": topic.description,
                    "order_index": topic.order_index,
                    "learning_objectives": topic.learning_objectives,
                    "estimated_duration": topic.estimated_duration,
                    "difficulty_level": topic.difficulty_level,
                    "problem_count": topic.problem_count or 0,
                    "completion_rate": topic.completion_rate or 0.0
                }
                for topic in topics
            ]
        
        # 전제조건 정보 포함
        if include_prerequisites:
            prerequisites = db.query(SubjectPrerequisite).filter(
                SubjectPrerequisite.subject_id == subject_id
            ).all()
            
            result["prerequisites"] = [
                {
                    "prerequisite_subject": {
                        "id": prereq.prerequisite_subject.id,
                        "key": prereq.prerequisite_subject.key,
                        "name": prereq.prerequisite_subject.name
                    },
                    "is_required": prereq.is_required
                }
                for prereq in prerequisites
            ]
        
        return {"success": True, "subject": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 과목 상세 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"과목 상세 조회 실패: {str(e)}")


@router.post("/subjects", response_model=Dict[str, Any])
async def create_subject(
    subject_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """새 과목 생성 (관리자만)"""
    try:
        # 이미 존재하는 키인지 확인
        existing = db.query(SubjectExtended).filter(
            SubjectExtended.key == subject_data.get('key')
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="이미 존재하는 과목 키입니다.")
        
        # 카테고리 존재 확인
        category = db.query(SubjectCategory).filter(
            SubjectCategory.id == subject_data['category_id']
        ).first()
        
        if not category:
            raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다.")
        
        # 새 과목 생성
        subject = SubjectExtended(
            key=subject_data['key'],
            name=subject_data['name'],
            description=subject_data.get('description'),
            category_id=subject_data['category_id'],
            difficulty_level=subject_data.get('difficulty_level', 'beginner'),
            estimated_duration=subject_data.get('estimated_duration'),
            icon_name=subject_data.get('icon_name'),
            color_code=subject_data.get('color_code'),
            is_active=subject_data.get('is_active', False),
            order_index=subject_data.get('order_index', 0)
        )
        
        db.add(subject)
        db.commit()
        db.refresh(subject)
        
        return {
            "success": True,
            "message": "과목이 성공적으로 생성되었습니다.",
            "subject": {
                "id": subject.id,
                "key": subject.key,
                "name": subject.name,
                "description": subject.description,
                "category_id": subject.category_id,
                "difficulty_level": subject.difficulty_level,
                "estimated_duration": subject.estimated_duration,
                "icon_name": subject.icon_name,
                "color_code": subject.color_code,
                "is_active": subject.is_active,
                "order_index": subject.order_index
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 과목 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"과목 생성 실패: {str(e)}")


@router.put("/subjects/{subject_id}", response_model=Dict[str, Any])
async def update_subject(
    subject_id: int,
    subject_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """과목 정보 수정"""
    try:
        subject = db.query(SubjectExtended).filter(SubjectExtended.id == subject_id).first()
        
        if not subject:
            raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")
        
        # 키 중복 확인 (다른 과목이 같은 키를 사용하는지)
        if 'key' in subject_data and subject_data['key'] != subject.key:
            existing = db.query(SubjectExtended).filter(
                SubjectExtended.key == subject_data['key'],
                SubjectExtended.id != subject_id
            ).first()
            
            if existing:
                raise HTTPException(status_code=400, detail="이미 존재하는 과목 키입니다.")
        
        # 카테고리 존재 확인
        if 'category_id' in subject_data:
            category = db.query(SubjectCategory).filter(
                SubjectCategory.id == subject_data['category_id']
            ).first()
            
            if not category:
                raise HTTPException(status_code=400, detail="존재하지 않는 카테고리입니다.")
        
        # 필드 업데이트
        for field, value in subject_data.items():
            if hasattr(subject, field):
                setattr(subject, field, value)
        
        subject.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(subject)
        
        return {
            "success": True,
            "message": "과목이 성공적으로 수정되었습니다.",
            "subject": {
                "id": subject.id,
                "key": subject.key,
                "name": subject.name,
                "description": subject.description,
                "category_id": subject.category_id,
                "difficulty_level": subject.difficulty_level,
                "estimated_duration": subject.estimated_duration,
                "icon_name": subject.icon_name,
                "color_code": subject.color_code,
                "is_active": subject.is_active,
                "order_index": subject.order_index,
                "updated_at": subject.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 과목 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"과목 수정 실패: {str(e)}")


# ============= 토픽 관리 API =============

@router.get("/subjects/{subject_id}/topics", response_model=Dict[str, Any])
async def get_subject_topics(
    subject_id: int,
    db: Session = Depends(get_db)
):
    """과목별 토픽 목록 조회"""
    try:
        # 과목 존재 확인
        subject = db.query(SubjectExtended).filter(SubjectExtended.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")
        
        topics = db.query(SubjectTopic).filter(
            SubjectTopic.subject_id == subject_id
        ).order_by(SubjectTopic.order_index).all()
        
        result = [
            {
                "id": topic.id,
                "topic_key": topic.topic_key,
                "topic_name": topic.topic_name,
                "description": topic.description,
                "order_index": topic.order_index,
                "parent_topic_id": topic.parent_topic_id,
                "learning_objectives": topic.learning_objectives,
                "estimated_duration": topic.estimated_duration,
                "difficulty_level": topic.difficulty_level,
                "problem_count": topic.problem_count or 0,
                "completion_rate": topic.completion_rate or 0.0,
                "created_at": topic.created_at.isoformat() if topic.created_at else None,
                "updated_at": topic.updated_at.isoformat() if topic.updated_at else None
            }
            for topic in topics
        ]
        
        return {"success": True, "topics": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 토픽 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"토픽 조회 실패: {str(e)}")


@router.post("/subjects/{subject_id}/topics", response_model=Dict[str, Any])
async def create_subject_topic(
    subject_id: int,
    topic_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """과목에 새 토픽 추가"""
    try:
        # 과목 존재 확인
        subject = db.query(SubjectExtended).filter(SubjectExtended.id == subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")
        
        # 같은 과목 내에서 토픽 키 중복 확인
        existing = db.query(SubjectTopic).filter(
            SubjectTopic.subject_id == subject_id,
            SubjectTopic.topic_key == topic_data.get('topic_key')
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="이미 존재하는 토픽 키입니다.")
        
        # 새 토픽 생성
        topic = SubjectTopic(
            subject_id=subject_id,
            topic_key=topic_data['topic_key'],
            topic_name=topic_data['topic_name'],
            description=topic_data.get('description'),
            order_index=topic_data.get('order_index', 0),
            parent_topic_id=topic_data.get('parent_topic_id'),
            learning_objectives=topic_data.get('learning_objectives', []),
            estimated_duration=topic_data.get('estimated_duration'),
            difficulty_level=topic_data.get('difficulty_level', 'beginner')
        )
        
        db.add(topic)
        db.commit()
        db.refresh(topic)
        
        return {
            "success": True,
            "message": "토픽이 성공적으로 생성되었습니다.",
            "topic": {
                "id": topic.id,
                "topic_key": topic.topic_key,
                "topic_name": topic.topic_name,
                "description": topic.description,
                "order_index": topic.order_index,
                "parent_topic_id": topic.parent_topic_id,
                "learning_objectives": topic.learning_objectives,
                "estimated_duration": topic.estimated_duration,
                "difficulty_level": topic.difficulty_level
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 토픽 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"토픽 생성 실패: {str(e)}")


# ============= 통계 및 진도 API =============

@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_system_overview(db: Session = Depends(get_db)):
    """전체 시스템 개요 통계"""
    try:
        # 전체 통계
        total_categories = db.query(SubjectCategory).count()
        total_subjects = db.query(SubjectExtended).count()
        active_subjects = db.query(SubjectExtended).filter(SubjectExtended.is_active == True).count()
        total_topics = db.query(SubjectTopic).count()
        total_learners = db.query(UserSubjectProgress).count()
        
        # 카테고리별 과목 수
        category_stats = []
        categories = db.query(SubjectCategory).order_by(SubjectCategory.order_index).all()
        
        for category in categories:
            subject_count = db.query(SubjectExtended).filter(
                SubjectExtended.category_id == category.id
            ).count()
            
            active_count = db.query(SubjectExtended).filter(
                SubjectExtended.category_id == category.id,
                SubjectExtended.is_active == True
            ).count()
            
            category_stats.append({
                "category": {
                    "id": category.id,
                    "key": category.key,
                    "name": category.name,
                    "color_code": category.color_code
                },
                "total_subjects": subject_count,
                "active_subjects": active_count
            })
        
        return {
            "success": True,
            "overview": {
                "totals": {
                    "categories": total_categories,
                    "subjects": total_subjects,
                    "active_subjects": active_subjects,
                    "topics": total_topics,
                    "learners": total_learners
                },
                "category_breakdown": category_stats
            }
        }
        
    except Exception as e:
        print(f"❌ 시스템 개요 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"시스템 개요 조회 실패: {str(e)}")


# ============= 사용자 진도 관리 API =============

@router.get("/users/{user_id}/progress", response_model=Dict[str, Any])
async def get_user_subject_progress(
    user_id: int,
    subject_id: Optional[int] = Query(None, description="특정 과목 진도만 조회"),
    db: Session = Depends(get_db)
):
    """사용자 과목별 진도 조회"""
    try:
        query = db.query(UserSubjectProgress).filter(
            UserSubjectProgress.user_id == user_id
        )
        
        if subject_id:
            query = query.filter(UserSubjectProgress.subject_id == subject_id)
        
        progress_records = query.all()
        
        result = []
        for progress in progress_records:
            result.append({
                "subject": {
                    "id": progress.subject.id,
                    "key": progress.subject.key,
                    "name": progress.subject.name,
                    "icon_name": progress.subject.icon_name,
                    "color_code": progress.subject.color_code
                },
                "progress": {
                    "current_topic_id": progress.current_topic_id,
                    "completed_topics": progress.completed_topics,
                    "progress_percentage": progress.progress_percentage,
                    "total_study_time": progress.total_study_time,
                    "problems_solved": progress.problems_solved,
                    "problems_correct": progress.problems_correct,
                    "current_streak": progress.current_streak,
                    "best_streak": progress.best_streak,
                    "started_at": progress.started_at.isoformat() if progress.started_at else None,
                    "last_studied_at": progress.last_studied_at.isoformat() if progress.last_studied_at else None
                }
            })
        
        return {"success": True, "user_progress": result}
        
    except Exception as e:
        print(f"❌ 사용자 진도 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사용자 진도 조회 실패: {str(e)}")
