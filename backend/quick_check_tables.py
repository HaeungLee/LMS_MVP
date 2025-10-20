"""빠른 테이블 확인"""
from app.core.database import SessionLocal
from sqlalchemy import inspect, text

db = SessionLocal()
inspector = inspect(db.bind)

print("=" * 60)
print("📊 현재 데이터베이스 테이블 목록")
print("=" * 60)

tables = sorted(inspector.get_table_names())
for table in tables:
    print(f"✅ {table}")

print(f"\n총 {len(tables)}개 테이블")

# 중요 테이블 데이터 확인
print("\n" + "=" * 60)
print("📈 중요 테이블 레코드 수")
print("=" * 60)

important_tables = ['users', 'subscriptions', 'payments', 'subjects', 'questions']
for table in important_tables:
    if table in tables:
        try:
            count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"✅ {table}: {count} rows")
        except Exception as e:
            print(f"❌ {table}: 오류 - {e}")
    else:
        print(f"⚠️  {table}: 테이블 없음")

db.close()
print("\n✅ 확인 완료!")
