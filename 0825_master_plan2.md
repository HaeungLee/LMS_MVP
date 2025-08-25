# LMS MVP — 통합 마스터 계획서 (2025-08-25)

## 🚀 **비전: SaaS 개발자 양성 플랫폼**
- **최종 목표**: 초급부터 SaaS 개발자까지 - 개인화된 학습 경로와 AI 피드백으로 실무 역량을 기르는 종합 교육 플랫폼
- **핵심 가치**: 개인화 학습, 실무 중심, AI 피드백, 진로 연계, 무한 확장성

## 목적
- 20명 이상 동시 사용을 견디면서 개인 수준과 진도에 맞춘 LLM 기반 피드백과 적응형 문제를 안정적으로 제공하는 학습 시스템 고도화.
- **SaaS 개발 전체 스택**으로 확장하여 체계적인 커리어 연계 교육 플랫폼 구축.

## 요약(코드베이스 분석 핵심)
- FastAPI 백엔드 + React(Vite) 프런트. LLM 연동은 `llm_providers.py`로 캡슐화되어 있음.
- 인증(JWT/쿠키/CSRF), 채점 서비스(`scoring_service.py`), 문제생성(`ai_question_generator.py`) 등 핵심 모듈 존재.
- 개인화 파이프라인(진도/약점 수집·스키마)은 골격만 있고 구현 부족.
- **현재 제약**: Python 기초만 지원, 하드코딩된 대시보드, 진로 연계 부재
- 현재 단점: 테스트 부족, 일부 보안 설정(과도한 CORS 허용), 인메모리 상태 의존, 동기적 AI 처리, 하드코딩된 프롬프트.

## 핵심 제안 (High-level)
1. **확장 가능한 커리큘럼 아키텍처** 구축 (Category → Track → Module 3단계 구조)
2. 개인화 데이터 파이프라인(스키마 + 수집)을 먼저 설계·마이그레이션한다.
3. 채점/AI 피드백은 비동기 백그라운드 처리로 전환하고 상태를 DB/Redis로 일원화한다.
4. **커리어 경로별 추천 엔진** 및 피드백 프롬프트에 사용자 컨텍스트를 주입한다.
5. 테스트·CI, 보안, 의존성 관리, 모니터링을 우선 도입한다.

---

## 🏗️ **확장 가능한 커리큘럼 아키텍처**

### **핵심 설계 원칙**
- **3단계 계층**: Category → Track → Module 구조로 무한 확장 가능
- **유연한 전제조건**: 모듈 간 동적 의존성 관리
- **업계별 특화**: 같은 기술도 업계별로 다른 접근 (핀테크, 이커머스, 엔터프라이즈)
- **난이도 세분화**: 5단계 (기초 → 전문가 → 마스터)

### **데이터베이스 스키마: 확장 가능한 구조**

```sql
-- 최상위: 커리큘럼 카테고리
CREATE TABLE curriculum_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- 'saas_development', 'react_specialist', 'data_engineering_advanced'
    display_name VARCHAR(100) NOT NULL, -- 'SaaS 개발자', 'React 전문가', '데이터 엔지니어 심화'
    description TEXT,
    target_audience VARCHAR(100), -- 'beginner_to_professional', 'intermediate_specialist'
    estimated_total_months INTEGER DEFAULT 12,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 중간: 학습 트랙 (기존 확장)
ALTER TABLE learning_tracks ADD COLUMN curriculum_category_id INTEGER REFERENCES curriculum_categories(id);
ALTER TABLE learning_tracks ADD COLUMN specialization_level VARCHAR(50) DEFAULT 'general'; 
-- 'general', 'specialist', 'expert', 'master'

-- 하위: 세부 모듈 (최고 세분화)
CREATE TABLE learning_modules (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES learning_tracks(id),
    name VARCHAR(100) NOT NULL, -- 'react_hooks', 'hadoop_basics', 'spark_streaming'
    display_name VARCHAR(100) NOT NULL,
    module_type VARCHAR(50) DEFAULT 'core', -- 'core', 'elective', 'project', 'certification'
    estimated_hours INTEGER DEFAULT 8,
    difficulty_level INTEGER DEFAULT 1, -- 1-5 (5단계로 확장)
    prerequisites TEXT[], -- 다른 모듈 이름들
    tags TEXT[], -- ['frontend', 'state-management', 'hooks']
    industry_focus VARCHAR(100), -- 'general', 'fintech', 'ecommerce', 'enterprise'
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI 참고자료 시스템 (모듈별 연결)
CREATE TABLE learning_resources (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES learning_modules(id),
    track_id INTEGER REFERENCES learning_tracks(id), -- 호환성 유지
    sub_topic VARCHAR(100),
    resource_type VARCHAR(50), -- 'documentation', 'tutorial', 'video', 'project', 'github_template'
    title VARCHAR(200) NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    difficulty_level INTEGER DEFAULT 1,
    industry_focus VARCHAR(100), -- 업계별 특화 자료
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **커리큘럼 예시: 확장성 시연**

#### **1. SaaS 개발자 종합과정 (기본)**
```sql
INSERT INTO curriculum_categories (name, display_name, target_audience, estimated_total_months) VALUES
('saas_development', 'SaaS 개발자 종합과정', 'beginner_to_professional', 18);

