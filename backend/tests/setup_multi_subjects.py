#!/usr/bin/env python3
"""
다중 과목 지원 인프라 구축
"""
from sqlalchemy import text, create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://lms_user:1234@localhost:15432/lms_mvp_db')

def setup_multi_subjects():
    """다중 과목 데이터베이스 구축"""
    print("🏗️ 다중 과목 지원 인프라 구축 시작")
    print("=" * 60)

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # 1. 새로운 과목들 추가
        print("📚 새로운 과목들 추가 중...")

        new_subjects = [
            {'key': 'web_frontend', 'title': '웹 프론트엔드 개발', 'version': 'v1.0'},
            {'key': 'javascript_basics', 'title': 'JavaScript 기초', 'version': 'v1.0'},
            {'key': 'react_fundamentals', 'title': 'React 기초', 'version': 'v1.0'},
            {'key': 'data_science', 'title': '데이터 과학 기초', 'version': 'v1.0'},
            {'key': 'sql_database', 'title': 'SQL 데이터베이스', 'version': 'v1.0'},
        ]

        for subject in new_subjects:
            try:
                # 중복 체크
                check = conn.execute(text('SELECT id FROM subjects WHERE key = :key'), {'key': subject['key']})
                if check.fetchone():
                    print(f"  ⚠️ {subject['key']} 과목이 이미 존재합니다")
                    continue

                # 새 과목 추가
                conn.execute(text("""
                    INSERT INTO subjects (key, title, version, created_at)
                    VALUES (:key, :title, :version, NOW())
                """), subject)
                print(f"  ✅ {subject['title']} 과목 추가됨")

            except Exception as e:
                print(f"  ❌ {subject['key']} 과목 추가 실패: {e}")

        conn.commit()

        # 2. 과목별 토픽들 추가
        print("\n📖 과목별 토픽들 추가 중...")

        subject_topics_data = {
            'web_frontend': [
                {'topic_key': 'html_basics', 'weight': 1.0, 'is_core': True, 'display_order': 1},
                {'topic_key': 'css_fundamentals', 'weight': 1.0, 'is_core': True, 'display_order': 2},
                {'topic_key': 'responsive_design', 'weight': 0.8, 'is_core': False, 'display_order': 3},
                {'topic_key': 'web_accessibility', 'weight': 0.6, 'is_core': False, 'display_order': 4},
            ],
            'javascript_basics': [
                {'topic_key': 'js_variables', 'weight': 1.0, 'is_core': True, 'display_order': 1},
                {'topic_key': 'js_functions', 'weight': 1.0, 'is_core': True, 'display_order': 2},
                {'topic_key': 'js_objects', 'weight': 1.0, 'is_core': True, 'display_order': 3},
                {'topic_key': 'dom_manipulation', 'weight': 0.9, 'is_core': True, 'display_order': 4},
                {'topic_key': 'event_handling', 'weight': 0.8, 'is_core': False, 'display_order': 5},
            ],
            'react_fundamentals': [
                {'topic_key': 'jsx_syntax', 'weight': 1.0, 'is_core': True, 'display_order': 1},
                {'topic_key': 'components', 'weight': 1.0, 'is_core': True, 'display_order': 2},
                {'topic_key': 'props_state', 'weight': 1.0, 'is_core': True, 'display_order': 3},
                {'topic_key': 'hooks_basics', 'weight': 0.9, 'is_core': True, 'display_order': 4},
                {'topic_key': 'lifecycle', 'weight': 0.7, 'is_core': False, 'display_order': 5},
            ],
            'data_science': [
                {'topic_key': 'numpy_arrays', 'weight': 1.0, 'is_core': True, 'display_order': 1},
                {'topic_key': 'pandas_dataframes', 'weight': 1.0, 'is_core': True, 'display_order': 2},
                {'topic_key': 'data_visualization', 'weight': 0.9, 'is_core': True, 'display_order': 3},
                {'topic_key': 'statistical_analysis', 'weight': 0.8, 'is_core': False, 'display_order': 4},
            ],
            'sql_database': [
                {'topic_key': 'sql_queries', 'weight': 1.0, 'is_core': True, 'display_order': 1},
                {'topic_key': 'table_operations', 'weight': 1.0, 'is_core': True, 'display_order': 2},
                {'topic_key': 'joins_relationships', 'weight': 0.9, 'is_core': True, 'display_order': 3},
                {'topic_key': 'database_design', 'weight': 0.8, 'is_core': False, 'display_order': 4},
            ]
        }

        for subject_key, topics in subject_topics_data.items():
            for topic in topics:
                try:
                    # 중복 체크
                    check = conn.execute(text("""
                        SELECT id FROM subject_topics
                        WHERE subject_key = :subject_key AND topic_key = :topic_key
                    """), {'subject_key': subject_key, 'topic_key': topic['topic_key']})

                    if check.fetchone():
                        print(f"  ⚠️ {subject_key}:{topic['topic_key']} 토픽이 이미 존재합니다")
                        continue

                    # 새 토픽 추가
                    conn.execute(text("""
                        INSERT INTO subject_topics
                        (subject_key, topic_key, weight, is_core, display_order, show_in_coverage)
                        VALUES (:subject_key, :topic_key, :weight, :is_core, :display_order, true)
                    """), {
                        'subject_key': subject_key,
                        'topic_key': topic['topic_key'],
                        'weight': topic['weight'],
                        'is_core': topic['is_core'],
                        'display_order': topic['display_order']
                    })
                    print(f"  ✅ {subject_key}:{topic['topic_key']} 토픽 추가됨")

                except Exception as e:
                    print(f"  ❌ {subject_key}:{topic['topic_key']} 토픽 추가 실패: {e}")

        conn.commit()

        # 3. 토픽 기본 정보 추가
        print("\n🏷️ 토픽 기본 정보 추가 중...")

        topic_info_data = {
            # Web Frontend
            'html_basics': {'title': 'HTML 기초', 'parent_topic_id': None},
            'css_fundamentals': {'title': 'CSS 기초', 'parent_topic_id': None},
            'responsive_design': {'title': '반응형 디자인', 'parent_topic_id': None},
            'web_accessibility': {'title': '웹 접근성', 'parent_topic_id': None},

            # JavaScript
            'js_variables': {'title': 'JavaScript 변수', 'parent_topic_id': None},
            'js_functions': {'title': 'JavaScript 함수', 'parent_topic_id': None},
            'js_objects': {'title': 'JavaScript 객체', 'parent_topic_id': None},
            'dom_manipulation': {'title': 'DOM 조작', 'parent_topic_id': None},
            'event_handling': {'title': '이벤트 처리', 'parent_topic_id': None},

            # React
            'jsx_syntax': {'title': 'JSX 문법', 'parent_topic_id': None},
            'components': {'title': '컴포넌트', 'parent_topic_id': None},
            'props_state': {'title': 'Props와 State', 'parent_topic_id': None},
            'hooks_basics': {'title': 'Hooks 기초', 'parent_topic_id': None},
            'lifecycle': {'title': '라이프사이클', 'parent_topic_id': None},

            # Data Science
            'numpy_arrays': {'title': 'NumPy 배열', 'parent_topic_id': None},
            'pandas_dataframes': {'title': 'Pandas DataFrame', 'parent_topic_id': None},
            'data_visualization': {'title': '데이터 시각화', 'parent_topic_id': None},
            'statistical_analysis': {'title': '통계 분석', 'parent_topic_id': None},

            # SQL Database
            'sql_queries': {'title': 'SQL 쿼리', 'parent_topic_id': None},
            'table_operations': {'title': '테이블 조작', 'parent_topic_id': None},
            'joins_relationships': {'title': '조인과 관계', 'parent_topic_id': None},
            'database_design': {'title': '데이터베이스 설계', 'parent_topic_id': None},
        }

        for topic_key, info in topic_info_data.items():
            try:
                # 중복 체크
                check = conn.execute(text('SELECT id FROM topics WHERE key = :key'), {'key': topic_key})
                if check.fetchone():
                    print(f"  ⚠️ {topic_key} 토픽 정보가 이미 존재합니다")
                    continue

                # 새 토픽 정보 추가
                conn.execute(text("""
                    INSERT INTO topics (key, title, parent_topic_id)
                    VALUES (:key, :title, :parent_topic_id)
                """), {
                    'key': topic_key,
                    'title': info['title'],
                    'parent_topic_id': info['parent_topic_id']
                })
                print(f"  ✅ {topic_key} 토픽 정보 추가됨")

            except Exception as e:
                print(f"  ❌ {topic_key} 토픽 정보 추가 실패: {e}")

        conn.commit()

        # 4. 구축 결과 확인
        print("\n📊 구축 결과 확인:")

        # 전체 과목 수 확인
        subjects_count = conn.execute(text('SELECT COUNT(*) FROM subjects')).fetchone()[0]
        print(f"  📚 전체 과목 수: {subjects_count}")

        # 전체 토픽 수 확인
        topics_count = conn.execute(text('SELECT COUNT(*) FROM topics')).fetchone()[0]
        print(f"  📖 전체 토픽 수: {topics_count}")

        # 과목별 토픽 수 확인
        subject_topics_count = conn.execute(text('SELECT COUNT(*) FROM subject_topics')).fetchone()[0]
        print(f"  🔗 과목-토픽 연결 수: {subject_topics_count}")

        # 각 과목별 토픽 수
        result = conn.execute(text("""
            SELECT s.key, s.title, COUNT(st.id) as topic_count
            FROM subjects s
            LEFT JOIN subject_topics st ON s.key = st.subject_key
            GROUP BY s.id, s.key, s.title
            ORDER BY s.key
        """))

        print("\n📋 과목별 토픽 현황:")
        for row in result.fetchall():
            print(f"  - {row[0]} ({row[1]}): {row[2]}개 토픽")

    print("\n" + "=" * 60)
    print("🎉 다중 과목 지원 인프라 구축 완료!")
    print("   이제 LMS에서 다양한 과목을 지원합니다.")
    print("=" * 60)

if __name__ == "__main__":
    setup_multi_subjects()
