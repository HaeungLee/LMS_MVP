# -*- coding: utf-8 -*-
"""
PDF 다운로드 API 엔드포인트

학습 자료를 PDF로 내보내기
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from app.core.database import get_db
from app.models.orm import UserNote, User
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/api/v1/pdf")


# ============================================================
# PDF 유틸리티 함수
# ============================================================

def create_pdf_buffer(title: str, content_items: List[dict]) -> BytesIO:
    """
    PDF 생성 헬퍼 함수
    
    Args:
        title: PDF 제목
        content_items: [{"title": "...", "content": "...", "created_at": "..."}, ...]
    
    Returns:
        BytesIO: PDF 데이터 버퍼
    """
    buffer = BytesIO()
    
    # PDF 문서 생성
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=25*mm,
        bottomMargin=25*mm
    )
    
    # 스타일 시트
    styles = getSampleStyleSheet()
    
    # 커스텀 스타일 (한글 지원)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor='#2563eb',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#1e40af',
        spaceAfter=6,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT
    )
    
    meta_style = ParagraphStyle(
        'MetaInfo',
        parent=styles['Normal'],
        fontSize=8,
        textColor='#6b7280',
        spaceAfter=6
    )
    
    # PDF 내용 구성
    story = []
    
    # 제목
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # 내용 아이템들
    for item in content_items:
        # 소제목
        if item.get('title'):
            story.append(Paragraph(item['title'], heading_style))
        
        # 메타 정보 (생성일 등)
        if item.get('created_at'):
            story.append(Paragraph(f"작성일: {item['created_at']}", meta_style))
        
        # 본문
        if item.get('content'):
            # 줄바꿈을 <br/>로 변환
            content = item['content'].replace('\n', '<br/>')
            story.append(Paragraph(content, body_style))
        
        story.append(Spacer(1, 12))
        
        # 구분선
        if item != content_items[-1]:  # 마지막 아이템이 아니면
            story.append(Spacer(1, 6))
    
    # PDF 생성
    doc.build(story)
    buffer.seek(0)
    
    return buffer


# ============================================================
# API 엔드포인트
# ============================================================

@router.get("/notes/export")
async def export_notes_to_pdf(
    track_id: int = None,
    module_id: int = None,
    is_important: bool = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    메모를 PDF로 내보내기
    
    **쿼리 파라미터:**
    - `track_id`: 특정 트랙의 메모만 내보내기
    - `module_id`: 특정 모듈의 메모만 내보내기
    - `is_important`: true이면 중요 메모만 내보내기
    
    **사용 예시:**
    ```
    GET /api/v1/pdf/notes/export?track_id=1&is_important=true
    ```
    
    **응답:**
    - Content-Type: application/pdf
    - 파일명: notes_export_{user_id}_{timestamp}.pdf
    """
    
    # 메모 조회
    query = db.query(UserNote).filter_by(user_id=user.id)
    
    if track_id is not None:
        query = query.filter_by(track_id=track_id)
    
    if module_id is not None:
        query = query.filter_by(module_id=module_id)
    
    if is_important is not None:
        query = query.filter_by(is_important=is_important)
    
    notes = query.order_by(UserNote.created_at.desc()).all()
    
    if not notes:
        raise HTTPException(status_code=404, detail="내보낼 메모가 없습니다")
    
    # PDF 제목
    title = f"{user.display_name or user.email}의 학습 메모"
    
    # 내용 구성
    content_items = []
    for note in notes:
        content_items.append({
            "title": note.title or f"메모 #{note.id}",
            "content": note.content,
            "created_at": note.created_at.strftime("%Y-%m-%d %H:%M")
        })
    
    # PDF 생성
    pdf_buffer = create_pdf_buffer(title, content_items)
    
    # 파일명 생성
    from datetime import datetime
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"notes_export_{user.id}_{timestamp}.pdf"
    
    # 스트리밍 응답
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/note/{note_id}")
async def export_single_note_to_pdf(
    note_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    단일 메모를 PDF로 내보내기
    
    **사용 예시:**
    ```
    GET /api/v1/pdf/note/123
    ```
    """
    
    # 메모 조회
    note = db.query(UserNote).filter_by(
        id=note_id,
        user_id=user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
    
    # PDF 제목
    title = note.title or f"메모 #{note.id}"
    
    # 내용 구성
    content_items = [{
        "title": title,
        "content": note.content,
        "created_at": note.created_at.strftime("%Y-%m-%d %H:%M")
    }]
    
    # PDF 생성
    pdf_buffer = create_pdf_buffer(title, content_items)
    
    # 파일명
    filename = f"note_{note_id}.pdf"
    
    # 스트리밍 응답
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

