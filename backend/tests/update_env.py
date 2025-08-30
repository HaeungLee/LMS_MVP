#!/usr/bin/env python3
"""
환경변수 파일 업데이트 스크립트
"""
import os
from pathlib import Path

def update_env_file():
    """환경변수 파일을 업데이트합니다."""
    project_root = Path(__file__).parent
    env_file = project_root / ".env"

    # .env 파일 존재 확인
    if not env_file.exists():
        print("❌ .env 파일을 찾을 수 없습니다.")
        return False

    try:
        # 현재 .env 파일 내용 읽기
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # API 키와 모의 모드 설정
        api_key = "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"
        use_mock = "true"

        # 기존 설정 업데이트 또는 추가
        updated_lines = []
        api_key_updated = False
        mock_mode_updated = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                updated_lines.append(line)
                continue

            if line.startswith('OPENROUTER_API_KEY='):
                updated_lines.append(f'OPENROUTER_API_KEY={api_key}')
                api_key_updated = True
                print("✅ OPENROUTER_API_KEY 업데이트됨")
            elif line.startswith('USE_MOCK_AI='):
                updated_lines.append(f'USE_MOCK_AI={use_mock}')
                mock_mode_updated = True
                print("✅ USE_MOCK_AI 업데이트됨")
            else:
                updated_lines.append(line)

        # 설정이 없으면 추가
        if not api_key_updated:
            updated_lines.append(f'OPENROUTER_API_KEY={api_key}')
            print("✅ OPENROUTER_API_KEY 추가됨")

        if not mock_mode_updated:
            updated_lines.append(f'USE_MOCK_AI={use_mock}')
            print("✅ USE_MOCK_AI 추가됨")

        # 파일에 쓰기
        with open(env_file, 'w', encoding='utf-8') as f:
            for line in updated_lines:
                f.write(line + '\n')

        print("🎉 .env 파일 업데이트 완료!")
        print(f"   API 키: {api_key[:20]}...")
        print(f"   모의 모드: {use_mock}")
        return True

    except Exception as e:
        print(f"💥 .env 파일 업데이트 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("🔧 환경변수 파일 업데이트 중...")
    success = update_env_file()

    if success:
        print("\n📝 설정 완료:")
        print("   - 실제 API 키는 유효하지 않아 모의 AI 모드로 설정")
        print("   - 교육적으로 의미 있는 응답을 제공하는 모의 AI 사용")
        print("   - 실제 유효한 API 키를 받으면 USE_MOCK_AI=false로 변경")
    else:
        print("❌ 환경변수 파일 업데이트 실패")