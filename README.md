# LMS MVP - AI 기반 개인화 학습 플랫폼

## 1) 프로젝트 소개

**AI 기반 개인화 학습 플랫폼**으로, 사용자가 원하는 교육 주제에 맞춰 AI가 자동으로 커리큘럼을 생성하고, 맞춤형 교재와 문제를 제공하는 종합 LMS(Learning Management System)입니다.

### 핵심 기능
- 🎯 **AI 커리큘럼 생성**: 학습 목표와 수준에 맞는 맞춤형 학습 계획 자동 생성
- 📚 **AI 교재 생성**: 각 학습 단계별 맞춤형 교육 콘텐츠 제공
- ✍️ **스마트 문제 생성**: AI 기반 맞춤형 연습 문제 및 퀴즈 자동 생성
- 🤖 **AI 멘토링**: 실시간 학습 지원 및 피드백 제공
- 📊 **학습 진도 관리**: 체계적인 진도 추적 및 성취도 분석
- 🎓 **복습 시스템**: 간격 반복 학습 기반 효과적인 복습 관리
- 💳 **구독 관리**: 프리미엄 기능을 위한 결제 시스템 통합

## 2) 기술 스택

### 백엔드
- **프레임워크**: FastAPI (Python 3.11+)
- **데이터베이스**: PostgreSQL (Neon 클라우드)
- **캐시/세션**: Redis (Upstash)
- **AI/LLM**: OpenRouter API (Qwen3 Coder)
- **인증**: JWT + httpOnly 쿠키
- **ORM**: SQLAlchemy + Alembic

### 프론트엔드
- **프레임워크**: React 18 + TypeScript
- **빌드 도구**: Vite
- **상태 관리**: TanStack Query (React Query)
- **라우팅**: React Router v6
- **스타일링**: Tailwind CSS
- **UI 컴포넌트**: 커스텀 컴포넌트 + Lucide Icons

### DevOps & 인프라
- **컨테이너**: Docker + Docker Compose
- **모니터링**: Prometheus + Grafana (옵션)
- **배포**: Render / Docker 기반 배포

## 3) 주요 기능 상세

### 3.1 AI 커리큘럼 생성 시스템
- **자동 커리큘럼 생성**: 사용자의 학습 목표, 수준, 가용 시간을 분석하여 최적의 학습 경로 생성
- **다양한 과목 지원**: 프로그래밍, 수학, 과학, 언어 등 다양한 분야
- **진도 기반 학습**: 단계별 학습 진행 및 선수 학습 확인

### 3.2 통합 학습 페이지
- **교재 섹션**: AI가 생성한 맞춤형 학습 콘텐츠
- **퀴즈 섹션**: 이해도 확인을 위한 즉각적인 퀴즈
- **실습 섹션**: 코딩 문제 등 실전 연습
- **AI 멘토**: 학습 중 실시간 질의응답 및 힌트 제공

### 3.3 스마트 문제 생성
- **난이도 자동 조정**: 학습자 수준에 맞는 문제 생성
- **다양한 문제 유형**: 객관식, 주관식, 코딩 문제
- **즉각적인 피드백**: AI 기반 상세한 해설 제공

### 3.4 AI 멘토링 & 상담
- **실시간 채팅**: 학습 중 궁금한 점을 즉시 질문
- **학습 분석**: 강점과 약점 분석 및 개선 방향 제시
- **동기 부여**: 학습 목표 달성을 위한 맞춤형 격려 및 조언

### 3.5 복습 시스템
- **간격 반복 학습**: 과학적으로 검증된 복습 스케줄
- **약점 집중**: 틀린 문제 우선 복습
- **성취도 추적**: 복습 진행률 및 개선도 시각화

### 3.6 학습 분석 대시보드
- **일일 학습 통계**: 학습 시간, 완료한 문제 수, 정답률
- **진도 현황**: 과목별/주제별 진행 상황
- **성취 배지**: 학습 마일스톤 달성 시 보상
- **학습 패턴 분석**: AI 기반 학습 습관 분석

