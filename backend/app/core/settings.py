"""
환경별 설정 관리

환경 변수 우선순위:
1. 실제 환경 변수
2. .env 파일
3. 기본값

사용법:
    from app.core.settings import get_settings
    
    settings = get_settings()
    print(settings.database_url)
"""
import os
from typing import List, Optional
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """애플리케이션 통합 설정"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ============================================
    # 환경 설정
    # ============================================
    environment: str = Field(default="development", description="실행 환경 (development/staging/production)")
    debug: bool = Field(default=True, description="디버그 모드")
    testing: bool = Field(default=False, description="테스트 모드")
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    # ============================================
    # 서버 설정
    # ============================================
    host: str = Field(default="127.0.0.1", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")
    workers: int = Field(default=1, description="Uvicorn 워커 수")
    
    # ============================================
    # 데이터베이스 설정
    # ============================================
    database_url: str = Field(
        default="postgresql://lms_user:1234@localhost:15432/lms_mvp_db",
        alias="DATABASE_URL",
        description="PostgreSQL 연결 문자열"
    )
    db_pool_size: int = Field(default=5, description="DB 커넥션 풀 크기")
    db_max_overflow: int = Field(default=10, description="최대 추가 커넥션")
    slow_query_ms: int = Field(default=300, alias="SLOW_QUERY_MS", description="슬로우 쿼리 임계값(ms)")
    
    # ============================================
    # Redis 설정
    # ============================================
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")
    upstash_redis_rest_url: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: Optional[str] = Field(default=None, alias="UPSTASH_REDIS_REST_TOKEN")
    
    # ============================================
    # JWT 인증 설정
    # ============================================
    jwt_secret: str = Field(
        default="dev_secret_change_me_in_production",
        alias="JWT_SECRET",
        description="JWT 서명 키 (프로덕션에서 반드시 변경)"
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expires_in_min: int = Field(default=120, alias="JWT_EXPIRES_IN_MIN", description="Access 토큰 만료(분)")
    refresh_expires_in_days: int = Field(default=14, alias="REFRESH_EXPIRES_IN_DAYS", description="Refresh 토큰 만료(일)")
    
    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v, info):
        """프로덕션에서 기본 시크릿 사용 방지"""
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production" and v == "dev_secret_change_me_in_production":
            raise ValueError("JWT_SECRET must be set in production!")
        return v
    
    # ============================================
    # CORS 설정
    # ============================================
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        description="허용된 CORS 오리진"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """문자열 또는 리스트 처리"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    # ============================================
    # AI/LLM 설정
    # ============================================
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    llm_provider: str = Field(default="openrouter", alias="LLM_PROVIDER")
    openrouter_model: str = Field(default="qwen/qwen3-coder:free", alias="OPENROUTER_MODEL")
    llm_enabled: bool = Field(default=True, alias="LLM_ENABLED")
    llm_timeout_ms: int = Field(default=30000, alias="LLM_TIMEOUT_MS")
    llm_max_retries: int = Field(default=2, alias="LLM_MAX_RETRIES")
    llm_cache_ttl_seconds: int = Field(default=600, alias="LLM_CACHE_TTL_SECONDS")
    llm_max_rpm: int = Field(default=20, alias="LLM_MAX_RPM", description="분당 최대 요청")
    
    # ============================================
    # 결제 설정
    # ============================================
    toss_client_key: Optional[str] = Field(default=None, alias="TOSS_CLIENT_KEY")
    toss_secret_key: Optional[str] = Field(default=None, alias="TOSS_SECRET_KEY")
    
    # ============================================
    # 이메일 설정
    # ============================================
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, alias="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    
    # ============================================
    # 로깅 설정
    # ============================================
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", description="로그 형식 (json/text)")
    
    # ============================================
    # 기능 플래그
    # ============================================
    ai_question_generation_enabled: bool = Field(default=True, alias="AI_QUESTION_GENERATION_ENABLED")
    ai_feedback_enabled: bool = Field(default=True, alias="AI_FEEDBACK_ENABLED")
    email_enabled: bool = Field(default=False, alias="EMAIL_ENABLED")


class DevelopmentSettings(AppSettings):
    """개발 환경 설정"""
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"


class StagingSettings(AppSettings):
    """스테이징 환경 설정"""
    environment: str = "staging"
    debug: bool = False


class ProductionSettings(AppSettings):
    """프로덕션 환경 설정"""
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        """프로덕션에서 로컬 DB 사용 방지"""
        if "localhost" in v or "127.0.0.1" in v:
            raise ValueError("Production database should not use localhost!")
        return v


class TestSettings(AppSettings):
    """테스트 환경 설정"""
    environment: str = "testing"
    testing: bool = True
    database_url: str = "sqlite:///./test.db"
    jwt_secret: str = "test_secret_key"


@lru_cache()
def get_settings() -> AppSettings:
    """환경에 따른 설정 반환 (캐싱됨)"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    settings_map = {
        "development": DevelopmentSettings,
        "staging": StagingSettings,
        "production": ProductionSettings,
        "testing": TestSettings,
    }
    
    settings_class = settings_map.get(environment, DevelopmentSettings)
    return settings_class()


def clear_settings_cache():
    """설정 캐시 클리어 (테스트용)"""
    get_settings.cache_clear()
