# LMS MVP Master Phase 구현 계획서 (2025-08-25)

## 🎯 **프로젝트 개요**

### **최종 목표**
"20명이 각자 다른 SaaS 개발 커리어 경로로 학습하는 시스템" 구축

### **핵심 비전**
- 초급부터 SaaS 개발자까지 개인화된 학습 경로
- AI 피드백으로 실무 역량 강화
- 무한 확장 가능한 커리큘럼 아키텍처
- 업계별 특화 모듈 (핀테크, 이커머스, 엔터프라이즈)

### **현재 코드베이스 상태**
- **기술 스택**: FastAPI + React(Vite) + PostgreSQL + OpenRouter LLM
- **구현된 기능**: 기본 인증, 문제 출제/채점, AI 피드백 골격
- **제약사항**: Python 기초만 지원, 하드코딩된 대시보드, 개인화 부재
- **완성도**: 약 35% (인프라는 견고하나 핵심 기능 부족)

---
## 📋 **전체 Phase 로드맵**
```
Phase 1 (Week 1-2): 커리큘럼 인프라 구축 → 35% → 50%
Phase 2 (Week 3-4): 개인화 엔진 구축 → 50% → 70%  
Phase 3 (Week 5-6): 확장성 인프라 → 70% → 85%
Phase 4 (Week 7-8): 사용자 경험 완성 → 85% → 95%
```

---
# 🥇 **Phase 1: 커리큘럼 인프라 구축** (Week 1-2)

## **목표**: Python 기초 → SaaS 개발 전체 스택으로 확장

### **Phase 1 상세 작업 계획**

#### **1.1 데이터베이스 스키마 확장 (2일)**

**새 테이블 생성:**
```sql
-- 최상위: 커리큘럼 카테고리
CREATE TABLE curriculum_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- 'saas_development', 'react_specialist'
    display_name VARCHAR(100) NOT NULL, -- 'SaaS 개발자', 'React 전문가'
    description TEXT,
    target_audience VARCHAR(100), -- 'beginner_to_professional'
    estimated_total_months INTEGER DEFAULT 12,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 세부 모듈 (최고 세분화)
CREATE TABLE learning_modules (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES learning_tracks(id),
    name VARCHAR(100) NOT NULL, -- 'react_hooks', 'python_functions'
    display_name VARCHAR(100) NOT NULL,
    module_type VARCHAR(50) DEFAULT 'core', -- 'core', 'elective', 'project'
    estimated_hours INTEGER DEFAULT 8,
    difficulty_level INTEGER DEFAULT 1, -- 1-5 단계
    prerequisites TEXT[], -- 다른 모듈 이름들
    tags TEXT[], -- ['frontend', 'state-management']
    industry_focus VARCHAR(100) DEFAULT 'general', -- 'fintech', 'ecommerce'
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI 참고자료 시스템
CREATE TABLE learning_resources (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES learning_modules(id),
    track_id INTEGER REFERENCES learning_tracks(id),
    sub_topic VARCHAR(100),
    resource_type VARCHAR(50), -- 'documentation', 'tutorial', 'video', 'project'
    title VARCHAR(200) NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    difficulty_level INTEGER DEFAULT 1,
    industry_focus VARCHAR(100) DEFAULT 'general',
    created_at TIMESTAMP DEFAULT NOW()
);
```

**기존 테이블 확장:**
```sql
-- 학습 트랙 확장
ALTER TABLE learning_tracks ADD COLUMN curriculum_category_id INTEGER REFERENCES curriculum_categories(id);
ALTER TABLE learning_tracks ADD COLUMN specialization_level VARCHAR(50) DEFAULT 'general';
-- 'general', 'specialist', 'expert', 'master'
```

**Alembic 마이그레이션 파일:** `backend/alembic/versions/xxxx_add_curriculum_architecture.py`

#### **1.2 커리어 경로 및 트랙 데이터 구축 (3일)**

**3가지 커리어 카테고리:**
```sql
INSERT INTO curriculum_categories (name, display_name, target_audience, estimated_total_months) VALUES
('saas_development', 'SaaS 개발자 종합과정', 'beginner_to_professional', 18),
('react_specialist', 'React 개발 전문가', 'intermediate_specialist', 8),
('data_engineering_advanced', '데이터 엔지니어링 심화', 'intermediate_specialist', 12);
```

**7개 기술 트랙 구성:**

**Foundation Tracks (4개):**
```sql
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('python_basics', 'Python 기초', 1, 'foundation', 'general', 1),
('html_css', 'HTML & CSS', 1, 'foundation', 'general', 1),
('javascript_basics', 'JavaScript 기초', 1, 'foundation', 'general', 1),
('data_structures', '자료구조 & 알고리즘', 1, 'foundation', 'general', 2);
```

**Development Tracks (3개):**
```sql
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('react_basics', 'React 기초', 1, 'development', 'general', 2),
('fastapi_backend', 'FastAPI 백엔드', 1, 'development', 'general', 2),
('database_design', '데이터베이스 설계', 1, 'development', 'general', 2);
```

**SaaS Specialization Tracks (추가 확장용):**
```sql
INSERT INTO learning_tracks (name, display_name, curriculum_category_id, category, specialization_level, difficulty_level) VALUES
('data_analysis', '데이터 분석', 1, 'specialization', 'specialist', 3),
('cloud_deployment', '클라우드 배포', 1, 'specialization', 'specialist', 3);
```

#### **1.3 학습 모듈 상세 정의 (2일)**

**Python 기초 트랙 모듈들:**
```sql
INSERT INTO learning_modules (track_id, name, display_name, module_type, estimated_hours, difficulty_level, prerequisites, tags) VALUES
-- Python 기초 트랙 (track_id = 1로 가정)
(1, 'variables_types', '변수와 자료형', 'core', 4, 1, ARRAY[]::TEXT[], ARRAY['python', 'basics', 'variables']),
(1, 'conditions', '조건문', 'core', 6, 1, ARRAY['variables_types'], ARRAY['python', 'control-flow', 'conditions']),
(1, 'loops', '반복문', 'core', 6, 1, ARRAY['conditions'], ARRAY['python', 'control-flow', 'loops']),
(1, 'functions', '함수', 'core', 8, 2, ARRAY['loops'], ARRAY['python', 'functions', 'scope']),
(1, 'data_structures', '리스트와 딕셔너리', 'core', 8, 2, ARRAY['functions'], ARRAY['python', 'data-structures']),
(1, 'classes', '클래스와 객체', 'core', 10, 3, ARRAY['data_structures'], ARRAY['python', 'oop', 'classes']);
```

