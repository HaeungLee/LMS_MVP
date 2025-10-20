"""
테스트용 사용자 생성 또는 조회
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("1. 새 테스트 계정 생성")
print("=" * 60)

# 회원가입 시도
signup_data = {
    "email": "test@example.com",
    "password": "test1234",
    "username": "테스터"
}

signup_response = requests.post(
    f"{BASE_URL}/api/v1/auth/signup",
    json=signup_data
)

print(f"Status: {signup_response.status_code}")

if signup_response.status_code == 200:
    print("✅ 새 계정 생성 성공")
    print(json.dumps(signup_response.json(), indent=2, ensure_ascii=False))
elif signup_response.status_code == 400:
    print("⚠️ 계정이 이미 존재합니다. 로그인을 시도합니다.")
else:
    print(f"❌ 회원가입 실패: {signup_response.text}")

print("\n" + "=" * 60)
print("2. 로그인 테스트")
print("=" * 60)

login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={
        "email": "test@example.com",
        "password": "test1234"
    }
)

print(f"Status: {login_response.status_code}")

if login_response.status_code == 200:
    print("✅ 로그인 성공")
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    print(f"Token: {access_token[:50]}...")
    
    # 토큰을 파일에 저장
    with open("test_token.txt", "w") as f:
        f.write(access_token)
    print("\n💾 토큰이 test_token.txt에 저장되었습니다.")
    
    print(f"\n사용자 정보:")
    print(f"- Email: {login_data.get('email')}")
    print(f"- Username: {login_data.get('username')}")
    
else:
    print(f"❌ 로그인 실패")
    print(login_response.text)
