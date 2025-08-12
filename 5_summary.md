### LMS MVP 상태 요약 및 권고안 (요청 요약)

#### 1) 현재 구현 상태 요약
- **백엔드(FastAPI)**
  - 엔드포인트: `/api/v1/questions/{subject}`, `/api/v1/submit`, `/api/v1/feedback`, `/api/v1/dashboard/stats` 구현.
  - 채점: `ScoringService.score_answer`로 0/0.5/1 점수, `analyze_by_topic` 제공.
  - 피드백: 비동기 요청+폴링 구조(템플릿 기반 피드백, OpenRouter 미연동).
  - 데이터: `backend/data/db.json` JSON 문제은행 사용. PostgreSQL 컨테이너만 준비(실연동 미완).

- **프론트엔드(React + Zustand)**
  - 퀴즈 흐름: 문제 로드 → 답안 입력/건너뛰기 → 확인 모달 → 제출 → 인라인 완료 화면 표시.
  - 피드백: `FeedbackModal`이 `/feedback` 요청 후 폴링하여 표시.
  - 대시보드: 백엔드 통계 + 최근활동(Zustand) 병합 표시. 인라인 스타일 위주, MUI/차트 미도입.

- **인프라**
  - `docker-compose.yml`로 PostgreSQL 17(포트 15432) 기동 준비.

#### 2) 계획(start_plan.md, next_plan.md, ideas_collection.md, 문제개선.md) 대비 미구현/불일치
- **제출 스키마/계약 불일치**
  - 백엔드 `Submission`은 `{ user_answers: [{question_id, user_answer}], subject }` 기대.
  - 프론트는 `{ answers, time_taken }` 형태로 전송하고 있어 422 가능성.

- **결과 표시 흐름 불일치**
  - 문서에는 결과 페이지 이동이 있으나, 현재는 `QuizPage` 내 인라인 완료 화면. `ResultsPage`는 로컬스토리지 의존으로 실제 제출 응답과 흐름이 어긋남.

- **대시보드 데이터 필드 미스매치**
  - 프론트가 `progress.username`을 참조하나, 백엔드 응답에는 해당 필드 없음.

- **피드백 식별자/저장**
  - 프론트가 `feedback_id`를 가정하는 경로 존재하나, 서버는 캐시 키 기반 일시 메모리 저장만 수행(영속 저장/ID 미제공).

- **AI 피드백 실제 연동 미구현**
  - OpenRouter/2-Agent(채점→검증) 미연동, 캐시 최적화/비용 관리 미적용.

- **PostgreSQL 실사용 미완**
  - SQLAlchemy 셋업/스키마 초안만 있음. 문제/제출/피드백은 JSON/메모리 의존.

- **관리자 문제 출제/권한**
  - `문제개선.md`의 관리자 CRUD, 권한(JWT) 등 미구현.

- **UI/시각화**
  - MUI/차트(Recharts/Chart.js) 미도입, 타이머 카운트다운 실구현 없음(정적 표시).

#### 3) 추가되면 좋은 점(우선순위 순)
- **계약 통일/정합성 회복(최우선)**
  - `/submit` 요청/응답 스키마를 프론트·백엔드 간 단일 계약으로 통일.
  - 결과 표시 정책 결정(인라인 vs `/results`) 후 일원화.
  - 대시보드 필드(`username` 등) 제거 또는 서버에서 제공.

- **AI 피드백 연동 + 캐싱**
  - OpenRouter 연동(시간/비용 고려한 캐시), 실패 폴백/재시도 로직 강화.

- **DB 전환(부분부터)**
  - `questions` 조회, `submissions` 기록부터 PostgreSQL 사용으로 전환(점진적).

- **채점/정답 매칭 정교화**
  - 대소문/공백/동의어/다중 정답 지원, 부분점수 기준 명확화.

- **UX 보강**
  - 타이머 카운트다운/자동 제출, 기본 차트 1-2종 도입, 스타일 시스템화(MUI 등).

- **권한/관리자 기능(다음 단계)**
  - JWT 기반 인증, 문제 CRUD, 문제 통계/관리 화면.

#### 4) 문서 간 불일치/의문점
- **제출 페이로드 최종안?**
  - `subject`, `skipped`, `time_taken`을 서버가 저장/분석에 사용하도록 포함할지 결정 필요.

- **결과 화면 정책?**
  - 인라인 완료 화면 유지 vs `/results` 페이지 이동 중 선택 필요.

- **피드백 저장/조회 정책?**
  - 일회성 캐시 키 vs 영속 `feedback_id` 발급/조회 API로 변경 여부.

- **과목/카테고리 체계**
  - `subject=python_basics` 유지 vs 상위 과목/세부분류(문서의 카테고리 설계)로 확장 시점.

#### 5) 즉시 수행 체크리스트(권장)
- [ ] 프론트 `submitAnswer` 페이로드를 서버 스키마에 맞추거나 서버가 현재 페이로드 수용하도록 조정(양쪽 중 하나 선택).
- [ ] 결과 표시 흐름 단일화(인라인 또는 `/results`) 및 저장/라우팅 정리.
- [ ] 대시보드의 `progress.username` 참조 제거 또는 서버 응답에 포함.
- [ ] 피드백 `feedback_id` 의존 제거 또는 서버에서 영속 ID 발급 후 반환.
- [ ] 최소 1개 차트 도입(주제별 정답률), 타이머 카운트다운 구현.
- [ ] OpenRouter 연동 1차 적용(단일 에이전트 + 캐시) 후 2-Agent로 확장.
- [ ] PostgreSQL로 `submissions` 기록 저장 시작(조회/분석 지표 신뢰도 확보).

참고 파일(핵심 위치)
- 백엔드: `backend/app/api/v1/{questions.py, submit.py, dashboard.py}`, `backend/app/services/scoring_service.py`, `backend/data/db.json`
- 프론트: `frontend/src/pages/{QuizPage.jsx, ResultsPage.jsx, DashboardPage.jsx}`, `frontend/src/services/apiClient.js`, `frontend/src/components/feedback/FeedbackModal.jsx`, `frontend/src/stores/quizStore.js`


