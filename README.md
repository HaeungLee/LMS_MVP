# LMS MVP 프로젝트 실행 가이드

## 1) 프로젝트 소개

AI 기반 코딩 학습 피드백을 제공하는 LMS(Learning Management System) MVP입니다. 사용자는 문제를 풀고 AI 피드백으로 학습합니다.

## 2) 기술 스택

- 백엔드: FastAPI (Python)
- 프론트엔드: React + TypeScript (Vite) + TanStack Query
- 데이터베이스: PostgreSQL (Docker) + JSON 호환
- 기타: Redis/Celery(옵션), Prometheus/Grafana(옵션)

## 3) 사전 준비물

- Python 3.11 권장 (3.9+ 동작)
- Node.js 18.x + npm
- Docker + Docker Compose

환경 변수 템플릿: 루트의 `env.sample`를 복사해 `.env`를 만듭니다. (필수는 아님)

```text
cp env.sample .env  # Windows PowerShell은 수동 복사 또는 편집기로 생성
```

중요 값 예시(루트 .env 또는 `backend/.env`):

```
DATABASE_URL=postgresql://lms_user:1234@localhost:15432/lms_mvp_db
JWT_SECRET=dev_secret_change_me
OPENROUTER_API_KEY=
```

프론트엔드 환경 변수(frontend/.env):

```
VITE_API_BASE_URL=http://localhost:8000

```
VITE_API_BASE_URL=http://localhost:8000
```

## 4) 로컬 실행 (개발용, Windows PowerShell)

### 4.0 데이터베이스(컨테이너) 시작

```powershell
docker-compose up -d
docker ps | findstr lms_mvp_db_container
```
`healthy`면 준비 완료입니다. 포트: 15432 → 컨테이너 5432.

### 4.1 백엔드 실행

```powershell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt

# (선택) 초기 데이터 시드
python -m scripts.seed_taxonomy
python -m scripts.seed_teacher
python -m scripts.seed_admin
# 필요 시: python -m scripts.seed_questions ; python -m scripts.seed_curriculum_phase1

# 서버 시작
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API: http://localhost:8000

### 4.2 프론트엔드 실행

프론트엔드는 새로운 TypeScript + Vite 구조로 마이그레이션되었습니다. 개발 서버 기본 포트는 `vite.config.ts`에 따라 5173입니다.

```powershell
cd frontend
npm install
npm run dev
```

웹: http://localhost:5173

## 5) 운영/패키징 (요약)

프로덕션 이미지는 각 디렉토리의 `Dockerfile.prod`를 사용합니다. 상위 `docker-compose.prod.yml`은 Redis/모니터링/NGINX까지 포함하므로 일부 로컬 파일(nginx 설정 등)이 추가로 필요할 수 있습니다. 최소 구성만 배포하려면 다음을 참고하세요.

- Postgres: compose 사용(포트 5432 매핑 필요 시 수정)
- Backend: `backend/Dockerfile.prod`로 빌드/실행 (환경변수로 DATABASE_URL 지정)
- Frontend: `frontend/Dockerfile.prod`로 빌드/실행 (Nginx 정적 서빙)

간단한 통합 실행 가이드는 `run.md`를 확인하세요.

## 6) 데이터베이스 관리

```powershell
# 시작/중지
docker-compose up -d
docker-compose down

# 로그 확인
docker logs lms_mvp_db_container

# psql 접속
docker exec -it lms_mvp_db_container psql -U lms_user -d lms_mvp_db
```

연결 정보
- 호스트: localhost
- 포트: 15432
- DB: lms_mvp_db
- 사용자: lms_user / 비밀번호: 1234

## 7) 인증/보안 요약

- 세션: httpOnly 쿠키(`access_token`, `refresh_token`), Remember me 시 refresh 30일
- CSRF: 더블 서브밋 쿠키(`csrf_token`) + 헤더(`x-csrf-token`)
- 결과 접근 제어: `/api/v1/results/secure/{submission_id}` 소유자/권한 확인
- CORS: `http://localhost:5173` 등 로컬 개발 도메인 허용, credentials 허용

## 8) 관리자/교사용 기능

- 출제 관리 UI: `/admin/questions` (등록/검색/페이징/택소노미/간단 수정/삭제)
- 교사용 대시보드: `/teacher/dashboard` (주제별 문제 수/정답률, 최근 제출 10건)

## 9) 코딩 테스트 기능 (Phase 7A)

### 9.1 개요
실제 코드를 작성하고 실행할 수 있는 Programmers 스타일의 코딩 테스트 환경을 제공합니다.

### 9.2 주요 기능
- **코드 에디터**: 좌측 문제 설명, 우측 코드 에디터 및 실행 결과
- **언어 지원**: Python, JavaScript, SQL (확장 가능)
- **문제 관리**: 문제 목록, 검색/필터링, 난이도별 분류
- **코드 실행**: 실시간 코드 실행 및 결과 확인
- **보안**: subprocess를 통한 안전한 코드 실행 환경

### 9.3 URL 구조
- `/code` - 샘플 문제로 바로 시작
- `/code/problems` - 문제 목록 페이지
- `/code/:problemId` - 특정 문제 풀이

### 9.4 구현된 컴포넌트
```
frontend/src/
├── components/code/
│   └── CodeExecutionLayout.jsx    # 메인 UI 레이아웃
├── pages/
│   ├── CodeExecutionPage.jsx      # 코드 실행 페이지
│   └── CodeProblemsPage.jsx       # 문제 목록 페이지
└── services/
    └── codeExecutionApi.js        # API 클라이언트

backend/app/
├── api/v1/
│   └── code_execution.py          # REST API 엔드포인트
└── services/
    └── code_execution_service.py  # 코드 실행 엔진
```

### 9.5 API 엔드포인트
- `POST /api/v1/code/execute` - 코드 실행
- `GET /api/v1/code/problems` - 문제 목록 조회
- `GET /api/v1/code/problems/{id}` - 특정 문제 조회
- `POST /api/v1/code/submit` - 코드 제출
- `GET /api/v1/code/languages` - 지원 언어 목록

### 9.6 보안 기능
- subprocess를 통한 격리된 코드 실행
- 실행 시간 제한 (기본 10초)
- 메모리 사용량 제한
- 위험한 모듈 import 차단 (향후 확장)

### 9.7 샘플 문제
현재 5개의 샘플 문제가 포함되어 있습니다:
1. 두 수의 합 (Easy)
2. 리스트 최댓값 찾기 (Easy)  
3. 문자열 뒤집기 (Medium)
4. 피보나치 수열 (Medium)
5. 데이터 분석 - 평균 계산 (Hard)

### 9.8 향후 계획 (Phase 7B)
- Monaco Editor 통합 (VS Code 스타일 에디터)
- Docker 컨테이너 기반 보안 강화
- 테스트 케이스 자동 채점 시스템
- 실시간 코드 힌트 및 오류 분석

## 10) 테스트 계정

- 교사: `test@test.com` / `test`
- 관리자: `admin@admin.com` / `admin`

