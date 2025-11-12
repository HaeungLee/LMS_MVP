# -*- coding: utf-8 -*-
"""
명언 API 엔드포인트

랜덤 명언 제공, 카테고리별 필터링
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import random

from app.core.database import get_db
from app.models.orm import Quote

router = APIRouter(prefix="/api/v1/quotes")


@router.get("/random")
async def get_random_quote(
    category: Optional[str] = Query(None, description="카테고리 필터 (courage, failure, success, persistence, dream, action, learning, time, change, effort, general)"),
    db: Session = Depends(get_db)
):
    """
    랜덤 명언 가져오기
    
    **카테고리:**
    - `courage`: 용기
    - `failure`: 실패
    - `success`: 성공
    - `persistence`: 끈기
    - `dream`: 꿈
    - `action`: 행동
    - `learning`: 학습
    - `time`: 시간
    - `change`: 변화
    - `effort`: 노력
    - `general`: 일반
    """
    
    # 활성화된 명언만 조회
    query = db.query(Quote).filter_by(is_active=True)
    
    # 카테고리 필터
    if category:
        query = query.filter_by(category=category)
    
    quotes = query.all()
    
    if not quotes:
        raise HTTPException(
            status_code=404,
            detail="명언을 찾을 수 없습니다. 다른 카테고리를 시도해보세요."
        )
    
    # 랜덤 선택
    selected = random.choice(quotes)
    
    return {
        "id": selected.id,
        "content": selected.content,
        "author": selected.author,
        "category": selected.category,
        "order_number": selected.order_number
    }


@router.get("/list")
async def list_quotes(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(20, ge=1, le=100, description="최대 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db)
):
    """
    명언 목록 조회 (페이지네이션)
    """
    
    query = db.query(Quote).filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    # 원본 순서대로 정렬
    query = query.order_by(Quote.order_number)
    
    total = query.count()
    quotes = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "quotes": [
            {
                "id": q.id,
                "content": q.content,
                "author": q.author,
                "category": q.category,
                "order_number": q.order_number
            }
            for q in quotes
        ]
    }


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """
    카테고리별 명언 개수
    """
    
    result = db.query(
        Quote.category,
        func.count(Quote.id).label('count')
    ).filter_by(is_active=True).group_by(Quote.category).all()
    
    return {
        "categories": [
            {
                "name": row[0],
                "count": row[1]
            }
            for row in result
        ]
    }


@router.get("/{quote_id}")
async def get_quote_by_id(
    quote_id: int,
    db: Session = Depends(get_db)
):
    """특정 명언 조회"""
    
    quote = db.query(Quote).filter_by(id=quote_id, is_active=True).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="명언을 찾을 수 없습니다")
    
    return {
        "id": quote.id,
        "content": quote.content,
        "author": quote.author,
        "category": quote.category,
        "order_number": quote.order_number
    }

