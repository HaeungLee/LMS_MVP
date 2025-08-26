#!/usr/bin/env python3
"""
간단한 서버 연결 테스트
- 빠른 연결 확인
- 타임아웃 설정 조정
"""

import requests
import time
from datetime import datetime

def test_server_connection():
    """서버 연결 테스트"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 간단한 서버 연결 테스트")
    print("=" * 40)
    
    # 1. 기본 연결 테스트 (짧은 타임아웃)
    print("1. 기본 연결 테스트 (5초 타임아웃)...")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/", timeout=5)
        end_time = time.time()
        
        print(f"   ✅ 연결 성공!")
        print(f"   📊 상태 코드: {response.status_code}")
        print(f"   ⏱️  응답 시간: {end_time - start_time:.2f}초")
        
    except requests.exceptions.Timeout:
        print("   ❌ 타임아웃 (5초)")
    except requests.exceptions.ConnectionError:
        print("   ❌ 연결 실패")
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
    
    # 2. API 문서 테스트 (긴 타임아웃)
    print("\n2. API 문서 테스트 (30초 타임아웃)...")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/docs", timeout=30)
        end_time = time.time()
        
        print(f"   ✅ 연결 성공!")
        print(f"   📊 상태 코드: {response.status_code}")
        print(f"   ⏱️  응답 시간: {end_time - start_time:.2f}초")
        
    except requests.exceptions.Timeout:
        print("   ❌ 타임아웃 (30초)")
    except requests.exceptions.ConnectionError:
        print("   ❌ 연결 실패")
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
    
    # 3. 대시보드 API 테스트
    print("\n3. 대시보드 API 테스트 (30초 타임아웃)...")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/v1/dashboard/stats", timeout=30)
        end_time = time.time()
        
        print(f"   ✅ 연결 성공!")
        print(f"   📊 상태 코드: {response.status_code}")
        print(f"   ⏱️  응답 시간: {end_time - start_time:.2f}초")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📄 응답 데이터: {type(data)}")
            except:
                print(f"   📄 응답 데이터: 텍스트 (길이: {len(response.text)})")
        
    except requests.exceptions.Timeout:
        print("   ❌ 타임아웃 (30초)")
    except requests.exceptions.ConnectionError:
        print("   ❌ 연결 실패")
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")
    
    # 4. 서버 상태 요약
    print("\n" + "=" * 40)
    print("📊 서버 상태 요약")
    print("=" * 40)
    
    # 포트 확인
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            print("✅ 포트 8000이 열려있음")
        else:
            print("❌ 포트 8000이 닫혀있음")
    except Exception as e:
        print(f"❌ 포트 확인 실패: {str(e)}")
    
    print(f"\n⏰ 테스트 시간: {datetime.now().isoformat()}")

if __name__ == "__main__":
    test_server_connection()

