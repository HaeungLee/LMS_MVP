### 최종 통합 구현 계획서 (MVP + 확장 로드맵)

본 문서는 `문제개선.md`(문제 출제/LLM 채점/카테고리/시각화), `next_plan.md`(단계별 로드맵), `6_current_goal_plan.md`(현재 목표 2주 실행계획)를 통합/정리한 최종 계획서입니다. `next_plan` 내 문제 DB 확장 파트는 `문제개선.md`의 상세 설계를 공식 대체합니다.

---
## 1) 통합 분석 요약

불필요/중복 정리(반영)
- 문제 DB 확장/카테고리/관리자 출제/LLM 채점/코드 실행 요구사항: `문제개선.md`를 표준으로 채택. `next_plan`의 해당 범위는 중복이므로 삭제/대체.
- 고급 기능(적응형/협업/리포트 자동화): 현 단계 문서에서 언급만 유지, 실제 구현은 DreamPlan로 이동.

정합성 이슈(핵심)
- 제출/응답 계약: 프론트(`answers`) vs 백엔드(`user_answers`, `subject`). 단일화 필요.
- 결과 표시: 인라인 완료 vs `/results` 페이지. 단일 정책 필요.
- 대시보드 필드: `progress.username` 불일치.
- 피드백 식별/보존: `feedback_id` vs 캐시 키(메모리). 영속/정책 필요.

의문/결정 필요(착수 전)
- 결과 화면 정책(인라인/페이지) 선택?
- 피드백 영속화 범위(저장/조회 기간)와 ID 정책?
- 차트 라이브러리(Recharts/Chart.js) 및 UI 프레임워크(MUI) 도입 시점?
- DB 마이그레이션 방식(Alembic vs SQL 스크립트)?

---

## 2) 확정 범위(Scope) — 현재 목표(2주)
- 출제: 최소 API/임포트로 문항 CRUD 가능(관리 UI는 후순위)
- 채점: 객관식/빈칸 자동 채점(0/0.5/1), 주관식은 템플릿→(선택) 오답 LLM 피드백
- 저장: 제출/문항 단위 결과를 PostgreSQL에 영속 저장
- 대시보드: 최근 시도/주제별 정답률(서버 계산 기반) + 차트 1종

---

## 3) 단계별 실행(2주) — 실행 체크리스트/AC

### Phase 0 (D+2): 계약/흐름 고정
- [x] `/submit` 요청/응답 계약 단일화(프론트·백엔드 동시 수정)
- [x] 제출 성공 시 `submission_id` 반환 → 프론트 `/results/:submission_id` 라우팅으로 이동
- [x] `/results/:submission_id` 조회 API(결과+주제별 분석+LLM 요약/조언) 신설
- [x] 대시보드 필드 정합성 수정(`username` 제거/제공)
- [x] 타이머 카운트다운 및 만료 처리(자동 제출 또는 확인)
AC: Contract/E2E 통과, 렌더 오류 0, 타이머 동작

### Phase 1 (D+7): DB 영속화 + 최소 시각화
- [x] PostgreSQL 스키마(아래 4테이블) 생성, 인덱싱
- [x] `/submit` 시 `submissions`/`submission_items` 저장
- [x] `/dashboard/stats` DB 집계 반영(주제별 정답률/최근 시도수)
- [x] 차트 어댑터 레이어 도입 + Victory 기반 최소 1종 차트(도넛/막대)
AC: 재시작 후 기록 보존(확인), 응답 < 500ms(예상, 캐시/인덱스 적용), 차트 정상 렌더(패키지 설치 후 확인)

### Phase 2 (D+14): 출제/채점 보강
- [ ] 문제 출제 API(POST/PUT/DELETE `/admin/questions`) + 임포트 스크립트
- [ ] 정답 매칭 정교화 v1(공백/대소문/토큰·동의어 최소 지원)
- [ ] LLM 피드백 1차 연동 + 캐시(오답 시 안내)
- [ ] 피드백 영구 저장 + 1년 TTL 옵션(배치/아카이빙 스위치) 적용 — 배치 주기: "매 시험(제출) 이후" 트리거
AC: CRUD/임포트 정상, 오판정률 감소, LLM 폴백/타임아웃/캐시 동작

---

## 4) 데이터 모델 v1(최소)
- `questions(id, subject, topic, question_type, stem/code_snippet, correct_answer, difficulty, rubric, created_by, created_at, is_active)`
- `submissions(id, user_id nullable, subject, total_score, max_score, submitted_at)`
- `submission_items(id, submission_id, question_id, user_answer, skipped, score, correct_answer, topic)`
- `feedbacks(id, submission_item_id, feedback_text, ai_generated, created_at)`