**React 기초 트랙 모듈들:**
```sql
INSERT INTO learning_modules (track_id, name, display_name, module_type, estimated_hours, difficulty_level, prerequisites, tags) VALUES
-- React 기초 트랙 (track_id = 5로 가정)
(5, 'jsx_basics', 'JSX 기초', 'core', 6, 2, ARRAY['javascript_basics'], ARRAY['react', 'jsx', 'components']),
(5, 'components_props', '컴포넌트와 Props', 'core', 8, 2, ARRAY['jsx_basics'], ARRAY['react', 'components', 'props']),
(5, 'state_events', 'State와 이벤트', 'core', 8, 2, ARRAY['components_props'], ARRAY['react', 'state', 'events']),
(5, 'hooks_basic', '기본 Hooks', 'core', 10, 3, ARRAY['state_events'], ARRAY['react', 'hooks', 'useState']);
```

#### **1.4 학습 자료 연결 시스템 (2일)**

**참고자료 데이터:**
```sql
INSERT INTO learning_resources (track_id, module_id, sub_topic, resource_type, title, url, description, difficulty_level) VALUES
-- Python 기초 자료
(1, 1, 'variables', 'documentation', 'Python 공식 문서 - 변수', 'https://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator', 'Python 변수와 기본 연산', 1),
(1, 1, 'types', 'tutorial', 'Real Python - Python 데이터 타입', 'https://realpython.com/python-data-types/', '파이썬 기본 데이터 타입 완벽 가이드', 1),

-- React 기초 자료  
(5, 10, 'jsx', 'documentation', 'React 공식 문서 - JSX', 'https://react.dev/learn/writing-markup-with-jsx', 'JSX 문법과 사용법', 2),
(5, 11, 'components', 'tutorial', 'React 컴포넌트 가이드', 'https://react.dev/learn/your-first-component', '첫 React 컴포넌트 만들기', 2);
```

#### **1.5 기본 API 엔드포인트 구현 (3일)**

**새 API 파일:** `backend/app/api/v1/curriculum.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_curriculum_categories(db: Session = Depends(get_db)):
    """커리큘럼 카테고리 목록 조회"""
    # curriculum_categories 테이블 조회 로직
    pass

@router.get("/categories/{category_id}/tracks", response_model=List[Dict[str, Any]])
async def get_category_tracks(category_id: int, db: Session = Depends(get_db)):
    """특정 카테고리의 학습 트랙 조회"""
    # learning_tracks 테이블 조회 로직
    pass

@router.get("/tracks/{track_id}/modules", response_model=List[Dict[str, Any]])
async def get_track_modules(track_id: int, db: Session = Depends(get_db)):
    """특정 트랙의 모듈 조회"""
    # learning_modules 테이블 조회 로직
    pass

@router.get("/recommend-path")
async def recommend_learning_path(
    career_goal: str,
    current_level: str = "beginner",
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """기본 학습 경로 추천 (규칙 기반)"""
    # 간단한 규칙 기반 추천 로직
    pass
```

#### **1.6 ORM 모델 추가**

**파일:** `backend/app/models/orm.py` (기존 파일에 추가)
```python
class CurriculumCategory(Base):
    __tablename__ = "curriculum_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    target_audience = Column(String(100), nullable=True)
    estimated_total_months = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class LearningModule(Base):
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    module_type = Column(String(50), default="core")
    estimated_hours = Column(Integer, default=8)
    difficulty_level = Column(Integer, default=1)
    prerequisites = Column(ARRAY(Text), default=[])
    tags = Column(ARRAY(Text), default=[])
    industry_focus = Column(String(100), default="general")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class LearningResource(Base):
    __tablename__ = "learning_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=True)
    track_id = Column(Integer, ForeignKey("learning_tracks.id"), nullable=False)
    sub_topic = Column(String(100), nullable=True)
    resource_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    difficulty_level = Column(Integer, default=1)
    industry_focus = Column(String(100), default="general")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

### **Phase 1 검증 기준 (Acceptance Criteria)**

#### **✅ 완료 체크리스트**
- [ ] 새로운 커리큘럼 카테고리 추가 시 기존 시스템에 영향 없음
- [ ] 7개 기술 트랙 데이터 완전 로드됨
- [ ] 3가지 커리어 경로 API로 조회 가능
- [ ] 모듈 간 전제조건 시스템 동작 확인
- [ ] 기본 학습 경로 추천 API 응답 (규칙 기반)
- [ ] 업계별 모듈 필터링 기능 동작
- [ ] 5단계 난이도 체계 적용 확인

#### **🧪 테스트 시나리오**
1. **새 카테고리 추가 테스트**: Flutter 모바일 개발 카테고리 추가
2. **경로 추천 테스트**: "saas_development" 목표 시 올바른 트랙 순서 추천
3. **전제조건 테스트**: React Hooks 모듈이 JavaScript 기초 완료 후에만 접근 가능
4. **업계 필터링 테스트**: "fintech" 태그 모듈만 필터링

#### **📊 성능 기준**
- 커리큘럼 카테고리 조회 < 100ms
- 트랙별 모듈 조회 < 200ms  
- 기본 추천 API < 300ms
- DB 마이그레이션 무중단 완료

---
# 🥈 **Phase 2: 개인화 엔진 구축** (Week 3-4)

## **목표**: 사용자 맞춤 추천 및 AI 피드백 개인화

### **Phase 2 상세 작업 계획**

#### **2.1 개인화 데이터 스키마 구축 (2일)**

```sql
-- 사용자별 진도 추적
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    topic VARCHAR(100) NOT NULL,
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    average_score FLOAT DEFAULT 0.0,
    mastery_level VARCHAR(20) DEFAULT 'basic', -- 'basic', 'intermediate', 'advanced'
    last_activity TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, topic)
);

-- 사용자별 약점 추적
CREATE TABLE user_weaknesses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    topic VARCHAR(100) NOT NULL,
    weakness_type VARCHAR(100) NOT NULL, -- 'syntax_error', 'logic_error'
    error_count INTEGER DEFAULT 1,
    last_error TIMESTAMP DEFAULT NOW(),
    decay_factor FLOAT DEFAULT 1.0, -- 시간 가중 감소
    UNIQUE(user_id, topic, weakness_type)
);

-- 트랙별 진도 추적
CREATE TABLE user_track_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    track_id INTEGER REFERENCES learning_tracks(id),
    curriculum_category_id INTEGER REFERENCES curriculum_categories(id),
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    mastery_percentage FLOAT DEFAULT 0.0,
    current_module_id INTEGER REFERENCES learning_modules(id),
    estimated_completion_date DATE,
    career_goal VARCHAR(100), -- 'fullstack', 'react_specialist', 'data_engineer'
    industry_preference VARCHAR(100) DEFAULT 'general',
    started_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, track_id)
);
```

#### **2.2 고급 추천 엔진 구현 (4일)**

**파일:** `backend/app/services/advanced_curriculum_engine.py`
```python
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.orm import User, UserProgress, UserTrackProgress, LearningModule

