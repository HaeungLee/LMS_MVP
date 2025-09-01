"""
Code Execution API Routes
코드 실행 관련 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.services.code_execution_service import code_execution_service, TestCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/code", tags=["code"])

# Request/Response 모델들
class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    user_input: str = ""
    test_cases: Optional[List[Dict]] = None

class CodeExecutionResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: int
    memory_usage_mb: float
    test_results: Optional[List[Dict]] = None

class CodeProblem(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    category: str
    examples: List[Dict]
    constraints: List[str]
    hints: List[str]
    template: str
    time_limit: str = "10초"
    memory_limit: str = "128MB"

class CodeSubmissionRequest(BaseModel):
    code: str
    language: str = "python"

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """코드 실행 API"""
    
    try:
        # 지원되는 언어 확인
        if request.language != "python":
            raise HTTPException(
                status_code=400, 
                detail=f"언어 '{request.language}'은 아직 지원되지 않습니다. 현재 Python만 지원됩니다."
            )

        # 테스트 케이스 변환
        test_cases = None
        if request.test_cases:
            test_cases = [
                TestCase(
                    input_data=tc.get('input', ''),
                    expected_output=tc.get('expected_output', ''),
                    description=tc.get('description', '')
                )
                for tc in request.test_cases
            ]

        # 코드 실행
        result = await code_execution_service.execute_python_code(
            code=request.code,
            test_cases=test_cases,
            user_input=request.user_input
        )

        return CodeExecutionResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            execution_time_ms=result.execution_time_ms,
            memory_usage_mb=result.memory_usage_mb,
            test_results=result.test_results
        )

    except Exception as e:
        logger.error(f"Code execution API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"코드 실행 중 오류가 발생했습니다: {str(e)}")

@router.get("/problems/{problem_id}", response_model=CodeProblem)
async def get_problem(problem_id: int, db: Session = Depends(get_db)):
    """특정 문제 정보 조회"""
    
    # TODO: 실제 데이터베이스에서 문제 조회
    # 현재는 샘플 데이터 반환
    
    sample_problems = {
        1: {
            "id": 1,
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
            "time_limit": "10초",
            "memory_limit": "128MB"
        },
        2: {
            "id": 2,
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
            "time_limit": "10초", 
            "memory_limit": "128MB"
        }
    }
    
    if problem_id not in sample_problems:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
    
    return CodeProblem(**sample_problems[problem_id])

@router.get("/problems", response_model=List[Dict])
async def list_problems(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """문제 목록 조회"""
    
    # TODO: 실제 데이터베이스에서 문제 목록 조회
    # 현재는 샘플 데이터 반환
    
    sample_problems = [
        {
            "id": 1,
            "title": "두 수의 합",
            "difficulty": "easy",
            "category": "Python 기초",
            "solved": False,
            "acceptance_rate": 85.5
        },
        {
            "id": 2, 
            "title": "리스트 최댓값 찾기",
            "difficulty": "easy",
            "category": "Python 기초",
            "solved": False,
            "acceptance_rate": 72.3
        },
        {
            "id": 3,
            "title": "팩토리얼 계산",
            "difficulty": "medium",
            "category": "Python 기초",
            "solved": False,
            "acceptance_rate": 68.1
        }
    ]
    
    # 필터링 적용
    filtered_problems = sample_problems
    if category:
        filtered_problems = [p for p in filtered_problems if p['category'] == category]
    if difficulty:
        filtered_problems = [p for p in filtered_problems if p['difficulty'] == difficulty]
    
    # 페이지네이션 적용
    return filtered_problems[offset:offset + limit]

@router.post("/problems/{problem_id}/submit")
async def submit_code(
    problem_id: int,
    request: CodeSubmissionRequest,
    db: Session = Depends(get_db)
):
    """코드 제출 API"""
    
    try:
        # 문제 정보 조회
        problem = await get_problem(problem_id, db)
        
        # 숨겨진 테스트 케이스로 검증 (실제 구현시)
        # 현재는 예제 테스트 케이스로 검증
        test_cases = [
            TestCase(
                input_data=example['input'],
                expected_output=example['output'],
                description=example.get('explanation', '')
            )
            for example in problem.examples
        ]
        
        # 코드 실행
        result = await code_execution_service.execute_python_code(
            code=request.code,
            test_cases=test_cases
        )
        
        # 제출 결과 저장 (TODO: 데이터베이스에 저장)
        submission_data = {
            "problem_id": problem_id,
            "code": request.code,
            "language": request.language,
            "success": result.success,
            "execution_time_ms": result.execution_time_ms,
            "memory_usage_mb": result.memory_usage_mb,
            "test_results": result.test_results,
            "submitted_at": "2024-09-02T10:30:00Z"  # TODO: 실제 타임스탬프
        }
        
        return {
            "success": True,
            "submission_id": f"sub_{problem_id}_{hash(request.code) % 10000}",
            "result": result.success,
            "message": "제출이 완료되었습니다." if result.success else "일부 테스트 케이스에서 실패했습니다.",
            "execution_details": {
                "execution_time_ms": result.execution_time_ms,
                "memory_usage_mb": result.memory_usage_mb,
                "test_results": result.test_results
            }
        }

    except Exception as e:
        logger.error(f"Code submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제출 중 오류가 발생했습니다: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """지원되는 프로그래밍 언어 목록"""
    
    return {
        "languages": [
            {
                "id": "python",
                "name": "Python",
                "version": "3.11",
                "supported": True
            },
            {
                "id": "javascript", 
                "name": "JavaScript",
                "version": "Node.js 18",
                "supported": False  # 향후 지원 예정
            },
            {
                "id": "sql",
                "name": "SQL", 
                "version": "PostgreSQL 15",
                "supported": False  # 향후 지원 예정
            }
        ]
    }