-- Foundation Tracks
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('python_basics', 'Python 기초', 1, 'foundation', 'general', 1),
('html_css', 'HTML & CSS', 1, 'foundation', 'general', 1),
('javascript_basics', 'JavaScript 기초', 1, 'foundation', 'general', 1),
('data_structures', '자료구조 & 알고리즘', 1, 'foundation', 'general', 2);

-- Development Tracks
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('react_basics', 'React 기초', 1, 'development', 'general', 2),
('fastapi_backend', 'FastAPI 백엔드', 1, 'development', 'general', 2),
('database_design', '데이터베이스 설계', 1, 'development', 'general', 2);

-- SaaS Specialization Tracks
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('data_analysis', '데이터 분석', 1, 'specialization', 'specialist', 3),
('cloud_deployment', '클라우드 배포', 1, 'specialization', 'specialist', 3);
```

#### **2. React 전문가 과정 (신규 확장)**
```sql
INSERT INTO curriculum_categories (name, display_name, target_audience, estimated_total_months) VALUES
('react_specialist', 'React 개발 전문가', 'intermediate_specialist', 8);

-- React 전문 트랙들
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('react_advanced', 'React 고급', 2, 'specialization', 'specialist', 3),
('react_performance', 'React 성능 최적화', 2, 'specialization', 'expert', 4),
('react_architecture', '대규모 React 아키텍처', 2, 'specialization', 'expert', 4),
('react_ecosystem', 'React 생태계 마스터', 2, 'specialization', 'master', 5);

-- 세부 모듈들
INSERT INTO learning_modules (track_id, name, display_name, module_type, estimated_hours, difficulty_level, prerequisites, tags) VALUES
-- React 고급 트랙 모듈들
(10, 'custom_hooks', 'Custom Hooks 마스터', 'core', 12, 3, ARRAY['react_basics'], ARRAY['react', 'hooks', 'reusability']),
(10, 'context_optimization', 'Context API 최적화', 'core', 10, 3, ARRAY['custom_hooks'], ARRAY['react', 'context', 'performance']),
(10, 'compound_components', 'Compound Components 패턴', 'elective', 8, 4, ARRAY['custom_hooks'], ARRAY['react', 'patterns', 'api-design']);
```

#### **3. 데이터 엔지니어링 심화 (신규 확장)**
```sql
INSERT INTO curriculum_categories (name, display_name, target_audience, estimated_total_months) VALUES
('data_engineering_advanced', '데이터 엔지니어링 심화', 'intermediate_specialist', 12);

-- 데이터 엔지니어링 전문 트랙들
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('hadoop_ecosystem', 'Hadoop 생태계', 3, 'specialization', 'specialist', 4),
('spark_mastery', 'Apache Spark 마스터', 3, 'specialization', 'expert', 4),
('streaming_analytics', '실시간 스트리밍 분석', 3, 'specialization', 'expert', 5),
('mlops_advanced', 'MLOps & 프로덕션 ML', 3, 'specialization', 'master', 5);

-- Hadoop 생태계 모듈들
INSERT INTO learning_modules (track_id, name, display_name, module_type, estimated_hours, difficulty_level, prerequisites, tags, industry_focus) VALUES
(13, 'hdfs_architecture', 'HDFS 아키텍처 & 운영', 'core', 16, 4, ARRAY['data_analysis'], ARRAY['hadoop', 'distributed-systems'], 'enterprise'),
(13, 'mapreduce_optimization', 'MapReduce 최적화', 'core', 20, 4, ARRAY['hdfs_architecture'], ARRAY['hadoop', 'mapreduce'], 'enterprise'),
(13, 'hive_advanced', 'Hive 고급 쿼리 & 튜닝', 'core', 18, 4, ARRAY['mapreduce_optimization'], ARRAY['hadoop', 'hive'], 'enterprise');

