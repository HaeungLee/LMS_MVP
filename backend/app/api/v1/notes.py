# -*- coding: utf-8 -*-
"""
사용자 메모 API 엔드포인트

학습 중 작성하는 메모 CRUD
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.orm import UserNote, User
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/api/v1/notes")


# ============================================================
# Pydantic 스키마
# ============================================================

class NoteCreate(BaseModel):
    """메모 생성 요청"""
    track_id: Optional[int] = None
    module_id: Optional[int] = None
    section: Optional[str] = None  # "textbook", "practice", "quiz", "general"
    title: Optional[str] = None
    content: str
    tags: List[str] = []
    is_important: bool = False


class NoteUpdate(BaseModel):
    """메모 수정 요청"""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_important: Optional[bool] = None


class NoteResponse(BaseModel):
    """메모 응답"""
    id: int
    user_id: int
    track_id: Optional[int]
    module_id: Optional[int]
    section: Optional[str]
    title: Optional[str]
    content: str
    tags: List[str]
    is_important: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# API 엔드포인트
# ============================================================

@router.post("", response_model=NoteResponse)
async def create_note(
    note_data: NoteCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새 메모 생성
    
    **사용 예시:**
    ```json
    {
      "track_id": 1,
      "module_id": 5,
      "section": "textbook",
      "title": "for 루프 정리",
      "content": "for i in range(10): 이렇게 사용한다",
      "tags": ["python", "loops"],
      "is_important": true
    }
    ```
    """
    
    note = UserNote(
        user_id=user.id,
        track_id=note_data.track_id,
        module_id=note_data.module_id,
        section=note_data.section,
        title=note_data.title,
        content=note_data.content,
        tags=note_data.tags,
        is_important=note_data.is_important
    )
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return note


@router.get("", response_model=List[NoteResponse])
async def list_notes(
    track_id: Optional[int] = Query(None, description="트랙 ID로 필터링"),
    module_id: Optional[int] = Query(None, description="모듈 ID로 필터링"),
    section: Optional[str] = Query(None, description="섹션으로 필터링"),
    is_important: Optional[bool] = Query(None, description="중요 메모만 조회"),
    tag: Optional[str] = Query(None, description="태그로 필터링"),
    limit: int = Query(50, ge=1, le=200, description="최대 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    메모 목록 조회 (필터링 & 페이지네이션)
    
    **쿼리 파라미터:**
    - `track_id`: 특정 트랙의 메모만 조회
    - `module_id`: 특정 모듈의 메모만 조회
    - `section`: textbook, practice, quiz, general 중 하나
    - `is_important`: true이면 중요 메모만 조회
    - `tag`: 특정 태그가 포함된 메모만 조회
    """
    
    query = db.query(UserNote).filter_by(user_id=user.id)
    
    # 필터 적용
    if track_id is not None:
        query = query.filter_by(track_id=track_id)
    
    if module_id is not None:
        query = query.filter_by(module_id=module_id)
    
    if section is not None:
        query = query.filter_by(section=section)
    
    if is_important is not None:
        query = query.filter_by(is_important=is_important)
    
    if tag is not None:
        # PostgreSQL ARRAY 필터링
        query = query.filter(UserNote.tags.contains([tag]))
    
    # 최신순 정렬
    query = query.order_by(UserNote.created_at.desc())
    
    # 페이지네이션
    notes = query.offset(offset).limit(limit).all()
    
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """특정 메모 조회"""
    
    note = db.query(UserNote).filter_by(
        id=note_id,
        user_id=user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
    
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    메모 수정
    
    **부분 수정 가능** - 변경할 필드만 전송하면 됩니다.
    """
    
    note = db.query(UserNote).filter_by(
        id=note_id,
        user_id=user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
    
    # 부분 업데이트
    if note_data.title is not None:
        note.title = note_data.title
    
    if note_data.content is not None:
        note.content = note_data.content
    
    if note_data.tags is not None:
        note.tags = note_data.tags
    
    if note_data.is_important is not None:
        note.is_important = note_data.is_important
    
    db.commit()
    db.refresh(note)
    
    return note


@router.delete("/{note_id}")
async def delete_note(
    note_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """메모 삭제"""
    
    note = db.query(UserNote).filter_by(
        id=note_id,
        user_id=user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
    
    db.delete(note)
    db.commit()
    
    return {"message": "메모가 삭제되었습니다", "note_id": note_id}


@router.get("/stats/summary")
async def get_note_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    메모 통계
    
    - 전체 메모 개수
    - 중요 메모 개수
    - 최근 7일 메모 개수
    - 사용된 태그 목록
    """
    from sqlalchemy import func
    from datetime import timedelta
    
    total_notes = db.query(func.count(UserNote.id)).filter_by(user_id=user.id).scalar()
    
    important_notes = db.query(func.count(UserNote.id)).filter_by(
        user_id=user.id,
        is_important=True
    ).scalar()
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_notes = db.query(func.count(UserNote.id)).filter(
        UserNote.user_id == user.id,
        UserNote.created_at >= seven_days_ago
    ).scalar()
    
    # 모든 태그 수집
    all_notes = db.query(UserNote.tags).filter_by(user_id=user.id).all()
    all_tags = set()
    for note in all_notes:
        if note.tags:
            all_tags.update(note.tags)
    
    return {
        "total_notes": total_notes,
        "important_notes": important_notes,
        "recent_notes": recent_notes,
        "all_tags": sorted(list(all_tags))
    }

