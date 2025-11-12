# -*- coding: utf-8 -*-
import psycopg2
import sys

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect('postgresql://lms_user:1234@localhost:15432/lms_mvp_db')
cur = conn.cursor()

# 모든 테이블 조회
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    ORDER BY table_name
""")

tables = cur.fetchall()
print(f'\n[OK] Total {len(tables)} tables created:\n')
for table in tables:
    print(f'  - {table[0]}')

# 주요 테이블 행 수 확인
important_tables = ['users', 'subjects', 'subject_topics', 'questions', 'subscriptions', 'payments']
print(f'\n[DATA] Record counts:')
for table_name in important_tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cur.fetchone()[0]
        print(f'  - {table_name}: {count} records')
    except Exception as e:
        print(f'  - {table_name}: NOT FOUND or ERROR')

conn.close()

