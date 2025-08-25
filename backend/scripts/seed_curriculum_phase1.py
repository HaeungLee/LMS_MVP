#!/usr/bin/env python3
"""
Phase 1 커리큘럼 데이터 시드 스크립트
- 3가지 커리어 카테고리
- 7개 기술 트랙
- 기본 모듈 및 리소스
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.orm import CurriculumCategory, LearningTrack, LearningModule, LearningResource
from datetime import datetime

def create_curriculum_categories(db: Session):
    """3가지 커리어 카테고리 생성"""
    categories = [
        {
            'name': 'saas_development',
            'display_name': 'SaaS 개발자 종합과정',
            'description': '초급부터 SaaS 개발자까지 - 개인화된 학습 경로와 AI 피드백으로 실무 역량을 기르는 종합 교육 플랫폼',
            'target_audience': 'beginner_to_professional',
            'estimated_total_months': 18
        },
        {
            'name': 'react_specialist',
            'display_name': 'React 개발 전문가',
            'description': 'React 생태계를 완전히 마스터하여 고성능 웹 애플리케이션을 구축하는 전문가 과정',
            'target_audience': 'intermediate_specialist',
            'estimated_total_months': 8
        },
        {
            'name': 'data_engineering_advanced',
            'display_name': '데이터 엔지니어링 심화',
            'description': '빅데이터 처리, 실시간 스트리밍, MLOps까지 데이터 엔지니어링 전문가 과정',
            'target_audience': 'intermediate_specialist',
            'estimated_total_months': 12
        }
    ]
    
    for cat_data in categories:
        # 기존 데이터 확인
        existing = db.query(CurriculumCategory).filter(
            CurriculumCategory.name == cat_data['name']
        ).first()
        
        if not existing:
            category = CurriculumCategory(**cat_data)
            db.add(category)
            print(f"✅ Created category: {cat_data['display_name']}")
        else:
            print(f"⚠️ Category already exists: {cat_data['display_name']}")
    
    db.commit()

def create_learning_tracks(db: Session):
    """7개 기술 트랙 생성"""
    
    # 커리어 카테고리 ID 조회
    saas_category = db.query(CurriculumCategory).filter(
        CurriculumCategory.name == 'saas_development'
    ).first()
    react_category = db.query(CurriculumCategory).filter(
        CurriculumCategory.name == 'react_specialist'
    ).first()
    data_category = db.query(CurriculumCategory).filter(
        CurriculumCategory.name == 'data_engineering_advanced'
    ).first()
    
    tracks = [
        # Foundation Tracks (4개)
        {
            'name': 'python_basics',
            'display_name': 'Python 기초',
            'category': 'foundation',
            'curriculum_category_id': saas_category.id,
            'specialization_level': 'general',
            'prerequisite_tracks': [],
            'difficulty_level': 1,
            'estimated_hours': 40,
            'description': 'Python 프로그래밍의 기초부터 객체지향 프로그래밍까지 완전 정복'
        },
        {
            'name': 'html_css',
            'display_name': 'HTML & CSS',
            'category': 'foundation',
            'curriculum_category_id': saas_category.id,
            'specialization_level': 'general',
            'prerequisite_tracks': [],
            'difficulty_level': 1,
            'estimated_hours': 35,
            'description': '웹 개발의 기초인 HTML과 CSS, 반응형 웹 디자인까지'
        },
        {
            'name': 'javascript_basics',
            'display_name': 'JavaScript 기초',
            'category': 'foundation',
            'curriculum_category_id': saas_category.id,
            'specialization_level': 'general',
            'prerequisite_tracks': ['html_css'],
            'difficulty_level': 1,
            'estimated_hours': 45,
            'description': 'JavaScript 기초 문법부터 ES6+ 모던 자바스크립트까지'
        },
        {
            'name': 'data_structures',
            'display_name': '자료구조 & 알고리즘',
            'category': 'foundation',
            'curriculum_category_id': saas_category.id,
            'specialization_level': 'general',
            'prerequisite_tracks': ['python_basics'],
            'difficulty_level': 2,
            'estimated_hours': 60,
            'description': '프로그래밍의 핵심인 자료구조와 알고리즘 완전 정복'
        },
        
        # Development Tracks (3개)
        {
            'name': 'react_basics',
            'display_name': 'React 기초',
            'category': 'development',
            'curriculum_category_id': saas_category.id,
            'specialization_level': 'general',
            'prerequisite_tracks': ['javascript_basics'],
            'difficulty_level': 2,
            'estimated_hours': 50,
            'description': 'React의 기초부터 Hooks, 상태관리까지 실무형 React 개발'
        },
        {
            'name': 'fastapi_backend',
            'display_name': 'FastAPI 백엔드',
            'category': 'development',
            'curriculum_category_id': saas_category.id,
            'specialization_level': 'general',
            'prerequisite_tracks': ['python_basics'],
            'difficulty_level': 2,
            'estimated_hours': 55,
            'description': 'FastAPI로 RESTful API 개발, 인증, 데이터베이스 연동까지'
        },
        {
            'name': 'database_design',
            'display_name': '데이터베이스 설계',
            'category': 'development',
            'curriculum_category_id': saas_category.id,
            'specialization_level': 'general',
            'prerequisite_tracks': ['python_basics'],
            'difficulty_level': 2,
            'estimated_hours': 40,
            'description': 'PostgreSQL, MongoDB부터 데이터베이스 설계 원칙까지'
        }
    ]
    
    for track_data in tracks:
        # 기존 데이터 확인
        existing = db.query(LearningTrack).filter(
            LearningTrack.name == track_data['name']
        ).first()
        
        if not existing:
            track = LearningTrack(**track_data)
            db.add(track)
            print(f"✅ Created track: {track_data['display_name']}")
        else:
            print(f"⚠️ Track already exists: {track_data['display_name']}")
    
    db.commit()

def create_basic_modules(db: Session):
    """기본 학습 모듈 생성"""
    
    # 트랙 ID 조회
    python_track = db.query(LearningTrack).filter(LearningTrack.name == 'python_basics').first()
    react_track = db.query(LearningTrack).filter(LearningTrack.name == 'react_basics').first()
    
    if not python_track or not react_track:
        print("❌ Required tracks not found. Cannot create modules.")
        return
    
    modules = [
        # Python 기초 모듈들
        {
            'track_id': python_track.id,
            'name': 'variables_types',
            'display_name': '변수와 자료형',
            'module_type': 'core',
            'estimated_hours': 4,
            'difficulty_level': 1,
            'prerequisites': [],
            'tags': ['python', 'basics', 'variables'],
            'industry_focus': 'general'
        },
        {
            'track_id': python_track.id,
            'name': 'conditions',
            'display_name': '조건문',
            'module_type': 'core',
            'estimated_hours': 6,
            'difficulty_level': 1,
            'prerequisites': ['variables_types'],
            'tags': ['python', 'control-flow', 'conditions'],
            'industry_focus': 'general'
        },
        {
            'track_id': python_track.id,
            'name': 'loops',
            'display_name': '반복문',
            'module_type': 'core',
            'estimated_hours': 6,
            'difficulty_level': 1,
            'prerequisites': ['conditions'],
            'tags': ['python', 'control-flow', 'loops'],
            'industry_focus': 'general'
        },
        {
            'track_id': python_track.id,
            'name': 'functions',
            'display_name': '함수',
            'module_type': 'core',
            'estimated_hours': 8,
            'difficulty_level': 2,
            'prerequisites': ['loops'],
            'tags': ['python', 'functions', 'scope'],
            'industry_focus': 'general'
        },
        {
            'track_id': python_track.id,
            'name': 'data_structures_python',
            'display_name': '리스트와 딕셔너리',
            'module_type': 'core',
            'estimated_hours': 8,
            'difficulty_level': 2,
            'prerequisites': ['functions'],
            'tags': ['python', 'data-structures', 'lists', 'dictionaries'],
            'industry_focus': 'general'
        },
        {
            'track_id': python_track.id,
            'name': 'classes',
            'display_name': '클래스와 객체',
            'module_type': 'core',
            'estimated_hours': 10,
            'difficulty_level': 3,
            'prerequisites': ['data_structures_python'],
            'tags': ['python', 'oop', 'classes'],
            'industry_focus': 'general'
        },
        
        # React 기초 모듈들
        {
            'track_id': react_track.id,
            'name': 'jsx_basics',
            'display_name': 'JSX 기초',
            'module_type': 'core',
            'estimated_hours': 6,
            'difficulty_level': 2,
            'prerequisites': ['javascript_basics'],
            'tags': ['react', 'jsx', 'components'],
            'industry_focus': 'general'
        },
        {
            'track_id': react_track.id,
            'name': 'components_props',
            'display_name': '컴포넌트와 Props',
            'module_type': 'core',
            'estimated_hours': 8,
            'difficulty_level': 2,
            'prerequisites': ['jsx_basics'],
            'tags': ['react', 'components', 'props'],
            'industry_focus': 'general'
        },
        {
            'track_id': react_track.id,
            'name': 'state_events',
            'display_name': 'State와 이벤트',
            'module_type': 'core',
            'estimated_hours': 8,
            'difficulty_level': 2,
            'prerequisites': ['components_props'],
            'tags': ['react', 'state', 'events'],
            'industry_focus': 'general'
        },
        {
            'track_id': react_track.id,
            'name': 'hooks_basic',
            'display_name': '기본 Hooks',
            'module_type': 'core',
            'estimated_hours': 10,
            'difficulty_level': 3,
            'prerequisites': ['state_events'],
            'tags': ['react', 'hooks', 'useState', 'useEffect'],
            'industry_focus': 'general'
        }
    ]
    
    for module_data in modules:
        # 기존 데이터 확인
        existing = db.query(LearningModule).filter(
            LearningModule.name == module_data['name']
        ).first()
        
        if not existing:
            module = LearningModule(**module_data)
            db.add(module)
            print(f"✅ Created module: {module_data['display_name']}")
        else:
            print(f"⚠️ Module already exists: {module_data['display_name']}")
    
    db.commit()

def create_learning_resources(db: Session):
    """학습 자료 생성"""
    
    # 트랙 ID 조회
    python_track = db.query(LearningTrack).filter(LearningTrack.name == 'python_basics').first()
    react_track = db.query(LearningTrack).filter(LearningTrack.name == 'react_basics').first()
    
    if not python_track or not react_track:
        print("❌ Required tracks not found. Cannot create resources.")
        return
    
    # 모듈 ID 조회
    variables_module = db.query(LearningModule).filter(LearningModule.name == 'variables_types').first()
    jsx_module = db.query(LearningModule).filter(LearningModule.name == 'jsx_basics').first()
    
    resources = [
        # Python 기초 자료
        {
            'track_id': python_track.id,
            'module_id': variables_module.id if variables_module else None,
            'sub_topic': 'variables',
            'resource_type': 'documentation',
            'title': 'Python 공식 문서 - 변수와 연산',
            'url': 'https://docs.python.org/3/tutorial/introduction.html#using-python-as-a-calculator',
            'description': 'Python 변수와 기본 연산자 사용법',
            'difficulty_level': 1,
            'industry_focus': 'general'
        },
        {
            'track_id': python_track.id,
            'module_id': variables_module.id if variables_module else None,
            'sub_topic': 'types',
            'resource_type': 'tutorial',
            'title': 'Real Python - Python 데이터 타입',
            'url': 'https://realpython.com/python-data-types/',
            'description': '파이썬 기본 데이터 타입 완벽 가이드',
            'difficulty_level': 1,
            'industry_focus': 'general'
        },
        {
            'track_id': python_track.id,
            'module_id': None,
            'sub_topic': 'general',
            'resource_type': 'project',
            'title': 'Python 계산기 프로젝트',
            'url': 'https://github.com/templates/python-calculator',
            'description': '기본 연산을 수행하는 계산기 프로젝트',
            'difficulty_level': 1,
            'industry_focus': 'general'
        },
        
        # React 기초 자료  
        {
            'track_id': react_track.id,
            'module_id': jsx_module.id if jsx_module else None,
            'sub_topic': 'jsx',
            'resource_type': 'documentation',
            'title': 'React 공식 문서 - JSX',
            'url': 'https://react.dev/learn/writing-markup-with-jsx',
            'description': 'JSX 문법과 사용법 완전 가이드',
            'difficulty_level': 2,
            'industry_focus': 'general'
        },
        {
            'track_id': react_track.id,
            'module_id': jsx_module.id if jsx_module else None,
            'sub_topic': 'components',
            'resource_type': 'tutorial',
            'title': 'React 컴포넌트 가이드',
            'url': 'https://react.dev/learn/your-first-component',
            'description': '첫 React 컴포넌트 만들기',
            'difficulty_level': 2,
            'industry_focus': 'general'
        },
        {
            'track_id': react_track.id,
            'module_id': None,
            'sub_topic': 'general',
            'resource_type': 'project',
            'title': 'React Todo 앱',
            'url': 'https://github.com/templates/react-todo',
            'description': 'React로 만드는 기본 Todo 애플리케이션',
            'difficulty_level': 2,
            'industry_focus': 'general'
        }
    ]
    
    for resource_data in resources:
        # 기존 데이터 확인 (URL 기준)
        existing = db.query(LearningResource).filter(
            LearningResource.url == resource_data['url']
        ).first()
        
        if not existing:
            resource = LearningResource(**resource_data)
            db.add(resource)
            print(f"✅ Created resource: {resource_data['title']}")
        else:
            print(f"⚠️ Resource already exists: {resource_data['title']}")
    
    db.commit()

def main():
    """메인 실행 함수"""
    print("🚀 Phase 1 커리큘럼 데이터 시드 시작...")
    
    # 데이터베이스 연결 테스트
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 데이터베이스 연결 성공")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return
    
    db = SessionLocal()
    
    try:
        print("\n📊 1단계: 커리큘럼 카테고리 생성...")
        create_curriculum_categories(db)
        
        print("\n📚 2단계: 학습 트랙 생성...")
        create_learning_tracks(db)
        
        print("\n🧩 3단계: 기본 모듈 생성...")
        create_basic_modules(db)
        
        print("\n📖 4단계: 학습 자료 생성...")
        create_learning_resources(db)
        
        print("\n🎉 Phase 1 커리큘럼 데이터 시드 완료!")
        
        # 요약 출력
        categories_count = db.query(CurriculumCategory).count()
        tracks_count = db.query(LearningTrack).count()
        modules_count = db.query(LearningModule).count()
        resources_count = db.query(LearningResource).count()
        
        print(f"\n📊 생성된 데이터 요약:")
        print(f"  - 커리큘럼 카테고리: {categories_count}개")
        print(f"  - 학습 트랙: {tracks_count}개")
        print(f"  - 학습 모듈: {modules_count}개")
        print(f"  - 학습 자료: {resources_count}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