class AdvancedCurriculumRecommendationEngine:
    def __init__(self):
        self.career_paths = {
            'saas_fullstack': {
                'curriculum_category': 'saas_development',
                'core_tracks': ['python_basics', 'html_css', 'react_basics', 'fastapi_backend'],
                'specialization_options': ['data_analysis', 'cloud_deployment'],
                'industry_adaptations': {
                    'fintech': ['real_time_data', 'security_advanced'],
                    'ecommerce': ['user_analytics', 'recommendation_systems'],
                    'enterprise': ['system_architecture', 'database_optimization']
                }
            },
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
    
    async def recommend_personalized_curriculum(
        self, 
        user_id: int, 
        career_goal: str, 
        industry: str = 'general',
        db: Session = None
    ) -> Dict[str, Any]:
        """개인화된 커리큘럼 추천"""
        
        # 1. 사용자 현재 스킬 평가
        current_skills = await self.assess_user_skills(user_id, db)
        
        # 2. 목표 커리큘럼 로드
        target_curriculum = self.career_paths.get(career_goal)
        if not target_curriculum:
            return {'error': 'Unknown career path'}
        
        # 3. 업계별 커스터마이징
        specialized_tracks = self._get_specialized_tracks(target_curriculum, industry)
        
        # 4. 개인화된 학습 순서 생성
        learning_path = await self.generate_adaptive_path(
            current_skills, 
            target_curriculum['core_tracks'], 
            specialized_tracks,
            db
        )
        
        return {
            'curriculum_category': target_curriculum['curriculum_category'],
            'personalized_path': learning_path,
            'estimated_completion_months': self.calculate_timeline(learning_path),
            'next_milestones': learning_path[:3],
            'industry_focus': industry,
            'weakness_focus_areas': await self.get_user_weaknesses(user_id, db)
        }
    
    async def recommend_next_questions(
        self,
        user_id: int,
        subject: str,
        count: int = 5,
        db: Session = None
    ) -> Dict[str, Any]:
        """개인화된 다음 문제 추천"""
        
        # 1. 사용자 최근 성과 분석
        recent_performance = await self.analyze_recent_performance(user_id, subject, db)
        
        # 2. 약점 영역 식별
        weakness_topics = await self.get_user_weaknesses(user_id, db)
        
        # 3. 난이도 조정
        target_difficulty = self.determine_optimal_difficulty(recent_performance)
        
        # 4. 문제 분포 결정
        question_distribution = {
            'weakness_focused': max(int(count * 0.6), 1),  # 60% 약점 보완
            'review_questions': max(int(count * 0.2), 1),   # 20% 복습
            'challenge_questions': max(int(count * 0.2), 1) # 20% 도전
        }
        
        return {
            'recommended_distribution': question_distribution,
            'target_difficulty': target_difficulty,
            'weakness_topics': weakness_topics[:3],
            'rationale': f"최근 정확도 {recent_performance['accuracy']:.1%} 기반 추천"
        }
    
    async def assess_user_skills(self, user_id: int, db: Session) -> Dict[str, float]:
        """사용자 현재 스킬 레벨 평가"""
        progress_records = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
        
        skills = {}
        for record in progress_records:
            if record.total_questions > 0:
                accuracy = record.correct_answers / record.total_questions
                skills[record.topic] = min(accuracy * record.average_score, 1.0)
        
        return skills
    
    async def get_user_weaknesses(self, user_id: int, db: Session) -> List[str]:
        """사용자 약점 영역 조회 (시간 가중)"""
        week_ago = datetime.now() - timedelta(days=7)
        
        weaknesses = db.query(UserWeaknesses).filter(
            UserWeaknesses.user_id == user_id,
            UserWeaknesses.last_error >= week_ago
        ).order_by(UserWeaknesses.error_count.desc()).limit(5).all()
        
        return [w.topic for w in weaknesses]
```

#### **2.3 AI 피드백 개인화 (3일)**

**프롬프트 템플릿 분리:** `backend/app/templates/feedback/`
```
feedback/
├── personalized_feedback.j2
├── weakness_focused.j2
├── encouragement.j2
└── project_suggestion.j2
```

**파일:** `backend/app/templates/feedback/personalized_feedback.j2`
```jinja2
당신은 {{ career_goal }} 분야의 전문 튜터입니다.

학습자 정보:
- 현재 레벨: {{ current_level }}
- 주요 약점: {{ weaknesses | join(', ') }}
- 최근 성과: {{ recent_accuracy }}% 정확도
- 목표 업계: {{ industry }}

문제: {{ question_text }}
학습자 답안: {{ user_answer }}
정답: {{ correct_answer }}
점수: {{ score }}/1.0

다음 형식으로 개인화된 피드백을 제공하세요:

1. **즉시 피드백**: 이 답안에 대한 구체적 평가
2. **약점 보완**: {{ weaknesses[0] }} 영역 개선 방법
3. **실무 연계**: {{ industry }} 업계에서 이 개념이 사용되는 예시
4. **다음 단계**: 추천 학습 자료 1개

격려하는 톤으로 구체적이고 실용적인 조언을 해주세요.
```

**피드백 서비스 개선:** `backend/app/services/scoring_service.py` (기존 파일 수정)
```python
async def generate_personalized_feedback(
    self, 
    question: Dict, 
    user_answer: str, 
    score: float, 
    user_id: int,
    db: Session
) -> str:
    """개인화된 AI 피드백 생성"""
    
    # 사용자 컨텍스트 수집
    user_progress = await self.get_user_context(user_id, db)
    
    # 템플릿 선택
    template_name = self.select_feedback_template(score, user_progress)
    
    # 프롬프트 생성
    personalized_prompt = self.render_template(template_name, {
        'career_goal': user_progress.get('career_goal', '개발자'),
        'current_level': user_progress.get('level', '초급'),
        'weaknesses': user_progress.get('weaknesses', []),
        'recent_accuracy': user_progress.get('accuracy', 0) * 100,
        'industry': user_progress.get('industry', 'general'),
        'question_text': question.get('code_snippet', ''),
        'user_answer': user_answer,
        'correct_answer': question.get('correct_answer', ''),
        'score': score
    })
    
    # LLM 호출 (캐시 포함)
    cache_key = self.make_personalized_cache_key(user_id, question, user_answer)
    return await self.call_llm_with_cache(personalized_prompt, cache_key)
```

#### **2.4 실무 프로젝트 연계 시스템 (3일)**

**GitHub 템플릿 프로젝트 DB:**
```sql
-- 실무 프로젝트 템플릿
CREATE TABLE project_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    difficulty_level INTEGER NOT NULL, -- 1-5
    track_id INTEGER REFERENCES learning_tracks(id),
    industry_focus VARCHAR(100) DEFAULT 'general',
    github_url TEXT NOT NULL,
    description TEXT,
    technologies TEXT[], -- ['react', 'typescript', 'node']
    estimated_hours INTEGER DEFAULT 20,
    prerequisites TEXT[], -- ['react_basics', 'javascript_basics']
    created_at TIMESTAMP DEFAULT NOW()
);
```

**프로젝트 추천 데이터:**
```sql
INSERT INTO project_templates (name, display_name, difficulty_level, track_id, industry_focus, github_url, technologies, estimated_hours, prerequisites) VALUES
-- React 프로젝트들
('todo_app_react', 'React Todo 앱', 2, 5, 'general', 'https://github.com/templates/react-todo', ARRAY['react', 'css'], 8, ARRAY['react_basics']),
('weather_dashboard', '날씨 대시보드', 3, 5, 'general', 'https://github.com/templates/weather-dashboard', ARRAY['react', 'api', 'charts'], 15, ARRAY['react_basics', 'javascript_apis']),
('ecommerce_frontend', '이커머스 프론트엔드', 4, 5, 'ecommerce', 'https://github.com/templates/ecommerce-react', ARRAY['react', 'redux', 'payment'], 25, ARRAY['react_advanced', 'state_management']),

