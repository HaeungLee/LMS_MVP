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


def main():
    db = SessionLocal()
    try:
        seed_python_basics(db)
        db.flush()
        db.commit()
        print("Seeded taxonomy/settings for python_basics")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


