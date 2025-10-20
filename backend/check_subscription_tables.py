"""
Subscription and Payment 테이블 확인 스크립트
"""

from app.core.database import SessionLocal
from app.models.orm import Subscription, Payment, User
from sqlalchemy import inspect, text

def check_tables():
    """테이블 존재 여부 확인"""
    db = SessionLocal()
    inspector = inspect(db.bind)
    
    print("=" * 60)
    print("📊 Database Tables Check")
    print("=" * 60)
    
    # 테이블 목록
    tables = inspector.get_table_names()
    
    if "subscriptions" in tables:
        print("✅ subscriptions 테이블 존재")
        
        # 컬럼 확인
        columns = inspector.get_columns("subscriptions")
        print(f"   - Columns: {len(columns)}")
        for col in columns:
            print(f"     • {col['name']}: {col['type']}")
        
        # 인덱스 확인
        indexes = inspector.get_indexes("subscriptions")
        print(f"   - Indexes: {len(indexes)}")
        for idx in indexes:
            print(f"     • {idx['name']}")
    else:
        print("❌ subscriptions 테이블 없음")
    
    print()
    
    if "payments" in tables:
        print("✅ payments 테이블 존재")
        
        # 컬럼 확인
        columns = inspector.get_columns("payments")
        print(f"   - Columns: {len(columns)}")
        for col in columns:
            print(f"     • {col['name']}: {col['type']}")
        
        # 인덱스 확인
        indexes = inspector.get_indexes("payments")
        print(f"   - Indexes: {len(indexes)}")
        for idx in indexes:
            print(f"     • {idx['name']}")
    else:
        print("❌ payments 테이블 없음")
    
    print()
    print("=" * 60)
    print("🔗 Foreign Keys Check")
    print("=" * 60)
    
    # subscriptions FK
    sub_fks = inspector.get_foreign_keys("subscriptions")
    print(f"✅ subscriptions foreign keys: {len(sub_fks)}")
    for fk in sub_fks:
        print(f"   - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
    
    # payments FK
    pay_fks = inspector.get_foreign_keys("payments")
    print(f"✅ payments foreign keys: {len(pay_fks)}")
    for fk in pay_fks:
        print(f"   - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
    
    print()
    print("=" * 60)
    print("📈 Data Count")
    print("=" * 60)
    
    user_count = db.query(User).count()
    sub_count = db.query(Subscription).count()
    pay_count = db.query(Payment).count()
    
    print(f"✅ Users: {user_count}")
    print(f"✅ Subscriptions: {sub_count}")
    print(f"✅ Payments: {pay_count}")
    
    db.close()
    print()
    print("✅ 모든 테이블 확인 완료!")

if __name__ == "__main__":
    check_tables()
