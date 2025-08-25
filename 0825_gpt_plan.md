## 0825 GPT Plan — 개인화 문제 풀이 시스템 고도화 계획

### 목표
- 20명 이상의 학생이 동시에 사용해도 안정적으로 동작하면서, 각자의 실력과 커리큘럼에 맞춘 의미 있는 LLM 기반 피드백과 적응형 문제를 제공하는 학습 시스템을 구축한다.
---

### Phase 1: Codebase Analysis Results

**Relevant Files Found:**
- `backend/app/main.py`: FastAPI 앱 구성, 미들웨어(CORS/RateLimit/Logging) 및 라우터 등록
- `backend/app/core/security.py`: JWT/쿠키 기반 인증, `get_current_user`, CSRF 토큰
- `backend/app/api/v1/auth.py`: 회원가입/로그인/토큰 갱신/로그아웃 엔드포인트
- `backend/app/models/orm.py`: SQLAlchemy 모델(사용자/문항/제출/과목·토픽·세팅/그룹·할당 등)
- `backend/app/api/v1/questions.py`: 과목별 문항 로딩(난이도 섞기·셔플)
- `backend/app/api/v1/submit.py`: 제출/채점/피드백 비동기 생성/결과 조회
- `backend/app/api/v1/ai_learning.py`: AI 문제생성·적응형·일일 플랜·품질피드백 등(일부 Fallback)
- `backend/app/api/v1/student.py`: 학생 학습지표 조회(커버리지/약점/진행/활동)
- `backend/app/services/scoring_service.py`: 유형별 채점(객관식/단답/코드완성/디버깅/OX), AI 피드백 생성(LLM/템플릿, 캐시)
- `backend/app/services/ai_question_generator.py`: 문제생성 로직(주제/혼합/적응형), LLM 호출/파싱
- `backend/app/services/curriculum_manager.py`: 진도·개인화 경로/반 전체 개요(일부 TODO/미완)
- `backend/app/services/llm_providers.py`: OpenRouter LLM 프로바이더/메트릭/레이트리밋
- `backend/app/services/llm_cache.py`: In-memory TTL 캐시와 피드백 캐시 키
- `backend/app/middleware/*`: 요청 ID, 레이트리밋, 로깅, 보안 헤더
- `frontend/src/*`: 로그인/퀴즈/결과/대시보드(학생·교사)/상태 관리(Zustand)/API 클라이언트

**Code Conventions Identified:**
- Naming: 파이썬(스네이크), 클래스 파스칼, 프런트(JS/JSX) 카멜/파스칼
- Architecture: FastAPI 레이어드(routers/services/models), LLM/캐시/레이트리밋 분리
- Styling: Pydantic 모델 검증, SQLAlchemy ORM, React + Vite, Zustand 스토어

**Key Dependencies & Patterns:**
- 인증: JWT 액세스/리프레시, httpOnly 쿠키 우선, CSRF 더블 서브밋
- LLM: OpenRouter, 타임아웃/재시도/레이트리밋/메트릭/캐시
- 채점: 문제유형별 규칙 + 의미 유사도(Fuzz), 템플릿 폴백
- 개인화: API 골격은 존재하나(일일 플랜/적응형 등), 개인별 진행·약점·난이도 적응 데이터 파이프라인/스키마는 미구현 상태

---

### Phase 2: Implementation Plan

#### Module: 학습 데이터 수집/모델링(개인화 기반)
**Summary:** 개인화의 근간이 되는 사용자별 진행/정답률/약점 추적 스키마와 수집 파이프라인 구축

**Tasks:**
- [ ] Alembic 마이그레이션: `user_progress`, `user_weaknesses` 테이블 추가
- [ ] 제출 처리 시 개인 지표 업데이트(주제별 총/정답/정확도/최근활동)
- [ ] 약점 추출 로직(오답 패턴/키워드 기반) 및 누적/감가(시간가중)

**Acceptance Criteria:**
- [ ] 제출 후 각 사용자·주제별 정확도/최근활동이 DB에 반영
- [ ] 최근 7일 활동·정확도 기준으로 약점 상위 N개 조회 가능
- [ ] 단일 제출 처리 95p<300ms(채점 제외)로 지표 업데이트

#### Module: 적응형 추천 엔진(문항 선택)
**Summary:** 개인 지표를 바탕으로 적정 난이도/약점 중심 문항을 추천

**Tasks:**
- [ ] `personalization_service` 또는 `curriculum_manager` 확장: 다음 문항 셋 산출
- [ ] 난이도 어댑션 정책(최근 평균점수/정확도 기반) 정의
- [ ] API `GET /api/v1/ai-learning/next-questions` 구현(주제/혼합유형 옵션)

**Acceptance Criteria:**
- [ ] 최근 성과에 따라 난이도 분포가 동적으로 변함
- [ ] 약점 토픽 비중 ≥ 50% 반영(설정 가능)
- [ ] 추천 API 95p<400ms(LLM 미포함, 캐시 사용시)

