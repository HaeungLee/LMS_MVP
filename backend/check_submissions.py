#!/usr/bin/env python3
"""
제출 기록과 학습 상태 디버깅
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.orm import Submission, SubmissionItem, User
from datetime import datetime, timedelta

def check_submissions():
    """제출 기록 확인"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        print("🔍 제출 기록 분석...")
        
        # 전체 제출 수
        total_submissions = db.query(Submission).count()
        print(f"📊 전체 제출 기록: {total_submissions}개")
        
        if total_submissions == 0:
            print("❌ 제출 기록이 없습니다!")
            print("💡 학습 지표가 0으로 표시되는 이유: 데이터가 없음")
            return
        
        # 최근 제출 확인
        recent_submission = db.query(Submission).order_by(Submission.submitted_at.desc()).first()
        if recent_submission:
            print(f"🕒 최근 제출: {recent_submission.submitted_at}")
            print(f"📚 과목: {recent_submission.subject}")
            print(f"👤 사용자 ID: {recent_submission.user_id}")
        
        # 과목별 제출 수
        subjects = db.execute(text("""
            SELECT subject, COUNT(*) as count 
            FROM submissions 
            GROUP BY subject
        """)).fetchall()
        
        print("\n📚 과목별 제출 기록:")
        for subject_row in subjects:
            print(f"  - {subject_row[0]}: {subject_row[1]}개")
        
        # 최근 7일 제출
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = db.query(Submission).filter(
            Submission.submitted_at >= seven_days_ago
        ).count()
        print(f"\n📅 최근 7일 제출: {recent_count}개")
        
        # 사용자별 제출 수
        users = db.execute(text("""
            SELECT user_id, COUNT(*) as count 
            FROM submissions 
            GROUP BY user_id
        """)).fetchall()
        
        print("\n👥 사용자별 제출 기록:")
        for user_row in users:
            print(f"  - 사용자 {user_row[0]}: {user_row[1]}개")
            
        # 세션 시간 확인
        avg_time = db.execute(text("""
            SELECT AVG(time_taken) as avg_time 
            FROM submissions 
            WHERE time_taken IS NOT NULL AND time_taken > 0
        """)).fetchone()
        
        if avg_time and avg_time[0]:
            print(f"\n⏱️ 평균 세션 시간: {float(avg_time[0])/60.0:.1f}분")
        else:
            print("\n⏱️ 세션 시간 데이터 없음")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_submissions()
