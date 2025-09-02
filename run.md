# LMS MVP 실행 가이드 (팀원 공유용)

이 문서는 팀원이 새로운 컴퓨터에서 LMS MVP를 처음부터 설정하고 실행하는 방법을 설명합니다.

## 🚀 빠른 시작 (권장)

### 1단계: 저장소 클론 및 환경 설정
```powershell
git clone <repository-url>
cd LMS_MVP

# 환경 변수 파일 생성
Copy-Item env.sample .env
```

### 2단계: Docker로 데이터베이스 시작
```powershell
# PostgreSQL 컨테이너 시작
docker-compose up -d

# 데이터베이스가 준비될 때까지 잠시 대기 (약 10-20초)
timeout /t 20 /nobreak
```

### 3단계: 백엔드 설정 및 데이터베이스 초기화
```powershell
cd backend

# Python 가상환경 생성 및 활성화
python -m venv venv
./venv/Scripts/Activate.ps1

# 패키지 설치
pip install -r requirements.txt

# 🔥 중요: 데이터베이스 마이그레이션 실행 (팀원 필수!)
alembic upgrade head

# 기본 데이터 시드 (반드시 순서대로 실행)
python -m scripts.seed_taxonomy      # 과목/토픽 구조 생성
python -m scripts.seed_admin         # 관리자 계정 생성
python -m scripts.seed_teacher       # 교사 계정 생성
python -m scripts.seed_questions     # 퀴즈 문제 데이터
python -m scripts.seed_curriculum_phase1  # 코딩 테스트 문제

# 백엔드 서버 시작
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4단계: 프론트엔드 실행 (새 터미널)
```powershell
cd frontend
npm install
npm run dev
```

## ✅ 접속 및 테스트

### 기본 접속 정보
- **Web UI**: http://localhost:5174
- **API 문서**: http://localhost:8000/docs
- **관리자 로그인**: admin@example.com / admin123
- **교사 로그인**: teacher@example.com / teacher123

### 🧪 주요 기능 테스트
1. **퀴즈 시스템**: http://localhost:5174/quiz
2. **코딩 테스트**: http://localhost:5174/code/problems
3. **관리자 기능**: http://localhost:5174/admin/questions
4. **동적 과목 관리**: http://localhost:5174/admin/dynamic-subjects

---

## 🔧 고급 설정 (선택사항)

### A. 로컬 개발 모드 (상세 버전)

1) **데이터베이스 컨테이너 관리**
```powershell
# 시작
docker-compose up -d

# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs postgres

# 정지
docker-compose down
```

2) **데이터베이스 상태 확인**
```powershell
cd backend
python check_db.py
```
- ✅ 연결 성공: 테이블 개수와 데이터 요약 표시
- ❌ 연결 실패: Docker 컨테이너 상태 확인 필요

3) **마이그레이션 수동 관리**
```powershell
cd backend

# 현재 마이그레이션 상태 확인
alembic current

# 마이그레이션 히스토리 확인
alembic history

# 특정 버전으로 마이그레이션
alembic upgrade head

# 마이그레이션 초기화 (주의: 데이터 삭제됨!)
alembic downgrade base
alembic upgrade head
```

4) **개별 시드 스크립트 실행**
```powershell
# 기본 구조만 생성
python -m scripts.seed_taxonomy

# 사용자 계정 생성
python -m scripts.seed_admin
python -m scripts.seed_teacher

# 문제 데이터 생성 (선택)
python -m scripts.seed_questions
python -m scripts.seed_curriculum_phase1
```

---

### B. Docker로 백엔드 실행

1) **백엔드 이미지 빌드 및 실행**
```powershell
cd backend

# 이미지 빌드
docker build -f Dockerfile.prod -t lms-backend:latest .

# 실행 (DB는 별도 컨테이너 사용)
docker run --rm -p 8000:8000 ^
  -e DATABASE_URL=postgresql://lms_user:1234@host.docker.internal:15432/lms_mvp_db ^
  --name lms_backend lms-backend:latest
