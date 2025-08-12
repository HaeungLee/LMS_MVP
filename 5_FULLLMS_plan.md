## Phase 1 Results: 코드베이스 분석

### Codebase Analysis Results
**Relevant Files Found:**
- `backend/app/api/v1/{questions.py, submit.py, dashboard.py}`: 문제 조회/채점/피드백, 대시보드 통계
- `backend/app/services/scoring_service.py`: 0/0.5/1 채점, 템플릿 피드백
- `backend/data/db.json`: 문제은행(JSON)
- `backend/app/core/{config.py, database.py}`: 환경/DB 준비(PSQL 미연동)
- `frontend/src/pages/{QuizPage.jsx, ResultsPage.jsx, DashboardPage.jsx}`: 퀴즈/결과/대시보드
- `frontend/src/components/feedback/FeedbackModal.jsx`: 피드백 폴링
- `frontend/src/stores/quizStore.js`: 상태관리(Zustand)
- `docker-compose.yml`: PostgreSQL 17 컨테이너

**Code Conventions Identified:**
- Naming: Python snake_case, JS camelCase/컴포넌트 PascalCase
- Architecture: 단일 서비스 + Router/Service/Model, JSON 스토리지, 프론트는 Vite/React/Zustand
- Styling: 인라인 스타일 위주(디자인 시스템/MUI 미도입)
- Error handling: FastAPI HTTPException, 프론트 fetch 단순 처리

**현재 “풀 LMS” 관점에서의 공백(핵심):**
- 인증/권한/멀티테넌시 부재(학생/교사/관리자/기관)
- 코스/모듈/레슨/수강/성적표/마감/지각 정책 등 핵심 도메인 미설계
- 평가/퀴즈 시도/문항 분석/그레이드북 없음(현 채점은 단일 제출/요약 분석 수준)
- 관리자 문제 출제/버전관리/워크플로/품질지표 미구현
- AI 피드백 실제 LLM 연동·가드레일·캐싱·비용모니터링 미흡
- 코드 실행 샌드박스(코딩문제) 부재
- 분석/리포팅/학습 경로/개인화는 초기 수준(샘플 데이터)
- 보안/컴플라이언스/로그·감사/백업·DR·가시성(Observability) 체계 미정립
- 확장성/성능(페이지네이션, 인덱싱, 캐시, 큐) 계획 미흡
- 접근성(WCAG)/다국어(i18n)/모바일 대응 전략 미정립
- 통합 표준(LTI/SCORM/xAPI), 외부 연동(SSO/Zoom 등) 미정의
---

## Phase 2 Plan: 구현 로드맵

### Module: Identity & Access (AuthN/AuthZ, 멀티테넌시)
**Summary:** 사용자/기관 단위 권한·데이터 경계를 확립.

**Tasks:**
- [ ] JWT/OIDC 기반 인증, 비밀번호 해시, 세션 보안
- [ ] RBAC(학생/교사/관리자) + 향후 ABAC 확장
- [ ] 멀티테넌시(기관/반/수업) 데이터 경계 설계(스키마/스코핑)

**Acceptance Criteria:**
- [ ] 권한별 API 보호(수강생은 본인 데이터만)
- [ ] 테넌트 경계 침범 0건(테스트 케이스)
- [ ] SSO(OIDC/SAML) 옵션 설계 문서화

### Module: Core Domain Modeling (Course/Module/Lesson/Enrollment/Assignment/Quiz/Attempt)
**Summary:** 학습 도메인 데이터 모델/흐름 정립.

**Tasks:**
- [ ] 코스/모듈/레슨/수강(Enrollment) 스키마
- [ ] 과제/퀴즈/시도(Attempts)/문항/제출/채점/피드백/성적 스키마
- [ ] 마감/지각/재채점/이의제기 정책 모델링

**Acceptance Criteria:**
- [ ] 단일 코스 수강부터 성적 산출까지 E2E 시나리오 통과
- [ ] 시도·문항 단위 리포트/재시도 규칙 동작

### Module: Assessment & Gradebook
**Summary:** 성적 산출/가중치/정책/성적표.

**Tasks:**
- [ ] 가중치 기반 성적 집계(퀴즈/과제/시험)
- [ ] 지각/재제출/최고점 규칙
- [ ] 성적표/Export(CSV)

**Acceptance Criteria:**
- [ ] 그레이드북 합계 오차 0
- [ ] 내보내기 파일 사양 합의·테스트

### Module: Question Bank & Authoring
**Summary:** 출제자용 CRUD·버전관리·워크플로·품질지표.

**Tasks:**
- [ ] 문제 CRUD, 태깅/난이도/메타데이터, 버전관리
- [ ] 제출 통계 기반 문항 분석(난이도/변별도), 품질 대시보드
- [ ] 출제 워크플로(작성→검토→승인)

**Acceptance Criteria:**
- [ ] 동일 문항 버전 히스토리/롤백
- [ ] 통계 지표(정답률, 평균 시간) 노출

### Module: AI Feedback Hardening
**Summary:** 2-Agent, 프롬프트/루브릭, 캐시/비용/가드레일.