-- Python 프로젝트들  
('web_scraper', '웹 스크래핑 도구', 2, 1, 'general', 'https://github.com/templates/python-scraper', ARRAY['python', 'requests', 'beautifulsoup'], 10, ARRAY['python_basics']),
('data_analysis_project', '데이터 분석 프로젝트', 3, 8, 'general', 'https://github.com/templates/data-analysis', ARRAY['python', 'pandas', 'matplotlib'], 20, ARRAY['data_analysis']),
('trading_bot', '금융 트레이딩 봇', 5, 8, 'fintech', 'https://github.com/templates/trading-bot', ARRAY['python', 'apis', 'algorithms'], 40, ARRAY['data_analysis', 'algorithms']);
```

### **Phase 2 검증 기준 (Acceptance Criteria)**

#### **✅ 완료 체크리스트**
- [ ] 커리어 목표별로 다른 학습 경로 추천 (풀스택 vs React전문가)
- [ ] 업계별 특화 모듈 우선 추천 (핀테크 → 실시간 스트리밍)
- [ ] 추천 결과가 최근 성과에 따라 난이도 분포 변경
- [ ] 약점 토픽 비중 기본값 ≥ 50% (설정 가능)
- [ ] 피드백 본문에 개인화 항목 1개 이상 포함 (80%+ 샘플)
- [ ] 문제 해결 후 관련 학습 자료 3개 이상 자동 추천
- [ ] 실력별 실무 프로젝트 제안 (초급자: Todo 앱, 중급자: API 연동)

#### **📊 성능 기준**
- 추천 API 응답 95p < 400ms (LLM 미포함)
- LLM 호출 95p 응답 < 2.5s (캐시 히트 시 <300ms)
- 개인화 데이터 업데이트 95p < 300ms

---

# 🥉 **Phase 3: 확장성 인프라** (Week 5-6)

## **목표**: 20명 동시 사용 지원 및 안정성 확보

### **Phase 3 상세 작업 계획**

#### **3.1 Redis + Celery 비동기 파이프라인 (4일)**

**Redis 설정:** `docker-compose.yml` 수정
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

**Celery 설정:** `backend/app/core/celery_app.py`
```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "lms_tasks",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    include=["app.tasks.scoring_tasks", "app.tasks.ai_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    task_routes={
        "app.tasks.scoring_tasks.*": {"queue": "scoring"},
        "app.tasks.ai_tasks.*": {"queue": "ai_processing"}
    }
)
```

**상태 관리 스키마 확장:**
```sql
-- submission 테이블에 상태 컬럼 추가
ALTER TABLE submissions ADD COLUMN status VARCHAR(20) DEFAULT 'pending';
-- 'pending', 'scoring', 'ai_processing', 'completed', 'failed'
ALTER TABLE submissions ADD COLUMN submitted_at TIMESTAMP DEFAULT NOW();
ALTER TABLE submissions ADD COLUMN completed_at TIMESTAMP;

-- 인덱스 추가
CREATE INDEX idx_submissions_status ON submissions(status);
CREATE INDEX idx_submissions_user_submitted ON submissions(user_id, submitted_at);
```

**비동기 태스크:** `backend/app/tasks/scoring_tasks.py`
```python
from celery import current_task
from app.core.celery_app import celery_app
from app.services.scoring_service import scoring_service
from app.core.database import SessionLocal

@celery_app.task(bind=True, max_retries=3)
def process_submission_async(self, submission_id: str, user_answers: list):
    """비동기 제출 처리"""
    try:
        db = SessionLocal()
        
        # 1. 상태 업데이트: scoring
        scoring_service.update_submission_status(submission_id, "scoring", db)
        
        # 2. 즉시 채점 (규칙 기반)
        quick_results = scoring_service.score_answers_fast(user_answers)
        
        # 3. 상태 업데이트: ai_processing  
        scoring_service.update_submission_status(submission_id, "ai_processing", db)
        
        # 4. AI 분석 호출 (별도 태스크)
        ai_analysis_task.delay(submission_id, quick_results)
        
        return {"status": "ai_processing", "quick_score": quick_results["total_score"]}
        
    except Exception as exc:
        # 재시도 로직
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        # 최종 실패
        scoring_service.update_submission_status(submission_id, "failed", db)
        raise exc
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=2)
def ai_analysis_task(self, submission_id: str, quick_results: dict):
    """AI 분석 태스크"""
    try:
        # AI 피드백 생성
        ai_feedback = scoring_service.generate_ai_feedback_batch(quick_results)
        
        # 개인화 추천 생성
        recommendations = scoring_service.generate_recommendations(submission_id)
        
        # 최종 결과 저장
        final_results = {**quick_results, "ai_feedback": ai_feedback, "recommendations": recommendations}
        scoring_service.save_final_results(submission_id, final_results)
        
        # 상태 업데이트: completed
        scoring_service.update_submission_status(submission_id, "completed")
        
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=120)
        scoring_service.update_submission_status(submission_id, "failed")
        raise exc
```

#### **3.2 상태 일원화 및 캐시 전략 (3일)**

**Redis 키 스키마:**
```python
# 상태 관리
SUBMISSION_STATUS_KEY = "sub:{submission_id}:status"
SUBMISSION_RESULT_KEY = "sub:{submission_id}:result"

