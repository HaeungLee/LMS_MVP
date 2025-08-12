### 0812 작업 요약 (Phase 2 목표 달성)

## 작업 개요
- Phase 0/1 완성 상태에서 Phase 2 핵심(출제/채점 보강, 관리자/교사용 기능, 보안)까지 구현·안착
- 주요 포커스: 출제 CRUD(웹 UI), 채점 정교화, 결과 접근 제어, CSRF, 교사용 대시보드, 택소노미 연동

## 변경 사항 (백엔드)
- 인증/세션/보안
  - Remember me 반영: `login` 시 refresh TTL 30일/14일 설정, 쿠키 `max_age` 반영
  - CSRF(더블 서브밋 쿠키): `csrf_token` 발급/재발급, `require_csrf()`로 POST 보호
  - 결과 접근 제어: `GET /api/v1/results/secure/{submission_id}`(소유자 또는 teacher/admin만 허용)
- 출제/관리 API
  - `admin` 라우트 신설: `GET/POST/PUT/DELETE /api/v1/admin/questions` (권한 가드 + CSRF)
  - 검색/q, 페이징(limit/offset), subject/topic 필터 지원
- 교사용 대시보드/택소노미 API
  - `GET /api/v1/teacher/dashboard/stats`(권한: teacher/admin): 주제별 문제 수/정답률/최근 제출/총 문제
  - `GET /api/v1/taxonomy/topics?subject=`: 토픽 리스트(표시순/코어 여부)
- 채점 정교화(v1)
  - 공백/대소문/구두점 정규화, 간단 동의어 맵, 토큰 무순서 완전일치, 빈칸·단답 부분점수(0.5)
  - LLM 피드백 v1: `OPENROUTER_API_KEY` 있으면 2~3문장 피드백, 없으면 템플릿 폴백

## 변경 사항 (프론트엔드)
- 인증 UX/세션
  - 전역 `authStore` 추가, 네비에서 사용자명/로그아웃 및 역할 기반 메뉴 노출
  - 자동 로그인: refresh 쿠키 있을 때만 `/auth/refresh` 시도(401 노이즈 제거)
- 결과 페이지 보호
  - 결과 조회 전에 `/results/secure/:id` 호출로 권한 확인 → 403/404 시 안내 후 홈 이동
- 출제 관리 UI (게시판 형식)
  - 경로: `/admin/questions` (Protected)
  - 기능: 등록(폼), 목록, 검색(q), 페이징(20개), 토픽 드롭다운(택소노미 연동), 간단 수정(정답), 삭제
- 교사용 대시보드 UI
  - 경로: `/teacher/dashboard` (Protected)
  - 차트: 주제별 문제 수(막대, 수평), 주제별 정답률(%)
  - 테이블: 최근 제출 10건(제출ID/학생ID/과목/시각/점수)
- 공통 네트워킹
  - `fetchWithTimeout` 도입(10s), 변경 메서드에만 CSRF 헤더 자동 첨부
  - CORS 프리플라이트 최소화(READ 메서드에 CSRF 헤더 제거)

## 데이터베이스/시드
- Docker Postgres(15432) 기동 및 스키마/시드 적용
- 택소노미 시드: `python_basics` 코어/확장 토픽 + 설정(min_attempts/min_accuracy)
- 테스트 계정 시드
  - 교사: `test@test.com / test` (role: teacher)
  - 관리자: `admin@admin.com / admin` (role: admin)

## 테스트 시나리오 (발췌)
- 로그인(remember ON) → 새로고침/재시작 시 자동 로그인 유지 확인
- 출제 UI: 등록 → 목록 반영, 검색(q), 페이징 이동, 정답 수정/삭제 동작
- 결과 보호: 타인 `submission_id` 접근 시 403, 본인은 OK
- 교사용 대시보드: 과목 선택 후 차트/최근 제출 정상 표시
- 제출/피드백 POST: CSRF 헤더 자동 첨부로 정상 동작

## 성능/보안/운영 포인트
- 캐시: 대시보드/학습지표 30s 캐시(기본 구조 유지)
- CSRF: 더블 서브밋(쿠키+헤더) 적용, 쿠키 SameSite=Lax
- CORS: `localhost/127.0.0.1:5173/5174` 허용, credentials 허용
- 로깅/관측성: (다음 단계) 요청ID/슬로우쿼리 경고 로그 노출 권장

## 남은 과제(우선순위)
- 출제 UI 고도화: 전체 수정 모달, 난이도/토픽 복합 필터, 과목 확장
- 교사용 대시보드 네비 링크 노출/서브메뉴 구성(역할 기반)
- 결과 페이지: 주제/문항별 상세 UI 강화(정답 해설/연동)
- 레이트리밋(출제/피드백), 요청ID/슬로우쿼리 로그 추가
- (선택) LLM 피드백 캐시/타임아웃/재시도/폴백 정책 고도화

## 오늘의 주요 변경 파일
- 백엔드: `app/api/v1/{auth,admin,submit,results_guard,teacher_dashboard,taxonomy}.py`, `app/core/security.py`, `app/main.py`, `services/scoring_service.py`
- 프론트: `src/pages/{AdminQuestions,TeacherDashboard,ResultsPage}.jsx`, `src/services/{apiClient,taxonomyClient}.js`, `src/stores/authStore.js`, `src/App.jsx`, `src/main.jsx`

## 릴리즈 메모
- Phase 2 핵심 기능(출제/교사용/보안) 완료. 다음 스프린트에서 출제 UI/교사용 대시보드 고도화 및 관측성/레이트리밋을 추가 예정.