**Tasks:**
- [ ] 채점 에이전트→검증 에이전트 체인, 루브릭 반영
- [ ] 캐시 키 설계(문항ID+답안해시+루브릭버전), 비용 모니터링
- [ ] 안전 가드(금칙어, 근거 강제, 컨텍스트 누락 방지)

**Acceptance Criteria:**
- [ ] 환각률 ↓ (샘플셋 평가 지표 달성)
- [ ] 동일 요청 캐시 적중률 ≥ 60%

### Module: Code Execution Sandbox (코딩 문제)
**Summary:** 격리된 실행 환경, 테스트케이스 자동 채점.

**Tasks:**
- [ ] 샌드박스/런너(리소스 제한, 타임아웃), 언어별 러너 플릿
- [ ] 테스트케이스/입출력/히든케이스 관리
- [ ] 결과 로그/성능 메트릭 수집

**Acceptance Criteria:**
- [ ] 무한루프/메모리 폭주 차단
- [ ] 채점 결과 재현성 100%

### Module: Analytics & Personalization
**Summary:** 학습 분석/취약영역/추천/리포트.

**Tasks:**
- [ ] 사용자·코스·문항 레벨 메트릭
- [ ] 취약영역 기반 추천(학습 경로)
- [ ] 데이터 웨어하우스/BI 연동(중장기)

**Acceptance Criteria:**
- [ ] 주제별 정답률/시도당 소요시간/경향 노출
- [ ] 추천 적합도 지표 설정

### Module: Content & Media Management
**Summary:** 파일 스토리지/CDN/권한/표준 호환.

**Tasks:**
- [ ] S3 호환 스토리지, 서명 URL, CDN
- [ ] SCORM/xAPI/LTI 임포트(우선순위 결정)

**Acceptance Criteria:**
- [ ] 대용량 업로드/스트리밍 원활
- [ ] 외부 콘텐츠 코스 편성 가능

### Module: Communication & Engagement
**Summary:** 공지/알림/캘린더/토론.

**Tasks:**
- [ ] 이메일·푸시 알림, 일정/마감 리마인더
- [ ] 과목별 공지, 토론/댓글(모더레이션)

**Acceptance Criteria:**
- [ ] 알림 실패율 < 1%, 구독/해제 정책 준수

### Module: Security & Compliance
**Summary:** 데이터 보호/감사/백업/DR/규정 준수.

**Tasks:**
- [ ] PII 암호화, 비밀관리, 감사로그, 접근로그
- [ ] 백업/복구/DR Runbook, 레이트리밋/WAF
- [ ] FERPA/GDPR/CCPA 고려(정책/기능)

**Acceptance Criteria:**
- [ ] 민감정보 유출 테스트 0건
- [ ] 백업 복구 리허설 성공

### Module: Ops, Performance, Observability
**Summary:** CI/CD, IaC, 모니터링, 스케일링.

**Tasks:**
- [ ] IaC(Terraform), 환경 승격(dev/stage/prod)
- [ ] 로그/메트릭/트레이싱, SLO/알람
- [ ] 인덱싱/페이지네이션/캐시/큐(비동기 작업)

**Acceptance Criteria:**
- [ ] p95 API < 300ms(핵심 경로)
- [ ] 장애시 알람/대응 MTTR 목표 달성

### Module: i18n & A11y
**Summary:** 다국어/접근성.

**Tasks:**
- [ ] i18n 프레임워크, RTL 대응
- [ ] WCAG 2.1 AA 준수(키보드/스크린리더)

**Acceptance Criteria:**
- [ ] 핵심 플로우 접근성 자동/수동 테스트 통과

### Module: Billing/Licensing(선택)
**Summary:** 구독/라이선스/결제.

**Tasks:**
- [ ] 요금제/결제/인보이스, 조직 라이선스
- [ ] 사용량 기반 과금(옵션)

**Acceptance Criteria:**
- [ ] 결제 실패/취소/환불 플로우 테스트 통과

---

## Phase 3 Implementation: 실행/검증

**2주 실행 묶음(권장):**
- 주 1: 계약 통일(`/submit` 요청/응답), 결과 화면 정책 일원화, 대시보드 필드 정합성, 타이머 카운트다운, 최소 1개 차트 도입
- 주 2: OpenRouter 1차 연동(+캐시), PostgreSQL로 최소 `submissions` 영속화, 샌드박스 PoC 범위 합의

**검증 게이트:**
- [ ] 스키마·계약 통일로 프론트/백엔드 422/렌더 오류 0
- [ ] 결과·대시보드 지표 실제 데이터 기반
- [ ] LLM 캐시 적중, 에러 폴백, 코스트 모니터링 대시보드
- [ ] DB 영속화 후 재시작/스케일 아웃 시 정합성 유지
- [ ] 알림/접근성/i18n 초기 프레임 마련

**한줄 조언:**
- 지금 단계에서 가장 ROI 높은 일은 “도메인 모델+계약 정합성+AI 연동 안정화+DB 영속화” 네 축입니다. 이 네 가지를 먼저 단단히 해두면, 이후 관리자 출제/분석/개인화/컴플라이언스까지 확장할 때 리스크가 크게 줄어듭니다.


