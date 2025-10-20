"""
테스트 사용자를 데이터베이스에 직접 생성
"""
import sys
import os

# backend 경로 추가
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.models.orm import User
from app.core.security import hash_password

# 환경변수에서 DB 정보 가져오기
DATABASE_URL = "postgresql://lms_user:1234@localhost:15432/lms_mvp_db"

print("=" * 60)
print("테스트 사용자 생성")
print("=" * 60)

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # 기존 사용자 확인
    existing_user = db.query(User).filter(User.email == "test@test.com").first()
    
    if existing_user:
        print("\n⚠️ test@test.com 계정이 이미 존재합니다.")
        print(f"ID: {existing_user.id}")
        print(f"Email: {existing_user.email}")
        print(f"Display Name: {existing_user.display_name}")
        print(f"Role: {existing_user.role}")
        print("\n비밀번호: test1234")
    else:
        # 새 사용자 생성
        pwd_hash, pwd_salt = hash_password("test1234")
        
        new_user = User(
            email="test@test.com",
            password_hash=pwd_hash,
            password_salt=pwd_salt,
            role="student",
            display_name="테스트유저",
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("\n✅ 새 사용자 생성 완료!")
        print(f"ID: {new_user.id}")
        print(f"Email: {new_user.email}")
        print(f"Display Name: {new_user.display_name}")
        print(f"비밀번호: test1234")
    
    print("\n" + "=" * 60)
    print("현재 등록된 모든 사용자 목록")
    print("=" * 60)
    
    all_users = db.query(User).all()
    for user in all_users:
        print(f"\nID: {user.id} | Email: {user.email} | Name: {user.display_name}")
    
    print(f"\n총 {len(all_users)}명의 사용자")
    
    db.close()
    
    print("\n💡 다음 정보로 로그인 가능합니다:")
    print("   Email: test@test.com")
    print("   Password: test1234")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
