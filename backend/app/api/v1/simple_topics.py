"""
간단한 토픽 API - 문제 해결용
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from app.core.database import engine
from sqlalchemy.orm import sessionmaker

# 세션 생성
SessionLocal = sessionmaker(bind=engine)

router = APIRouter(tags=["Simple Topics"])

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/simple-topics/{subject_key}")
async def get_simple_topics(subject_key: str, db: Session = Depends(get_db)):
    """간단한 토픽 조회 API"""
    try:
        print(f"🔍 간단한 토픽 조회: {subject_key}")
        
        # 직접 SQL 사용
        result = db.execute(
            text("SELECT * FROM subject_topics WHERE subject_key = :key ORDER BY display_order"),
            {"key": subject_key}
        )
        rows = result.fetchall()
        
        topics = []
        for row in rows:
            # 컬럼 이름으로 접근
            topic = {
                "id": row[0],
                "subject_key": row[1],
                "topic_key": row[2],
                "weight": row[3],
                "is_core": row[4],
                "display_order": row[5],
                "show_in_coverage": row[6],
                "topic_name": row[7] if len(row) > 7 else None,
                "description": row[8] if len(row) > 8 else None
            }
            topics.append(topic)
        
        return {
            "success": True,
            "subject_key": subject_key,
            "topic_count": len(topics),
            "topics": topics,
            "method": "simple_sql"
        }
        
    except Exception as e:
        print(f"❌ 간단한 토픽 조회 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "subject_key": subject_key
        }
