#!/usr/bin/env python3
"""
백엔드 서버 상태 및 API 엔드포인트 종합 테스트
- 서버 연결 상태 확인
- 데이터베이스 연결 확인
- API 엔드포인트 응답 테스트
- 환경 변수 설정 확인
"""

import sys
import os
import asyncio
import aiohttp
import json
import time
import requests
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.config import settings

class BackendHealthChecker:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.api_prefix = "/api/v1"
        self.results = {
            "server_status": "unknown",
            "database_status": "unknown",
            "api_endpoints": [],
            "environment_check": [],
            "overall_status": "unknown",
            "timestamp": datetime.now().isoformat()
        }
    
    def run_all_checks(self):
        """모든 상태 확인 실행"""
        print("🔍 백엔드 서버 종합 상태 확인 시작...")
        print("=" * 60)
        
        # 1. 환경 변수 확인
        self.check_environment()
        
        # 2. 데이터베이스 연결 확인
        self.check_database()
        
        # 3. 서버 연결 확인
        self.check_server_connection()
        
        # 4. API 엔드포인트 테스트
        self.check_api_endpoints()
        
        # 5. 결과 요약
        self.print_summary()
        
        return self.results
    
    def check_environment(self):
        """환경 변수 설정 확인"""
        print("📋 환경 변수 확인 중...")
        
        env_checks = [
            ("DATABASE_URL", settings.database_url, "데이터베이스 연결 문자열"),
            ("ENVIRONMENT", settings.environment, "실행 환경"),
            ("POSTGRES_HOST", settings.postgres_host, "PostgreSQL 호스트"),
            ("POSTGRES_PORT", settings.postgres_port, "PostgreSQL 포트"),
            ("POSTGRES_USER", settings.postgres_user, "PostgreSQL 사용자"),
            ("POSTGRES_DB", settings.postgres_db, "PostgreSQL 데이터베이스"),
            ("OPENROUTER_API_KEY", "설정됨" if settings.openrouter_api_key else "미설정", "OpenRouter API 키"),
            ("LLM_PROVIDER", settings.llm_provider, "LLM 제공자"),
        ]
        
        for var_name, value, description in env_checks:
            status = "✅" if value else "❌"
            self.results["environment_check"].append({
                "variable": var_name,
                "value": str(value)[:50] + "..." if len(str(value)) > 50 else str(value),
                "description": description,
                "status": "ok" if value else "missing"
            })
            print(f"  {status} {var_name}: {value}")
    
    def check_database(self):
        """데이터베이스 연결 확인"""
        print("\n🗄️  데이터베이스 연결 확인 중...")
        
        try:
            db = SessionLocal()
            
            # 간단한 쿼리 실행
            from sqlalchemy import text
            result = db.execute(text("SELECT 1 as test")).scalar()
            
            if result == 1:
                self.results["database_status"] = "connected"
                print("  ✅ 데이터베이스 연결 성공")
                
                # 테이블 존재 확인
                tables = db.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)).fetchall()
                
                table_names = [row[0] for row in tables]
                print(f"  📊 발견된 테이블: {len(table_names)}개")
                for table in table_names[:5]:  # 처음 5개만 표시
                    print(f"    - {table}")
                if len(table_names) > 5:
                    print(f"    ... 및 {len(table_names) - 5}개 더")
                    
            else:
                self.results["database_status"] = "query_failed"
                print("  ❌ 데이터베이스 쿼리 실패")
                
        except Exception as e:
            self.results["database_status"] = "connection_failed"
            print(f"  ❌ 데이터베이스 연결 실패: {str(e)}")
        finally:
            try:
                db.close()
            except:
                pass
    
    def check_server_connection(self):
        """서버 연결 확인"""
        print("\n🌐 서버 연결 확인 중...")
        
        try:
            # 기본 연결 테스트
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                self.results["server_status"] = "running"
                print("  ✅ 서버 연결 성공")
            else:
                self.results["server_status"] = f"unexpected_status_{response.status_code}"
                print(f"  ⚠️  서버 응답: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.results["server_status"] = "connection_failed"
            print("  ❌ 서버 연결 실패 - 서버가 실행 중인지 확인하세요")
        except requests.exceptions.Timeout:
            self.results["server_status"] = "timeout"
            print("  ❌ 서버 응답 시간 초과")
        except Exception as e:
            self.results["server_status"] = "error"
            print(f"  ❌ 서버 연결 오류: {str(e)}")
    
    def check_api_endpoints(self):
        """API 엔드포인트 테스트"""
        print("\n🔌 API 엔드포인트 테스트 중...")
        
        endpoints = [
            ("/docs", "API 문서"),
            ("/openapi.json", "OpenAPI 스키마"),
            (f"{self.api_prefix}/dashboard/stats", "대시보드 통계"),
            (f"{self.api_prefix}/questions/python_basics", "문제 목록"),
            (f"{self.api_prefix}/auth/me", "인증 상태"),
        ]
        
        for endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                status = "✅" if response.status_code < 400 else "⚠️" if response.status_code < 500 else "❌"
                
                self.results["api_endpoints"].append({
                    "endpoint": endpoint,
                    "description": description,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "status": "success" if response.status_code < 400 else "error"
                })
                
                print(f"  {status} {endpoint} ({description}): {response.status_code} - {response.elapsed.total_seconds():.2f}s")
                
            except requests.exceptions.RequestException as e:
                self.results["api_endpoints"].append({
                    "endpoint": endpoint,
                    "description": description,
                    "status_code": None,
                    "response_time": None,
                    "status": "failed",
                    "error": str(e)
                })
                print(f"  ❌ {endpoint} ({description}): 연결 실패 - {str(e)}")
    
    def print_summary(self):
        """결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 백엔드 상태 요약")
        print("=" * 60)
        
        # 전체 상태 결정
        server_ok = self.results["server_status"] == "running"
        db_ok = self.results["database_status"] == "connected"
        api_ok = all(ep["status"] in ["success", "error"] for ep in self.results["api_endpoints"])
        
        if server_ok and db_ok:
            self.results["overall_status"] = "healthy"
            print("🎉 백엔드 서버가 정상적으로 작동하고 있습니다!")
        elif server_ok and not db_ok:
            self.results["overall_status"] = "database_issue"
            print("⚠️  서버는 실행 중이지만 데이터베이스에 문제가 있습니다.")
        elif not server_ok:
            self.results["overall_status"] = "server_issue"
            print("❌ 서버가 실행되지 않고 있습니다.")
        else:
            self.results["overall_status"] = "unknown"
            print("❓ 서버 상태를 확인할 수 없습니다.")
        
        print(f"\n📋 상세 상태:")
        print(f"  서버: {self.results['server_status']}")
        print(f"  데이터베이스: {self.results['database_status']}")
        print(f"  API 엔드포인트: {len([ep for ep in self.results['api_endpoints'] if ep['status'] == 'success'])}/{len(self.results['api_endpoints'])} 정상")
        
        # 문제 해결 가이드
        if self.results["overall_status"] != "healthy":
            print(f"\n🔧 문제 해결 가이드:")
            
            if self.results["server_status"] != "running":
                print("  1. 백엔드 서버를 시작하세요:")
                print("     cd backend")
                print("     python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
            
            if self.results["database_status"] != "connected":
                print("  2. 데이터베이스를 확인하세요:")
                print("     docker-compose up -d")
                print("     python check_db.py")
            
            if any(ep["status"] == "failed" for ep in self.results["api_endpoints"]):
                print("  3. API 엔드포인트 문제를 확인하세요:")
                print("     - 서버 로그 확인")
                print("     - 환경 변수 설정 확인")
        
        print(f"\n⏰ 검사 시간: {self.results['timestamp']}")

def main():
    """메인 실행 함수"""
    checker = BackendHealthChecker()
    results = checker.run_all_checks()
    
    # 결과를 JSON 파일로 저장
    with open("backend_health_check_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과가 'backend_health_check_results.json'에 저장되었습니다.")
    
    return results

if __name__ == "__main__":
    main()
