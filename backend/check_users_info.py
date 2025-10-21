"""
사용자 정보 확인 스크립트
"""

from app.core.database import get_db
from app.models.orm import User

def check_users():
    db = next(get_db())
    
    print("=" * 60)
    print("등록된 사용자 목록")
    print("=" * 60)
    
    users = db.query(User).all()
    
    if not users:
        print("\n⚠️ 등록된 사용자가 없습니다!")
    else:
        for user in users:
            print(f"\nUser ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Username: {user.username}")
            print(f"Role: {user.role}")
            print(f"Created: {user.created_at}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_users()