```

---

### C. 프론트엔드 Nginx 배포

```powershell
cd frontend

# 프로덕션 빌드 이미지 생성
docker build -f Dockerfile.prod -t lms-frontend:latest .

# 실행
docker run --rm -p 8080:80 --name lms_frontend lms-frontend:latest
```
- 접속: http://localhost:8080

---

### D. 전체 스택 Docker Compose

```powershell
# 전체 서비스 실행 (Postgres, Redis, Backend, Frontend, 모니터링)
docker compose -f docker-compose.prod.yml --env-file .env up -d --build

# 정지
docker compose -f docker-compose.prod.yml down
```

---

## 🚨 문제 해결 가이드

### 팀원 공유 시 흔한 문제들

#### 1. 데이터베이스 테이블이 없음
```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```
**해결방법:**
```powershell
cd backend
alembic upgrade head
python -m scripts.seed_taxonomy
```

#### 2. 코딩 테스트 문제가 없음
```
빈 문제 목록 또는 "No problems found" 메시지
```
**해결방법:**
```powershell
cd backend
python -m scripts.seed_curriculum_phase1
```

#### 3. 로그인 계정이 없음
**해결방법:**
```powershell
cd backend
python -m scripts.seed_admin
python -m scripts.seed_teacher
```

#### 4. 퀴즈 문제가 없음
**해결방법:**
```powershell
cd backend
python -m scripts.seed_questions
```

#### 5. 데이터베이스 연결 실패
```
psycopg2.OperationalError: could not connect to server
```
**해결방법:**
```powershell
# Docker 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재시작
docker-compose restart postgres

# 포트 확인 (15432가 사용 중인지)
netstat -an | findstr 15432
```

#### 6. PowerShell 실행 정책 오류
```
execution of scripts is disabled on this system
```
**해결방법:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

#### 7. npm 패키지 설치 실패
**해결방법:**
```powershell
# npm 캐시 정리
npm cache clean --force
npm install

# 또는 yarn 사용
yarn install
```

---

## 📋 체크리스트 (팀원용)

새로운 컴퓨터에서 설정할 때 다음을 순서대로 확인하세요:

- [ ] Git 저장소 클론 완료
- [ ] Docker Desktop 설치 및 실행 중
- [ ] Node.js (v16+) 설치 완료
- [ ] Python (3.8+) 설치 완료
- [ ] `.env` 파일 생성 완료
- [ ] `docker-compose up -d` 실행 완료
- [ ] PostgreSQL 컨테이너 정상 동작 확인
- [ ] `alembic upgrade head` 실행 완료
- [ ] 모든 시드 스크립트 실행 완료
- [ ] 백엔드 서버 시작 (포트 8000)
- [ ] 프론트엔드 서버 시작 (포트 5174)
- [ ] 관리자 로그인 테스트 완료
- [ ] 퀴즈 기능 테스트 완료
- [ ] 코딩 테스트 기능 테스트 완료

---

## 🔗 주요 URL 정리

### 로컬 개발
- **메인**: http://localhost:5174
- **API 문서**: http://localhost:8000/docs
- **관리자 패널**: http://localhost:5174/admin/questions

### 기본 계정
- **관리자**: admin@example.com / admin123
- **교사**: teacher@example.com / teacher123

### 주요 기능 페이지
- **대시보드**: http://localhost:5174/
- **퀴즈 선택**: http://localhost:5174/quiz
- **코딩 문제**: http://localhost:5174/code/problems
- **문제 관리**: http://localhost:5174/admin/questions
- **동적 과목**: http://localhost:5174/admin/dynamic-subjects

---

## 💡 팀 협업 팁

1. **환경 통일**: 모든 팀원이 같은 Docker Compose 설정 사용
2. **데이터 공유**: 시드 스크립트로 동일한 기본 데이터 보장
3. **마이그레이션**: 새로운 테이블 변경 시 알림 공유
4. **포트 충돌**: 기본 포트 사용 시 충돌 방지를 위해 사전 확인
