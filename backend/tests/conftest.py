"""
pytest 설정 및 공통 fixtures
테스트 실행: uv run pytest tests/ -v
"""
import os
import sys
import pytest
from typing import Generator, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 테스트 환경 설정 (다른 import 전에 설정해야 함)
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET"] = "test_secret_key_for_testing"
os.environ["ENVIRONMENT"] = "testing"
os.environ["LLM_ENABLED"] = "false"
os.environ["OPENROUTER_API_KEY"] = "test_dummy_key_for_testing"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.orm import Base, User
from app.core.security import hash_password


# ============================================
# 테스트 DB 설정
# PostgreSQL ARRAY 타입 때문에 SQLite 사용 불가
# 실제 PostgreSQL 또는 기존 DB 사용
# ============================================

# 테스트용 PostgreSQL (Docker 실행 중일 때)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://lms_user:1234@localhost:15432/lms_mvp_db"
)

try:
    engine = create_engine(TEST_DATABASE_URL)
    # 연결 테스트
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DB_AVAILABLE = True
except Exception as e:
    print(f"⚠️ 테스트 DB 연결 실패: {e}")
    DB_AVAILABLE = False
    engine = None
    TestingSessionLocal = None


def override_get_db() -> Generator[Session, None, None]:
    """테스트용 DB 세션"""
    if not DB_AVAILABLE:
        pytest.skip("테스트 DB 연결 불가")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """테스트 DB 세션"""
    if not DB_AVAILABLE:
        pytest.skip("테스트 DB 연결 불가 - Docker PostgreSQL 실행 필요")
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db: Optional[Session] = None) -> Generator[TestClient, None, None]:
    """FastAPI 테스트 클라이언트"""
    if DB_AVAILABLE:
        app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_db() -> Generator[TestClient, None, None]:
    """DB 없이 사용 가능한 테스트 클라이언트 (health check용)"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user(db: Session) -> User:
    """테스트용 일반 사용자 생성"""
    # 기존 유저 확인
    existing = db.query(User).filter(User.email == "test@example.com").first()
    if existing:
        return existing
    
    pwd_hash, pwd_salt = hash_password("testpassword123")
    user = User(
        email="test@example.com",
        password_hash=pwd_hash,
        password_salt=pwd_salt,
        role="student",
        display_name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session) -> User:
    """테스트용 관리자 사용자 생성"""
    existing = db.query(User).filter(User.email == "admin@example.com").first()
    if existing:
        return existing
    
    pwd_hash, pwd_salt = hash_password("adminpassword123")
    user = User(
        email="admin@example.com",
        password_hash=pwd_hash,
        password_salt=pwd_salt,
        role="admin",
        display_name="Admin User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client: TestClient, test_user: User) -> TestClient:
    """로그인된 상태의 테스트 클라이언트"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    return client


@pytest.fixture
def admin_client(client: TestClient, admin_user: User) -> TestClient:
    """관리자로 로그인된 상태의 테스트 클라이언트"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "adminpassword123"}
    )
    assert response.status_code == 200
    return client
