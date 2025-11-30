"""
pytest 설정 및 공통 fixtures
테스트 실행: pytest tests/ -v
"""
import os
import sys
import pytest
from typing import Generator
from unittest.mock import MagicMock, patch

# 테스트 환경 설정 (다른 import 전에 설정해야 함)
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test_secret_key_for_testing"
os.environ["ENVIRONMENT"] = "testing"
os.environ["LLM_ENABLED"] = "false"

# 선택적 의존성 모킹 (openai, anthropic 등)
sys.modules['openai'] = MagicMock()
sys.modules['anthropic'] = MagicMock()
sys.modules['langchain'] = MagicMock()
sys.modules['langchain_openai'] = MagicMock()
sys.modules['langchain_community'] = MagicMock()
sys.modules['langchain_core'] = MagicMock()

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.orm import Base, User
from app.core.security import hash_password


# 테스트용 SQLite 인메모리 DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """테스트용 DB 세션"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """각 테스트마다 새로운 DB 생성/삭제"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI 테스트 클라이언트"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """테스트용 일반 사용자 생성"""
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
