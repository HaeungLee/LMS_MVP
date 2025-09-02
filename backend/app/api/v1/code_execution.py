"""
Code Execution API Routes
코드 실행 관련 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.services.code_execution_service import code_execution_service, TestCase
from app.services.code_problem_service import CodeProblemService, get_code_problem_service
from app.services.database_migration_service import DatabaseMigrationService, get_migration_service
from app.models.code_problem import CodeProblem as CodeProblemModel

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
async def get_problem(problem_id: int, problem_service: CodeProblemService = Depends(get_code_problem_service)):
    """특정 문제 정보 조회"""
    
    try:
        problem = problem_service.get_problem(problem_id, include_hidden_tests=False)
        if not problem:
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
        
        # 응답 모델에 맞게 변환
        return CodeProblem(
            id=problem.id,
            title=problem.title,
            description=problem.description,
            difficulty=problem.difficulty,
            category=problem.category,
            examples=problem.examples,
            constraints=problem.constraints,
            hints=problem.hints,
            template=problem.template or "",
            time_limit=f"{problem.time_limit_ms/1000}초",
            memory_limit=f"{problem.memory_limit_mb}MB"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="문제 조회 중 오류가 발생했습니다.")

@router.get("/problems", response_model=List[Dict])
async def list_problems(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "id",
    sort_order: str = "asc",
    problem_service: CodeProblemService = Depends(get_code_problem_service)
):
    """문제 목록 조회"""
    
    try:
        problems = problem_service.list_problems(
            category=category,
            difficulty=difficulty,
            search_query=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return problems
        
    except Exception as e:
        logger.error(f"Error listing problems: {str(e)}")
        raise HTTPException(status_code=500, detail="문제 목록 조회 중 오류가 발생했습니다.")

@router.post("/problems/{problem_id}/submit")
async def submit_code(
    problem_id: int,
    request: CodeSubmissionRequest,
    problem_service: CodeProblemService = Depends(get_code_problem_service)
):
    """코드 제출 API"""
    
    try:
        # 문제 정보 조회 (숨겨진 테스트 케이스 포함)
        problem = problem_service.get_problem(problem_id, include_hidden_tests=True)
        if not problem:
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
        
        # 테스트 케이스 변환
        test_cases = [
            TestCase(
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                description=tc.description or ''
            )
            for tc in problem.test_cases
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

    except HTTPException:
        raise
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

@router.get("/categories")
async def get_categories(problem_service: CodeProblemService = Depends(get_code_problem_service)):
    """문제 카테고리 목록 조회"""
    
    try:
        categories = problem_service.get_categories()
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="카테고리 조회 중 오류가 발생했습니다.")

@router.get("/statistics")
async def get_statistics(problem_service: CodeProblemService = Depends(get_code_problem_service)):
    """문제 통계 조회"""
    
    try:
        stats = problem_service.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="통계 조회 중 오류가 발생했습니다.")

# === 관리자 전용 API ===

class CreateProblemRequest(BaseModel):
    title: str
    description: str
    difficulty: str  # easy, medium, hard
    category: str
    examples: List[Dict[str, Any]]
    constraints: List[str]
    hints: List[str]
    template: Optional[str] = ""
    time_limit_ms: Optional[int] = 10000
    memory_limit_mb: Optional[int] = 128
    test_cases: List[Dict[str, Any]]

class UpdateProblemRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    category: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None
    constraints: Optional[List[str]] = None
    hints: Optional[List[str]] = None
    template: Optional[str] = None
    time_limit_ms: Optional[int] = None
    memory_limit_mb: Optional[int] = None
    test_cases: Optional[List[Dict[str, Any]]] = None

@router.post("/admin/problems", status_code=status.HTTP_201_CREATED)
async def create_problem(
    request: CreateProblemRequest,
    problem_service: CodeProblemService = Depends(get_code_problem_service)
    # TODO: 현재 사용자 인증 및 관리자 권한 확인 추가
):
    """새 문제 생성 (관리자 전용)"""
    
    try:
        # TODO: 현재 사용자 ID 가져오기 (인증 구현 후)
        created_by_id = 1  # 임시로 하드코딩
        
        problem_data = {
            "title": request.title,
            "description": request.description,
            "difficulty": request.difficulty,
            "category": request.category,
            "examples": request.examples,
            "constraints": request.constraints,
            "hints": request.hints,
            "template": request.template,
            "time_limit_ms": request.time_limit_ms,
            "memory_limit_mb": request.memory_limit_mb,
            "test_cases": request.test_cases
        }
        
        problem = problem_service.create_problem(problem_data, created_by_id)
        
        return {
            "success": True,
            "message": "문제가 성공적으로 생성되었습니다.",
            "problem_id": problem.id
        }
        
    except Exception as e:
        logger.error(f"Error creating problem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/admin/problems/{problem_id}")
async def get_admin_problem(
    problem_id: int,
    problem_service: CodeProblemService = Depends(get_code_problem_service)
    # TODO: 관리자 권한 확인 추가
):
    """관리자용 문제 상세 조회 (숨겨진 테스트 케이스 포함)"""
    
    try:
        problem = problem_service.get_problem(problem_id, include_hidden_tests=True)
        if not problem:
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
        
        # 테스트 케이스 정보 포함
        test_cases = [
            {
                "id": tc.id,
                "input_data": tc.input_data,
                "expected_output": tc.expected_output,
                "description": tc.description,
                "is_hidden": tc.is_hidden,
                "is_sample": tc.is_sample,
                "weight": tc.weight
            }
            for tc in problem.test_cases
        ]
        
        return {
            "id": problem.id,
            "title": problem.title,
            "description": problem.description,
            "difficulty": problem.difficulty,
            "category": problem.category,
            "examples": problem.examples,
            "constraints": problem.constraints,
            "hints": problem.hints,
            "template": problem.template,
            "time_limit_ms": problem.time_limit_ms,
            "memory_limit_mb": problem.memory_limit_mb,
            "test_cases": test_cases,
            "statistics": {
                "total_submissions": problem.total_submissions,
                "accepted_submissions": problem.accepted_submissions,
                "acceptance_rate": problem.acceptance_rate
            },
            "created_at": problem.created_at.isoformat() if problem.created_at else None,
            "updated_at": problem.updated_at.isoformat() if problem.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="문제 조회 중 오류가 발생했습니다.")

@router.put("/admin/problems/{problem_id}")
async def update_problem(
    problem_id: int,
    request: UpdateProblemRequest,
    problem_service: CodeProblemService = Depends(get_code_problem_service)
    # TODO: 관리자 권한 확인 추가
):
    """문제 수정 (관리자 전용)"""
    
    try:
        # 수정할 데이터만 추출
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")
        
        problem = problem_service.update_problem(problem_id, update_data)
        if not problem:
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
        
        return {
            "success": True,
            "message": "문제가 성공적으로 수정되었습니다.",
            "problem_id": problem.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/admin/problems/{problem_id}")
async def delete_problem(
    problem_id: int,
    problem_service: CodeProblemService = Depends(get_code_problem_service)
    # TODO: 관리자 권한 확인 추가
):
    """문제 삭제 (관리자 전용)"""
    
    try:
        success = problem_service.delete_problem(problem_id)
        if not success:
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
        
        return {
            "success": True,
            "message": "문제가 성공적으로 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 삭제 중 오류가 발생했습니다: {str(e)}")

@router.post("/admin/migrate-sample-problems")
async def migrate_sample_problems(
    problem_service: CodeProblemService = Depends(get_code_problem_service)
    # TODO: 관리자 권한 확인 추가
):
    """샘플 문제를 데이터베이스로 마이그레이션 (관리자 전용)"""
    
    try:
        # TODO: 현재 사용자 ID 가져오기
        created_by_id = 1  # 임시로 하드코딩
        
        problem_service.migrate_sample_problems(created_by_id)
        return {
            "success": True,
            "message": "샘플 문제가 성공적으로 마이그레이션되었습니다."
        }
        
    except Exception as e:
        logger.error(f"Error migrating sample problems: {str(e)}")
        raise HTTPException(status_code=500, detail=f"마이그레이션 중 오류가 발생했습니다: {str(e)}")


# ========== 데이터베이스 마이그레이션 API ==========

@router.post("/admin/db/create-tables")
async def create_code_problem_tables(
    migration_service: DatabaseMigrationService = Depends(get_migration_service)
):
    """코딩테스트 관련 데이터베이스 테이블 생성"""
    try:
        success = migration_service.create_tables()
        
        if success:
            return {
                "success": True,
                "message": "코딩테스트 테이블이 성공적으로 생성되었습니다."
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail="테이블 생성에 실패했습니다."
            )
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"테이블 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/admin/db/check-tables")
async def check_tables_status(
    migration_service: DatabaseMigrationService = Depends(get_migration_service)
):
    """코딩테스트 관련 테이블 존재 여부 확인"""
    try:
        table_status = migration_service.check_tables_exist()
        
        return {
            "success": True,
            "tables": table_status,
            "all_exist": all(table_status.values()) if table_status else False
        }
        
    except Exception as e:
        logger.error(f"Error checking tables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"테이블 확인 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/admin/db/migrate-samples")
async def migrate_sample_problems_to_db(
    created_by_id: int = 1,
    migration_service: DatabaseMigrationService = Depends(get_migration_service)
):
    """하드코딩된 샘플 문제들을 데이터베이스로 마이그레이션"""
    try:
        success = migration_service.migrate_sample_problems(created_by_id)
        
        if success:
            return {
                "success": True,
                "message": "샘플 문제가 성공적으로 데이터베이스로 마이그레이션되었습니다."
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="샘플 문제 마이그레이션에 실패했습니다."
            )
        
    except Exception as e:
        logger.error(f"Error migrating sample problems: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"샘플 문제 마이그레이션 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/admin/db/create-tags")
async def create_default_tags(
    migration_service: DatabaseMigrationService = Depends(get_migration_service)
):
    """기본 문제 태그들 생성"""
    try:
        success = migration_service.create_default_tags()
        
        if success:
            return {
                "success": True,
                "message": "기본 태그가 성공적으로 생성되었습니다."
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="기본 태그 생성에 실패했습니다."
            )
        
    except Exception as e:
        logger.error(f"Error creating default tags: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"기본 태그 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/admin/db/full-migration")
async def full_database_migration(
    created_by_id: int = 1,
    migration_service: DatabaseMigrationService = Depends(get_migration_service)
):
    """전체 데이터베이스 마이그레이션 (테이블 생성 + 샘플 데이터 + 태그)"""
    try:
        results = {}
        
        # 1. 테이블 생성
        table_creation = migration_service.create_tables()
        results["table_creation"] = table_creation
        
        # 2. 기본 태그 생성
        tag_creation = migration_service.create_default_tags()
        results["tag_creation"] = tag_creation
        
        # 3. 샘플 문제 마이그레이션
        sample_migration = migration_service.migrate_sample_problems(created_by_id)
        results["sample_migration"] = sample_migration
        
        # 4. 테이블 상태 확인
        table_status = migration_service.check_tables_exist()
        results["table_status"] = table_status
        
        success = all([table_creation, tag_creation, sample_migration])
        
        return {
            "success": success,
            "message": "전체 데이터베이스 마이그레이션이 완료되었습니다." if success else "일부 마이그레이션이 실패했습니다.",
            "details": results
        }
        
    except Exception as e:
        logger.error(f"Error in full migration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"전체 마이그레이션 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/admin/db/drop-tables")
async def drop_code_problem_tables(
    migration_service: DatabaseMigrationService = Depends(get_migration_service)
):
    """코딩테스트 관련 테이블 삭제 (개발용)"""
    try:
        success = migration_service.drop_tables()
        
        if success:
            return {
                "success": True,
                "message": "코딩테스트 테이블이 성공적으로 삭제되었습니다."
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="테이블 삭제에 실패했습니다."
            )
        
    except Exception as e:
        logger.error(f"Error dropping tables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"테이블 삭제 중 오류가 발생했습니다: {str(e)}"
        )


# ========== 추가 관리자 API ==========

@router.get("/admin/problems")
async def list_admin_problems(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    problem_service: CodeProblemService = Depends(get_code_problem_service)
):
    """관리자용 문제 목록 조회 (통계 포함)"""
    
    try:
        problems = problem_service.list_problems(
            category=category,
            difficulty=difficulty,
            search_query=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            include_stats=True
        )
        
        return problems
        
    except Exception as e:
        logger.error(f"Error listing admin problems: {str(e)}")
        raise HTTPException(status_code=500, detail="문제 목록 조회 중 오류가 발생했습니다.")


@router.get("/admin/tags")
async def list_admin_tags(
    migration_service: DatabaseMigrationService = Depends(get_migration_service)
):
    """관리자용 태그 목록 조회"""
    
    try:
        db = migration_service.SessionLocal()
        
        # ProblemTag 임포트를 위해 직접 쿼리
        from app.models.code_problem import ProblemTag
        tags = db.query(ProblemTag).all()
        
        tag_list = [
            {
                "id": tag.id,
                "name": tag.name,
                "description": tag.description,
                "color": tag.color,
                "created_at": tag.created_at.isoformat() if tag.created_at else None
            }
            for tag in tags
        ]
        
        return tag_list
        
    except Exception as e:
        logger.error(f"Error listing admin tags: {str(e)}")
        raise HTTPException(status_code=500, detail="태그 목록 조회 중 오류가 발생했습니다.")
    finally:
        db.close()


@router.delete("/admin/problems/{problem_id}")
async def delete_problem(
    problem_id: int,
    problem_service: CodeProblemService = Depends(get_code_problem_service)
):
    """문제 삭제 (관리자 전용)"""
    
    try:
        success = problem_service.delete_problem(problem_id)
        
        if success:
            return {
                "success": True,
                "message": "문제가 성공적으로 삭제되었습니다."
            }
        else:
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting problem {problem_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="문제 삭제 중 오류가 발생했습니다.")


@router.get("/admin/statistics")
async def get_admin_statistics(
    problem_service: CodeProblemService = Depends(get_code_problem_service)
):
    """관리자용 전체 통계 조회"""
    
    try:
        stats = problem_service.get_admin_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting admin statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="통계 조회 중 오류가 발생했습니다.")
