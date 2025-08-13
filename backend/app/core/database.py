from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()

# PostgreSQL 데이터베이스 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://lms_user:1234@localhost:15432/lms_mvp_db",
)

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# Slow query warning (basic): logs queries exceeding threshold
SLOW_QUERY_MS = int(os.getenv("SLOW_QUERY_MS", "300"))  # default 300ms

_query_timer = {}

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    key = id(cursor)
    _query_timer[key] = time.time()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    key = id(cursor)
    start = _query_timer.pop(key, None)
    if start is None:
        return
    dur_ms = int((time.time() - start) * 1000)
    if dur_ms >= SLOW_QUERY_MS:
        log = {
            "level": "warn",
            "message": "slow_query",
            "duration_ms": dur_ms,
            "statement": statement[:500],  # truncate
        }
        try:
            print(json.dumps(log, ensure_ascii=False))
        except Exception:
            pass

# 세션 로컬 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
