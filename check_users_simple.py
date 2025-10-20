"""
데이터베이스 사용자 확인 (psycopg2 사용)
"""
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=15432,
        database="lms_db",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    # 사용자 조회
    cur.execute("SELECT id, email, username, created_at FROM users ORDER BY id")
    users = cur.fetchall()
    
    print("=" * 70)
    print("데이터베이스에 등록된 사용자 목록")
    print("=" * 70)
    
    for user in users:
        print(f"\nID: {user[0]}")
        print(f"Email: {user[1]}")
        print(f"Username: {user[2]}")
        print(f"Created: {user[3]}")
    
    print("\n" + "=" * 70)
    print(f"총 {len(users)}명의 사용자")
    print("=" * 70)
    
    print("\n💡 테스트용으로 사용할 수 있는 이메일 주소를 확인하세요.")
    print("💡 비밀번호는 회원가입 시 설정한 것을 사용해야 합니다.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
