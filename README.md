# LMS MVP 프로젝트 실행 가이드

## 1. 프로젝트 소개

AI 기반 코딩 학습 피드백을 제공하는 LMS(Learning Management System)의 MVP(Minimum Viable Product) 버전입니다. 사용자는 문제를 풀고 AI가 제공하는 피드백을 통해 학습할 수 있습니다.

## 2. 기술 스택

- **백엔드**: FastAPI (Python)
- **프론트엔드**: React (Vite) + Zustand
- **데이터베이스**: PostgreSQL (Docker) + JSON (기존 호환성)
- **상태관리**: Zustand (20명 동시접속 최적화)

## 3. 사전 준비 사항

프로젝트를 실행하기 위해 아래의 프로그램들이 설치되어 있어야 합니다.

- Python (3.8 이상 권장)
- Node.js (18.x 이상 권장) 및 npm
- Docker & Docker Compose

## 4. 실행 절차

### 4.0. PostgreSQL 데이터베이스 시작 (Docker)

1. **PostgreSQL 컨테이너 실행**
   ```bash
   docker-compose up -d
   ```
   
2. **데이터베이스 상태 확인**
   ```bash
   docker ps | findstr lms
   ```
   `healthy` 상태가 표시되면 정상입니다.

### 4.1. 백엔드 서버 실행

1. **환경 변수 설정**
   - 기본값으로 동작합니다. 필요 시 `backend/.env`에 아래 예시로 설정하세요.
   ```env
   DATABASE_URL=postgresql://lms_user:1234@localhost:15432/lms_mvp_db
   JWT_SECRET=dev_secret_change_me
   JWT_EXPIRES_IN_MIN=15
   REFRESH_EXPIRES_IN_DAYS=14
   OPENROUTER_API_KEY=
   ```

2. **의존성 설치 (venv 권장)**
   ```bash
   cd backend
   python -m venv venv
   ./venv/Scripts/pip install -r requirements_new.txt  # Windows
   # 또는: source venv/bin/activate && pip install -r requirements_new.txt
   ```

3. **시드 스크립트 실행(최초 1회)**
   ```bash
   ./venv/Scripts/python -m scripts.seed_taxonomy
   ./venv/Scripts/python -m scripts.seed_teacher
   ./venv/Scripts.python -m scripts.seed_admin
   ```

4. **백엔드 서버 시작**
   ```bash
   ./venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   서버가 정상적으로 실행되면 `http://localhost:8000` 에서 API가 활성화됩니다.### 4.2. 프론트엔드 클라이언트 실행

1.  **의존성 설치**
    새로운 터미널을 열고 `frontend` 디렉토리로 이동한 후, 아래 명령어를 실행하여 Node.js 패키지를 설치합니다.
    ```bash
    cd frontend
    npm install
    ```

2.  **프론트엔드 개발 서버 시작**
    아래 명령어를 실행하여 React 개발 서버를 시작합니다.
    ```bash
    npm run dev
    ```
    서버가 시작되면 브라우저에서 `http://localhost:5173` (또는 `5174`)로 접속합니다.

## 5. 참고 사항

- **실행 순서**: 
  1. Docker PostgreSQL 컨테이너 (`docker-compose up -d`)
  2. 백엔드 서버 (`uvicorn` 명령어)
  3. 프론트엔드 서버 (`npm run dev`)

- **데이터 관리**: 
  - 문제 데이터: `backend/data/db.json` (30개 Python 문제)
  - 사용자 활동: PostgreSQL 데이터베이스 (Docker)
  - 최근 활동: Zustand 상태관리로 실시간 업데이트

- **상태관리**: Zustand를 사용하여 20명 동시접속에 최적화

- **사용자 편의성**:
  - 진행률 바에서 원하는 문제로 즉시 이동 가능
  - 건너뛰기 버튼으로 문제 스킵 후 나중에 돌아올 수 있음
  - 퀴즈 완료 시 자동으로 최근 활동에 기록

- **라우팅(핵심)**
  - `/`: 학생 대시보드
  - `/quiz`: 퀴즈(보호 라우트)
  - `/results/:submission_id`: 결과(보호 + 사전 권한 점검)
  - `/admin/questions`: 출제 관리(교사/관리자)
  - `/teacher/dashboard`: 교사용 대시보드(교사/관리자)

## 6. 데이터베이스 관리

### PostgreSQL 컨테이너 관리
```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 컨테이너 로그 확인
docker logs lms_mvp_db_container

# 데이터베이스 접속
docker exec -it lms_mvp_db_container psql -U lms_user -d lms_mvp_db
```

### 연결 정보
- **호스트**: localhost
- **포트**: 15432 (기본 포트 충돌 방지)
- **데이터베이스**: lms_mvp_db
- **사용자**: lms_user
- **비밀번호**: 1234


## 7. 인증/보안 요약

- 세션: httpOnly 쿠키(`access_token`, `refresh_token`), Remember me ON 시 refresh 30일 유지
- CSRF: 더블 서브밋 쿠키(`csrf_token`) + 헤더(`x-csrf-token`)
  - 프론트에서 POST/PUT/DELETE 시 자동 첨부됨
- 결과 접근 제어: `/api/v1/results/secure/{submission_id}`로 소유자/권한 확인 후 결과 조회
- CORS: `http://localhost:5173`, `http://localhost:5174`, `http://127.0.0.1:5173/5174` 허용, credentials 허용

## 8. 관리자/교사용 기능

- 출제 관리 UI: `/admin/questions`
  - 등록/목록/검색(q)/페이징/토픽 드롭다운(택소노미)/간단 수정/삭제
- 교사용 대시보드: `/teacher/dashboard`
  - 주제별 문제 수/정답률, 최근 제출 10건

## 9. 테스트 계정

- 교사: `test@test.com` / `test`
- 관리자: `admin@admin.com` / `admin`

