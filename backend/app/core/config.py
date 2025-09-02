import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
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
        "http://localhost:5174",  # 새로운 포트 추가
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",   # 새로운 포트 추가
        "http://192.168.0.104:5174",
        "http://172.25.64.1:5174",
        "http://172.31.80.1:5174",
        "https://localhost:5174",
        "https://127.0.0.1:5174"
    ]
    
    # 개발 환경에서는 더 관대한 CORS 설정
    development_mode: bool = True
    
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
    
    # LLM/Feedback settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "openrouter")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b")
    llm_timeout_ms: int = int(os.getenv("LLM_TIMEOUT_MS", "10000"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    llm_enabled: bool = os.getenv("LLM_ENABLED", "true").lower() in ("1", "true", "yes")
    llm_cache_ttl_seconds: int = int(os.getenv("LLM_CACHE_TTL_SECONDS", "600"))
    llm_max_rpm: int = int(os.getenv("LLM_MAX_RPM", "20"))  # 무료 계정용 보수적 설정

settings = Settings()