# 피드백 캐시  
FEEDBACK_KEY = "fb:{user_id}:{question_id}:{answer_hash}"

# 추천 캐시
RECOMMENDATION_KEY = "rec:{user_id}:{career_goal}:{timestamp}"

# 사용자 세션
USER_SESSION_KEY = "session:{user_id}"

# TTL 설정
TTL_FEEDBACK = 600  # 10분
TTL_STATUS = 86400  # 24시간  
TTL_RESULT = 604800  # 7일
```

**캐시 서비스:** `backend/app/services/redis_service.py`
```python
import redis
import json
from typing import Any, Optional
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            decode_responses=True
        )
    
    def set_submission_status(self, submission_id: str, status: str) -> None:
        """제출 상태 설정"""
        key = f"sub:{submission_id}:status"
        self.redis_client.setex(key, 86400, status)  # 24시간
    
    def get_submission_status(self, submission_id: str) -> Optional[str]:
        """제출 상태 조회"""
        key = f"sub:{submission_id}:status"
        return self.redis_client.get(key)
    
    def set_submission_result(self, submission_id: str, result: dict) -> None:
        """제출 결과 저장"""
        key = f"sub:{submission_id}:result"
        self.redis_client.setex(key, 604800, json.dumps(result))  # 7일
    
    def get_submission_result(self, submission_id: str) -> Optional[dict]:
        """제출 결과 조회"""
        key = f"sub:{submission_id}:result"
        result = self.redis_client.get(key)
        return json.loads(result) if result else None

redis_service = RedisService()
```

#### **3.3 레이트리밋 및 LLM 백오프 정책 (2일)**

**사용자별 레이트리밋:** `backend/app/middleware/rate_limit.py` (기존 파일 수정)
```python
from fastapi import HTTPException
import time
from app.services.redis_service import redis_service

class PersonalizedRateLimiter:
    def __init__(self):
        self.limits = {
            'submission': {'requests': 10, 'window': 300},    # 5분에 10회
            'feedback': {'requests': 20, 'window': 300},      # 5분에 20회  
            'ai_generation': {'requests': 5, 'window': 600}   # 10분에 5회
        }
    
    def check_limit(self, user_id: int, action: str) -> bool:
        """사용자별 액션 제한 확인"""
        if action not in self.limits:
            return True
            
        limit_config = self.limits[action]
        key = f"rate_limit:{user_id}:{action}"
        
        current_time = int(time.time())
        window_start = current_time - limit_config['window']
        
        # 슬라이딩 윈도우 구현
        pipe = redis_service.redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, limit_config['window'])
        
        results = pipe.execute()
        current_requests = results[1]
        
        return current_requests < limit_config['requests']

rate_limiter = PersonalizedRateLimiter()
```

**LLM 백오프 정책:** `backend/app/services/llm_rate_limiter.py` (기존 파일 수정)
```python
import asyncio
import random
from typing import Optional

class AdvancedLLMRateLimiter:
    def __init__(self):
        self.request_queue = asyncio.Queue(maxsize=50)
        self.processing = False
        self.failure_count = 0
        self.last_failure_time = 0
        
    async def execute_with_backoff(self, llm_call, max_retries: int = 3) -> Optional[str]:
        """지수 백오프와 함께 LLM 호출"""
        
        for attempt in range(max_retries):
            try:
                # 실패 기반 지연
                if self.failure_count > 0:
                    delay = min(60, 2 ** self.failure_count + random.uniform(0, 1))
                    await asyncio.sleep(delay)
                
                # 큐 기반 처리
                await self.request_queue.put(llm_call)
                result = await self._process_queue_item()
                
                # 성공 시 실패 카운트 리셋
                self.failure_count = 0
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if attempt == max_retries - 1:
                    raise e
                    
                # 재시도 지연
                await asyncio.sleep(2 ** attempt)
        
        return None
```

#### **3.4 로드 밸런싱 및 수평 확장 준비 (2일)**

**환경 설정:** `backend/app/core/config.py` (기존 파일 수정)
```python
class Settings(BaseSettings):
    # 기존 설정들...
    
    # Redis 설정
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # Celery 설정
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # 동시성 설정
    max_concurrent_users: int = 20
    max_concurrent_llm_requests: int = 5
    
    # 성능 튜닝
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    class Config:
        env_file = ".env"
```

**데이터베이스 연결 풀 최적화:** `backend/app/core/database.py` (기존 파일 수정)
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def create_optimized_engine():
    return create_engine(
        settings.database_url,
        poolclass=QueuePool,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,  # 1시간마다 연결 재생성
        echo=False
    )

engine = create_optimized_engine()
```

### **Phase 3 검증 기준 (Acceptance Criteria)**

#### **✅ 완료 체크리스트**
- [ ] 제출 시 즉시(빠른 규칙 기반) 응답, 상세 AI 분석은 비동기 진행
- [ ] Redis 도입으로 서버 재시작/수평확장 시 상태 유지
- [ ] 20명 동시 제출 시 시스템 응답성 유지
- [ ] LLM 요청 실패 시 지수 백오프 정상 동작
- [ ] 사용자별 레이트리밋 정상 동작
- [ ] Celery 워커 장애 시 태스크 재시도 정상 동작

#### **📊 성능 기준**
- 즉시 제출 응답 < 1초
- 20명 동시 사용 시 평균 응답 시간 < 2초
- Redis 캐시 히트율 > 80%
- LLM 요청 성공률 > 95%
- 시스템 가용성 > 99%

---

# 🎨 **Phase 4: 사용자 경험 완성** (Week 7-8)

## **목표**: 완전한 개인화 학습 경험 및 운영 도구

### **Phase 4 상세 작업 계획**

#### **4.1 커리어별 대시보드 차별화 (3일)**

