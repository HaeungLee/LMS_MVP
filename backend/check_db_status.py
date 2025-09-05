"""
DB 연결 및 테이블 확인
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def check_database():
    """데이터베이스 상태 확인"""
    
    print("🔍 데이터베이스 연결 및 테이블 확인")
    print("=" * 50)
    
    # 다양한 연결 설정 시도
    connection_configs = [
        {
            'name': 'Docker Compose 설정',
            'config': {
                'host': 'localhost',
                'port': '15433',
                'database': 'lms_mvp_test_db',
                'user': 'lms_user',
                'password': '1234'
            }
        },
        {
            'name': '기본 설정 1',
            'config': {
                'host': 'localhost',
                'port': '5432',
                'database': 'lms',
                'user': 'lms_user',
                'password': 'lms_password'
            }
        },
        {
            'name': '기본 설정 2',
            'config': {
                'host': 'localhost',
                'port': '5432',
                'database': 'lms_db',
                'user': 'postgres',
                'password': 'password'
            }
        }
    ]
    
    for conn_info in connection_configs:
        print(f"\n📡 시도: {conn_info['name']}")
        try:
            conn = psycopg2.connect(**conn_info['config'])
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            print(f"✅ 연결 성공!")
            
            # 데이터베이스 정보 확인
            cursor.execute("SELECT current_database(), current_user")
            db_info = cursor.fetchone()
            print(f"   데이터베이스: {db_info['current_database']}")
            print(f"   사용자: {db_info['current_user']}")
            
            # 테이블 목록 확인
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
            """)
            
            tables = cursor.fetchall()
            print(f"   테이블 수: {len(tables)}개")
            
            # 주요 테이블들 확인
            table_names = [table['tablename'] for table in tables]
            subject_hierarchy_exists = 'subject_hierarchy' in table_names
            questions_exists = 'questions' in table_names
            
            print(f"   subject_hierarchy 테이블 존재: {subject_hierarchy_exists}")
            print(f"   questions 테이블 존재: {questions_exists}")
            
            if subject_hierarchy_exists:
                cursor.execute("SELECT COUNT(*) FROM subject_hierarchy")
                count = cursor.fetchone()['count']
                print(f"   subject_hierarchy 레코드 수: {count}개")
            
            if questions_exists:
                # questions 테이블의 subject_path 컬럼 확인
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'questions' AND column_name = 'subject_path'
                """)
                
                subject_path_column = cursor.fetchone()
                if subject_path_column:
                    print(f"   questions.subject_path 컬럼: 존재 ({subject_path_column['data_type']})")
                else:
                    print(f"   questions.subject_path 컬럼: 없음")
            
            # Alembic 버전 확인
            try:
                cursor.execute("""
                    SELECT version_num 
                    FROM alembic_version 
                    ORDER BY version_num DESC 
                    LIMIT 1
                """)
                
                alembic_version = cursor.fetchone()
                if alembic_version:
                    print(f"   Alembic 버전: {alembic_version['version_num']}")
                else:
                    print(f"   Alembic 버전: 없음")
            except:
                print(f"   Alembic 테이블: 없음")
            
            cursor.close()
            conn.close()
            
            return conn_info  # 성공한 연결 정보 반환
            
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            continue
    
    print("\n💥 모든 연결 시도 실패")
    return None

if __name__ == "__main__":
    check_database()
