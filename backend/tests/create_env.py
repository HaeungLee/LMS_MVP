#!/usr/bin/env python3
"""환경변수 파일 생성 스크립트"""

env_content = """# PostgreSQL 데이터베이스 설정 (Docker 연동)
DATABASE_URL=postgresql://lms_user:1234@localhost:15432/lms_mvp_db

# 개발 환경 설정
ENVIRONMENT=development
DEBUG=True

# API 설정
API_HOST=0.0.0.0
API_PORT=8000

# PostgreSQL 직접 연결 설정
POSTGRES_HOST=localhost
POSTGRES_PORT=15432
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=1234
POSTGRES_DB=lms_mvp_db

# OpenRouter AI 설정
OPENROUTER_API_KEY=sk-or-v1-12345678901234567890123456789012345678901234567890
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free

# JWT 설정
SECRET_KEY=lms_mvp_jwt_secret_key_for_development_only_2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM 설정
LLM_PROVIDER=openrouter
LLM_ENABLED=true
LLM_TIMEOUT_MS=15000
LLM_MAX_RETRIES=2
LLM_CACHE_TTL_SECONDS=600
LLM_MAX_RPM=60

# Redis 설정
REDIS_URL=redis://localhost:6379

# CORS 설정
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"]
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print('.env 파일 생성 완료!')
print('OPENROUTER_API_KEY가 설정되었습니다.')
print('이제 AI API 테스트를 실행할 수 있습니다.')
