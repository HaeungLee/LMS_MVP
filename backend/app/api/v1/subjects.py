"""
과목 관리 API
다중 과목 지원을 위한 REST API 엔드포인트들
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.subject_manager import get_subject_manager
from pydantic import BaseModel

# Pydantic 모델들
class SubjectResponse(BaseModel):
    id: int
    key: str
    title: str
    version: str
    created_at: str
    topic_count: int
    core_topic_count: int

class TopicResponse(BaseModel):
    id: int
    key: str
    title: str
    weight: float
    is_core: bool
    display_order: int
    show_in_coverage: bool

class SubjectDetailResponse(BaseModel):
    id: int
    key: str
    title: str
    version: str
    created_at: str
    topic_count: int
    topics: List[TopicResponse]

class SubjectStatisticsResponse(BaseModel):
    total_subjects: int
    total_topics: int
    total_connections: int
    subject_details: List[dict]

# 라우터 생성
router = APIRouter(
    prefix="/subjects",
    tags=["subjects"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(
    db: Session = Depends(get_db)
):
    """
    모든 과목 목록 조회
    """
    subject_manager = get_subject_manager()
    subjects = await subject_manager.get_all_subjects(db)
    return subjects

@router.get("/{subject_key}", response_model=SubjectDetailResponse)
async def get_subject_detail(
    subject_key: str,
    db: Session = Depends(get_db)
):
    """
    특정 과목의 상세 정보 조회 (토픽 목록 포함)
    """
    subject_manager = get_subject_manager()
    subject_detail = await subject_manager.get_subject_with_topics(db, subject_key)

    if not subject_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"과목 '{subject_key}'을 찾을 수 없습니다"
        )

    return subject_detail

@router.get("/{subject_key}/topics", response_model=List[TopicResponse])
async def get_subject_topics(
    subject_key: str,
    db: Session = Depends(get_db)
):
    """
    특정 과목의 토픽 목록 조회
    """
    subject_manager = get_subject_manager()

    # 과목 존재 여부 확인
    subject = await subject_manager.get_subject_by_key(db, subject_key)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"과목 '{subject_key}'을 찾을 수 없습니다"
        )

    topics = await subject_manager.get_subject_topics(db, subject_key)
    return topics

@router.get("/stats/overview", response_model=SubjectStatisticsResponse)
async def get_subject_statistics(
    db: Session = Depends(get_db)
):
    """
    과목 통계 정보 조회
    """
    subject_manager = get_subject_manager()
    stats = await subject_manager.get_subject_statistics(db)
    return stats

@router.get("/available/list")
async def get_available_subjects():
    """
    사용 가능한 과목 키 목록 조회 (간단 버전)
    """
    # 하드코딩된 과목 목록 (실제로는 데이터베이스에서 동적 조회 권장)
    available_subjects = [
        {"key": "python_basics", "title": "Python 기초", "description": "프로그래밍 기초를 배우는 파이썬 과정"},
        {"key": "web_frontend", "title": "웹 프론트엔드 개발", "description": "HTML, CSS, JavaScript를 활용한 웹 개발"},
        {"key": "javascript_basics", "title": "JavaScript 기초", "description": "웹 개발의 핵심 언어인 JavaScript 기초"},
        {"key": "react_fundamentals", "title": "React 기초", "description": "현대적인 웹 UI 라이브러리 React 학습"},
        {"key": "data_science", "title": "데이터 과학 기초", "description": "데이터 분석과 시각화를 위한 Python 도구들"},
        {"key": "sql_database", "title": "SQL 데이터베이스", "description": "관계형 데이터베이스 관리와 SQL 쿼리"}
    ]

    return {
        "subjects": available_subjects,
        "total_count": len(available_subjects)
    }

@router.get("/{subject_key}/validate")
async def validate_subject_access(
    subject_key: str,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    과목 접근 권한 검증
    """
    subject_manager = get_subject_manager()
    is_valid = await subject_manager.validate_subject_access(db, subject_key, user_id)

    return {
        "subject_key": subject_key,
        "is_accessible": is_valid,
        "user_id": user_id
    }
