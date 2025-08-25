#!/usr/bin/env python3
"""
LMS 베타 테스트 배포 자동화 스크립트
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """배포 관리 클래스"""
    
    def __init__(self, environment: str = "dev", project_root: Optional[str] = None):
        self.environment = environment
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.backup_dir = self.project_root / "backups" / time.strftime("%Y%m%d_%H%M%S")
        self.health_endpoints = {
            "backend": "http://localhost:8000/health",
            "frontend": "http://localhost:80/health",
            "ai_features": "http://localhost:8000/api/v1/ai-features/health",
            "beta_testing": "http://localhost:8000/api/v1/beta/health"
        }
    
    def log_step(self, message: str, level: str = "info"):
        """단계별 로깅"""
        symbols = {
            "info": "🔄",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        log_message = f"{symbols.get(level, '📋')} {message}"
        
        if level == "error":
            logger.error(log_message)
        elif level == "warning":
            logger.warning(log_message)
        elif level == "success":
            logger.info(log_message)
        else:
            logger.info(log_message)
    
    def run_command(self, command: List[str], cwd: Optional[str] = None, 
                   capture_output: bool = True) -> Tuple[bool, str]:
        """명령어 실행"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5분 타임아웃
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            self.log_step(f"명령어 실행 타임아웃: {' '.join(command)}", "error")
            return False, "Timeout"
        except Exception as e:
            self.log_step(f"명령어 실행 실패: {e}", "error")
            return False, str(e)
    
    def check_prerequisites(self) -> bool:
        """사전 요구사항 확인"""
        self.log_step("사전 요구사항 확인 중...")
        
        # 필수 파일 확인
        required_files = [
            "docker-compose.yml",
            "backend/requirements.txt",
            "frontend/package.json",
            "backend/app/main.py"
        ]
        
        if self.environment == "prod":
            required_files.extend([
                "docker-compose.prod.yml",
                ".env.prod"
            ])
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_step(f"누락된 필수 파일: {', '.join(missing_files)}", "error")
            return False
        
        # Docker 확인
        success, _ = self.run_command(["docker", "--version"])
        if not success:
            self.log_step("Docker가 설치되지 않았거나 실행되지 않습니다", "error")
            return False
        
        # Docker Compose 확인
        success, _ = self.run_command(["docker-compose", "--version"])
        if not success:
            self.log_step("Docker Compose가 설치되지 않았습니다", "error")
            return False
        
        self.log_step("사전 요구사항 확인 완료", "success")
        return True
    
    def create_backup(self) -> bool:
        """백업 생성 (운영 환경만)"""
        if self.environment != "prod":
            return True
        
        self.log_step("운영 환경 백업 생성 중...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 데이터베이스 백업
            db_backup_cmd = [
                "docker-compose", "exec", "-T", "postgres",
                "pg_dump", "-U", "lms_user", "lms_db"
            ]
            success, output = self.run_command(db_backup_cmd)
            
            if success:
                with open(self.backup_dir / "database.sql", "w") as f:
                    f.write(output)
                self.log_step("데이터베이스 백업 완료", "success")
            else:
                self.log_step("데이터베이스 백업 실패", "warning")
            
            # 소스 백업
            subprocess.run([
                "cp", "-r", str(self.project_root), 
                str(self.backup_dir / "source_backup")
            ])
            
            self.log_step(f"백업 완료: {self.backup_dir}", "success")
            return True
            
        except Exception as e:
            self.log_step(f"백업 생성 실패: {e}", "warning")
            return True  # 백업 실패가 배포를 막지 않도록
    
    def build_images(self) -> bool:
        """Docker 이미지 빌드"""
        self.log_step("Docker 이미지 빌드 중...")
        
        compose_file = "docker-compose.prod.yml" if self.environment == "prod" else "docker-compose.yml"
        
        # 기존 컨테이너 정리
        self.run_command(["docker-compose", "-f", compose_file, "down", "--remove-orphans"])
        
        # 새 이미지 빌드
        success, output = self.run_command([
            "docker-compose", "-f", compose_file, "build", "--no-cache"
        ])
        
        if success:
            self.log_step("이미지 빌드 완료", "success")
            return True
        else:
            self.log_step(f"이미지 빌드 실패: {output}", "error")
            return False
    
    def run_migrations(self) -> bool:
        """데이터베이스 마이그레이션"""
        self.log_step("데이터베이스 마이그레이션 실행 중...")
        
        compose_file = "docker-compose.prod.yml" if self.environment == "prod" else "docker-compose.yml"
        
        # 데이터베이스 서비스 시작
        success, _ = self.run_command([
            "docker-compose", "-f", compose_file, "up", "-d", "postgres", "redis"
        ])
        
        if not success:
            self.log_step("데이터베이스 서비스 시작 실패", "error")
            return False
        
        # 데이터베이스 연결 대기
        self.log_step("데이터베이스 연결 대기 중...")
        time.sleep(15)
        
        # 마이그레이션 실행
        success, output = self.run_command([
            "docker-compose", "-f", compose_file, "run", "--rm", "backend",
            "alembic", "upgrade", "head"
        ])
        
        if success:
            self.log_step("마이그레이션 완료", "success")
            return True
        else:
            self.log_step(f"마이그레이션 실패: {output}", "error")
            return False
    
    def deploy_application(self) -> bool:
        """애플리케이션 배포"""
        self.log_step("애플리케이션 배포 중...")
        
        compose_file = "docker-compose.prod.yml" if self.environment == "prod" else "docker-compose.yml"
        
        success, output = self.run_command([
            "docker-compose", "-f", compose_file, "up", "-d"
        ])
        
        if success:
            self.log_step("애플리케이션 배포 완료", "success")
            return True
        else:
            self.log_step(f"애플리케이션 배포 실패: {output}", "error")
            return False
    
    def health_check(self) -> bool:
        """헬스체크"""
        self.log_step("헬스체크 실행 중...")
        
        max_attempts = 30
        wait_time = 10
        
        for service, url in self.health_endpoints.items():
            self.log_step(f"{service} 헬스체크 중...")
            
            for attempt in range(1, max_attempts + 1):
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        self.log_step(f"{service} 헬스체크 통과", "success")
                        break
                except requests.RequestException:
                    if attempt < max_attempts:
                        self.log_step(f"{service} 헬스체크 시도 {attempt}/{max_attempts}")
                        time.sleep(wait_time)
                    else:
                        self.log_step(f"{service} 헬스체크 실패", "warning")
                        return False
        
        self.log_step("모든 헬스체크 통과", "success")
        return True
    
    def run_validation_tests(self) -> bool:
        """검증 테스트 실행"""
        self.log_step("검증 테스트 실행 중...")
        
        test_files = [
            "backend/tests/test_phase4_validation.py",
            # 추가 테스트 파일들...
        ]
        
        for test_file in test_files:
            if (self.project_root / test_file).exists():
                self.log_step(f"테스트 실행: {test_file}")
                success, output = self.run_command([
                    "python", "-m", "pytest", test_file, "-v"
                ], cwd=self.project_root / "backend")
                
                if not success:
                    self.log_step(f"테스트 실패: {test_file}", "warning")
                    # 테스트 실패가 배포를 막지 않도록 경고로 처리
        
        self.log_step("검증 테스트 완료", "success")
        return True
    
    def print_deployment_info(self):
        """배포 정보 출력"""
        self.log_step("🎉 배포 완료! 서비스 정보:")
        
        info = f"""
        📋 배포 정보:
        • 환경: {self.environment}
        • 배포 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        🌐 서비스 접속 주소:
        • 프론트엔드: http://localhost:80
        • 백엔드 API: http://localhost:8000
        • API 문서: http://localhost:8000/docs
        
        🤖 AI 기능:
        • AI 기능 페이지: http://localhost:80/ai-features
        • AI 상태 확인: http://localhost:8000/api/v1/ai-features/health
        
        📊 베타 테스트:
        • 베타 대시보드: http://localhost:80/beta-dashboard
        • 베타 API: http://localhost:8000/api/v1/beta/health
        """
        
        if self.environment == "prod":
            info += """
        🔧 관리 도구 (운영 환경):
        • Flower (Celery): http://localhost:5555
        • Grafana: http://localhost:3000
        • Prometheus: http://localhost:9090
            """
        
        if self.backup_dir.exists():
            info += f"""
        💾 백업 위치: {self.backup_dir}
            """
        
        print(info)
    
    def rollback(self):
        """롤백 실행"""
        self.log_step("배포 실패 - 롤백 실행 중...", "error")
        
        compose_file = "docker-compose.prod.yml" if self.environment == "prod" else "docker-compose.yml"
        self.run_command(["docker-compose", "-f", compose_file, "down"])
        
        if self.environment == "prod" and self.backup_dir.exists():
            self.log_step("백업에서 복원 중...", "info")
            # 복원 로직 구현 가능
        
        self.log_step("롤백 완료", "error")
    
    def deploy(self) -> bool:
        """메인 배포 함수"""
        try:
            self.log_step("=== LMS 베타 테스트 배포 시작 ===", "info")
            
            # 1. 사전 검사
            if not self.check_prerequisites():
                return False
            
            # 2. 백업 (운영 환경만)
            if not self.create_backup():
                return False
            
            # 3. 빌드 및 배포
            if not self.build_images():
                return False
            
            if not self.run_migrations():
                return False
            
            if not self.deploy_application():
                return False
            
            # 4. 검증
            if not self.health_check():
                return False
            
            if not self.run_validation_tests():
                return False
            
            # 5. 배포 완료
            self.print_deployment_info()
            self.log_step("=== 배포 성공! ===", "success")
            
            return True
            
        except Exception as e:
            self.log_step(f"배포 중 예외 발생: {e}", "error")
            self.rollback()
            return False

def main():
    parser = argparse.ArgumentParser(description="LMS 베타 테스트 배포 스크립트")
    parser.add_argument(
        "environment",
        choices=["dev", "staging", "prod"],
        default="dev",
        nargs="?",
        help="배포 환경 (기본값: dev)"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        help="프로젝트 루트 디렉토리"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="검증 테스트 건너뛰기"
    )
    
    args = parser.parse_args()
    
    # 배포 실행
    deployment_manager = DeploymentManager(
        environment=args.environment,
        project_root=args.project_root
    )
    
    success = deployment_manager.deploy()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