### 3.7 구독 & 결제 시스템
- **무료 플랜**: 기본 학습 기능
- **프리미엄 플랜**: 무제한 AI 멘토링, 고급 분석, 우선 지원
- **결제 통합**: 안전한 결제 처리 및 구독 관리

## 4) 사전 준비물

- Python 3.11 권장 (3.9+ 동작)
- Node.js 18.x + npm
- Docker + Docker Compose

환경 변수 템플릿: 루트의 `env.sample`를 복사해 `.env`를 만듭니다. (필수는 아님)

```text
cp env.sample .env  # Windows PowerShell은 수동 복사 또는 편집기로 생성
```

중요 값 예시(루트 .env 또는 `backend/.env`):

```env
# 데이터베이스 (Neon PostgreSQL)
DATABASE_URL=postgresql://neondb_owner:npg_xxxxx@ep-xxxxx.aws.neon.tech/neondb?sslmode=require

# Redis (Upstash)
UPSTASH_REDIS_REST_URL=https://xxxxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxxxxxxxxx

# JWT 인증
JWT_SECRET=your_secret_key_here
JWT_EXPIRES_IN_MIN=15
REFRESH_EXPIRES_IN_DAYS=14

# OpenRouter API (AI 기능)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
LLM_PROVIDER=openrouter
OPENROUTER_MODEL=qwen/qwen3-coder:free
LLM_ENABLED=true

# AI 기능 설정
AI_QUESTION_GENERATION_ENABLED=true
AI_FEEDBACK_ENABLED=true
```

프론트엔드 환경 변수(frontend/.env):

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 5) 로컬 실행 (개발용, Windows PowerShell)

### 5.0 데이터베이스(컨테이너) 시작

로컬 개발 시 Docker를 사용하거나, 클라우드 데이터베이스(Neon)를 사용할 수 있습니다.

**Docker 사용 시:**
```powershell
docker-compose up -d
docker ps | findstr lms_mvp_db_container
```
`healthy`면 준비 완료입니다. 포트: 15432 → 컨테이너 5432.

**클라우드 DB 사용 시:**
`.env` 파일에 `DATABASE_URL`을 설정하면 별도의 Docker 실행 없이 사용 가능합니다.

### 5.1 백엔드 실행

```powershell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt

# 초기 데이터베이스 마이그레이션 (최초 1회)
alembic upgrade head

# (선택) 초기 데이터 시드
python -m scripts.seed_admin        # 관리자 계정 생성
python -m scripts.seed_taxonomy     # 과목/주제 분류 데이터

# 서버 시작
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API 문서: http://localhost:8000/docs

### 5.2 프론트엔드 실행

### 5.2 프론트엔드 실행

프론트엔드는 React + TypeScript + Vite 구조로 구성되어 있습니다.

```powershell
cd frontend
npm install
npm run dev
```

웹: http://localhost:5173

### 5.3 주요 페이지 구조
- `/` - 랜딩 페이지
- `/login` - 로그인
- `/register` - 회원가입
- `/onboarding` - 초기 설정 (학습 목표, 수준 선택)
- `/dashboard` - 메인 대시보드 (학습 통계, 진도 현황)
- `/learning` - 학습 페이지 (커리큘럼 목록)
- `/learning/:subjectId/:chapterId/:topicId` - 통합 학습 페이지
- `/review` - 복습 관리
- `/ai-assistant` - AI 어시스턴트 (멘토링, 상담)
- `/analytics` - 학습 분석
- `/settings` - 설정 및 구독 관리
- `/pricing` - 요금제 안내

## 6) 운영/패키징 (요약)

## 6) 운영/패키징 (요약)

프로덕션 배포는 Render, AWS, Azure 등 다양한 플랫폼에서 가능합니다.

### 6.1 프로덕션 빌드
```powershell
# 백엔드
cd backend
docker build -f Dockerfile.prod -t lms-backend:prod .

