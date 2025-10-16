from datetime import datetime
from typing import List, Dict

from app.core.database import SessionLocal
from app.models.orm import Subject, Topic, SubjectTopic, SubjectSettings


def upsert_subject(db, key: str, title: str, version: str = "v1") -> Subject:
    subj = db.query(Subject).filter(Subject.key == key).first()
    if subj:
        subj.title = title
        subj.version = version
        return subj
    subj = Subject(key=key, title=title, version=version, created_at=datetime.utcnow())
    db.add(subj)
    return subj


def upsert_topic(db, key: str, title: str) -> Topic:
    t = db.query(Topic).filter(Topic.key == key).first()
    if t:
        t.title = title
        return t
    t = Topic(key=key, title=title)
    db.add(t)
    return t


def ensure_subject_topic(
    db,
    subject_key: str,
    topic_key: str,
    *,
    weight: float = 1.0,
    is_core: bool = True,
    display_order: int = 0,
    show_in_coverage: bool = True,
):
    st = (
        db.query(SubjectTopic)
        .filter(SubjectTopic.subject_key == subject_key, SubjectTopic.topic_key == topic_key)
        .first()
    )
    if st:
        st.weight = weight
        st.is_core = is_core
        st.display_order = display_order
        st.show_in_coverage = show_in_coverage
        return st
    st = SubjectTopic(
        subject_key=subject_key,
        topic_key=topic_key,
        weight=weight,
        is_core=is_core,
        display_order=display_order,
        show_in_coverage=show_in_coverage,
    )
    db.add(st)
    return st


def upsert_settings(db, subject_key: str, min_attempts: int = 3, min_accuracy: float = 0.6) -> SubjectSettings:
    s = db.query(SubjectSettings).filter(SubjectSettings.subject_key == subject_key).first()
    if s:
        s.min_attempts = min_attempts
        s.min_accuracy = min_accuracy
        return s
    s = SubjectSettings(subject_key=subject_key, min_attempts=min_attempts, min_accuracy=min_accuracy)
    db.add(s)
    return s


def seed_python_basics(db):
    subject_key = "python_basics"
    upsert_subject(db, subject_key, "Python 기초", version="v1")

    core_topics = [
        ("operators", "연산자"),
        ("variables", "변수·상수"),
        ("data_types", "자료형"),
        ("tuples", "튜플"),
        ("lists", "리스트"),
        ("dicts", "딕셔너리"),
        ("conditionals", "조건문"),
        ("loops", "반복문"),
    ]
    ext_topics = [
        ("functions", "함수"),
        ("classes", "클래스"),
        ("exceptions", "예외"),
        ("modules", "모듈"),
    ]

    # 1) 토픽 업서트 먼저 모두 처리
    for key, title in core_topics + ext_topics:
        upsert_topic(db, key, title)

    # flush로 topics 선반영(FK 순서 보장)
    db.flush()

    # 2) 매핑 삽입(코어 → 확장 순서)
    order = 0
    for key, _ in core_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=True,
            display_order=order,
            show_in_coverage=True,
        )
        order += 1

    for key, _ in ext_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=False,
            display_order=order,
            show_in_coverage=False,
        )
        order += 1

    upsert_settings(db, subject_key, min_attempts=3, min_accuracy=0.6)


def seed_web_frontend(db):
    subject_key = "web_frontend"
    upsert_subject(db, subject_key, "웹 프론트엔드 개발", version="v1")

    core_topics = [
        ("html_basics", "HTML 기초"),
        ("css_basics", "CSS 기초"),
        ("css_layout", "CSS 레이아웃"),
        ("responsive_design", "반응형 디자인"),
        ("javascript_intro", "JavaScript 소개"),
    ]
    ext_topics = [
        ("dom_manipulation", "DOM 조작"),
        ("event_handling", "이벤트 처리"),
        ("forms_validation", "폼과 유효성 검사"),
        ("web_apis", "웹 API"),
    ]

    for key, title in core_topics + ext_topics:
        upsert_topic(db, key, title)

    db.flush()

    order = 0
    for key, _ in core_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=True,
            display_order=order,
            show_in_coverage=True,
        )
        order += 1

    for key, _ in ext_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=False,
            display_order=order,
            show_in_coverage=False,
        )
        order += 1

    upsert_settings(db, subject_key, min_attempts=3, min_accuracy=0.6)