**프론트엔드 컴포넌트:** `frontend/src/components/dashboard/CareerDashboard.jsx`
```jsx
import React, { useEffect, useState } from 'react';
import { getPersonalizedDashboard } from '../../services/apiClient';
import SkillRadarChart from './SkillRadarChart';
import CareerRoadmap from './CareerRoadmap';
import ProjectRecommendations from './ProjectRecommendations';

const CareerDashboard = ({ careerGoal, industry }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPersonalizedData = async () => {
      try {
        const data = await getPersonalizedDashboard(careerGoal, industry);
        setDashboardData(data);
      } catch (error) {
        console.error('Dashboard data fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPersonalizedData();
  }, [careerGoal, industry]);

  if (loading) return <div>로딩 중...</div>;
  if (!dashboardData) return <div>데이터를 불러올 수 없습니다.</div>;

  const { skillMastery, learningPath, recommendations, progress } = dashboardData;

  return (
    <div className="career-dashboard">
      {/* 커리어별 헤더 */}
      <div className="dashboard-header">
        <h1>{getCareerTitle(careerGoal)} 학습 대시보드</h1>
        <div className="career-progress">
          <span>전체 진도: {progress.overall}%</span>
          <span>예상 완료: {progress.estimatedCompletion}</span>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* 스킬 레이더 차트 */}
        <div className="chart-section">
          <h3>기술 숙련도</h3>
          <SkillRadarChart 
            skills={skillMastery} 
            careerGoal={careerGoal}
          />
        </div>

        {/* 커리어 로드맵 */}
        <div className="roadmap-section">
          <h3>학습 경로</h3>
          <CareerRoadmap 
            path={learningPath} 
            currentPosition={progress.currentModule}
            careerGoal={careerGoal}
          />
        </div>

        {/* 개인화된 추천 */}
        <div className="recommendations-section">
          <h3>추천 학습 자료</h3>
          <ProjectRecommendations 
            projects={recommendations.projects}
            resources={recommendations.resources}
            userLevel={progress.currentLevel}
          />
        </div>

        {/* 약점 분석 */}
        <div className="weakness-section">
          <h3>개선 영역</h3>
          <WeaknessAnalysis 
            weaknesses={recommendations.weaknesses}
            industry={industry}
          />
        </div>
      </div>
    </div>
  );
};

const getCareerTitle = (careerGoal) => {
  const titles = {
    'saas_fullstack': 'SaaS 풀스택 개발자',
    'react_specialist': 'React 전문가',
    'data_engineer_advanced': '데이터 엔지니어'
  };
  return titles[careerGoal] || '개발자';
};
```

