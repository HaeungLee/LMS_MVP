# 0826 베타 테스트 체크리스트

다음 문서는 레포 분석을 바탕으로 베타 테스트 시작 전에 확인해야 할 항목들을 우선순위별로 정리한 체크리스트입니다.

---

## 요약
- 목표: 베타 테스트 전 시스템 안정성·보안·품질을 확보하고, 참가자 온보딩과 피드백 수집 경로를 준비한다.
- 적용 범위: `backend`, `frontend`, 데이터베이스, 배포(도커/k8s), 모니터링/로깅, 운영·문서.

---

## 체크리스트 (최상단에 간단 항목)
- [ ] 로컬/컨테이너에서 전체 스택 기동 확인 (백엔드 + 프론트 + DB)
- [ ] DB 마이그레이션(`alembic upgrade head`) 및 시드 스크립트 실행 확인
- [ ] 핵심 API(로그인, 주요 CRUD)와 프론트 온보딩 플로우 동작 확인
- [ ] 환경변수·시크릿 노출 여부 점검 (`env.sample` 기준)
- [ ] 백업·롤백 절차 문서화
- [ ] 자동화된 테스트(backend/tests/) 전부 실행 및 통과
- [ ] 모니터링(Prometheus, Grafana)과 로깅(Sentry/파일) 기본 동작 확인
- [ ] 베타 가이드(참가자용) 및 피드백 채널 준비

---

## 우선순위별 상세 항목

P0 (즉시 확인)
- 런/빌드 검증
  - 백엔드: 종속성 설치, 앱 실행(로컬/도커), `/health` 응답
  - 프론트: `npm install` 및 `npm run dev` 또는 `npm run build` 후 정적 서빙 확인
- DB 마이그레이션 & 시드
  - `alembic upgrade head` 성공
  - `scripts/seed_admin.py`, `seed_teacher.py` 등으로 테스트 계정 생성
- 인증·권한
  - 베타 계정과 관리자 계정 분리 및 토큰/권한 흐름 점검
- 시크릿 관리
  - 민감정보가 리포지토리에 하드코딩 되어 있지 않은지 확인
- 백업·롤백 계획
  - 배포 전 DB 스냅샷/백업 절차 문서화

P1 (중요)
- 자동화된 테스트 실행 및 실패 해결
- 스모크/엔드투엔드 시나리오 점검(회원가입 → 온보딩 → 주요 기능)
- 로깅·오류 수집 (Sentry 또는 중앙 로그) 설정 확인
- 모니터링·알람(에러율, 5xx, CPU, 메모리) 기본 설정
- 간단 부하 테스트로 병목 확인

P2 (권장)
- 피드백·이슈 수집 채널(폼, 슬랙/메일, 이슈템플릿) 준비
- 개인정보·법률(데이터 보존·삭제) 검토
- 테스트 데이터와 실제 데이터 분리(네임스페이스/DB 별도)
- 보안 스캔(의존성 취약점, CORS/CSP 확인)

---

## 스모크 체크리스트 (핵심 흐름)
- Backend
  - `alembic upgrade head` 적용
  - 시드 후 관리자 로그인 확인
  - `/health` 응답
  - 로그인/토큰 발급 API 동작
  - 문제 생성/조회/채점(핵심 엔드포인트) 정상 동작
- Frontend
  - 앱이 로컬에서 로드되고 라우트가 동작하는지 확인
  - `BetaOnboarding2` 컴포넌트에서 폼 제출 → 백엔드 API 호출 성공
- 통합
  - 프론트에서 인증 후 보호된 API 호출 성공
  - 정적 파일(nginx) 서빙 확인
- 모니터링
  - Prometheus 메트릭 수집, Grafana 대시보드 데이터 표시

---

## 빠른 실행(참고) — PowerShell 명령 예시
(환경과 venv/도구에 따라 경로/명령 조정 필요)

```powershell
# Backend: 가상환경 활성화(Windows)
cd C:\Aprojects\LMS_MVP\backend
venv\Scripts\Activate.ps1; pip install -r requirements.txt; alembic upgrade head

# Backend: 테스트 실행
cd C:\Aprojects\LMS_MVP\backend
venv\Scripts\Activate.ps1; pytest tests

# Frontend: 개발 서버
cd C:\Aprojects\LMS_MVP\frontend
npm install; npm run dev

# Frontend: 빌드
cd C:\Aprojects\LMS_MVP\frontend
npm install; npm run build
```

---

## 우선 작업 권장 순서 (1~3일 계획)
1. 전체 스택 기동 및 핵심 스모크 테스트(P0)
2. 자동화 테스트 실행 및 실패 해결(P1)
3. 모니터링/로깅 기본 세팅과 대시보드(P1)
4. 베타 참가자용 문서 및 피드백 채널 정비(P2)

---

## 리스크 및 완화 방안 (요약)
- 데이터 손상: 베타용 분리 DB, 배포 전 백업 권장
- 시크릿 노출: CI/CD 시크릿 관리 도입, 리포지토리 스캔
- 관찰성 부족: Sentry/로그집중화 우선 도입
- 사용자 혼란: 명확한 안내문, 알려진 이슈 리스트 제공

---

## 다음 제안 (원하면 내가 바로 실행)
- (A) 로컬에서 전체 스택 기동 후 스모크 테스트 자동 실행 → 결과 리포트 작성
- (B) 스모크 자동화 스크립트(파이썬 또는 PowerShell) 작성
- (C) Sentry 연동 예시 설정 및 PR 생성

원하시면 A/B/C 중 선택해 주세요. 선택하시면 바로 실행하거나 필요한 파일들을 생성/편집하겠습니다.
