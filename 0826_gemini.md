# Gemini의 백엔드 리팩토링 및 베타 런칭 점검 계획 (2025-08-26)

## 1. 파일 및 디렉토리 구조 리팩토링

- [x] **`backend/` 루트 디렉토리**
    - [x] `check_db.py`, `test_db_connection.py` 역할에 맞게 `scripts` 폴더로 이동 및 이름 변경
    - [ ] `test_openrouter.py`를 `tests/` 디렉토리로 이동하여 테스트 스위트에 통합

- [x] **`backend/app/api/v1/` 디렉토리**
    - [x] `ai_learning_backup.py` 삭제 (Git으로 버전 관리)
    - [x] `ai_learning_backup_disabled.py` 삭제 (Git으로 버전 관리)
    - [x] `ai_learning_test.py` 삭제 (테스트 코드는 `tests/` 디렉토리로)

- [x] **`backend/app/middleware/` 디렉토리**
    - [x] `advanced_rate_limit.py`의 기능을 `rate_limit.py`로 통합하고 미사용 파일 삭제
    - [x] `monitoring.py`의 잘못된 import 경로 수정 완료

- [x] **`backend/app/services/` 디렉토리**
    - [x] `advanced_llm_optimizer.py` 역할 분석 완료 (유지 결정)
    - [x] `deep_learning_analyzer.py` 역할 분석 완료 (유지 결정)

## 2. 베타 런칭 (20명 동시 접속) 준비 상태 점검

- [x] **비동기 처리 (Celery) 설정 최적화**
    - [x] `docker-compose.prod.yml`의 Celery 워커 수를 4개로 증설 (`replicas: 4`)
    - [ ] (선택) Celery 모니터링 도구 `Flower` 도입 검토

- [ ] **캐싱 전략 (Redis) 구체화 - (진행 중)**
    - [ ] `llm_cache.py`를 현재의 **인메모리 캐시**에서 **Redis 공유 캐시**로 변경 필요
    - [ ] 캐시 유효 시간(TTL) 설정값 확인 및 최적화
    - [ ] 캐시 키(Key) 생성 전략 점검 (사용자별/콘텐츠별 캐싱 정책 확인)

- [ ] **속도 제한 (Rate Limiting) 설정 최적화**
    - [ ] API 및 LLM 호출에 대한 Rate Limit 임계값 구체화 및 설정 (사용자별/전체)

- [ ] **데이터베이스 커넥션 풀링 최적화**
    - [ ] `core/database.py`의 `create_engine`에 `pool_size`, `max_overflow` 설정 추가 검토

- [ ] **LLM API 안정성 강화**
    - [ ] LLM API 호출 시 `timeout` 설정 적용
    - [ ] 일시적 오류에 대한 `retry` 로직 추가 검토

- [ ] **로깅 및 에러 모니터링 연동 강화**
    - [ ] 주요 에러(HTTP 500, Celery Task Fail) 발생 시 로깅 및 알림(Alert) 설정 확인
    - [ ] Grafana 대시보드에 핵심 성능 지표(API 응답 시간, LLM 응답 시간 등) 추가

- [ ] **보안 점검**
    - [ ] `config.py` 및 소스코드 전체에 민감 정보(API 키 등) 하드코딩 여부 최종 확인