"""
AITeachingSession 데이터 확인 스크립트
"""

import asyncio
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.ai_curriculum import AITeachingSession, AIGeneratedCurriculum
from app.models.orm import User

async def check_ai_teaching_sessions():
    db = next(get_db())
    
    print("=" * 60)
    print("AITeachingSession 테이블 데이터 확인")
    print("=" * 60)
    
    # 1. 전체 세션 수
    total_sessions = db.query(AITeachingSession).count()
    print(f"\n📊 전체 Teaching Session: {total_sessions}개")
    
    # 2. 상태별 세션 수
    statuses = db.query(
        AITeachingSession.session_status,
        func.count(AITeachingSession.id)
    ).group_by(AITeachingSession.session_status).all()
    
    print("\n📈 세션 상태별 분포:")
    for status, count in statuses:
        print(f"   - {status}: {count}개")
    
    # 3. 사용자별 세션 통계
    print("\n👤 사용자별 세션 현황:")
    user_stats = db.query(
        AITeachingSession.user_id,
        User.email,
        func.count(AITeachingSession.id).label('total_sessions'),
        func.avg(AITeachingSession.completion_percentage).label('avg_progress')
    ).join(
        User, AITeachingSession.user_id == User.id
    ).group_by(
        AITeachingSession.user_id, User.email
    ).all()
    
    for stat in user_stats:
        print(f"\n   User ID {stat.user_id} ({stat.email}):")
        print(f"   - 총 세션: {stat.total_sessions}개")
        print(f"   - 평균 진도: {stat.avg_progress:.1f}%")
    
    # 4. 최근 5개 세션 상세
    print("\n📋 최근 Teaching Session 5개:")
    recent_sessions = db.query(AITeachingSession).order_by(
        AITeachingSession.last_activity_at.desc()
    ).limit(5).all()
    
    for session in recent_sessions:
        print(f"\n   세션 ID: {session.id}")
        print(f"   User ID: {session.user_id}")
        print(f"   제목: {session.session_title}")
        print(f"   진도: {session.completion_percentage}%")
        print(f"   현재 단계: {session.current_step}/{session.total_steps}")
        print(f"   상태: {session.session_status}")
        print(f"   시작: {session.started_at}")
        print(f"   마지막 활동: {session.last_activity_at}")
        if session.completed_at:
            print(f"   완료: {session.completed_at}")
    
    # 5. 날짜별 학습 기록 (achievement stats 기준)
    print("\n📅 날짜별 학습 기록 (Achievement Stats 기준):")
    from sqlalchemy import desc
    date_records = db.query(
        func.date(AITeachingSession.last_activity_at).label('study_date'),
        func.count(AITeachingSession.id).label('sessions'),
        AITeachingSession.user_id
    ).filter(
        AITeachingSession.last_activity_at.isnot(None)
    ).group_by(
        func.date(AITeachingSession.last_activity_at),
        AITeachingSession.user_id
    ).order_by(
        desc('study_date')
    ).limit(10).all()
    
    if date_records:
        for record in date_records:
            print(f"   {record.study_date} - User {record.user_id}: {record.sessions}개 세션")
    else:
        print("   ⚠️ 학습 기록이 없습니다!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check_ai_teaching_sessions())
