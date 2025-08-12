import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 키
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # 서버 설정
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True
    
    # CORS 설정
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # 데이터베이스 경로 (기존 JSON 파일)
    database_path: str = "data/db.json"
    
    # PostgreSQL 설정 (새로 추가)
    database_url: str = os.getenv("DATABASE_URL", "")
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_host: str = os.getenv("API_HOST", "localhost")
    api_port: str = os.getenv("API_PORT", "8000")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "15432")
    postgres_user: str = os.getenv("POSTGRES_USER", "lms_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "1234")
    postgres_db: str = os.getenv("POSTGRES_DB", "lms_mvp_db")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 추가 필드 허용

settings = Settings()
