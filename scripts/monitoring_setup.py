#!/usr/bin/env python3
"""
LMS 베타 테스트 모니터링 설정 스크립트
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoringSetup:
    """모니터링 시스템 설정 클래스"""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.monitoring_endpoints = {
            "prometheus": "http://localhost:9090",
            "grafana": "http://localhost:3000",
            "backend_metrics": "http://localhost:8000/api/v1/monitoring/prometheus-metrics",
            "ai_metrics": "http://localhost:8000/api/v1/ai-features/metrics"
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
    
    def create_monitoring_directories(self):
        """모니터링 관련 디렉토리 생성"""
        self.log_step("모니터링 디렉토리 생성 중...")
        
        directories = [
            "monitoring",
            "monitoring/prometheus",
            "monitoring/grafana",
            "monitoring/grafana/dashboards",
            "monitoring/grafana/provisioning",
            "monitoring/alertmanager",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.log_step(f"디렉토리 생성: {directory}")
        
        self.log_step("모니터링 디렉토리 생성 완료", "success")
    
    def setup_prometheus_config(self):
        """Prometheus 설정 파일 생성"""
        self.log_step("Prometheus 설정 파일 생성 중...")
        
        config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "rule_files": [
                "rules/*.yml"
            ],
            "scrape_configs": [
                {
                    "job_name": "lms-backend",
                    "static_configs": [
                        {"targets": ["backend:8000"]}
                    ],
                    "metrics_path": "/api/v1/monitoring/prometheus-metrics",
                    "scrape_interval": "10s"
                },
                {
                    "job_name": "lms-ai-features", 
                    "static_configs": [
                        {"targets": ["backend:8000"]}
                    ],
                    "metrics_path": "/api/v1/ai-features/metrics",
                    "scrape_interval": "30s"
                },
                {
                    "job_name": "lms-beta-testing",
                    "static_configs": [
                        {"targets": ["backend:8000"]}
                    ],
                    "metrics_path": "/api/v1/beta/metrics",
                    "scrape_interval": "60s"
                }
            ]
        }
        
        # YAML 형식으로 저장
        import yaml
        config_path = self.project_root / "monitoring" / "prometheus" / "prometheus.yml"
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        self.log_step("Prometheus 설정 파일 생성 완료", "success")
    
    def setup_grafana_datasources(self):
        """Grafana 데이터소스 설정"""
        self.log_step("Grafana 데이터소스 설정 중...")
        
        datasources_config = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "access": "proxy",
                    "url": "http://prometheus:9090",
                    "isDefault": True,
                    "editable": True
                }
            ]
        }
        
        provisioning_dir = self.project_root / "monitoring" / "grafana" / "provisioning"
        provisioning_dir.mkdir(parents=True, exist_ok=True)
        
        datasources_path = provisioning_dir / "datasources.yml"
        with open(datasources_path, "w") as f:
            json.dump(datasources_config, f, indent=2)
        
        self.log_step("Grafana 데이터소스 설정 완료", "success")
    
    def setup_grafana_dashboards(self):
        """Grafana 대시보드 설정"""
        self.log_step("Grafana 대시보드 설정 중...")
        
        # 대시보드 프로비저닝 설정
        dashboard_config = {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "lms-dashboards",
                    "orgId": 1,
                    "folder": "",
                    "type": "file",
                    "disableDeletion": False,
                    "updateIntervalSeconds": 10,
                    "allowUiUpdates": True,
                    "options": {
                        "path": "/etc/grafana/provisioning/dashboards"
                    }
                }
            ]
        }
        
        provisioning_dir = self.project_root / "monitoring" / "grafana" / "provisioning"
        dashboard_config_path = provisioning_dir / "dashboards.yml"
        with open(dashboard_config_path, "w") as f:
            json.dump(dashboard_config, f, indent=2)
        
        # 기본 LMS 대시보드 생성
        self.create_lms_dashboard()
        
        self.log_step("Grafana 대시보드 설정 완료", "success")
    
    def create_lms_dashboard(self):
        """LMS 전용 대시보드 생성"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "LMS Beta Test Monitoring",
                "tags": ["lms", "beta", "monitoring"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "API Response Times",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "95th percentile"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "AI Feature Usage",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(ai_feature_calls_total[5m])",
                                "legendFormat": "AI Calls/sec"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "5s"
            }
        }
        
        dashboard_path = self.project_root / "monitoring" / "grafana" / "dashboards" / "lms_dashboard.json"
        with open(dashboard_path, "w") as f:
            json.dump(dashboard, f, indent=2)
    
    def setup_alerting_rules(self):
        """알림 규칙 설정"""
        self.log_step("알림 규칙 설정 중...")
        
        alert_rules = {
            "groups": [
                {
                    "name": "lms_alerts",
                    "rules": [
                        {
                            "alert": "HighErrorRate",
                            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) > 0.1",
                            "for": "2m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "High error rate detected",
                                "description": "Error rate is {{ $value }} errors per second"
                            }
                        },
                        {
                            "alert": "HighAIAPIErrorRate",
                            "expr": "rate(ai_api_errors_total[5m]) > 0.05",
                            "for": "3m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High AI API error rate",
                                "description": "AI API error rate is {{ $value }} errors per second"
                            }
                        }
                    ]
                }
            ]
        }
        
        import yaml
        rules_dir = self.project_root / "monitoring" / "prometheus" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        rules_path = rules_dir / "lms_alerts.yml"
        with open(rules_path, "w") as f:
            yaml.dump(alert_rules, f, default_flow_style=False)
        
        self.log_step("알림 규칙 설정 완료", "success")
    
    def setup_docker_compose_monitoring(self):
        """모니터링용 Docker Compose 설정"""
        self.log_step("모니터링 Docker Compose 설정 중...")
        
        monitoring_compose = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "lms_prometheus",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./monitoring/prometheus:/etc/prometheus",
                        "prometheus_data:/prometheus"
                    ],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=15d",
                        "--web.enable-lifecycle"
                    ],
                    "restart": "unless-stopped"
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "lms_grafana",
                    "ports": ["3000:3000"],
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./monitoring/grafana/provisioning:/etc/grafana/provisioning",
                        "./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards"
                    ],
                    "environment": [
                        "GF_SECURITY_ADMIN_PASSWORD=admin123",
                        "GF_USERS_ALLOW_SIGN_UP=false"
                    ],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "prometheus_data": {},
                "grafana_data": {}
            },
            "networks": {
                "default": {
                    "external": {
                        "name": "lms_mvp_default"
                    }
                }
            }
        }
        
        import yaml
        compose_path = self.project_root / "docker-compose.monitoring.yml"
        with open(compose_path, "w") as f:
            yaml.dump(monitoring_compose, f, default_flow_style=False)
        
        self.log_step("모니터링 Docker Compose 설정 완료", "success")
    
    def start_monitoring_services(self):
        """모니터링 서비스 시작"""
        self.log_step("모니터링 서비스 시작 중...")
        
        try:
            # 모니터링 서비스 시작
            subprocess.run([
                "docker-compose", "-f", "docker-compose.monitoring.yml", "up", "-d"
            ], cwd=self.project_root, check=True)
            
            # 서비스 시작 대기
            time.sleep(10)
            
            self.log_step("모니터링 서비스 시작 완료", "success")
            
        except subprocess.CalledProcessError as e:
            self.log_step(f"모니터링 서비스 시작 실패: {e}", "error")
            return False
        
        return True
    
    def verify_monitoring_services(self):
        """모니터링 서비스 확인"""
        self.log_step("모니터링 서비스 상태 확인 중...")
        
        for service, url in self.monitoring_endpoints.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.log_step(f"{service} 정상 동작 확인", "success")
                else:
                    self.log_step(f"{service} 응답 오류: {response.status_code}", "warning")
            except requests.RequestException:
                self.log_step(f"{service} 연결 실패", "warning")
    
    def generate_monitoring_guide(self):
        """모니터링 가이드 생성"""
        guide = """
# LMS 베타 테스트 모니터링 가이드

## 🚀 시작하기

### 모니터링 서비스 접속
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)

### 주요 메트릭 확인
1. **시스템 상태**: Service Health Overview 패널
2. **API 성능**: API Response Times 그래프
3. **AI 기능 사용량**: AI Feature Usage 차트
4. **베타 사용자 활동**: Beta User Activity 패널

## 📊 대시보드 가이드

### LMS Beta Test Monitoring 대시보드
- 시스템 전반의 상태를 모니터링
- AI 기능별 사용량 추적
- 베타 테스터 활동 분석
- 오류율 및 성능 지표 확인

## 🚨 알림 설정

### 주요 알림 규칙
1. **높은 오류율**: 5분간 5xx 오류율 > 10%
2. **AI API 오류율**: 5분간 AI API 오류율 > 5%
3. **서비스 다운**: 서비스 응답 없음
4. **높은 응답 시간**: 95퍼센타일 응답시간 > 2초

## 🔧 관리 명령어

### 모니터링 서비스 제어
```bash
# 시작
docker-compose -f docker-compose.monitoring.yml up -d

# 중지
docker-compose -f docker-compose.monitoring.yml down

# 로그 확인
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 메트릭 수집 확인
```bash
# Prometheus 타겟 상태 확인
curl http://localhost:9090/api/v1/targets

# 백엔드 메트릭 직접 확인
curl http://localhost:8000/api/v1/monitoring/prometheus-metrics
```

## 📈 베타 테스트 KPI

### 추적해야 할 주요 지표
1. **사용자 참여도**
   - 일일 활성 베타 사용자 수
   - 평균 세션 시간
   - 기능별 사용률

2. **AI 기능 성능**
   - AI API 응답 시간
   - AI 기능 오류율
   - 사용자당 AI 기능 사용 횟수

3. **시스템 안정성**
   - 서비스 가용성 (Uptime)
   - API 응답 시간
   - 데이터베이스 성능

4. **사용자 만족도**
   - 피드백 점수 평균
   - 버그 신고 건수
   - 기능 완료율

## 🛠️ 트러블슈팅

### 일반적인 문제들
1. **Grafana 접속 불가**: Docker 컨테이너 상태 확인
2. **메트릭 수집 안됨**: Prometheus 설정 및 타겟 확인
3. **대시보드 표시 안됨**: 데이터소스 연결 상태 확인

### 로그 확인 방법
```bash
# 애플리케이션 로그
docker-compose logs backend

# 모니터링 서비스 로그
docker-compose -f docker-compose.monitoring.yml logs grafana
docker-compose -f docker-compose.monitoring.yml logs prometheus
```
        """
        
        guide_path = self.project_root / "MONITORING_GUIDE.md"
        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(guide)
        
        self.log_step("모니터링 가이드 생성 완료", "success")
    
    def setup(self):
        """전체 모니터링 설정 실행"""
        try:
            self.log_step("=== LMS 베타 테스트 모니터링 설정 시작 ===")
            
            # 1. 디렉토리 구조 생성
            self.create_monitoring_directories()
            
            # 2. Prometheus 설정
            self.setup_prometheus_config()
            self.setup_alerting_rules()
            
            # 3. Grafana 설정
            self.setup_grafana_datasources()
            self.setup_grafana_dashboards()
            
            # 4. Docker Compose 설정
            self.setup_docker_compose_monitoring()
            
            # 5. 서비스 시작
            if self.start_monitoring_services():
                # 6. 서비스 확인
                time.sleep(15)  # 서비스 시작 대기
                self.verify_monitoring_services()
            
            # 7. 가이드 생성
            self.generate_monitoring_guide()
            
            self.log_step("=== 모니터링 설정 완료 ===", "success")
            
            # 접속 정보 출력
            print("\n🎉 모니터링 시스템이 준비되었습니다!")
            print("📊 Grafana: http://localhost:3000 (admin/admin123)")
            print("📈 Prometheus: http://localhost:9090")
            print("📋 가이드: ./MONITORING_GUIDE.md 파일을 참조하세요")
            
            return True
            
        except Exception as e:
            self.log_step(f"모니터링 설정 중 오류 발생: {e}", "error")
            return False

def main():
    parser = argparse.ArgumentParser(description="LMS 베타 테스트 모니터링 설정 스크립트")
    parser.add_argument(
        "--project-root",
        type=str,
        help="프로젝트 루트 디렉토리"
    )
    
    args = parser.parse_args()
    
    # 모니터링 설정 실행
    monitoring_setup = MonitoringSetup(project_root=args.project_root)
    success = monitoring_setup.setup()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
