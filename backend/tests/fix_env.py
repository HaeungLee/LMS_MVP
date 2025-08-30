#!/usr/bin/env python3
"""USE_MOCK_AI 설정을 false로 변경하는 스크립트"""

def fix_env_file():
    """환경 파일 수정"""
    env_file = '.env'

    try:
        # 파일 읽기
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # USE_MOCK_AI 설정 변경
        if 'USE_MOCK_AI=true' in content:
            content = content.replace('USE_MOCK_AI=true', 'USE_MOCK_AI=false')

            # 변경된 내용 저장
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print('✅ USE_MOCK_AI를 false로 변경 완료!')
            print('🚀 이제 실제 AI 모드로 작동합니다.')
            return True
        else:
            print('⚠️ USE_MOCK_AI=true 설정을 찾을 수 없습니다.')
            return False

    except Exception as e:
        print(f'❌ 파일 수정 실패: {e}')
        return False

if __name__ == "__main__":
    fix_env_file()