---

## 5) API 계약 요약(핵심)
- `GET /api/v1/questions/{subject}`: 쿼리 `shuffle, easy_count, medium_count, hard_count`
- `POST /api/v1/submit`(확정):
  - Req: `{ subject, user_answers: [{ question_id, user_answer, skipped? }] }`
  - Res: `{ submission_id, total_score, max_score, results: [{ question_id, user_answer, correct_answer, score, topic }], topic_analysis }`
- `GET /api/v1/results/{submission_id}`: DB 기반 결과 + 주제별 분석 + LLM 요약/조언 반환
  - Res: `{ submission_id, total_score, max_score, results: [...], topic_analysis, summary, recommendations }`
- `POST /api/v1/feedback`(선택): `{ question_id, user_answer }` → 캐시/ID 반환, 폴링 `GET /feedback/{id}`
- `GET /api/v1/dashboard/stats`: DB 집계값 반환(주제/난이도/최근활동)
- `POST/PUT/DELETE /api/v1/admin/questions`(Phase 2): 기본 검증/페이징

---

## 6) 리스크/완화
- LLM 비용/지연: 캐시·레이트리밋·폴백, 초기 템플릿 허용
- DB 마이그레이션: 백업/롤백 스크립트, 트랜잭션/인덱스 점검
- 정답 매칭: 규칙 명세/테스트케이스화, 회귀 테스트

---

## 7) KPI
- 제출→저장→대시보드 반영 평균 < 2초(LLM 제외)
- 제출 데이터 유실 0건(재시작 후)
- 대시보드 초기 로딩 < 800ms(캐시 포함)

---

## 8) Post-MVP 확장(문제개선.md 기반)
- 관리자 출제 UI(코드 에디터, 미리보기), 버전관리/워크플로
- 2-Agent LLM 채점(루브릭 기반), 코드 실행 샌드박스(언어별 런너)
- 카테고리/학습 경로/시각화 대시보드(히트맵/레이더 등)
- 인증/권한(JWT/RBAC) 및 멀티테넌시, 분석·개인화 추천

---

## 9) 결정 사항(확정)
1. 결과 화면: 제출 성공 시 `submission_id` 수신 → `/results/:submission_id` 라우팅 확정. 서버는 DB 기반 결과/LLM 요약/조언을 반환.
2. 피드백 저장: 기본 영구 저장 + “1년 TTL 토글 가능” 옵션 병행(배치/아카이빙으로 관리).
3. 차트/UI: “차트 어댑터 레이어” 도입, 최초 구현은 Victory 채택.
4. 마이그레이션/운영: Alembic 채택, (옵션) Neon 브랜치 워크플로 사용.

---

## 10) 라우팅 대안 비교(/results/:submission_id) — 채택 근거
- `/results/:submission_id` (채택)
  - 장점: 공유/딥링크 용이, SSR/CSR 모두 대응, 캐싱 키 명확, 확장 시 샤딩/리버스 프록시 경로 기반 라우팅 용이
  - 단점: ID 노출(접근제어 필요), URL 길이 고정 패턴 강제
- `/results?sid=...` (쿼리스트링)
  - 장점: 구현 간단, 동일 기능 가능
  - 단점: 캐시/보안 정책에서 경로 기반보다 덜 선호, 링크 가독성 저하
- `/results` (세션/스토리지 의존)
  - 장점: URL 단순
  - 단점: 새로고침/장치 전환에 취약, 동시접속·확장성/공유 불리
성능/확장: 100 동시접속 기준 CSR 렌더로 충분. 확장 시 CDN 캐싱(비식별 데이터), API 읽기 스케일아웃, N+1 제거/인덱싱으로 선대응.

---

## 11) 운영 가드/추가 제안(권장 반영)
- LLM 가드: `model_version/rubric_version` 저장, 요약/피드백 캐시 키 설계 `(submission_id or question_id + normalized_answer + rubric_version)`
- 멱등성: 제출·피드백 요청에 `client_request_id` 헤더로 중복 처리 방지
- 개인정보/보안: 제출/답안/피드백 본문 로깅 금지, 관리자 API 레이트리밋/WAF
- 관측성: 요청ID/오류 추적, 에러율·p95 응답시간 대시보드, 에러 버짓/SLO 설정
- 데이터 수명: 피드백 TTL 토글 시 배치로 아카이빙/삭제(소프트 삭제 우선)
- 차트 어댑터: Victory 추상화 후 필요 시 Recharts/ECharts로 스왑 가능 API 유지
- 마이그레이션: Alembic 버전 태깅·롤백 스크립트, CI에 마이그 실행/검증 포함


