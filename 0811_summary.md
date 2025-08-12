### 0811 작업 요약 (진행 상황 및 다음 단계)

## 완료 사항

- 백엔드
  - 토픽 택소노미 스키마 추가: `subjects`, `topics`, `subject_topics`, `subject_settings`
  - 시드 스크립트: `backend/scripts/seed_taxonomy.py` (python_basics 코어 8토픽 + 확장 토픽 functions/classes/exceptions/modules, 설정 포함)
  - 학습 지표 API 신설: `GET /api/v1/student/learning-status?subject=`
    - coverage(가중치 기반), weaknesses(Top3), topic_progress(시도/정답률), streak(골격), recent7dAttempts
  - 대시보드 API 개선: 최근활동 항목에 `submission_id` 포함
  - 제출 API 강화: 익명 제출 금지(인증 사용자 ID 저장)
  - 인증 뼈대 추가
    - 스키마: `users`, `refresh_tokens`
    - 보안 유틸: `app/core/security.py`(bcrypt, JWT, get_current_user, require_role)
    - 엔드포인트(초안): `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`

- 프론트엔드
  - 학생 대시보드 재구성(학생 중심):
    - 상단 진행률 → coverage(%) 기반 게이지
    - "나의 약점 Top 3" 카드(정답률 % 표시, 데이터 부족 시 안내)
    - "토픽별 진행도(시도수)" 차트(수평 막대, 라벨 축약, 툴팁)
    - 과목 선택 필터(초기 `python_basics`)
    - “주제별 문제 현황” 섹션은 교사용으로 이관(학생 메인 비노출)
  - 최근활동 클릭 → `/results/:submission_id` 이동 복원
  - ChartAdapter 개선: 수평 막대/툴팁(`VictoryTooltip`)/축약 라벨 옵션 추가
  - 인증 화면 추가: 로그인(`/login`, Remember me), 회원가입(`/register`)
  - 자동 로그인: 앱 부팅 시 `GET /auth/me` → 실패 시 `POST /auth/refresh` 후 재시도(쿠키 기반 세션)

- 런/검증
  - DB 테이블 생성/시드 적용 완료
  - `GET /api/v1/student/learning-status?subject=python_basics` 응답 확인(정상)
  - 대시보드 페이지에서 coverage/약점/진행도/최근활동 연동 확인

## 현재 제약/이슈

- 인증 라이브러리 미설치로 서버 기동 시 `ModuleNotFoundError: No module named 'jwt'`
  - 필요: `pyjwt`, `bcrypt`를 백엔드 의존성에 추가 설치
  - 일시적으로 인증 라우트 호출 404/미적용 상태였음(재기동 타이밍 + 미설치 영향)

## 다음 단계(0810_plan 1번 목표 계속)

- 필수 의존성 설치 및 서버 재기동
  - backend/requirements_new.txt(or requirements.txt)에 다음을 반영 후 설치: `pyjwt`, `bcrypt`
  - uvicorn 재기동 → 인증 라우트 정상화, `/submit` 인증 가드 활성화

- 인증/RBAC 완성도 향상
  - `POST /api/v1/auth/refresh`, `GET /api/v1/auth/me` 추가(초안 반영, 의존성/쿠키 처리 방식 보완 예정)
  - Refresh 토큰 로테이션/리보크 적용, httpOnly 쿠키 설정 보강(SameSite/secure)
  - `require_role(['teacher'])`로 교사용 엔드포인트 분리: `GET /api/v1/teacher/dashboard/stats`

- 프론트 인증 연동(로그인/회원가입 화면)
  - 로그인/회원가입 UI + 쿠키 기반 세션 처리(보호 라우팅)
  - 자동 로그인(Silent Refresh), 로그아웃 처리

## 테스트 체크리스트(발췌)

- 대시보드
  - 320/768/1024/1440 폭에서 라벨 겹침 0, 초기 로딩 < 800ms(캐시 hit)
  - coverage % 정확, 약점 Top3 최소 시도수 임계치 반영
  - 최근활동 → 결과 이동 및 새로고침/직접 진입 정상

- 인증
  - register/login/logout/refresh/me 흐름 정상, 쿠키 httpOnly 설정
  - 익명 제출 차단: `/submit` 호출 시 인증 필수, DB `submissions.user_id` 저장 확인
  - 학생이 타인 `submission_id` 접근 시 403
  - 프론트: 로그인/회원가입 라우트 연결, Remember me 옵션 UI 제공, 부팅 시 자동 로그인 연동

## 정책 반영(기술적 합의)

- Access TTL: 15분, Refresh TTL: 기본 14일, Remember me ON 시 30일
- Refresh 발급 시 쿠키 max_age 반영, 로테이션/리보크 설계 전제로 진행

## 변경 파일 요약

- 백엔드: `app/models/orm.py`, `app/api/v1/student.py`, `app/api/v1/dashboard.py`, `app/api/v1/submit.py`, `app/api/v1/auth.py`, `app/core/security.py`, `app/main.py`, `scripts/seed_taxonomy.py`
- 프론트: `src/pages/DashboardPage.jsx`, `src/services/apiClient.js`, `src/components/common/charts/ChartAdapter.jsx`

## 실행 메모

- 백엔드: `cd backend; venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
- 프론트: `cd frontend; npm run dev`


