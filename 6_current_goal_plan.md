### 현재 목표 실행 계획

목표: 빠른 시일 내에 문제 출제 및 채점 자동화, 결과를 DB에 저장하는 애플리케이션 생성

#### 범위(Scope)
- 문제 출제: 최소한의 관리용 API(또는 CSV/JSON 임포트)로 문항 CRUD 가능
- 채점 자동화: 객관식/빈칸형의 자동 채점(0/0.5/1), 주관식은 템플릿 피드백 - 오답에 대한 LLM 피드백
- 결과 저장: 제출/문항 단위 결과를 PostgreSQL에 영속 저장
- 최소 대시보드: 최근 시도 수/주제별 정답률 요약(서버 계산값 기반)

#### 아키텍처 요약
- Backend: FastAPI + SQLAlchemy(PostgreSQL), 기존 JSON 문제은행은 초기 병행 허용
- Frontend: 기존 React/Zustand 재사용(관리 UI는 2차선, 우선은 API로 출제 가능)
- DB: Docker PostgreSQL(15432), 테이블: `questions`, `submissions`, `submission_items`, `feedbacks`

#### 데이터 모델(최소)
- questions(id, subject, topic, question_type, stem/code_snippet, correct_answer, difficulty, rubric, created_by, created_at, is_active)
- submissions(id, user_id nullable, subject, total_score, max_score, submitted_at)
- submission_items(id, submission_id, question_id, user_answer, skipped, score, correct_answer, topic)
- feedbacks(id, submission_item_id, feedback_text, ai_generated, created_at)

#### 단계별 실행(2주)

### Phase 0 (D+2): 계약 정합성/핵심 흐름 고정
- [ ] `/submit` 요청/응답 계약 단일화(프론트/백엔드)
- [ ] 결과 표시 경로 일원화(인라인 또는 `/results` 중 택1)
- [ ] 대시보드 필드 미스매치 제거(`username` 등)
- [ ] 타이머 카운트다운 및 만료 처리(자동 제출 또는 확인 모달)

AC:
- [ ] Swagger/Contract 테스트 통과, 제출→결과 플로우 무에러
- [ ] 타이머 만료 UX 동작

### Phase 1 (D+7): DB 영속화 + 최소 시각화
- [ ] PostgreSQL 스키마 생성(위 4개 테이블)
- [ ] `/submit` 시 `submissions`/`submission_items` 저장
- [ ] `/dashboard/stats`가 DB 집계값을 반영(주제별 정답률/최근 시도수)
- [ ] 최소 차트 1종(주제별 정답률 도넛/막대) 도입

AC:
- [ ] 서버 재시작 후 기록 보존, 기본 인덱싱으로 응답 < 500ms
- [ ] 대시보드 차트 정상 렌더, 빈 데이터/에러 처리 포함

### Phase 2 (D+14): 출제 흐름/채점 보강
- [ ] 문제 출제 API(관리용) 제공: POST/PUT/DELETE `/admin/questions`
- [ ] JSON→DB 임포트 스크립트(배치)
- [ ] 정답 매칭 정교화 v1(공백/대소문/토큰 분리/동의어 최소 지원)
- [ ] (선택) OpenRouter 1차 연동 + 캐시(템플릿→LLM 피드백)

AC:
- [ ] 문제 CRUD 정상 동작(권한은 추후 강화), 임포트 성공
- [ ] 오판정률 감소(샘플 20문항 회귀), LLM 연동 시 폴백/타임아웃/캐시 동작

#### 작업 세부(체크리스트)
- Backend
  - [ ] SQLAlchemy 모델/마이그레이션(SQL 파일 또는 Alembic)
  - [ ] `/submit`: 스코어 계산→DB 저장→응답(총점/주제별 분석)
  - [ ] `/dashboard/stats`: DB 집계값 반환(최근 7일 시도수, 주제별)
  - [ ] `/admin/questions`: 기본 검증/페이징(간단)
  - [ ] (선택) `/feedback`: LLM 호출/캐시/폴백
- Frontend
  - [ ] 제출 계약 반영, 결과 화면 단일화
  - [ ] 차트 1종 도입(반응형, 에러/로딩 처리)
  - [ ] 관리자 UI는 2차선(우선은 API/임포트)

#### 리스크/완화
- LLM 비용/지연: 캐시/레이트 리밋/폴백 메시지 준비, 초기엔 템플릿 유지 가능
- DB 마이그레이션: 백업/롤백 스크립트 준비, 트랜잭션/인덱스 점검
- 정답 매칭: 토큰화/트림/케이싱 규칙 명세화 및 테스트 케이스화

#### 성공 지표(KPI)
- [ ] 제출→저장→대시보드 반영까지 평균 < 2초(LLM 제외)
- [ ] 제출 데이터 유실 0건(재시작 후)
- [ ] 대시보드/차트 초기 로딩 < 800ms(캐시 포함)


