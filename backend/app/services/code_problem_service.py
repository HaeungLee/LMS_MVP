"""
Code Problem Management Service
코딩테스트 문제 관리 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from fastapi import Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.code_problem import CodeProblem, CodeTestCase, CodeSubmission, ProblemTag
from app.core.database import get_db

logger = logging.getLogger(__name__)

class CodeProblemService:
    """코딩테스트 문제 관리 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def create_problem(self, problem_data: Dict[str, Any], created_by_id: int) -> CodeProblem:
        """새 문제 생성"""
        try:
            # 문제 생성
            problem = CodeProblem(
                title=problem_data['title'],
                description=problem_data['description'],
                difficulty=problem_data['difficulty'],
                category=problem_data['category'],
                examples=problem_data.get('examples', []),
                constraints=problem_data.get('constraints', []),
                hints=problem_data.get('hints', []),
                template=problem_data.get('template', ''),
                time_limit_ms=problem_data.get('time_limit_ms', 10000),
                memory_limit_mb=problem_data.get('memory_limit_mb', 128),
                created_by_id=created_by_id
            )
            
            self.db.add(problem)
            self.db.flush()  # ID 할당을 위해 flush
            
            # 테스트 케이스 추가
            if 'test_cases' in problem_data:
                for test_case_data in problem_data['test_cases']:
                    test_case = CodeTestCase(
                        problem_id=problem.id,
                        input_data=test_case_data['input_data'],
                        expected_output=test_case_data['expected_output'],
                        description=test_case_data.get('description', ''),
                        is_hidden=test_case_data.get('is_hidden', True),
                        is_sample=test_case_data.get('is_sample', False),
                        weight=test_case_data.get('weight', 1.0)
                    )
                    self.db.add(test_case)
            
            self.db.commit()
            self.db.refresh(problem)
            
            logger.info(f"Created new problem: {problem.title} (ID: {problem.id})")
            return problem
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating problem: {str(e)}")
            raise

    def get_problem(self, problem_id: int, include_hidden_tests: bool = False) -> Optional[CodeProblem]:
        """문제 조회"""
        try:
            problem = self.db.query(CodeProblem).filter(
                CodeProblem.id == problem_id,
                CodeProblem.is_active == True
            ).first()
            
            if not problem:
                return None
            
            # 테스트 케이스 필터링
            if not include_hidden_tests:
                # 일반 사용자는 공개 테스트 케이스만 볼 수 있음
                problem.test_cases = [tc for tc in problem.test_cases if not tc.is_hidden]
            
            return problem
            
        except Exception as e:
            logger.error(f"Error getting problem {problem_id}: {str(e)}")
            raise

    def list_problems(
        self, 
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        search_query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: str = "asc"
    ) -> List[Dict[str, Any]]:
        """문제 목록 조회"""
        try:
            query = self.db.query(CodeProblem).filter(CodeProblem.is_active == True)
            
            # 필터 적용
            if category:
                query = query.filter(CodeProblem.category == category)
            
            if difficulty:
                query = query.filter(CodeProblem.difficulty == difficulty)
            
            if search_query:
                query = query.filter(
                    or_(
                        CodeProblem.title.ilike(f"%{search_query}%"),
                        CodeProblem.description.ilike(f"%{search_query}%")
                    )
                )
            
            # 정렬
            if sort_by == "difficulty":
                # 난이도 순서: easy -> medium -> hard
                difficulty_order = func.case(
                    (CodeProblem.difficulty == 'easy', 1),
                    (CodeProblem.difficulty == 'medium', 2),
                    (CodeProblem.difficulty == 'hard', 3),
                    else_=4
                )
                if sort_order == "desc":
                    query = query.order_by(difficulty_order.desc())
                else:
                    query = query.order_by(difficulty_order.asc())
            elif sort_by == "acceptance_rate":
                if sort_order == "desc":
                    query = query.order_by(CodeProblem.acceptance_rate.desc())
                else:
                    query = query.order_by(CodeProblem.acceptance_rate.asc())
            else:
                # 기본 정렬 (id, title, created_at 등)
                column = getattr(CodeProblem, sort_by, CodeProblem.id)
                if sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
            
            # 페이지네이션
            problems = query.offset(offset).limit(limit).all()
            
            # 결과 변환
            result = []
            for problem in problems:
                result.append({
                    "id": problem.id,
                    "title": problem.title,
                    "difficulty": problem.difficulty,
                    "category": problem.category,
                    "acceptance_rate": problem.acceptance_rate,
                    "total_submissions": problem.total_submissions,
                    "solved": False,  # TODO: 사용자별 해결 여부 확인
                    "created_at": problem.created_at.isoformat() if problem.created_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing problems: {str(e)}")
            raise

    def update_problem(self, problem_id: int, problem_data: Dict[str, Any]) -> Optional[CodeProblem]:
        """문제 수정"""
        try:
            problem = self.db.query(CodeProblem).filter(CodeProblem.id == problem_id).first()
            if not problem:
                return None
            
            # 기본 정보 업데이트
            for field in ['title', 'description', 'difficulty', 'category', 'examples', 
                         'constraints', 'hints', 'template', 'time_limit_ms', 'memory_limit_mb']:
                if field in problem_data:
                    setattr(problem, field, problem_data[field])
            
            # 테스트 케이스 업데이트
            if 'test_cases' in problem_data:
                # 기존 테스트 케이스 삭제
                self.db.query(CodeTestCase).filter(CodeTestCase.problem_id == problem_id).delete()
                
                # 새 테스트 케이스 추가
                for test_case_data in problem_data['test_cases']:
                    test_case = CodeTestCase(
                        problem_id=problem.id,
                        input_data=test_case_data['input_data'],
                        expected_output=test_case_data['expected_output'],
                        description=test_case_data.get('description', ''),
                        is_hidden=test_case_data.get('is_hidden', True),
                        is_sample=test_case_data.get('is_sample', False),
                        weight=test_case_data.get('weight', 1.0)
                    )
                    self.db.add(test_case)
            
            self.db.commit()
            self.db.refresh(problem)
            
            logger.info(f"Updated problem: {problem.title} (ID: {problem.id})")
            return problem
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating problem {problem_id}: {str(e)}")
            raise

    def delete_problem(self, problem_id: int) -> bool:
        """문제 삭제 (소프트 삭제)"""
        try:
            problem = self.db.query(CodeProblem).filter(CodeProblem.id == problem_id).first()
            if not problem:
                return False
            
            problem.is_active = False
            self.db.commit()
            
            logger.info(f"Deleted problem: {problem.title} (ID: {problem.id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting problem {problem_id}: {str(e)}")
            raise

    def get_categories(self) -> List[Dict[str, Any]]:
        """카테고리 목록 조회"""
        try:
            categories = self.db.query(
                CodeProblem.category,
                func.count(CodeProblem.id).label('problem_count')
            ).filter(
                CodeProblem.is_active == True
            ).group_by(
                CodeProblem.category
            ).all()
            
            return [
                {
                    "name": category,
                    "problem_count": count
                }
                for category, count in categories
            ]
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """전체 통계 조회"""
        try:
            total_problems = self.db.query(func.count(CodeProblem.id)).filter(
                CodeProblem.is_active == True
            ).scalar()
            
            difficulty_stats = self.db.query(
                CodeProblem.difficulty,
                func.count(CodeProblem.id).label('count')
            ).filter(
                CodeProblem.is_active == True
            ).group_by(
                CodeProblem.difficulty
            ).all()
            
            category_stats = self.db.query(
                CodeProblem.category,
                func.count(CodeProblem.id).label('count')
            ).filter(
                CodeProblem.is_active == True
            ).group_by(
                CodeProblem.category
            ).all()
            
            total_submissions = self.db.query(func.count(CodeSubmission.id)).scalar()
            
            return {
                "total_problems": total_problems,
                "total_submissions": total_submissions,
                "difficulty_distribution": {
                    difficulty: count for difficulty, count in difficulty_stats
                },
                "category_distribution": {
                    category: count for category, count in category_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise

    def migrate_sample_problems(self, created_by_id: int):
        """기존 샘플 문제를 데이터베이스로 마이그레이션"""
        try:
            # 기존 샘플 문제들
            sample_problems = [
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
                    "test_cases": [
                        {
                            "input_data": "3 5",
                            "expected_output": "8",
                            "description": "기본 예제",
                            "is_hidden": False,
                            "is_sample": True
                        },
                        {
                            "input_data": "-1000 1000",
                            "expected_output": "0",
                            "description": "경계값 테스트",
                            "is_hidden": True,
                            "is_sample": False
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
                    "test_cases": [
                        {
                            "input_data": "5\n1 3 7 2 5",
                            "expected_output": "7",
                            "description": "기본 예제",
                            "is_hidden": False,
                            "is_sample": True
                        },
                        {
                            "input_data": "1\n42",
                            "expected_output": "42",
                            "description": "단일 원소",
                            "is_hidden": True,
                            "is_sample": False
                        }
                    ]
                },
                {
                    "title": "팩토리얼 계산",
                    "description": "주어진 양의 정수 n에 대해 n!을 계산하는 프로그램을 작성하세요.",
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
                        "n은 양의 정수입니다."
                    ],
                    "hints": [
                        "반복문이나 재귀함수를 사용할 수 있습니다.",
                        "math.factorial() 함수를 사용할 수도 있습니다."
                    ],
                    "template": "# 팩토리얼 계산\nn = int(input())\n# 여기에 코드를 작성하세요",
                    "test_cases": [
                        {
                            "input_data": "5",
                            "expected_output": "120",
                            "description": "기본 예제",
                            "is_hidden": False,
                            "is_sample": True
                        },
                        {
                            "input_data": "1",
                            "expected_output": "1",
                            "description": "경계값",
                            "is_hidden": True,
                            "is_sample": False
                        },
                        {
                            "input_data": "10",
                            "expected_output": "3628800",
                            "description": "최대값",
                            "is_hidden": True,
                            "is_sample": False
                        }
                    ]
                }
            ]
            
            # 기존 문제가 있는지 확인
            existing_count = self.db.query(func.count(CodeProblem.id)).scalar()
            if existing_count > 0:
                logger.info("Sample problems already exist in database")
                return
            
            # 샘플 문제들 생성
            for problem_data in sample_problems:
                self.create_problem(problem_data, created_by_id)
            
            logger.info(f"Migrated {len(sample_problems)} sample problems to database")
            
        except Exception as e:
            logger.error(f"Error migrating sample problems: {str(e)}")
            raise

    def delete_problem(self, problem_id: int) -> bool:
        """문제 삭제 (소프트 삭제)"""
        try:
            problem = self.db.query(CodeProblem).filter(CodeProblem.id == problem_id).first()
            if not problem:
                return False
            
            # 소프트 삭제 (is_active를 False로 설정)
            problem.is_active = False
            self.db.commit()
            
            logger.info(f"Deleted problem: {problem.title} (ID: {problem_id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting problem {problem_id}: {str(e)}")
            raise

    def get_categories(self) -> List[str]:
        """문제 카테고리 목록 조회"""
        try:
            categories = self.db.query(CodeProblem.category).filter(
                CodeProblem.is_active == True
            ).distinct().all()
            
            return [category[0] for category in categories if category[0]]
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """기본 통계 정보 조회"""
        try:
            total_problems = self.db.query(func.count(CodeProblem.id)).filter(
                CodeProblem.is_active == True
            ).scalar()
            
            difficulty_stats = self.db.query(
                CodeProblem.difficulty,
                func.count(CodeProblem.id)
            ).filter(
                CodeProblem.is_active == True
            ).group_by(CodeProblem.difficulty).all()
            
            category_stats = self.db.query(
                CodeProblem.category,
                func.count(CodeProblem.id)
            ).filter(
                CodeProblem.is_active == True
            ).group_by(CodeProblem.category).all()
            
            return {
                "total_problems": total_problems,
                "by_difficulty": {diff: count for diff, count in difficulty_stats},
                "by_category": {cat: count for cat, count in category_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise

    def get_admin_statistics(self) -> Dict[str, Any]:
        """관리자용 상세 통계 정보 조회"""
        try:
            # 기본 통계
            basic_stats = self.get_statistics()
            
            # 추가 통계
            total_submissions = self.db.query(func.count(CodeSubmission.id)).scalar()
            
            avg_acceptance_rate = self.db.query(
                func.avg(CodeProblem.acceptance_rate)
            ).filter(CodeProblem.is_active == True).scalar()
            
            recent_problems = self.db.query(func.count(CodeProblem.id)).filter(
                CodeProblem.is_active == True,
                CodeProblem.created_at >= datetime.utcnow() - timedelta(days=7)
            ).scalar()
            
            # 최근 활동
            recent_submissions = self.db.query(func.count(CodeSubmission.id)).filter(
                CodeSubmission.submitted_at >= datetime.utcnow() - timedelta(days=7)
            ).scalar()
            
            return {
                **basic_stats,
                "total_submissions": total_submissions or 0,
                "average_acceptance_rate": round(float(avg_acceptance_rate or 0), 2),
                "recent_problems_7days": recent_problems or 0,
                "recent_submissions_7days": recent_submissions or 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting admin statistics: {str(e)}")
            raise

    def list_problems(
        self, 
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        search_query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "id",
        sort_order: str = "asc",
        include_stats: bool = False
    ) -> List[Dict[str, Any]]:
        """문제 목록 조회 (개선된 버전)"""
        try:
            query = self.db.query(CodeProblem).filter(CodeProblem.is_active == True)
            
            # 필터 적용
            if category:
                query = query.filter(CodeProblem.category == category)
            
            if difficulty:
                query = query.filter(CodeProblem.difficulty == difficulty)
            
            if search_query:
                query = query.filter(
                    or_(
                        CodeProblem.title.ilike(f"%{search_query}%"),
                        CodeProblem.description.ilike(f"%{search_query}%")
                    )
                )
            
            # 정렬
            if sort_by == "difficulty":
                # 난이도 순서: easy -> medium -> hard
                difficulty_order = func.case(
                    (CodeProblem.difficulty == 'easy', 1),
                    (CodeProblem.difficulty == 'medium', 2),
                    (CodeProblem.difficulty == 'hard', 3),
                    else_=4
                )
                if sort_order == "desc":
                    query = query.order_by(difficulty_order.desc())
                else:
                    query = query.order_by(difficulty_order.asc())
            elif sort_by == "acceptance_rate":
                if sort_order == "desc":
                    query = query.order_by(CodeProblem.acceptance_rate.desc())
                else:
                    query = query.order_by(CodeProblem.acceptance_rate.asc())
            else:
                # 기본 정렬 (id, title, created_at 등)
                column = getattr(CodeProblem, sort_by, CodeProblem.id)
                if sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
            
            # 페이지네이션
            problems = query.offset(offset).limit(limit).all()
            
            # 결과 변환
            result = []
            for problem in problems:
                problem_data = {
                    "id": problem.id,
                    "title": problem.title,
                    "difficulty": problem.difficulty,
                    "category": problem.category,
                    "acceptance_rate": problem.acceptance_rate,
                    "total_submissions": problem.total_submissions,
                    "solved": False,  # TODO: 사용자별 해결 여부 확인
                    "created_at": problem.created_at.isoformat() if problem.created_at else None
                }
                
                # 관리자용 추가 정보
                if include_stats:
                    problem_data.update({
                        "description": problem.description[:100] + "..." if len(problem.description) > 100 else problem.description,
                        "time_limit_ms": problem.time_limit_ms,
                        "memory_limit_mb": problem.memory_limit_mb,
                        "test_cases_count": len(problem.test_cases),
                        "updated_at": problem.updated_at.isoformat() if problem.updated_at else None
                    })
                
                result.append(problem_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing problems: {str(e)}")
            raise

# 전역 서비스 인스턴스를 생성하는 의존성 함수
def get_code_problem_service(db: Session = Depends(get_db)) -> CodeProblemService:
    return CodeProblemService(db)
