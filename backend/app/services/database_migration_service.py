"""
Database initialization and migration script for Code Problems
코딩테스트 문제 관련 데이터베이스 초기화 및 마이그레이션
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
from typing import List, Dict, Any

from app.core.database import get_database_url
from app.models.orm import Base
from app.models.code_problem import CodeProblem, CodeTestCase, CodeSubmission, ProblemTag, ProblemTagAssociation

logger = logging.getLogger(__name__)

class DatabaseMigrationService:
    """데이터베이스 마이그레이션 서비스"""
    
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self) -> bool:
        """코딩테스트 관련 테이블 생성"""
        try:
            # 모든 테이블 생성
            Base.metadata.create_all(bind=self.engine, 
                                   tables=[
                                       CodeProblem.__table__,
                                       CodeTestCase.__table__,
                                       CodeSubmission.__table__,
                                       ProblemTag.__table__,
                                       ProblemTagAssociation.__table__
                                   ])
            logger.info("코딩테스트 테이블이 성공적으로 생성되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"테이블 생성 중 오류 발생: {str(e)}")
            return False
    
    def drop_tables(self) -> bool:
        """코딩테스트 관련 테이블 삭제 (개발용)"""
        try:
            Base.metadata.drop_all(bind=self.engine, 
                                 tables=[
                                     ProblemTagAssociation.__table__,
                                     CodeSubmission.__table__,
                                     CodeTestCase.__table__,
                                     CodeProblem.__table__,
                                     ProblemTag.__table__
                                 ])
            logger.info("코딩테스트 테이블이 성공적으로 삭제되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"테이블 삭제 중 오류 발생: {str(e)}")
            return False
    
    def check_tables_exist(self) -> Dict[str, bool]:
        """테이블 존재 여부 확인"""
        try:
            with self.engine.connect() as connection:
                table_status = {}
                
                tables_to_check = [
                    'code_problems',
                    'code_test_cases', 
                    'code_submissions',
                    'problem_tags',
                    'problem_tag_associations'
                ]
                
                for table_name in tables_to_check:
                    result = connection.execute(
                        text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'")
                    )
                    table_status[table_name] = result.scalar() > 0
                
                return table_status
                
        except Exception as e:
            logger.error(f"테이블 확인 중 오류 발생: {str(e)}")
            return {}
    
    def migrate_sample_problems(self, created_by_id: int = 1) -> bool:
        """하드코딩된 샘플 문제들을 데이터베이스로 마이그레이션"""
        
        # 기존 하드코딩된 샘플 문제들
        sample_problems_data = [
            {
                "title": "두 수의 합",
                "description": "두 개의 정수 a와 b가 주어졌을 때, a와 b의 합을 출력하는 프로그램을 작성하세요.",
                "difficulty": "easy",
                "category": "Python 기초",
                "examples": [
                    {
                        "input": "3 5",
                        "output": "8",
                        "explanation": "3과 5를 더하면 8입니다."
                    }
                ],
                "constraints": [
                    "-1000 ≤ a, b ≤ 1000",
                    "a와 b는 정수입니다."
                ],
                "hints": [
                    "input() 함수를 사용해서 입력을 받을 수 있습니다.",
                    "split() 함수를 사용해서 공백으로 구분된 값을 나눌 수 있습니다."
                ],
                "template": "# 두 수의 합 구하기\na, b = map(int, input().split())\nresult = a + b\nprint(result)",
                "time_limit_ms": 10000,
                "memory_limit_mb": 128,
                "test_cases": [
                    {
                        "input_data": "3 5",
                        "expected_output": "8",
                        "description": "기본 예제",
                        "is_hidden": False,
                        "is_sample": True,
                        "weight": 1.0
                    },
                    {
                        "input_data": "-10 15",
                        "expected_output": "5",
                        "description": "음수 포함",
                        "is_hidden": True,
                        "is_sample": False,
                        "weight": 1.0
                    },
                    {
                        "input_data": "0 0",
                        "expected_output": "0",
                        "description": "0 입력",
                        "is_hidden": True,
                        "is_sample": False,
                        "weight": 1.0
                    }
                ]
            },
            {
                "title": "리스트 최댓값 찾기",
                "description": "주어진 리스트에서 최댓값을 찾아 출력하는 프로그램을 작성하세요.",
                "difficulty": "easy",
                "category": "Python 기초",
                "examples": [
                    {
                        "input": "5\n1 3 7 2 5",
                        "output": "7",
                        "explanation": "리스트 [1, 3, 7, 2, 5]에서 최댓값은 7입니다."
                    }
                ],
                "constraints": [
                    "1 ≤ 리스트 길이 ≤ 100",
                    "각 원소는 정수입니다."
                ],
                "hints": [
                    "max() 함수를 사용할 수 있습니다.",
                    "반복문을 사용해서 직접 구현해볼 수도 있습니다."
                ],
                "template": "# 리스트 최댓값 찾기\nn = int(input())\nnumbers = list(map(int, input().split()))\n# 여기에 코드를 작성하세요",
                "time_limit_ms": 10000,
                "memory_limit_mb": 128,
                "test_cases": [
                    {
                        "input_data": "5\n1 3 7 2 5",
                        "expected_output": "7",
                        "description": "기본 예제",
                        "is_hidden": False,
                        "is_sample": True,
                        "weight": 1.0
                    },
                    {
                        "input_data": "3\n-5 -2 -8",
                        "expected_output": "-2",
                        "description": "음수만 있는 경우",
                        "is_hidden": True,
                        "is_sample": False,
                        "weight": 1.0
                    },
                    {
                        "input_data": "1\n42",
                        "expected_output": "42",
                        "description": "원소가 하나인 경우",
                        "is_hidden": True,
                        "is_sample": False,
                        "weight": 1.0
                    }
                ]
            },
            {
                "title": "팩토리얼 계산",
                "description": "주어진 자연수 n의 팩토리얼을 계산하여 출력하는 프로그램을 작성하세요.",
                "difficulty": "medium",
                "category": "Python 기초",
                "examples": [
                    {
                        "input": "5",
                        "output": "120",
                        "explanation": "5! = 5 × 4 × 3 × 2 × 1 = 120입니다."
                    }
                ],
                "constraints": [
                    "1 ≤ n ≤ 10",
                    "n은 자연수입니다."
                ],
                "hints": [
                    "반복문을 사용해서 계산할 수 있습니다.",
                    "재귀함수를 사용할 수도 있습니다.",
                    "math.factorial() 함수도 사용할 수 있습니다."
                ],
                "template": "# 팩토리얼 계산\nn = int(input())\n# 여기에 코드를 작성하세요",
                "time_limit_ms": 10000,
                "memory_limit_mb": 128,
                "test_cases": [
                    {
                        "input_data": "5",
                        "expected_output": "120",
                        "description": "기본 예제",
                        "is_hidden": False,
                        "is_sample": True,
                        "weight": 1.0
                    },
                    {
                        "input_data": "1",
                        "expected_output": "1",
                        "description": "최소값",
                        "is_hidden": True,
                        "is_sample": False,
                        "weight": 1.0
                    },
                    {
                        "input_data": "10",
                        "expected_output": "3628800",
                        "description": "최대값",
                        "is_hidden": True,
                        "is_sample": False,
                        "weight": 1.0
                    }
                ]
            }
        ]
        
        try:
            db = self.SessionLocal()
            
            # 기존 샘플 문제 확인
            existing_count = db.query(CodeProblem).count()
            if existing_count > 0:
                logger.info(f"이미 {existing_count}개의 문제가 존재합니다. 마이그레이션을 건너뜁니다.")
                return True
            
            for problem_data in sample_problems_data:
                # 문제 생성
                test_cases_data = problem_data.pop('test_cases')
                
                problem = CodeProblem(
                    created_by_id=created_by_id,
                    **problem_data
                )
                
                db.add(problem)
                db.flush()  # ID를 얻기 위해 flush
                
                # 테스트 케이스 생성
                for tc_data in test_cases_data:
                    test_case = CodeTestCase(
                        problem_id=problem.id,
                        **tc_data
                    )
                    db.add(test_case)
            
            db.commit()
            logger.info(f"샘플 문제 {len(sample_problems_data)}개가 성공적으로 마이그레이션되었습니다.")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"샘플 문제 마이그레이션 중 오류 발생: {str(e)}")
            return False
            
        finally:
            db.close()
    
    def create_default_tags(self) -> bool:
        """기본 태그들 생성"""
        
        default_tags = [
            {"name": "기초", "description": "프로그래밍 기초 문제", "color": "#10B981"},
            {"name": "알고리즘", "description": "알고리즘 설계 문제", "color": "#3B82F6"},
            {"name": "자료구조", "description": "자료구조 활용 문제", "color": "#8B5CF6"},
            {"name": "구현", "description": "구현 및 시뮬레이션 문제", "color": "#F59E0B"},
            {"name": "수학", "description": "수학적 사고 문제", "color": "#EF4444"},
            {"name": "문자열", "description": "문자열 처리 문제", "color": "#06B6D4"},
            {"name": "그리디", "description": "그리디 알고리즘 문제", "color": "#84CC16"},
            {"name": "DP", "description": "동적 프로그래밍 문제", "color": "#6366F1"}
        ]
        
        try:
            db = self.SessionLocal()
            
            # 기존 태그 확인
            existing_tags = db.query(ProblemTag).count()
            if existing_tags > 0:
                logger.info(f"이미 {existing_tags}개의 태그가 존재합니다.")
                return True
            
            for tag_data in default_tags:
                tag = ProblemTag(**tag_data)
                db.add(tag)
            
            db.commit()
            logger.info(f"기본 태그 {len(default_tags)}개가 성공적으로 생성되었습니다.")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"기본 태그 생성 중 오류 발생: {str(e)}")
            return False
            
        finally:
            db.close()

# 전역 인스턴스
migration_service = DatabaseMigrationService()

def get_migration_service() -> DatabaseMigrationService:
    """마이그레이션 서비스 인스턴스 반환"""
    return migration_service