def seed_javascript_basics(db):
    subject_key = "javascript_basics"
    upsert_subject(db, subject_key, "JavaScript 기초", version="v1")

    core_topics = [
        ("js_variables", "변수와 상수"),
        ("js_data_types", "자료형"),
        ("js_operators", "연산자"),
        ("js_functions", "함수"),
        ("js_objects", "객체"),
        ("js_arrays", "배열"),
    ]
    ext_topics = [
        ("js_dom", "DOM"),
        ("js_events", "이벤트"),
        ("js_async", "비동기 프로그래밍"),
        ("js_es6", "ES6+ 기능"),
    ]

    for key, title in core_topics + ext_topics:
        upsert_topic(db, key, title)

    db.flush()

    order = 0
    for key, _ in core_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=True,
            display_order=order,
            show_in_coverage=True,
        )
        order += 1

    for key, _ in ext_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=False,
            display_order=order,
            show_in_coverage=False,
        )
        order += 1

    upsert_settings(db, subject_key, min_attempts=3, min_accuracy=0.6)


def seed_react_basics(db):
    subject_key = "react_basics"
    upsert_subject(db, subject_key, "React 기초", version="v1")

    core_topics = [
        ("react_intro", "React 소개"),
        ("jsx", "JSX"),
        ("components", "컴포넌트"),
        ("props", "Props"),
        ("state", "State"),
        ("lifecycle", "라이프사이클"),
    ]
    ext_topics = [
        ("hooks", "Hooks"),
        ("context", "Context API"),
        ("routing", "라우팅"),
        ("forms", "폼 처리"),
    ]

    for key, title in core_topics + ext_topics:
        upsert_topic(db, key, title)

    db.flush()

    order = 0
    for key, _ in core_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=True,
            display_order=order,
            show_in_coverage=True,
        )
        order += 1

    for key, _ in ext_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=False,
            display_order=order,
            show_in_coverage=False,
        )
        order += 1

    upsert_settings(db, subject_key, min_attempts=3, min_accuracy=0.6)


def seed_data_science_basics(db):
    subject_key = "data_science_basics"
    upsert_subject(db, subject_key, "데이터 과학 기초", version="v1")

    core_topics = [
        ("numpy_intro", "NumPy 소개"),
        ("numpy_arrays", "NumPy 배열"),
        ("pandas_intro", "Pandas 소개"),
        ("pandas_dataframe", "DataFrame"),
        ("data_cleaning", "데이터 정제"),
        ("data_visualization", "데이터 시각화"),
    ]
    ext_topics = [
        ("statistics", "통계 기초"),
        ("machine_learning_intro", "머신러닝 소개"),
        ("scikit_learn", "Scikit-learn"),
        ("data_analysis", "데이터 분석"),
    ]

    for key, title in core_topics + ext_topics:
        upsert_topic(db, key, title)

    db.flush()

    order = 0
    for key, _ in core_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=True,
            display_order=order,
            show_in_coverage=True,
        )
        order += 1

    for key, _ in ext_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=False,
            display_order=order,
            show_in_coverage=False,
        )
        order += 1

    upsert_settings(db, subject_key, min_attempts=3, min_accuracy=0.6)


def seed_sql_database(db):
    subject_key = "sql_database"
    upsert_subject(db, subject_key, "SQL 데이터베이스", version="v1")

    core_topics = [
        ("sql_intro", "SQL 소개"),
        ("select_queries", "SELECT 쿼리"),
        ("where_clauses", "WHERE 절"),
        ("joins", "JOIN"),
        ("group_by", "GROUP BY"),
        ("insert_update_delete", "INSERT/UPDATE/DELETE"),
    ]
    ext_topics = [
        ("indexes", "인덱스"),
        ("transactions", "트랜잭션"),
        ("stored_procedures", "저장 프로시저"),
        ("database_design", "데이터베이스 설계"),
    ]

    for key, title in core_topics + ext_topics:
        upsert_topic(db, key, title)

    db.flush()

    order = 0
    for key, _ in core_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=True,
            display_order=order,
            show_in_coverage=True,
        )
        order += 1

    for key, _ in ext_topics:
        ensure_subject_topic(
            db,
            subject_key,
            key,
            weight=1.0,
            is_core=False,
            display_order=order,
            show_in_coverage=False,
        )
        order += 1

    upsert_settings(db, subject_key, min_attempts=3, min_accuracy=0.6)


def main():
    db = SessionLocal()
    try:
        seed_python_basics(db)
        seed_web_frontend(db)
        seed_javascript_basics(db)
        seed_react_basics(db)
        seed_data_science_basics(db)
        seed_sql_database(db)
        db.flush()
        db.commit()
        print("Seeded taxonomy/settings for all subjects")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


