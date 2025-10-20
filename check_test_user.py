"""
데이터베이스에 있는 실제 사용자 확인
"""
import sys
sys.path.append('backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:15432/lms_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# 모든 사용자 조회
from app.models.orm import User

users = db.query(User).all()

print("=" * 60)
print("데이터베이스에 등록된 사용자 목록")
print("=" * 60)

for user in users:
    print(f"\nID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Username: {user.username}")
    print(f"Created: {user.created_at}")

db.close()

print("\n" + "=" * 60)
print(f"총 {len(users)}명의 사용자")
print("=" * 60)