# 프론트엔드
cd frontend
npm run build
docker build -f Dockerfile.prod -t lms-frontend:prod .
```

### 6.2 환경 변수 설정
프로덕션 환경에서는 `.env` 파일 대신 환경 변수를 직접 설정하세요:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`: Redis 연결 정보
- `JWT_SECRET`: 강력한 시크릿 키
- `OPENROUTER_API_KEY`: OpenRouter API 키
- `ENVIRONMENT=production`

### 6.3 Docker Compose
전체 스택 실행:
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

간단한 통합 실행 가이드는 `run.md`를 확인하세요.

## 7) 데이터베이스 관리

## 7) 데이터베이스 관리

### 7.1 로컬 Docker 데이터베이스
```powershell
# 시작/중지
docker-compose up -d
docker-compose down

# 로그 확인
docker logs lms_mvp_db_container

# psql 접속
docker exec -it lms_mvp_db_container psql -U lms_user -d lms_mvp_db
```

연결 정보:
- 호스트: localhost
- 포트: 15432
- DB: lms_mvp_db
- 사용자: lms_user / 비밀번호: 1234

### 7.2 마이그레이션 (Alembic)
```powershell
cd backend

# 새 마이그레이션 생성
alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1
```

## 8) API 엔드포인트 주요 구조

### 8.1 인증 (`/api/v1/auth`)
- `POST /register` - 회원가입
- `POST /login` - 로그인
- `POST /logout` - 로그아웃
- `POST /refresh` - 토큰 갱신

### 8.2 커리큘럼 (`/api/v1/curriculum`, `/api/v1/ai-curriculum`)
- `GET /subjects` - 과목 목록
- `GET /subjects/{id}/chapters` - 챕터 목록
- `POST /ai-curriculum/generate` - AI 커리큘럼 생성
- `GET /progress` - 학습 진도 조회

### 8.3 학습 (`/api/v1/unified-learning`)
- `GET /{topic_id}` - 학습 콘텐츠 조회
- `POST /{topic_id}/textbook/complete` - 교재 완료 처리
- `POST /{topic_id}/quiz/submit` - 퀴즈 제출
- `POST /{topic_id}/practice/submit` - 실습 제출

### 8.4 AI 기능
- `/api/v1/ai-teaching` - AI 교육 세션
- `/api/v1/ai-questions` - AI 문제 생성
- `/api/v1/ai-counseling` - AI 학습 상담
- `/api/v1/ai-features` - AI 피드백 및 분석

### 8.5 복습 (`/api/v1/review-system`)
- `GET /items` - 복습 항목 조회
- `POST /submit` - 복습 제출

### 8.6 결제 (`/api/v1/payment`)
- `POST /create-checkout` - 결제 세션 생성
- `POST /webhook` - 결제 웹훅 처리
- `GET /subscription` - 구독 정보 조회

### 8.7 관리자 (`/api/v1/admin`)
- `GET /users` - 사용자 관리
- `POST /questions` - 문제 관리
- `GET /stats` - 통계 조회

전체 API 문서: http://localhost:8000/docs

## 9) 인증/보안 요약

## 9) 인증/보안 요약

- **세션 관리**: httpOnly 쿠키 기반 (`access_token`, `refresh_token`)
- **CSRF 보호**: 더블 서브밋 쿠키 패턴
- **비밀번호**: bcrypt 해싱
- **JWT**: 15분 액세스 토큰, 14일 리프레시 토큰
- **CORS**: 허용된 도메인에서만 접근 가능
- **Rate Limiting**: API 엔드포인트별 요청 제한
- **보안 헤더**: XSS, Clickjacking 방지

## 10) 프로젝트 구조

