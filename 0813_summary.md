### 0813 요약 (Pre-DreamPlan 하드닝 Day)

## 완료 사항
- 계획/문서
  - `0813_plan.md` 작성 및 업데이트(LLM 인사이트 모듈 G 포함)
  - `0813_phase2_plan.md` 생성: DreamPlan 전 완료해야 할 범위/AC/일정 정리

- LLM 관측성/안정성
  - 메트릭 수집기 추가: `calls_total/success_total/failure_total/cache_hit_total/latency_p50/p95`
    - 파일: `backend/app/services/llm_metrics.py`
  - 캐시 hit/호출 성공·실패·지연 기록 연동
    - `backend/app/services/llm_cache.py`(cache hit 증가), `backend/app/services/llm_providers.py`(호출 기록)
  - 헬스 확장: `GET /api/v1/feedback/providers/health`에 메트릭 포함 응답

- 출제 기능 하드닝(정렬 일관화)
  - 서버: `GET /api/v1/admin/questions?sort_by=latest|difficulty_asc|difficulty_desc|topic_asc`
    - 파일: `backend/app/api/v1/admin.py`
  - 프론트: 정렬 드롭다운 값 → API `sort_by` 전달 및 의존성 반영
    - 파일: `frontend/src/pages/AdminQuestions.jsx`, `frontend/src/services/apiClient.js`

- 학습 스코핑/인사이트 v1
  - 스키마: `StudentAssignment` 추가
    - 파일: `backend/app/models/orm.py`
  - 학습 지표: Assign 스코프 반영 및 응답에 `assign.topic_keys` 포함
    - 파일: `backend/app/api/v1/student.py` (`GET /student/learning-status`)
  - 인사이트 API v1: `GET /student/insights?subject=` (요약/추천/델타)
    - 파일: `backend/app/api/v1/student.py`
  - 프론트 클라이언트: `getStudentInsights(subject)` 추가
    - 파일: `frontend/src/services/apiClient.js`

## 검증 포인트
- LLM 헬스: `GET /api/v1/feedback/providers/health` → 설정 + 메트릭 노출 확인
- 출제 정렬: 드롭다운 변경 시 서버 정렬 적용(새로고침 후 URL 상태 일관)
- 학습 지표: Assign 데이터가 있을 경우 해당 토픽만 노출, 응답에 `assign.topic_keys` 확인
- 인사이트: `GET /student/insights` 응답에 summary/suggestions/deltas 존재

## 남은 작업(내일 우선)
- FE 대시보드에 인사이트 카드 v1 렌더(요약 2~3문장 + 추천 2개)
- Assign 관리 API(교사용) 간단 추가 및 시드/테스트
- 교수/원장 리뷰 세션 2~3회 진행(검색/정렬/임포트/권한/CSRF)
- 인덱스 2종 적용 확인(`questions(subject,topic)`, `submissions(user_id,submitted_at)`) 및 p95 체크

## 리스크/메모
- LLM 비용/쿼터: 메트릭 기반 모니터링, 필요 시 서킷 open/저비용 모드로 폴백
- Assign은 과목 단위 스코프부터 적용(사용자별 세분화는 관리 API 추가 후 확장)