#### Module: 개인화 AI 피드백(LLM 컨텍스트)
**Summary:** LLM 피드백에 사용자 맥락(과거 오답/약점/목표)을 포함해 질 향상

**Tasks:**
- [ ] 피드백 프롬프트에 사용자 프로필(레벨/약점/반복실수/개선도) 주입
- [ ] 캐시 키 설계: 사용자/문항/유형/정규화답변 기준(중복 방지·품질 보장)
- [ ] 피드백 품질 가드(최소 길이·키워드 포함·톤) 및 폴백 강화

**Acceptance Criteria:**
- [ ] 피드백 본문에 개인화 항목(약점·개선 제안) 최소 1개 이상 포함(샘플 검사 80%+)
- [ ] 95p 응답 지연 < 2.5s(LLM 호출, 캐시 히트시 <300ms)
- [ ] 실패 시 템플릿 폴백으로 UX 저하 최소화

#### Module: 프런트 통합(20명+ 동시 사용성)
**Summary:** 퀴즈 진행 중 개인화 추천/피드백 노출, UX 최적화

**Tasks:**
- [ ] `useQuiz`/`quizStore`에 추천 API 연동(다음 문제 셋 교체)
- [ ] 피드백 UI에 개인화 섹션(약점 요약/다음 학습 제안) 표시
- [ ] 로딩/재시도/부분결과 스트리밍(옵션) UX

**Acceptance Criteria:**
- [ ] 20명 동시 세션에서 UX 저하 없이 다음 문제/피드백 표시
- [ ] 네트워크 실패 시 재시도/오프라인 큐로 유실 방지
- [ ] 주요 사용자행동에 대한 계측 이벤트 송신

#### Module: 교사/운영 대시보드(학급 단위 관찰)
**Summary:** 반/그룹 단위 진행도·약점 분포·활동 현황 가시화

**Tasks:**
- [ ] 집계 API: 반/그룹별 평균 정확도/진도/활동률
- [ ] 위험군(정확도<60%/활동↓) 자동 탐지와 추천 처방
- [ ] UI 차트 통합(기존 대시보드 확장)

**Acceptance Criteria:**
- [ ] 그룹 단위 핵심 KPI 3가지 이상(정확도/진도/활동) 1초 내 로딩
- [ ] 위험군 리스트업 및 일괄 과제 배정 액션 제공

#### Module: 신뢰성/성능/거버넌스
**Summary:** 20+ 동시 사용자 안정성 확보와 모니터링

**Tasks:**
- [ ] 레이트리밋 정책 per-user 세분화 및 모니터링 대시보드
- [ ] LLM 메트릭(지연/실패/캐시 히트) 시각화, 알림
- [ ] 장애 폴백 시나리오(LLM 불가/DB 느림) 점검, 카나리 릴리즈

**Acceptance Criteria:**
- [ ] 서버 오류율 < 1%, LLM 실패 폴백 성공률 > 99%
- [ ] 피크 시간(20~30 동시) 평균 응답 < 600ms(LLM 제외), 타임아웃 < 1%
- [ ] 주요 경로에 대한 로깅/트레이싱 샘플링 적용

---

### Phase 3: Implementation Execution (Gates)
- 구현 시 다음 품질 게이트를 통과해야 함:
  - [ ] 수집·추천·피드백 Acceptance Criteria 충족
  - [ ] 20명 동시 세션에서 응답/에러 SLO 만족
  - [ ] 폴백·로그·메트릭 정상 동작

---

### Milestones (권장 일정)
- D1: 스키마/수집 파이프라인 + 기본 추천 엔진
- D2: 개인화 피드백 프롬프트/캐시 키/가드 + 프런트 통합
- D3: 교사 대시보드 확장 + 모니터링/부하 테스트 + 파일럿(20명)

### Success Metrics & SLO
- 기능: 개인화 추천 반영률 ≥ 50%, 피드백 개인화 항목 포함률 ≥ 80%
- 성능: 추천 API 95p<400ms(LLM 제외), 피드백 95p<2.5s(LLM 포함)
- 안정성: 에러율 < 1%, LLM 폴백 성공률 > 99%

### Risks & Mitigations
- LLM 지연/한도: 캐시·레이트리밋·템플릿 폴백 강화, 사전 워밍
- 데이터 희소성: 최소 시드/부트스트랩 규칙, 보수적 기본값
- 동시성 급증: per-user 레이트리밋, 큐잉/백오프, 관찰성(메트릭·로그)

### Open Questions
- 학습 주제·난이도 정책의 초기 파라미터(교사별 커스터마이즈 범위)
- 피드백 톤/형식(수업 스타일 반영 필요 여부)
- 학생 그룹/할당 운영 정책(자동/수동 혼합 비율)


