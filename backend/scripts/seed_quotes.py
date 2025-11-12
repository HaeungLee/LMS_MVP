# -*- coding: utf-8 -*-
"""
명언 시딩 스크립트

명언집 파일을 파싱하여 DB에 저장
"""
import sys
import os
import re
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 백엔드 경로를 sys.path에 추가
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.orm import Quote

def parse_quote_line(line: str, order_num: int) -> dict | None:
    """
    명언 한 줄을 파싱
    
    형식: "1. 내용 - 저자"
    예시: "1. 평생 살 것처럼 꿈을 꾸어라. 그리고 내일 죽을 것 처럼 오늘을 살아라. - 제임스 딘"
    """
    line = line.strip()
    if not line:
        return None
    
    # "숫자. 내용 - 저자" 형식 파싱
    match = re.match(r'^\d+\.\s+(.+?)(?:\s+-\s+(.+))?$', line)
    if not match:
        return None
    
    content, author = match.groups()
    
    # 카테고리 자동 분류 (키워드 기반)
    category = categorize_quote(content)
    
    return {
        "order_number": order_num,
        "content": content.strip(),
        "author": author.strip() if author else None,
        "category": category,
        "is_active": True
    }


def categorize_quote(content: str) -> str:
    """
    명언 내용을 기반으로 카테고리 자동 분류
    """
    content_lower = content.lower()
    
    # 카테고리 키워드 매핑
    categories = {
        "courage": ["용기", "두려움", "도전", "모험"],
        "failure": ["실패", "실수", "넘어", "좌절"],
        "success": ["성공", "승리", "이룬", "달성"],
        "persistence": ["계속", "끈기", "꾸준", "포기"],
        "dream": ["꿈", "비전", "희망", "상상"],
        "action": ["행동", "실천", "움직", "시작"],
        "learning": ["배우", "학습", "지식", "깨달"],
        "time": ["시간", "오늘", "내일", "순간"],
        "change": ["변화", "바꾸", "새로운", "다른"],
        "effort": ["노력", "열심", "최선", "힘"],
    }
    
    for category, keywords in categories.items():
        if any(keyword in content_lower for keyword in keywords):
            return category
    
    return "general"  # 기본 카테고리


def seed_quotes():
    """명언집 파일을 읽어 DB에 시딩"""
    
    # 명언집 파일 경로
    quotes_file = backend_path.parent / "명언집"
    
    if not quotes_file.exists():
        print(f"❌ 명언집 파일을 찾을 수 없습니다: {quotes_file}")
        return
    
    print(f"📖 명언집 파일 읽기: {quotes_file}")
    
    # 파일 읽기
    with open(quotes_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📝 총 {len(lines)}줄 발견")
    
    # 파싱
    quotes_data = []
    for i, line in enumerate(lines, start=1):
        parsed = parse_quote_line(line, i)
        if parsed:
            quotes_data.append(parsed)
    
    print(f"✅ {len(quotes_data)}개 명언 파싱 완료")
    
    # DB에 저장
    db = SessionLocal()
    try:
        # 기존 명언 삭제 (재시딩 가능하도록)
        db.execute(text("DELETE FROM quotes"))
        db.commit()
        print("🗑️  기존 명언 삭제 완료")
        
        # 새 명언 추가
        for quote_dict in quotes_data:
            quote = Quote(**quote_dict)
            db.add(quote)
        
        db.commit()
        print(f"💾 {len(quotes_data)}개 명언 DB 저장 완료")
        
        # 통계 출력
        print("\n📊 카테고리별 통계:")
        result = db.execute(text("""
            SELECT category, COUNT(*) as count
            FROM quotes
            GROUP BY category
            ORDER BY count DESC
        """))
        
        for row in result:
            print(f"  - {row[0]}: {row[1]}개")
        
        print("\n🎉 명언 시딩 완료!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 에러 발생: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_quotes()

