#!/usr/bin/env python3
"""
데이터베이스 연결 및 문제 데이터 확인 스크립트
"""

from app.core.database import get_db
from app.models.orm import Question, Submission, SubmissionItem
from datetime import datetime, timedelta

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
        
        # 제출 기록 확인
        print("\n🔍 제출 기록 분석...")
        total_submissions = db.query(Submission).count()
        print(f"📊 전체 제출 기록: {total_submissions}개")
        
        if total_submissions == 0:
            print("❌ 제출 기록이 없습니다!")
            print("💡 학습 지표가 0으로 표시되는 이유: 데이터가 없음")
            print("💡 해결책: 퀴즈를 풀어서 제출 기록을 생성해야 합니다.")
        else:
            # 최근 제출 확인
            recent_submission = db.query(Submission).order_by(Submission.submitted_at.desc()).first()
            if recent_submission:
                print(f"🕒 최근 제출: {recent_submission.submitted_at}")
                print(f"📚 과목: {recent_submission.subject}")
                print(f"👤 사용자 ID: {recent_submission.user_id}")
            
            # 최근 7일 제출
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_count = db.query(Submission).filter(
                Submission.submitted_at >= seven_days_ago
            ).count()
            print(f"📅 최근 7일 제출: {recent_count}개")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