-- Spark 마스터 모듈들  
INSERT INTO learning_modules (track_id, name, display_name, module_type, estimated_hours, difficulty_level, prerequisites, tags, industry_focus) VALUES
(14, 'spark_core_advanced', 'Spark Core 심화', 'core', 25, 4, ARRAY['hadoop_ecosystem'], ARRAY['spark', 'rdd'], 'general'),
(14, 'spark_streaming', 'Spark Streaming 실시간 처리', 'core', 25, 5, ARRAY['spark_core_advanced'], ARRAY['spark', 'streaming'], 'fintech'),
(14, 'spark_mllib', 'Spark MLlib 머신러닝', 'core', 30, 5, ARRAY['spark_core_advanced'], ARRAY['spark', 'machine-learning'], 'general');
```

### **동적 커리큘럼 추천 시스템**

```python
class AdvancedCurriculumRecommendationEngine:
    def __init__(self):
        self.career_paths = {
            # 기존 SaaS 개발자
            'saas_fullstack': {
                'curriculum_category': 'saas_development',
                'core_tracks': ['python_basics', 'html_css', 'react_basics', 'fastapi_backend'],
                'specialization_options': ['data_analysis', 'cloud_deployment']
            },
            
            # 신규 React 전문가
            'react_specialist': {
                'curriculum_category': 'react_specialist',
                'prerequisites': ['javascript_basics', 'react_basics'],
                'core_tracks': ['react_advanced', 'react_performance'],
                'specialization_options': ['react_architecture', 'react_ecosystem'],
                'industry_adaptations': {
                    'ecommerce': ['react_performance', 'react_ssr'],
                    'enterprise': ['react_architecture', 'react_testing']
                }
            },
            
            # 신규 데이터 엔지니어
            'data_engineer_advanced': {
                'curriculum_category': 'data_engineering_advanced',
                'prerequisites': ['python_intermediate', 'data_analysis'],
                'core_tracks': ['hadoop_ecosystem', 'spark_mastery'],
                'specialization_options': ['streaming_analytics', 'mlops_advanced'],
                'industry_adaptations': {
                    'fintech': ['streaming_analytics', 'real_time_fraud'],
                    'enterprise': ['hadoop_ecosystem', 'data_governance']
                }
            }
        }
    
    async def recommend_personalized_curriculum(self, user_id: int, career_goal: str, industry: str = 'general') -> Dict:
        # 1. 사용자 현재 스킬 평가
        current_skills = await self.assess_user_skills(user_id)
        
        # 2. 목표 커리큘럼 로드
        target_curriculum = self.career_paths.get(career_goal)
        if not target_curriculum:
            return {'error': 'Unknown career path'}
        
        # 3. 업계별 커스터마이징
        if industry in target_curriculum.get('industry_adaptations', {}):
            specialized_tracks = target_curriculum['industry_adaptations'][industry]
        else:
            specialized_tracks = target_curriculum['specialization_options']
        
        # 4. 개인화된 학습 순서 생성
        learning_path = await self.generate_adaptive_path(
            current_skills, 
            target_curriculum['core_tracks'], 
            specialized_tracks
        )
        
        return {
            'curriculum_category': target_curriculum['curriculum_category'],
            'personalized_path': learning_path,
            'estimated_completion_months': self.calculate_timeline(learning_path),
            'next_milestones': learning_path[:3],  # 다음 3개 마일스톤
            'industry_focus': industry
        }
```

### **무한 확장 예시**

#### **새로운 커리큘럼 추가 (Flutter 모바일 개발)**
```sql
-- 1단계: 카테고리 추가
INSERT INTO curriculum_categories (name, display_name, target_audience) VALUES
('flutter_specialist', 'Flutter 모바일 개발 전문가', 'intermediate_specialist');

-- 2단계: 트랙 추가
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, specialization_level) VALUES
('flutter_basics', 'Flutter 기초', 4, 'general'),
('flutter_advanced', 'Flutter 고급', 4, 'specialist'),
('flutter_native', 'Flutter Native 통합', 4, 'expert');