### 백엔드 주요 디렉토리
```
backend/
├── app/
│   ├── api/v1/           # API 엔드포인트
│   │   ├── auth.py       # 인증
│   │   ├── curriculum.py # 커리큘럼
│   │   ├── ai_curriculum.py  # AI 커리큘럼 생성
│   │   ├── ai_teaching.py    # AI 교육 세션
│   │   ├── ai_questions.py   # AI 문제 생성
│   │   ├── ai_counseling.py  # AI 상담
│   │   ├── unified_learning.py  # 통합 학습
│   │   ├── review_system.py  # 복습 시스템
│   │   ├── payment.py    # 결제
│   │   └── ...
│   ├── core/            # 핵심 설정
│   ├── models/          # 데이터베이스 모델
│   ├── schemas/         # Pydantic 스키마
│   ├── services/        # 비즈니스 로직
│   └── middleware/      # 미들웨어
├── alembic/            # 데이터베이스 마이그레이션
├── scripts/            # 유틸리티 스크립트
└── tests/              # 테스트

### 프론트엔드 주요 디렉토리
```
frontend/
├── src/
│   ├── features/           # 기능별 모듈
│   │   ├── dashboard/      # 대시보드
│   │   ├── learning/       # 학습 페이지
│   │   ├── unified-learning/  # 통합 학습
│   │   ├── ai-assistant/   # AI 어시스턴트
│   │   ├── review/         # 복습
│   │   ├── payment/        # 결제
│   │   └── ...
│   ├── layouts/           # 레이아웃 컴포넌트
│   ├── pages/             # 페이지 컴포넌트
│   ├── shared/            # 공유 컴포넌트/훅
│   │   ├── components/    # 공통 컴포넌트
│   │   ├── hooks/         # 커스텀 훅
│   │   └── services/      # API 클라이언트
│   └── App.tsx            # 메인 앱
```

## 11) 개발 로드맵 & 히스토리

### 완료된 주요 마일스톤
- ✅ Phase 1-4: 기본 문제 풀이 시스템
- ✅ Phase 5-6: AI 피드백 및 멘토링
- ✅ Phase 7: 코드 실행 엔진
- ✅ Phase 8: 동적 과목 관리
- ✅ Phase 9: AI 커리큘럼 생성 & 교육 세션
- ✅ Phase 10: 스마트 문제 생성 & AI 상담
- ✅ MVP: 통합 학습 시스템, 복습 시스템, 결제 시스템

### 향후 계획
- 🔄 소셜 학습 기능 (스터디 그룹, 리더보드)
- 🔄 모바일 앱 개발
- 🔄 다국어 지원
- 🔄 고급 학습 분석 (예측 모델링)
- 🔄 실시간 화상 과외 연결

자세한 내용은 `FUTURE_ROADMAP.md` 참조

## 12) 테스트

## 12) 테스트

### 12.1 백엔드 테스트
```powershell
cd backend

# 전체 테스트 실행
pytest

# 특정 테스트 실행
pytest tests/test_auth.py
pytest tests/test_curriculum.py

# 커버리지 포함
pytest --cov=app tests/
```

### 12.2 테스트 계정
개발/테스트용 계정:
- **관리자**: `admin@admin.com` / `admin`
- **일반 사용자**: `test@test.com` / `test`

## 13) 문제 해결 (Troubleshooting)

### 13.1 데이터베이스 연결 실패
```powershell
# Docker 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs lms_mvp_db_container

# 재시작
docker-compose restart
```

### 13.2 포트 충돌
- 백엔드(8000): `netstat -ano | findstr :8000`으로 확인 후 프로세스 종료
- 프론트엔드(5173): `vite.config.ts`에서 포트 변경 가능

### 13.3 패키지 설치 오류
```powershell
# Python 의존성 재설치
cd backend
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Node 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 13.4 AI 기능 동작 안 함
- `.env` 파일의 `OPENROUTER_API_KEY` 확인
- `LLM_ENABLED=true` 설정 확인
- API 할당량 확인

## 14) 기여 및 라이선스

### 기여 방법
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 관련 문서
- `DEPLOYMENT_GUIDE.md` - 배포 가이드
- `FUTURE_ROADMAP.md` - 향후 계획
- `run.md` - 빠른 실행 가이드

---

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

**Made with ❤️ for learners**