"""
UserProgress 데이터 확인 스크립트
- last_accessed_at 필드가 제대로 업데이트되고 있는지 확인
"""

import asyncio
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.orm import UserProgress, User

async def check_user_progress():
    db = next(get_db())
    
    print("=" * 60)
    print("UserProgress 테이블 데이터 확인")
    print("=" * 60)
    
    # 1. 전체 UserProgress 레코드 수
    total_records = db.query(UserProgress).count()
    print(f"\n📊 전체 UserProgress 레코드: {total_records}개")
    
    # 2. last_accessed_at이 NULL인 레코드 수
    null_accessed = db.query(UserProgress).filter(
        UserProgress.last_accessed_at.is_(None)
    ).count()
    print(f"   - last_accessed_at이 NULL인 레코드: {null_accessed}개")
    print(f"   - last_accessed_at이 있는 레코드: {total_records - null_accessed}개")
    
    # 3. time_spent_minutes가 0이 아닌 레코드
    has_time = db.query(UserProgress).filter(
        UserProgress.time_spent_minutes > 0
    ).count()
    print(f"   - time_spent_minutes > 0인 레코드: {has_time}개")
    
    # 4. 사용자별 통계
    print("\n👤 사용자별 UserProgress 현황:")
    user_stats = db.query(
        UserProgress.user_id,
        User.email,
        func.count(UserProgress.id).label('total_progress'),
        func.sum(UserProgress.time_spent_minutes).label('total_minutes'),
        func.count(UserProgress.last_accessed_at).label('has_accessed_at')
    ).join(
        User, UserProgress.user_id == User.id
    ).group_by(
        UserProgress.user_id, User.email
    ).all()
    
    for stat in user_stats:
        print(f"\n   User ID {stat.user_id} ({stat.email}):")
        print(f"   - 총 Progress 레코드: {stat.total_progress}개")
        print(f"   - 총 학습 시간: {stat.total_minutes or 0}분")
        print(f"   - last_accessed_at 있음: {stat.has_accessed_at}개")
    
    # 5. 최근 5개 레코드 상세 조회
    print("\n📋 최근 UserProgress 레코드 5개:")
    recent_records = db.query(UserProgress).order_by(
        UserProgress.updated_at.desc()
    ).limit(5).all()
    
    for record in recent_records:
        print(f"\n   ID: {record.id}")
        print(f"   User ID: {record.user_id}")
        print(f"   Lesson ID: {record.lesson_id}")
        print(f"   Progress: {record.progress_percentage}%")
        print(f"   Time Spent: {record.time_spent_minutes}분")
        print(f"   Last Accessed: {record.last_accessed_at}")
        print(f"   Updated At: {record.updated_at}")
    
    # 6. 날짜별 학습 기록 (achievement stats에서 사용하는 쿼리)
    print("\n📅 날짜별 학습 기록 (Achievement Stats 기준):")
    from sqlalchemy import desc
    progress_records = db.query(
        func.date(UserProgress.last_accessed_at).label('study_date'),
        func.count(UserProgress.id).label('activities'),
        UserProgress.user_id
    ).filter(
        UserProgress.last_accessed_at.isnot(None)
    ).group_by(
        func.date(UserProgress.last_accessed_at),
        UserProgress.user_id
    ).order_by(
        desc('study_date')
    ).limit(10).all()
    
    if progress_records:
        for record in progress_records:
            print(f"   {record.study_date} - User {record.user_id}: {record.activities}개 활동")
    else:
        print("   ⚠️ last_accessed_at 데이터가 없습니다!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_user_progress())
