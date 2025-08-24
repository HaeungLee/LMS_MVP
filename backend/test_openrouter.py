#!/usr/bin/env python3
"""
OpenRouter API 테스트 스크립트
google/gemma-3-27b-it:free 모델 테스트
"""

import os
import sys
import httpx
import asyncio
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

async def test_openrouter_api():
    """OpenRouter API 테스트"""
    
    print("🔑 API 키 확인...")
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY가 설정되지 않았습니다.")
        return False
    
    print(f"✅ API 키: {OPENROUTER_API_KEY[:20]}...")
    print(f"🌐 Base URL: {OPENROUTER_BASE_URL}")
    
    # 테스트 요청 데이터
    test_data = {
        "model": "qwen/qwen3-coder:free",
        "messages": [
            {
                "role": "user", 
                "content": "안녕하세요! 파이썬 학습에 대한 간단한 조언을 해주세요."
            }
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",  # Optional
        "X-Title": "LMS MVP AI Learning System"   # Optional
    }
    
    print("\n🚀 OpenRouter API 호출 테스트...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                json=test_data,
                headers=headers
            )
            
            print(f"📊 응답 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API 호출 성공!")
                print("\n🤖 AI 응답:")
                print("-" * 50)
                
                # 응답 구조 확인
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    print(ai_response)
                    print("-" * 50)
                    
                    # 사용량 정보
                    if "usage" in result:
                        usage = result["usage"]
                        print(f"\n📈 토큰 사용량:")
                        print(f"   입력: {usage.get('prompt_tokens', 0)} 토큰")
                        print(f"   출력: {usage.get('completion_tokens', 0)} 토큰")
                        print(f"   총합: {usage.get('total_tokens', 0)} 토큰")
                    
                    return True
                else:
                    print("❌ 응답에 choices가 없습니다.")
                    print(f"응답 데이터: {result}")
                    return False
                    
            else:
                print(f"❌ API 호출 실패: {response.status_code}")
                print(f"오류 내용: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("❌ 요청 시간 초과 (30초)")
        return False
    except Exception as e:
        print(f"❌ 예외 발생: {str(e)}")
        return False

async def test_learning_prompt():
    """학습 관련 프롬프트 테스트"""
    
    print("\n" + "="*60)
    print("🎓 학습 관련 AI 응답 테스트")
    print("="*60)
    
    learning_data = {
        "model": "qwen/qwen3-coder:free",
        "messages": [
            {
                "role": "system",
                "content": "당신은 파이썬 프로그래밍 교육 전문가입니다. 학습자의 수준에 맞는 맞춤형 학습 계획을 제공해주세요."
            },
            {
                "role": "user", 
                "content": """
                학습자 정보:
                - 현재 주제: Python 기초 (변수, 조건문)
                - 최근 정답률: 70%
                - 취약점: 리스트 슬라이싱, 반복문
                
                오늘의 학습 계획을 JSON 형식으로 제안해주세요.
                """
            }
        ],
        "max_tokens": 300,
        "temperature": 0.3
    }
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "LMS MVP AI Learning System"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                json=learning_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                print("🎯 학습 계획 AI 응답:")
                print("-" * 50)
                print(ai_response)
                print("-" * 50)
                return True
            else:
                print(f"❌ 학습 계획 API 실패: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 학습 계획 테스트 오류: {str(e)}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🤖 OpenRouter API 테스트 시작")
    print("="*60)
    
    # 기본 API 테스트
    basic_test = await test_openrouter_api()
    
    if basic_test:
        # 학습 관련 테스트
        learning_test = await test_learning_prompt()
        
        if learning_test:
            print("\n🎉 모든 테스트 통과!")
            print("✅ 실제 AI 기능 활성화 준비 완료")
        else:
            print("\n⚠️  기본 API는 작동하지만 학습 프롬프트에 문제가 있습니다.")
    else:
        print("\n❌ 기본 API 테스트 실패")
        print("API 키나 설정을 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(main())
