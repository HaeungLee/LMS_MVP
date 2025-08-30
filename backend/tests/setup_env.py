#!/usr/bin/env python3
"""
환경변수 설정 도우미 스크립트
"""
import os
import sys
from pathlib import Path

def setup_environment():
    """환경변수 설정"""
    print("🔧 LMS MVP 환경변수 설정 도우미")
    print("=" * 50)

    # .env 파일 경로
    env_file = Path(__file__).parent / ".env"

    # 기본 환경변수 템플릿
    env_template = """# PostgreSQL 데이터베이스 설정
DATABASE_URL=postgresql://lms_user:1234@localhost:15432/lms_mvp_db

# 개발 환경 설정
ENVIRONMENT=development
DEBUG=True

# API 설정
API_HOST=0.0.0.0
API_PORT=8000

# OpenRouter AI 설정
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# JWT 설정
SECRET_KEY=your_jwt_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM 설정
LLM_PROVIDER=openrouter
LLM_ENABLED=true
LLM_TIMEOUT_MS=15000
LLM_MAX_RETRIES=2

# Redis 설정
REDIS_URL=redis://localhost:6379
"""

    if not env_file.exists():
        print("📝 .env 파일이 존재하지 않습니다. 새로 생성합니다...")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
        print(f"✅ .env 파일 생성 완료: {env_file}")
    else:
        print(f"📋 .env 파일이 이미 존재합니다: {env_file}")

    print("\n⚠️  다음 단계들을 따라주세요:")
    print("1. OpenRouter에서 무료 API 키 발급: https://openrouter.ai/")
    print("2. 발급받은 API 키를 .env 파일의 OPENROUTER_API_KEY에 입력")
    print("3. JWT_SECRET_KEY도 안전한 값으로 변경")
    print("4. python test_ai_api.py 명령어로 API 연결 테스트")

    print("\n🔗 관련 링크:")
    print("- OpenRouter API 키 발급: https://openrouter.ai/keys")
    print("- LMS MVP 문서: https://github.com/your-repo/lms-mvp")

    return True

if __name__ == "__main__":
    try:
        setup_environment()
    except Exception as e:
        print(f"❌ 설정 중 오류 발생: {e}")
        sys.exit(1)
