import json
import os
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.orm import Base, Question


def load_questions_from_json(json_path: Path) -> List[Dict[str, Any]]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])


def seed(db_url: str, json_path: Path) -> None:
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # 이미 데이터가 있으면 스킵
        existing = session.query(Question).count()
        if existing > 0:
            print(f"Questions already present: {existing}. Skipping seed.")
            return

        items = load_questions_from_json(json_path)
        for q in items:
            session.add(
                Question(
                    id=q["id"],
                    subject=q.get("subject", "python_basics"),
                    topic=q.get("topic", "기타"),
                    question_type=q.get("question_type", "fill_in_the_blank"),
                    code_snippet=q.get("code_snippet", ""),
                    correct_answer=q.get("answer", ""),
                    difficulty=q.get("difficulty", "easy"),
                    rubric=q.get("rubric", ""),
                    created_by="seed",
                    is_active=True,
                )
            )
        session.commit()
        print(f"Seeded {len(items)} questions.")
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    DEFAULT_DB_URL = os.getenv(
        "DATABASE_URL", "postgresql://lms_user:1234@localhost:15432/lms_mvp_db"
    )
    ROOT = Path(__file__).resolve().parents[1]
    JSON_PATH = ROOT / "data" / "db.json"
    seed(DEFAULT_DB_URL, JSON_PATH)



