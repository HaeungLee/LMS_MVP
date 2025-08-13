### 0813 Phase 2 실행 계획 (Pre-DreamPlan)

## 1) 목표/범위
- 출제 기능 하드닝(교수/원장 리뷰 대비)과 학습 인사이트 v1 제공을 최우선으로 완성
- LLM 가시성/안정성(서킷/메트릭) 강화, 기본 성능(인덱스/캐시) 확보, 테스트/문서화 정비

---

## 2) 작업 목록(체크리스트)

### MUST
- 출제 하드닝(교사용)
  - 정렬/필터 서버-클라이언트 일관화: `sort_by=latest|difficulty_asc|difficulty_desc|topic_asc`
  - 검색/페이지 유지, 저장/삭제 확인, 빈 상태/오류 메시지 표준화
  - 권한/CSRF/레이트리밋 스모크 테스트(401/403/429/422 재현 0)
  - 임포트: dry-run 에러 표시 개선, 대량 처리 시 피드백 근거 표시
- LLM 안정성/가시성
  - 서킷 브레이커/쿼터: 메트릭 기반 상태(open/half-open/closed) 노출
  - 메트릭 대시보드(요약): success율, latency p95, cache_hit, calls_total
  - 헬스 확장: `GET /api/v1/feedback/providers/health`에 메트릭 포함(구현됨)
- 성능/인덱스/캐시
  - 인덱스: `questions(subject, topic)`, `submissions(user_id, submitted_at)`
  - 캐시: 대시보드/학습지표 키(`user_id+subject`), TTL 30s 명세/적용
- 테스트/문서화
  - 유닛: 채점(정규화/유사도) 주요 케이스
  - API: 출제/권한/CSRF/결과 접근 스모크
  - E2E: 로그인→출제→풀이→결과→교사 대시보드
  - README/운영가이드: 쿠키/CSRF/LLM 설정/메트릭 사용법

### SHOULD
- LLM 인사이트 v1(학생)
  - API: `GET /api/v1/student/insights?subject=` → `{ summary, suggestions:[...], deltas:{ score_7d_pct, streak, recent7dAttempts } }`
  - 캐시 TTL 60s, 실패 시 템플릿 폴백
  - 대시보드 카드: "오늘의 인사이트"(요약 2~3문장 + 추천 2개)
- 학생 Assign 스코핑(초안)
  - 스키마: `student_assignments(user_id, subject, topic_key nullable)`
  - API: `GET /api/v1/student/assignments`(본인), 교사용 목록/추가
  - 읽기 경로 필터: 학생 대시보드/질문 조회에서 미할당 숨김

### COULD
- 비용 가드 v1: 사용자/일별 상한 초과 시 저비용 모드(LLM 비활성/캐시-only)
- 교사용 네비 UX 개선(가드/배너/빈 상태)

---

## 3) API/DB 변경 요약
- API
  - 출제 목록: `GET /api/v1/admin/questions?sort_by=`(서버 정렬) — BE 구현됨, FE 연동 필요
  - LLM 헬스: `GET /api/v1/feedback/providers/health`(설정+메트릭) — 구현됨
  - 인사이트: `GET /api/v1/student/insights?subject=` — 신규
  - Assign: `GET /api/v1/student/assignments`(본인) / 교사용 관리 — 신규
- DB (Alembic)
  - 테이블: `student_assignments`
  - 인덱스: `questions(subject, topic)`, `submissions(user_id, submitted_at)`

---

## 4) 수용 기준(AC)
- 출제 하드닝: 교수/원장 리뷰 세션에서 치명적 버그 0, 저장/삭제/검색/정렬/임포트 주요 동선 100% 성공
- 보안/권한: 보호 라우트/CSRF/레이트리밋 스모크 재현 0
- LLM: success율/latency p95 메트릭 노출, 장애 시 템플릿 폴백으로 UX 안정
- 성능: 대시보드/학습지표 p95 20~30% 개선(인덱스+캐시 기준)
- 테스트: 유닛/스모크/E2E 그린, 커버리지 ≥ 80%
- 인사이트: 서버 지표와 요약/추천 일치, 캐시 hit 1s 내, 미캐시 5s 내 폴백 포함 응답

---

## 5) 일정(제안)
- Week 1
  - 출제 하드닝(FE 정렬 연동, UX/오류/임포트 개선)
  - 인덱스/캐시 적용, LLM 메트릭 카드(요약) 노출
  - 유닛/스모크/E2E 기본 세트
- Week 2
  - 학생 Assign 스키마/읽기 적용, 인사이트 API/카드 v1
  - 문서/운영가이드, 리뷰 세션 운영(2~3회) 및 피드백 반영

---

## 6) 리뷰/피드백 루프
- 이해관계자(교수/원장) 리뷰 일정 고정(주 2회), 시나리오 체크리스트 기반 시연
- 이슈 관리(라벨: severity/area), 48h 내 핫픽스 또는 차주 계획 반영
- 주간 리포트: 메트릭(p95, success, 오류), 사용성 피드백, 개선 내역

---

## 7) Done 정의(Pre-DreamPlan)
- 출제 기능이 실제 수업/운영에서 곧장 사용 가능한 품질(치명 버그 0, 성능/보안 기준 충족)
- LLM 인사이트 v1로 "어제의 나 vs 오늘의 나" 가치 제공
- 관측성/운영/문서가 기본 수준을 충족
- 이후 DreamPlan Phase A(2-Agent 루브릭, 샌드박스, 출제 워크플로)로 전환 준비 완료