-- 3단계: 모듈 추가 (자동으로 기존 시스템과 연동)
```

#### **업계별 특화 (핀테크 전문)**
```sql
-- 업계 특화 모듈들
INSERT INTO learning_modules (track_id, name, display_name, industry_focus, tags) VALUES
(14, 'blockchain_integration', '블록체인 연동', 'fintech', ARRAY['blockchain', 'crypto', 'defi']),
(14, 'payment_systems', '결제 시스템 아키텍처', 'fintech', ARRAY['payments', 'security', 'compliance']),
(14, 'fraud_detection_ml', 'ML 기반 사기 탐지', 'fintech', ARRAY['machine-learning', 'fraud', 'real-time']);
```

---

## 통합 구현 계획 (모듈별)

### A. **다중 기술 스택 확장** (확장 가능한 커리큘럼 구조)
목적: Python 중심 → SaaS 개발 전체 스택으로 확장하며 무한 확장 가능한 아키텍처 구축.

작업:
- **확장 가능한 커리큘럼 아키텍처** 구현: Category → Track → Module 3단계 구조
- Alembic 마이그레이션: `curriculum_categories`, `learning_modules` 테이블 추가
- 기존 `learning_tracks` 확장: `curriculum_category_id`, `specialization_level` 추가
- **7개 기술 트랙** 초기 데이터: Foundation(4) + Development(3) + SaaS Specialization(5)
- **3가지 커리어 경로** 정의: 풀스택 개발자, React 전문가, 데이터 엔지니어 심화
- 업계별 특화 모듈 (핀테크, 이커머스, 엔터프라이즈)

Acceptance Criteria:
- 새로운 커리큘럼 카테고리를 기존 시스템 변경 없이 추가 가능
- 모듈 간 동적 전제조건 시스템 동작
- 업계별 특화 모듈 필터링 및 추천 기능
- 5단계 난이도 체계로 전문가 수준까지 지원

### B. **개인화 커리어 경로 추천 엔진** (적응형 문항 선택 확장)
목적: 개인 지표 + 커리어 목표 + 업계 기반으로 맞춤 학습 경로 추천.

작업:
- `AdvancedCurriculumRecommendationEngine` 구현: 커리어별 + 업계별 맞춤 추천
- `curriculum_manager` 확장: 다음 문항 분포 + 커리어 경로 산출 로직
- 난이도 어댑션 정책 정의(최근 평균점수·정확도 기반, 약점 반영 비중 설정 가능)
- API 확장: `GET /api/v1/curriculum/recommend-path`, `GET /api/v1/ai-learning/next-questions`
- **실무 프로젝트 연계**: 트랙별 GitHub 템플릿 프로젝트 추천

Acceptance Criteria:
- 커리어 목표별로 다른 학습 경로 추천 (풀스택 vs React 전문가 vs 데이터 엔지니어)
- 업계별 특화 모듈 우선 추천 (핀테크 → 실시간 스트리밍, 엔터프라이즈 → Hadoop)
- 추천 결과가 최근 성과에 따라 난이도 분포를 변경
- 약점 토픽 비중 기본값 ≥ 50% (설정 가능)
- 추천 API 응답 95p < 400ms (LLM 미포함)

---

### C. 개인화 AI 피드백 (LLM 컨텍스트 포함)
목적: 사용자 맥락을 포함한 고품질 LLM 피드백 제공.

작업:
- 피드백 프롬프트 템플릿 분리(.j2/.txt) 및 사용자 프로필(레벨/약점/반복오답) 주입.
- 캐시 키 설계: (user_id, question_id, answer_hash, feedback_type, normalized_answer).
- 피드백 가드라인(최소 길이·핵심 키워드 포함·톤) 및 템플릿 폴백 구현.

Acceptance Criteria:
- 피드백 본문에 개인화 항목 1개 이상 포함(샘플 검사 80%+).
- LLM 호출 95p 응답 < 2.5s(캐시 히트 시 <300ms).
- 실패 시 템플릿 폴백으로 UX 저하 최소화.

---

### D. 비동기화·상태 관리·인프라
목적: 확장성·신뢰성 확보를 위한 상태 일원화 및 비동기 처리.

작업:
- 채점·AI 분석을 Celery(또는 RQ) + Redis 조합으로 백그라운드화.
- 임시 인메모리 대신 Redis 캐시와 DB 상태(`submission.status`) 사용.
- 레이트리밋 세분화(사용자별) 및 LLM 요청 큐/백오프 정책.

Acceptance Criteria:
- 제출 시 즉시(빠른 규칙 기반) 응답, 상세 AI 분석은 비동기로 진행.
- Redis 도입으로 서버 재시작/수평확장 시 상태 유지.

---

### E. 프런트 통합 및 UX
목적: 추천·피드백을 자연스럽게 노출하고 동시 사용성 확보.

작업:
- `useQuiz`/`quizStore`에 추천 API 연동, 피드백 영역에 개인화 섹션 추가.
- 스트리밍/부분 결과(옵션)와 로딩/재시도 UX 처리.
- 계측 이벤트(다음문제 요청, 피드백 요청·수신 등) 전송.

Acceptance Criteria:
- 20명 동시에서 다음 문제/피드백 UX 저하 없음(간단 부하 테스트 기준).
- 네트워크 실패 시 재시도/오프라인 큐로 유실 방지.

---

### F. 교사/운영 대시보드
목적: 그룹 단위 KPI·약점 분포 가시화 및 위험군 자동 탐지.

작업:
- 집계 API: 그룹별 평균 정확도·진도·활동률 제공.
- 위험군(정확도<60% 등) 자동 탐지 및 일괄 과제 배정 액션.
- 기존 대시보드에 차트 통합.

Acceptance Criteria:
- 그룹 KPI 3개 이상 1초 내 로딩(쿼리·캐시 최적화 필요).
- 위험군 리스트업 및 배정 기능 동작.

---

## 운영, 품질 및 보안 권장사항 (Gemini 제안 통합)
- 테스트: 백엔드 `pytest` 도입, 프런트 `vitest` + React Testing Library 추가. CI(간단 GitHub Actions)로 PR마다 테스트 실행.
- 보안: CORS 허용 헤더 축소(예: `Content-Type`, `Authorization`), 토큰 만료/리프레시 정책 검토, 민감 로그 마스킹.
- 의존성: `requirements.txt`는 패키지 버전 고정(pinning). 프론트는 `package-lock.json` 유지.
- 프롬프트 관리: 프롬프트를 파일 템플릿으로 분리(Jinja2 등)해 운영자가 수정 가능하게 함.
- 채점 고도화: 코드 채점에 AST 기반 비교 도입, 주관식 유사도는 임베딩(Cosine) 병행.
- 관찰성: LLM 메트릭(지연/실패/캐시 히트), 레이트리밋 지표, 오류율 모니터링 + 알림.

---

## 테스트 전략과 CI 계획

### 백엔드 (pytest)
- 스모크: 인증(auth), 제출(submit), 추천(next-questions, 규칙 기반), 피드백 템플릿 폴백 4종
- 서비스 단위: `scoring_service` 유형별 채점, 약점 추출, 토픽별 분석
- API 통합: `test_submit_then_get_results`, `test_feedback_async_polling`
- 커버리지 목표: ≥ 80%

### 프런트 (vitest + React Testing Library)
- 컴포넌트: 문제 카드, 피드백 모달, 진행바 상호작용
- 훅/스토어: `useQuiz` 다음 문제 로딩, 오류/재시도 처리
- 통합: 로그인→퀴즈→제출→피드백 흐름

### CI (GitHub Actions 권장)
- 워크플로우: on PR → 백엔드/프런트 테스트 병렬 실행, 린트, 타입체크, 커버리지 배지 생성
- 캐시: pip/npm 캐시 활용, 평균 2~3분 내 완료 목표

---

## 상태 일원화 설계 (비동기/Redis)

### 상태머신 (Submission)
- states: `pending` → `scoring` → `ai_processing` → `completed` (에러: `failed`)
- 전이 규칙: 제출 수신 시 `pending` 생성 → 규칙 채점 후 `scoring` → 백그라운드 AI 분석 `ai_processing` → 결과 집계 `completed`

### Redis 키 스키마 (예시)
- `sub:{submission_id}:status` → 상태 문자열
- `sub:{submission_id}:result` → 최종 결과 JSON
- `fb:{user_id}:{question_id}:{answer_hash}` → 피드백 본문 캐시
- TTL: 피드백 10분, 상태 24시간, 결과 7일 (설정화)

### 비동기 파이프라인
- Celery + Redis(브로커/백엔드) 또는 RQ 대안
- 재시도/백오프: 지수 백오프, 최대 3회, 타임아웃 가드
- 워커 동시성: 로컬 2~4, 파일럿 4~8, LLM 레이트리밋과 연동

---

## 핵심 API 계약 (초안)

### GET /api/v1/ai-learning/next-questions
- query: `subject`, `count`(default 5)
- resp: `{ questions: [...], rationale: { determined_difficulty, weakness_topics } }`

### POST /api/v1/ai-learning/submit-answer-with-feedback
- body: `{ question_id, answer, question_type, question_data? }`
- resp: `{ score, feedback, question_type, performance_analysis }`

### POST /api/v1/submit
- body: `{ subject, time_taken?, user_answers: [{question_id, user_answer}] }`
- resp: `{ submission_id, total_score, results, topic_analysis, summary, recommendations }`

### GET /api/v1/results/{submission_id}
- resp: `SubmissionResult`

오류 공통 형식:
- `{ error: { code: string, message: string, details?: any } }`

---

## 보안 강화 체크리스트
- CORS: 허용 도메인 화이트리스트, 헤더 명시(`Content-Type`, `Authorization`)
- 인증: 액세스 15m, 리프레시 14d, 토큰 회전, 로그아웃 시 토큰 철회
- CSRF: 더블 서브밋 쿠키 유지, 민감 엔드포인트 검증 강제
- 로깅: PII 마스킹(email 일부), 토큰/키 미로그, 샘플링 비율 10~20%
- 비밀: 환경변수/시크릿 매니저 사용, 저장소 커밋 금지
- 권한: 교사/관리자 엔드포인트 RBAC 확인(테스트 포함)

---

## DB 스키마 상세 (개인화 핵심)

### user_progress
- cols: `id PK`, `user_id FK`, `topic`, `total_questions`, `correct_answers`, `average_score`, `mastery_level`, `last_activity`
- idx: `(user_id, topic)` 유니크, `last_activity` 인덱스
- 규칙: 제출 시 증분 업데이트, `average_score`는 이동평균, `mastery_level`은 구간(basic/intermediate/advanced)

### user_weaknesses
- cols: `id PK`, `user_id FK`, `topic`, `weakness_type`, `error_count`, `last_error`
- idx: `(user_id, topic)`, `(user_id, weakness_type)`
- 규칙: 오답 유형 매칭 시 `error_count` 증가, 7일 단위 감가(예: 0.9^주)

### submission 상태 컬럼
- `status ENUM('pending','scoring','ai_processing','completed','failed')`, `submitted_at`, `completed_at`
- 인덱스: `user_id`, `submitted_at`

### 성능 가이드
- 읽기 많은 통계는 뷰/머티리얼라이즈드 뷰/주기적 집계 고려
- 핵심 쿼리: 최근 7일 활동, 주제별 정확도 TopN/BottomN, 약점 상위 N


---

## Milestones & 일정(권장)
- D1 (초기, ~2w): DB 스키마 + 지표 수집 파이프라인 + 기본 추천 엔진(규칙 기반).
- D2 (~3w): 피드백 프롬프트 템플릿·캐시 키·비동기 파이프라인(Celery) 통합 + 프런트 기본 노출.
- D3 (~2w): 교사 대시보드 확장 + 부하 테스트(20명) + 모니터링 대시보드.

---

## Success Metrics & SLO
- 추천 반영률(개인화 토픽 비중) ≥ 50%.
- 피드백 개인화 포함률 ≥ 80%.
- 추천 API 95p < 400ms(LLM 제외), 피드백 95p < 2.5s(LLM 포함).
- 서버 오류율 < 1%, LLM 폴백 성공률 > 99%.

---

## 위험 및 완화
- LLM 지연/한도: 캐시·레이트리밋·템플릿 폴백, 사전 워밍.
- 데이터 희소성: 시드/부트스트랩 규칙, 보수적 기본 추천.
- 동시성 급증: per-user 레이트리밋, 큐잉, 수평 확장.

---

## 우선순위 실행 체크리스트 (권장 순서)
1. DB 스키마(Alembic) 및 `submission.status` 도입 — 필수.
2. Redis 도입 + Celery로 채점/AI 분석 비동기화 — 높은 우선순위.
3. 프롬프트 템플릿 분리 + 캐시 키 전략 — 높은.
4. 추천 API(규칙 기반) 및 `curriculum_manager` 확장 — 높은.
5. 테스트 프레임워크(backend: pytest, frontend: vitest) + CI — 필수.
6. 교사 대시보드와 모니터링(LLM 메트릭) — 중간.

---

## 다음 작업(단계별 권장 실행)
1. (오늘) PRD 확인 후 Alembic 마이그레이션 초안 작성.
2. Redis·Celery 환경 로컬 테스트 구성(간단한 작업 큐 예제).
3. `ai_question_generator` 프롬프트를 템플릿 파일로 분리.
4. 최소한의 단위 테스트 3개(제출 처리, 지표 업데이트, 추천 API) 작성.

---

파일 작성자: 자동 통합 스케치



