"""
커리큘럼 데이터 확인
"""

from app.core.database import get_db
from app.models.orm import User
from app.models.ai_curriculum import AIGeneratedCurriculum

def check_data():
    db = next(get_db())
    
    print("=" * 60)
    print("데이터베이스 확인")
    print("=" * 60)
    
    # 1. 모든 사용자 조회
    users = db.query(User).all()
    print(f"\n👤 총 사용자: {len(users)}명")
    for user in users:
        print(f"   - ID {user.id}: {user.email}")
    
    # 2. 모든 커리큘럼 조회
    curricula = db.query(AIGeneratedCurriculum).all()
    print(f"\n📚 총 커리큘럼: {len(curricula)}개")
    for curriculum in curricula:
        print(f"\n   커리큘럼 ID: {curriculum.id}")
        print(f"   User ID: {curriculum.user_id}")
        print(f"   Goal: {curriculum.subject_key}")
        print(f"   Status: {curriculum.status}")
        print(f"   생성일: {curriculum.created_at}")
        if curriculum.generated_syllabus:
            syllabus = curriculum.generated_syllabus
            print(f"   제목: {syllabus.get('title', 'N/A')}")
            print(f"   주차: {syllabus.get('duration_weeks', 'N/A')}주")
    
    # 3. User ID 1의 커리큘럼
    print("\n" + "=" * 60)
    print("User ID 1의 커리큘럼:")
    user1_curricula = db.query(AIGeneratedCurriculum).filter(
        AIGeneratedCurriculum.user_id == 1
    ).all()
    print(f"   총 {len(user1_curricula)}개")
    for c in user1_curricula:
        print(f"   - ID {c.id}: {c.subject_key} ({c.status})")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_data()
