#!/usr/bin/env python3
"""
데이터베이스 연결 및 문제 데이터 확인 스크립트
"""

from app.core.database import get_db
from app.models.orm import Question

def check_database():
    try:
        db = next(get_db())
        print("✅ 데이터베이스 연결 성공")
        
        # 전체 문제 개수 확인
        total_questions = db.query(Question).count()
        print(f"📊 전체 문제 개수: {total_questions}")
        
        # python_basics 문제 확인
        python_questions = db.query(Question).filter(Question.subject == 'python_basics').all()
        print(f"📊 python_basics 문제 개수: {len(python_questions)}")
        
        if python_questions:
            print("\n📝 python_basics 문제 샘플:")
            for i, q in enumerate(python_questions[:3]):
                title = q.code_snippet[:50] if q.code_snippet else "제목 없음"
                print(f"  {i+1}. ID: {q.id}, 제목: {title}...")
                print(f"     타입: {q.question_type}, 난이도: {q.difficulty}")
        
        # 난이도별 분포 확인
        easy = [q for q in python_questions if (q.difficulty or '').lower() == 'easy']
        medium = [q for q in python_questions if (q.difficulty or '').lower() == 'medium']  
        hard = [q for q in python_questions if (q.difficulty or '').lower() == 'hard']
        
        print(f"\n📊 난이도별 분포:")
        print(f"  - Easy: {len(easy)}개")
        print(f"  - Medium: {len(medium)}개") 
        print(f"  - Hard: {len(hard)}개")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
