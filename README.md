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
   프로젝트 최상위 경로에 `backend/.env` 파일이 자동으로 설정되어 있습니다. PostgreSQL 연결 정보가 포함되어 있습니다.

2. **의존성 설치**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **백엔드 서버 시작**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
    서버가 시작되면 브라우저에서 `http://localhost:5173` (또는 터미널에 표시되는 다른 포트 번호)으로 접속하여 애플리케이션을 확인할 수 있습니다.

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

- **라우팅**: 프론트엔드에는 기본적인 페이지 라우팅이 설정되어 있습니다.
  - `/`: 대시보드 페이지
  - `/quiz`: 퀴즈 페이지 (난이도별 문제 설정 가능)
  - `/results`: 결과 페이지

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


