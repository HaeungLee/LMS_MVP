#!/usr/bin/env python3
"""
subject_topics 테이블 연결 문제 해결
"""
from sqlalchemy import text, create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://lms_user:1234@localhost:15432/lms_mvp_db')

def fix_subject_topics():
    """subject_topics 테이블 연결 복구"""
    print("🔧 subject_topics 테이블 연결 문제 해결")
    print("=" * 60)

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # 1. 현재 상태 확인
        print("📊 현재 상태 확인:")

        subjects_count = conn.execute(text('SELECT COUNT(*) FROM subjects')).fetchone()[0]
        topics_count = conn.execute(text('SELECT COUNT(*) FROM topics')).fetchone()[0]
        subject_topics_count = conn.execute(text('SELECT COUNT(*) FROM subject_topics')).fetchone()[0]

        print(f"  📚 subjects: {subjects_count}개")
        print(f"  📖 topics: {topics_count}개")
        print(f"  🔗 subject_topics: {subject_topics_count}개")

        # 2. 누락된 subject_topics 연결 추가
        print("\n🔗 누락된 subject_topics 연결 추가 중...")

        # 각 과목별로 토픽 연결 생성
        subject_topic_mappings = {
            'web_frontend': ['html_basics', 'css_fundamentals', 'responsive_design', 'web_accessibility'],
            'javascript_basics': ['js_variables', 'js_functions', 'js_objects', 'dom_manipulation', 'event_handling'],
            'react_fundamentals': ['jsx_syntax', 'components', 'props_state', 'hooks_basics', 'lifecycle'],
            'data_science': ['numpy_arrays', 'pandas_dataframes', 'data_visualization', 'statistical_analysis'],
            'sql_database': ['sql_queries', 'table_operations', 'joins_relationships', 'database_design']
        }

        total_added = 0

        for subject_key, topic_keys in subject_topic_mappings.items():
            for i, topic_key in enumerate(topic_keys, 1):
                try:
                    # 이미 존재하는지 확인
                    check = conn.execute(text("""
                        SELECT id FROM subject_topics
                        WHERE subject_key = :subject_key AND topic_key = :topic_key
                    """), {'subject_key': subject_key, 'topic_key': topic_key})

                    if check.fetchone():
                        print(f"  ⚠️ {subject_key}:{topic_key} 이미 존재")
                        continue

                    # 토픽이 topics 테이블에 존재하는지 확인
                    topic_check = conn.execute(text("""
                        SELECT id FROM topics WHERE key = :topic_key
                    """), {'topic_key': topic_key})

                    if not topic_check.fetchone():
                        print(f"  ❌ {topic_key} 토픽이 topics 테이블에 없음")
                        continue

                    # subject_topics에 추가
                    is_core = i <= 3  # 처음 3개는 핵심 토픽
                    weight = 1.0 if is_core else 0.8

                    conn.execute(text("""
                        INSERT INTO subject_topics
                        (subject_key, topic_key, weight, is_core, display_order, show_in_coverage)
                        VALUES (:subject_key, :topic_key, :weight, :is_core, :display_order, true)
                    """), {
                        'subject_key': subject_key,
                        'topic_key': topic_key,
                        'weight': weight,
                        'is_core': is_core,
                        'display_order': i
                    })

                    total_added += 1
                    print(f"  ✅ {subject_key}:{topic_key} 연결 추가됨")

                except Exception as e:
                    print(f"  ❌ {subject_key}:{topic_key} 연결 실패: {e}")

        conn.commit()

        # 3. 결과 확인
        print("\n📊 연결 결과 확인:")
        subject_topics_final = conn.execute(text('SELECT COUNT(*) FROM subject_topics')).fetchone()[0]
        print(f"  🔗 subject_topics 최종: {subject_topics_final}개 (+{total_added}개 추가됨)")

        # 과목별 토픽 수 확인
        result = conn.execute(text("""
            SELECT s.key, s.title, COUNT(st.id) as topic_count
            FROM subjects s
            LEFT JOIN subject_topics st ON s.key = st.subject_key
            GROUP BY s.id, s.key, s.title
            ORDER BY s.key
        """))

        print("\n📋 최종 과목별 토픽 현황:")
        for row in result.fetchall():
            print(f"  - {row[0]} ({row[1]}): {row[2]}개 토픽")

        # 각 과목의 토픽 목록 확인
        print("\n📖 각 과목의 토픽 목록:")
        for subject_key in subject_topic_mappings.keys():
            topics_result = conn.execute(text("""
                SELECT t.title, st.weight, st.is_core
                FROM subject_topics st
                JOIN topics t ON st.topic_key = t.key
                WHERE st.subject_key = :subject_key
                ORDER BY st.display_order
            """), {'subject_key': subject_key})

            topics = topics_result.fetchall()
            if topics:
                print(f"  🎯 {subject_key}:")
                for topic in topics:
                    core_mark = "⭐" if topic[2] else "📖"
                    print(f"    {core_mark} {topic[0]} (가중치: {topic[1]})")

    print("\n" + "=" * 60)
    print("🎉 subject_topics 연결 문제 해결 완료!")
    print(f"   총 {total_added}개의 새로운 연결이 추가되었습니다.")
    print("=" * 60)

if __name__ == "__main__":
    fix_subject_topics()