**스킬 레이더 차트:** `frontend/src/components/dashboard/SkillRadarChart.jsx`
```jsx
import React from 'react';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  Legend
} from 'recharts';

const SkillRadarChart = ({ skills, careerGoal }) => {
  // 커리어별 스킬 매핑
  const skillMappings = {
    'saas_fullstack': [
      { skill: 'Python', key: 'python_basics' },
      { skill: 'JavaScript', key: 'javascript_basics' },
      { skill: 'React', key: 'react_basics' },
      { skill: 'Backend', key: 'fastapi_backend' },
      { skill: 'Database', key: 'database_design' },
      { skill: 'DevOps', key: 'cloud_deployment' }
    ],
    'react_specialist': [
      { skill: 'JSX', key: 'jsx_basics' },
      { skill: 'Components', key: 'components_props' },
      { skill: 'State', key: 'state_events' },
      { skill: 'Hooks', key: 'hooks_basic' },
      { skill: 'Performance', key: 'react_performance' },
      { skill: 'Architecture', key: 'react_architecture' }
    ]
  };

  const chartData = (skillMappings[careerGoal] || []).map(({ skill, key }) => ({
    skill,
    mastery: (skills[key] || 0) * 100,
    target: 80 // 목표 숙련도
  }));

  return (
    <div className="skill-radar-chart">
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="skill" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar
            name="현재 수준"
            dataKey="mastery"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.3}
          />
          <Radar
            name="목표 수준"
            dataKey="target"
            stroke="#ef4444"
            fill="transparent"
            strokeDasharray="5 5"
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
      
      <div className="skill-details">
        {chartData.map(({ skill, mastery }) => (
          <div key={skill} className="skill-item">
            <span>{skill}</span>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${mastery}%` }}
              />
            </div>
            <span>{Math.round(mastery)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### **4.2 교사 대시보드 고도화 (3일)**

**교사 대시보드 API:** `backend/app/api/v1/teacher_dashboard.py` (기존 파일 확장)
```python
@router.get("/career-analytics")
async def get_career_path_analytics(
    group_id: Optional[int] = None,
    career_goal: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """커리어 경로별 학습 현황 분석"""
    
    if not current_user.role == "teacher":
        raise HTTPException(status_code=403, detail="Teacher access required")
    
    # 그룹별 또는 전체 학생 조회
    students_query = db.query(User).filter(User.role == "student")
    if group_id:
        students_query = students_query.join(GroupMember).filter(GroupMember.group_id == group_id)
    
    students = students_query.all()
    
    analytics = {
        'career_distribution': {},
        'progress_by_career': {},
        'at_risk_students': [],
        'top_performers': [],
        'completion_rates': {}
    }
    
    for student in students:
        # 각 학생의 커리어 경로 및 진도 분석
        student_progress = analyze_student_career_progress(student.id, db)
        
        career = student_progress.get('career_goal', 'unknown')
        
        # 분포 계산
        analytics['career_distribution'][career] = analytics['career_distribution'].get(career, 0) + 1
        
        # 진도별 그룹화
        if career not in analytics['progress_by_career']:
            analytics['progress_by_career'][career] = []
        analytics['progress_by_career'][career].append(student_progress)
        
        # 위험군 식별 (정확도 < 60% or 비활성 7일+)
        if (student_progress.get('accuracy', 1.0) < 0.6 or 
            student_progress.get('days_inactive', 0) > 7):
            analytics['at_risk_students'].append({
                'student_id': student.id,
                'name': student.display_name,
                'career_goal': career,
                'risk_factors': identify_risk_factors(student_progress)
            })
    
    return analytics

def identify_risk_factors(student_progress: dict) -> list:
    """위험 요소 식별"""
    risks = []
    
    if student_progress.get('accuracy', 1.0) < 0.6:
        risks.append('low_accuracy')
    if student_progress.get('days_inactive', 0) > 7:
        risks.append('inactive')
    if student_progress.get('completion_rate', 1.0) < 0.3:
        risks.append('low_completion')
    if len(student_progress.get('weaknesses', [])) > 5:
        risks.append('multiple_weaknesses')
        
    return risks
```

**위험군 자동 탐지:** `backend/app/services/student_monitoring.py`
```python
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session

class StudentMonitoringService:
    def __init__(self):
        self.risk_thresholds = {
            'accuracy_threshold': 0.6,
            'inactivity_days': 7,
            'completion_rate_threshold': 0.3,
            'max_weaknesses': 5
        }
    
    async def detect_at_risk_students(self, group_id: int, db: Session) -> List[Dict]:
        """위험군 학생 자동 탐지"""
        
        students = self.get_group_students(group_id, db)
        at_risk = []
        
        for student in students:
            risk_score, risk_factors = self.calculate_risk_score(student.id, db)
            
            if risk_score >= 0.6:  # 60% 이상 위험도
                at_risk.append({
                    'student_id': student.id,
                    'student_name': student.display_name,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'recommended_actions': self.get_recommended_actions(risk_factors)
                })
        
        return sorted(at_risk, key=lambda x: x['risk_score'], reverse=True)
    
    def calculate_risk_score(self, student_id: int, db: Session) -> tuple:
        """학생별 위험도 점수 계산"""
        
        # 최근 활동 분석
        recent_activity = self.get_recent_activity(student_id, db)
        accuracy = recent_activity.get('accuracy', 1.0)
        days_inactive = recent_activity.get('days_inactive', 0)
        completion_rate = recent_activity.get('completion_rate', 1.0)
        weakness_count = len(recent_activity.get('weaknesses', []))
        
        # 가중치 기반 위험도 계산
        risk_score = 0.0
        risk_factors = []
        
        if accuracy < self.risk_thresholds['accuracy_threshold']:
            risk_score += 0.3
            risk_factors.append('low_accuracy')
            
        if days_inactive > self.risk_thresholds['inactivity_days']:
            risk_score += 0.4  # 비활성이 가장 큰 위험 요소
            risk_factors.append('inactive')
            
        if completion_rate < self.risk_thresholds['completion_rate_threshold']:
            risk_score += 0.2
            risk_factors.append('low_completion')
            
        if weakness_count > self.risk_thresholds['max_weaknesses']:
            risk_score += 0.1
            risk_factors.append('multiple_weaknesses')
        
        return min(risk_score, 1.0), risk_factors
    
    def get_recommended_actions(self, risk_factors: List[str]) -> List[str]:
        """위험 요소별 권장 조치"""
        actions = []
        
        action_mapping = {
            'low_accuracy': '개별 튜터링 세션 배정',
            'inactive': '학습 동기 부여 상담',
            'low_completion': '학습 계획 재조정',
            'multiple_weaknesses': '기초 개념 복습 과제 제공'
        }
        
        for factor in risk_factors:
            if factor in action_mapping:
                actions.append(action_mapping[factor])
        
        return actions

monitoring_service = StudentMonitoringService()
```

#### **4.3 실시간 모니터링 대시보드 (2일)**

**LLM 메트릭 수집:** `backend/app/services/llm_metrics.py` (기존 파일 확장)
```python
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List
import json

@dataclass
class LLMMetrics:
    timestamp: datetime
    provider: str
    model: str
    request_type: str  # 'feedback', 'question_generation'
    response_time_ms: int
    token_count: int
    success: bool
    error_type: str = None
    cache_hit: bool = False
    user_id: int = None

class EnhancedLLMMetrics:
    def __init__(self):
        self.metrics_buffer = []
        self.realtime_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'avg_response_time': 0.0,
            'cache_hit_rate': 0.0,
            'error_rate': 0.0
        }
    
    def record_llm_request(self, metrics: LLMMetrics):
        """LLM 요청 메트릭 기록"""
        self.metrics_buffer.append(metrics)
        self.update_realtime_stats(metrics)
        
        # 버퍼가 100개 이상이면 DB 저장
        if len(self.metrics_buffer) >= 100:
            self.flush_metrics_to_db()
    
    def update_realtime_stats(self, metrics: LLMMetrics):
        """실시간 통계 업데이트"""
        self.realtime_stats['total_requests'] += 1
        
        if metrics.success:
            self.realtime_stats['successful_requests'] += 1
        
        # 이동평균으로 응답시간 계산
        current_avg = self.realtime_stats['avg_response_time']
        total = self.realtime_stats['total_requests']
        self.realtime_stats['avg_response_time'] = (
            (current_avg * (total - 1) + metrics.response_time_ms) / total
        )
        
        # 성공률, 캐시 히트율 등 계산
        success_rate = self.realtime_stats['successful_requests'] / total
        self.realtime_stats['error_rate'] = 1.0 - success_rate
        
        if metrics.cache_hit:
            # 캐시 히트율 계산 로직
            pass
    
    def get_current_metrics(self) -> Dict:
        """현재 메트릭 조회"""
        return {
            'realtime_stats': self.realtime_stats,
            'recent_errors': self.get_recent_errors(),
            'performance_trend': self.get_performance_trend(),
            'user_distribution': self.get_user_distribution()
        }

llm_metrics = EnhancedLLMMetrics()
```

**모니터링 API:** `backend/app/api/v1/monitoring.py`
```python
@router.get("/llm-metrics")
async def get_llm_metrics(
    timeframe: str = "1h",  # 1h, 6h, 24h, 7d
    current_user: User = Depends(get_current_user)
):
    """LLM 성능 메트릭 조회"""
    
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    metrics = llm_metrics.get_current_metrics()
    
    return {
        'timeframe': timeframe,
        'metrics': metrics,
        'alerts': check_performance_alerts(metrics),
        'recommendations': generate_performance_recommendations(metrics)
    }

def check_performance_alerts(metrics: Dict) -> List[Dict]:
    """성능 알림 확인"""
    alerts = []
    
    if metrics['realtime_stats']['error_rate'] > 0.1:  # 10% 이상 오류율
        alerts.append({
            'level': 'warning',
            'message': f"LLM 오류율이 {metrics['realtime_stats']['error_rate']:.1%}로 높습니다",
            'action': 'LLM 제공자 상태 확인 필요'
        })
    
    if metrics['realtime_stats']['avg_response_time'] > 5000:  # 5초 이상
        alerts.append({
            'level': 'critical',
            'message': f"LLM 응답 시간이 {metrics['realtime_stats']['avg_response_time']/1000:.1f}초로 지연되고 있습니다",
            'action': '트래픽 분산 또는 캐시 최적화 필요'
        })
    
    return alerts
```

#### **4.4 20명 동시 사용 부하 테스트 (3일)**

**부하 테스트 스크립트:** `backend/tests/load_test.py`
```python
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

class LMSLoadTester:
    def __init__(self, base_url: str, concurrent_users: int = 20):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []
    
    async def simulate_user_session(self, user_id: int, session: aiohttp.ClientSession):
        """사용자 세션 시뮬레이션"""
        start_time = time.time()
        
        try:
            # 1. 로그인
            login_result = await self.perform_login(user_id, session)
            
            # 2. 대시보드 조회
            dashboard_result = await self.fetch_dashboard(session)
            
            # 3. 문제 조회
            questions_result = await self.fetch_questions(session)
            
            # 4. 답안 제출 (5문제)
            submission_results = []
            for i in range(5):
                result = await self.submit_answer(i, session)
                submission_results.append(result)
            
            # 5. 피드백 요청
            feedback_result = await self.request_feedback(session)
            
            session_time = time.time() - start_time
            
            return {
                'user_id': user_id,
                'session_time': session_time,
                'success': True,
                'operations': {
                    'login': login_result,
                    'dashboard': dashboard_result,
                    'questions': questions_result,
                    'submissions': submission_results,
                    'feedback': feedback_result
                }
            }
            
        except Exception as e:
            return {
                'user_id': user_id,
                'session_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    async def run_load_test(self, duration_minutes: int = 10):
        """부하 테스트 실행"""
        print(f"Starting load test: {self.concurrent_users} users for {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                tasks = []
                
                # 동시 사용자 시뮬레이션
                for user_id in range(self.concurrent_users):
                    task = self.simulate_user_session(user_id, session)
                    tasks.append(task)
                
                # 모든 사용자 세션 실행
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                self.results.extend(batch_results)
                
                # 다음 배치까지 잠시 대기
                await asyncio.sleep(30)  # 30초 간격
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict:
        """결과 분석"""
        total_sessions = len(self.results)
        successful_sessions = sum(1 for r in self.results if r.get('success', False))
        
        response_times = [r['session_time'] for r in self.results if 'session_time' in r]
        
        analysis = {
            'total_sessions': total_sessions,
            'successful_sessions': successful_sessions,
            'success_rate': successful_sessions / total_sessions if total_sessions > 0 else 0,
            'avg_session_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_session_time': min(response_times) if response_times else 0,
            'max_session_time': max(response_times) if response_times else 0,
            'concurrent_users': self.concurrent_users,
            'errors': [r for r in self.results if not r.get('success', True)]
        }
        
        return analysis

# 실행 스크립트
async def main():
    tester = LMSLoadTester("http://localhost:8000", concurrent_users=20)
    results = await tester.run_load_test(duration_minutes=5)
    
    print("=== Load Test Results ===")
    print(f"Success Rate: {results['success_rate']:.1%}")
    print(f"Average Session Time: {results['avg_session_time']:.2f}s")
    print(f"Concurrent Users: {results['concurrent_users']}")
    
    if results['errors']:
        print(f"Errors: {len(results['errors'])}")
        for error in results['errors'][:5]:  # 처음 5개 오류만 표시
            print(f"  - User {error['user_id']}: {error.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **Phase 4 검증 기준 (Acceptance Criteria)**

#### **✅ 완료 체크리스트**
- [ ] 20명 동시 사용에서 다음 문제/피드백 UX 저하 없음
- [ ] 커리어 경로별로 다른 대시보드 표시 (풀스택 vs React 전문가)
- [ ] 트랙별 학습 진도 실시간 업데이트
- [ ] 스킬 마스터리 레이더 차트 정상 동작
- [ ] 교사 대시보드에서 위험군 자동 탐지
- [ ] LLM 메트릭 실시간 모니터링
- [ ] 부하 테스트 통과 (95% 성공률)

#### **📊 최종 성능 목표**
- **교육적 성과**: 7개 기술 트랙 + 3가지 커리어 경로 완성
- **기술적 성과**: 추천 API 95p < 400ms, 피드백 95p < 2.5s
- **사용자 경험**: 20명 동시 사용 시 평균 응답 시간 < 2초
- **시스템 안정성**: 가용성 > 99%, 오류율 < 1%

---

# 📊 **전체 프로젝트 관리**

## **진도 추적 체크리스트**

### **Phase 1 (Week 1-2) - 커리큘럼 인프라**
- [ ] DB 스키마 설계 및 마이그레이션
- [ ] 3가지 커리어 카테고리 데이터 생성
- [ ] 7개 기술 트랙 구축
- [ ] 학습 모듈 상세 정의
- [ ] 기본 추천 API 구현
- [ ] Phase 1 검증 완료

### **Phase 2 (Week 3-4) - 개인화 엔진**
- [ ] 개인화 데이터 스키마 구축
- [ ] AdvancedCurriculumRecommendationEngine 구현
- [ ] AI 피드백 개인화 (프롬프트 템플릿)
- [ ] 실무 프로젝트 연계 시스템
- [ ] 약점 분석 알고리즘
- [ ] Phase 2 검증 완료

### **Phase 3 (Week 5-6) - 확장성 인프라**
- [ ] Redis + Celery 비동기 파이프라인
- [ ] 상태 일원화 및 캐시 전략
- [ ] 사용자별 레이트리밋
- [ ] LLM 백오프 정책
- [ ] DB 연결 풀 최적화
- [ ] Phase 3 검증 완료

### **Phase 4 (Week 7-8) - 사용자 경험**
- [ ] 커리어별 대시보드 차별화
- [ ] 스킬 마스터리 레이더 차트
- [ ] 교사 대시보드 고도화
- [ ] 위험군 자동 탐지
- [ ] LLM 모니터링 시스템
- [ ] 20명 동시 사용 부하 테스트
- [ ] **최종 목표 달성**: 각자 다른 SaaS 커리어 경로 학습 시스템

## **위험 관리 계획**

### **기술적 위험**
- **LLM API 장애**: 템플릿 폴백 + 다중 제공자 지원
- **데이터베이스 성능**: 인덱스 최적화 + 읽기 전용 복제본
- **동시성 문제**: Redis 분산 락 + 큐 기반 처리

### **일정 위험**
- **Phase별 의존성**: 각 Phase 완료 후 다음 진행
- **복잡도 증가**: 핵심 기능 우선, 부가 기능은 추후
- **통합 테스트**: 각 Phase마다 통합 검증

## **성공 측정 지표**

### **비즈니스 지표**
- 20명 동시 사용자 지원 ✅
- 3가지 커리어 경로 제공 ✅
- 7개 기술 스택 지원 ✅

### **기술 지표**
- API 응답 시간 < 400ms ✅
- LLM 응답 시간 < 2.5s ✅
- 시스템 가용성 > 99% ✅

### **사용자 경험 지표**
- 개인화 피드백 포함률 > 80% ✅
- 추천 정확도 만족도 ✅
- 학습 완성도 향상 ✅

---

# 🚀 **다음 단계 실행 가이드**

## **즉시 시작할 작업 (Phase 1 킥오프)**

1. **Phase 1 시작 명령**
   ```bash
   # 새 브랜치 생성
   git checkout -b phase1-curriculum-architecture
   
   # Alembic 마이그레이션 생성
   cd backend
   alembic revision --autogenerate -m "add_curriculum_architecture"
   ```

2. **우선순위 1: DB 스키마 작성**
   - `curriculum_categories` 테이블
   - `learning_modules` 테이블  
   - `learning_resources` 테이블

3. **우선순위 2: 시드 데이터 준비**
   - 3가지 커리어 카테고리
   - 7개 기술 트랙
   - 기본 모듈 데이터

4. **검증 및 다음 Phase 준비**
   - Phase 1 Acceptance Criteria 확인
   - Phase 2 상세 계획 수립

이 문서는 전체 Master Plan을 Phase별로 실행 가능한 형태로 구성했습니다. 각 Phase는 독립적으로 실행 가능하며, 이전 Phase의 결과물을 기반으로 다음 Phase를 진행할 수 있습니다.
