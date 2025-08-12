#!/usr/bin/env python3
"""
PostgreSQL 연결 테스트 스크립트
Docker 컨테이너가 정상적으로 시작된 후 데이터베이스 연결을 확인합니다.
"""

import os
import sys
import time
import psycopg2
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_connection():
    """PostgreSQL 연결 테스트"""
    max_retries = 10
    retry_delay = 3
    
    connection_params = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '15432'),
        'database': os.getenv('POSTGRES_DB', 'lms_mvp_db'),
        'user': os.getenv('POSTGRES_USER', 'lms_user'),
        'password': os.getenv('POSTGRES_PASSWORD', '1234')
    }
    
    print("🔄 PostgreSQL 연결 테스트 시작...")
    print(f"   ├─ 호스트: {connection_params['host']}")
    print(f"   ├─ 포트: {connection_params['port']}")
    print(f"   ├─ 데이터베이스: {connection_params['database']}")
    print(f"   └─ 사용자: {connection_params['user']}")
    print()
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"📡 연결 시도 {attempt}/{max_retries}...")
            
            # 데이터베이스 연결
            conn = psycopg2.connect(**connection_params)
            cursor = conn.cursor()
            
            # 기본 쿼리 실행
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT current_database(), current_user, now();")
            db_info = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            print("✅ PostgreSQL 연결 성공!")
            print(f"   ├─ 버전: {version.split(',')[0]}")
            print(f"   ├─ 데이터베이스: {db_info[0]}")
            print(f"   ├─ 사용자: {db_info[1]}")
            print(f"   └─ 시간: {db_info[2]}")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ 연결 실패 (시도 {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                print(f"⏱️  {retry_delay}초 후 재시도...")
                time.sleep(retry_delay)
            else:
                print("💥 모든 연결 시도 실패!")
                return False
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return False
    
    return False

if __name__ == "__main__":
    if test_connection():
        print("\n🎉 데이터베이스 연결 테스트 성공!")
        sys.exit(0)
    else:
        print("\n💀 데이터베이스 연결 테스트 실패!")
        sys.exit(1)
