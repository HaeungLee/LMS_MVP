### **LMS MVP 프로젝트 구조**

이 문서는 LMS MVP 프로젝트의 전체 폴더 및 파일 구조를 정의합니다.

```
LMS_MVP/
│
├── .env                # (생성 예정) API 키, DB 접속 정보 등 환경 변수 저장
├── .gitignore          # Git이 추적하지 않을 파일/폴더 목록 (node_modules, .env, __pycache__ 등)
├── MVP_plan.txt        # 초기 기획 아이디어
├── MVP_structure.md    # 현재 이 파일 (프로젝트 구조 정의)
├── start_plan.md       # 최종 확정된 상세 개발 계획서
├── 주관식 채점.txt     # 주관식 채점 관련 리서치
│
├── backend/            # FastAPI 백엔드 서버
│   │
│   ├── app/            # 핵심 애플리케이션 로직
│   │   ├── __init__.py
│   │   ├── main.py     # FastAPI 앱의 메인 엔트리포인트, 라우터 포함
│   │   │
│   │   ├── api/        # API 엔드포인트 (라우터) 관리
│   │   │   ├── __init__.py
│   │   │   └── v1/     # API 버전 1
│   │   │       ├── __init__.py
│   │   │       ├── questions.py  # 문제 관련 API (GET /api/questions/{subject})
│   │   │       └── submit.py     # 답안 제출 및 피드백 관련 API (POST /api/submit, /api/feedback)
│   │   │
│   │   ├── core/       # 설정, 보안 등 핵심 로직
│   │   │   ├── __init__.py
│   │   │   └── config.py     # .env 파일에서 환경 변수를 로드하는 설정
│   │   │
│   │   ├── models/     # Pydantic 데이터 모델 (Request/Response Body 정의)
│   │   │   ├── __init__.py
│   │   │   ├── question.py   # Question 관련 모델
│   │   │   └── submission.py # Submission, Feedback 관련 모델
│   │   │
│   │   └── services/   # 2-Agent 채점 등 비즈니스 로직 처리
│   │       ├── __init__.py
│   │       └── scoring_service.py # 2-Agent 시스템을 호출하고 결과를 처리하는 서비스
│   │
│   ├── data/           # MVP용 데이터 저장소
│   │   └── db.json     # 문제 은행 (Question Bank)
│   │
│   └── requirements.txt  # Python 의존성 목록 (fastapi, uvicorn, python-dotenv 등)
│
└── frontend/           # React 프론트엔드 애플리케이션
    │
    ├── public/         # 정적 파일 (index.html, favicon 등)
    ├── src/
    │   ├── assets/       # 이미지, 폰트, 글로벌 CSS 등
    │   ├── components/   # 재사용 가능한 React 컴포넌트
    │   │   ├── common/     # 버튼, 모달 등 범용 컴포넌트
    │   │   ├── quiz/       # 퀴즈 관련 컴포넌트 (QuestionCard, ProgressBar 등)
    │   │   └── dashboard/  # 대시보드 관련 컴포넌트 (Chart, Summary 등)
    │   │
    │   ├── hooks/        # 커스텀 훅 (예: useQuiz, useTimer)
    │   ├── pages/        # 페이지 단위 컴포넌트 (라우팅 대상)
    │   │   ├── DashboardPage.jsx
    │   │   ├── QuizPage.jsx
    │   │   └── ResultsPage.jsx
    │   │
    │   ├── services/     # 백엔드 API 통신 로직
    │   │   └── apiClient.js  # Axios 또는 Fetch 인스턴스 및 API 호출 함수
    │   │
    │   ├── App.jsx       # 메인 앱 컴포넌트 (라우터 설정)
    │   └── main.jsx      # React 앱 진입점
    │
    ├── .gitignore      # 프론트엔드용 gitignore
    ├── package.json    # Node.js 의존성 및 스크립트 목록
    └── vite.config.js  # (Vite 사용시) Vite 설정 파일

```
