from app.core.database import engine
from sqlalchemy import text

print("🔍 데이터베이스 사용자 확인 중...")

try:
    with engine.connect() as conn:
        # test@test.com 사용자 확인
        result = conn.execute(text("SELECT id, email, role, display_name, created_at FROM users WHERE email = 'test@test.com'"))
        user = result.fetchone()
        
        if user:
            print(f"✅ test@test.com 사용자 발견:")
            print(f"   - ID: {user[0]}")
            print(f"   - 이메일: {user[1]}")
            print(f"   - 역할: {user[2]}")
            print(f"   - 이름: {user[3]}")
            print(f"   - 생성일: {user[4]}")
        else:
            print("❌ test@test.com 사용자가 없습니다")
            
        # 전체 사용자 목록
        result = conn.execute(text("SELECT id, email, role FROM users ORDER BY id LIMIT 10"))
        users = result.fetchall()
        print(f"\n📋 전체 사용자 목록 ({len(users)}명):")
        for u in users:
            print(f"   - ID={u[0]}, 이메일={u[1]}, 역할={u[2]}")
            
except Exception as e:
    print(f"❌ 데이터베이스 오류: {e}")