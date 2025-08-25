# 실행 방법 한눈에 보기 (Windows PowerShell 기준)

아래는 가장 흔한 실행 시나리오를 통합한 빠른 참조입니다. 상세 설명은 README.md 참고.

## 0) 준비
- 루트에서 `env.sample`를 참고해 `.env`를 생성(선택)합니다. 최소 값 예시:
  - DATABASE_URL=postgresql://lms_user:1234@localhost:15432/lms_mvp_db
  - VITE_API_BASE_URL=http://localhost:8000

---

## A. 로컬 개발 (가장 간단)

1) DB 컨테이너 기동
```powershell
docker-compose up -d
```

2) 백엔드 (FastAPI)
```powershell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements_new.txt

# (최초 1회) 시드
python -m scripts.seed_taxonomy
python -m scripts.seed_teacher
python -m scripts.seed_admin
# 필요 시: python -m scripts.seed_questions ; python -m scripts.seed_curriculum_phase1

# 서버 시작
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

3) 프론트엔드 (Vite React)
```powershell
cd frontend
npm install
npm run dev
```

- API: http://localhost:8000
- Web: http://localhost:5174

---

## B. Docker로 백엔드만 실행 (DB는 compose 사용)

1) DB 컨테이너 계속 실행 상태 유지

2) 백엔드 이미지 빌드/실행
```powershell
cd backend
# 이미지 빌드 (태그는 예시)
docker build -f Dockerfile.prod -t lms-backend:latest .

# 실행 (DATABASE_URL은 로컬 호스트 기준)
docker run --rm -p 8000:8000 ^
  -e DATABASE_URL=postgresql://lms_user:1234@host.docker.internal:15432/lms_mvp_db ^
  --name lms_backend lms-backend:latest
```

---

## C. 프론트엔드 Nginx 이미지 (정적 호스팅)
```powershell
cd frontend
# 프로덕션 빌드 이미지 생성
docker build -f Dockerfile.prod -t lms-frontend:latest .

# 실행 (80 포트 바인딩)
docker run --rm -p 8080:80 --name lms_frontend lms-frontend:latest
```
- 접속: http://localhost:8080
- API 주소는 빌드/실행 시 Nginx 설정 또는 프론트 env로 맞추세요.

---

## D. 풀스택(확장) docker-compose.prod.yml
`docker-compose.prod.yml`는 Postgres/Redis/Backend/Frontend/NGINX/Prometheus/Grafana까지 포함합니다. 필요한 .env 키들이 많고(예: POSTGRES_*, REDIS_PASSWORD, JWT_SECRET_KEY 등), 일부 로컬 파일(nginx 설정 등) 경로를 맞춰야 합니다.

기본 명령:
```powershell
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```
정지:
```powershell
docker compose -f docker-compose.prod.yml down
```

---

## E. 트러블슈팅 Quick Tips
- DB가 `healthy`가 아니면 백엔드가 자동 테이블 생성 실패할 수 있습니다. 먼저 DB 상태 확인 후 재시작.
- Windows에서 PowerShell 스크립트 실행 정책 문제 시: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (임시)
- 프론트가 백엔드에 접근 못하면 CORS/포트 및 VITE_API_BASE_URL을 확인하세요.
