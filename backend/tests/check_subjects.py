#!/usr/bin/env python3
"""
과목 및 토픽 데이터 확인
"""
from sqlalchemy import text, create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://lms_user:1234@localhost:15432/lms_mvp_db')

def check_subjects_data():
    """과목 관련 데이터 확인"""
    print("📚 과목 시스템 데이터 확인")
    print("=" * 50)

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # subjects 테이블 확인
        try:
            print("\n📋 subjects 테이블 스키마:")
            schema = conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'subjects'
                ORDER BY ordinal_position
            """))
            for col in schema.fetchall():
                print(f"  - {col[0]}: {col[1]}")

            print("\n📚 subjects 테이블 데이터:")
            result = conn.execute(text('SELECT id, key, title, version FROM subjects LIMIT 10'))
            for row in result.fetchall():
                key = row[1] or "키 없음"
                title = row[2] or "제목 없음"
                version = row[3] or "버전 없음"
                print(f"  - ID: {row[0]}, 키: {key}, 제목: {title}, 버전: {version}")

        except Exception as e:
            print(f"❌ subjects 테이블 조회 실패: {e}")

        # subject_topics 테이블 확인
        try:
            print("\n📋 subject_topics 테이블 스키마:")
            schema = conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'subject_topics'
                ORDER BY ordinal_position
            """))
            for col in schema.fetchall():
                print(f"  - {col[0]}: {col[1]}")

            print("\n📖 subject_topics 테이블 데이터:")
            result = conn.execute(text('SELECT id, subject_key, topic_key, weight FROM subject_topics LIMIT 10'))
            for row in result.fetchall():
                print(f"  - ID: {row[0]}, 과목키: {row[1]}, 토픽키: {row[2]}, 가중치: {row[3]}")

        except Exception as e:
            print(f"❌ subject_topics 테이블 조회 실패: {e}")

        # topics 테이블 확인
        try:
            print("\n📋 topics 테이블 스키마:")
            schema = conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'topics'
                ORDER BY ordinal_position
            """))
            for col in schema.fetchall():
                print(f"  - {col[0]}: {col[1]}")

            print("\n📖 topics 테이블 데이터:")
            result = conn.execute(text('SELECT id, subject, name, description FROM topics LIMIT 10'))
            for row in result.fetchall():
                desc = row[3] or "설명 없음"
                print(f"  - ID: {row[0]}, 과목: {row[1]}, 이름: {row[2]}, 설명: {desc}")

        except Exception as e:
            print(f"❌ topics 테이블 조회 실패: {e}")

if __name__ == "__main__":
    check_subjects_data()
