"""
Code Execution Service
코드 실행을 위한 보안 서비스
"""
import asyncio
import subprocess
import tempfile
import os
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    memory_usage_mb: float = 0.0
    test_results: Optional[List[Dict]] = None

@dataclass
class TestCase:
    input_data: str
    expected_output: str
    description: Optional[str] = None

class CodeExecutionService:
    """안전한 코드 실행 서비스"""
    
    # 보안 설정
    BLOCKED_IMPORTS = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests', 
        'eval', 'exec', 'open', 'file', '__import__', 'globals', 
        'locals', 'vars', 'dir', 'help', 'input', 'raw_input'
    }
    
    RESOURCE_LIMITS = {
        'timeout': 10,      # 10초 제한
        'memory': 128,      # 128MB 제한 
        'output_size': 1024 # 1KB 출력 제한
    }

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    async def execute_python_code(
        self, 
        code: str, 
        test_cases: List[TestCase] = None,
        user_input: str = ""
    ) -> ExecutionResult:
        """Python 코드 실행"""
        
        try:
            # 보안 검증
            if not self._validate_code_safety(code):
                return ExecutionResult(
                    success=False,
                    error="보안상 허용되지 않는 코드가 포함되어 있습니다."
                )

            # 코드 실행
            if test_cases:
                return await self._execute_with_test_cases(code, test_cases)
            else:
                return await self._execute_single(code, user_input)

        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return ExecutionResult(
                success=False,
                error=f"실행 중 오류가 발생했습니다: {str(e)}"
            )

    def _validate_code_safety(self, code: str) -> bool:
        """코드 안전성 검증"""
        
        # 블록된 키워드 검사
        for blocked in self.BLOCKED_IMPORTS:
            if blocked in code:
                # 더 정교한 검사 (단순 문자열 포함이 아닌 실제 import/사용 여부)
                if f"import {blocked}" in code or f"from {blocked}" in code:
                    return False
                if f"{blocked}(" in code:
                    return False
        
        # 위험한 패턴 검사
        dangerous_patterns = [
            '__import__',
            'exec(',
            'eval(',
            'open(',
            'file(',
            'subprocess',
            'os.system',
            'os.popen'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return False
                
        return True

    async def _execute_single(self, code: str, user_input: str = "") -> ExecutionResult:
        """단일 코드 실행"""
        
        start_time = time.time()
        
        try:
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # Python 실행 명령어
            cmd = ['python', temp_file]
            
            # 프로세스 실행
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir
            )

            try:
                # 실행 및 결과 수집
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=user_input.encode()),
                    timeout=self.RESOURCE_LIMITS['timeout']
                )
                
                execution_time = int((time.time() - start_time) * 1000)
                
                # 결과 처리
                if process.returncode == 0:
                    output = stdout.decode('utf-8')
                    if len(output) > self.RESOURCE_LIMITS['output_size']:
                        output = output[:self.RESOURCE_LIMITS['output_size']] + "\n... (출력이 너무 깁니다)"
                    
                    return ExecutionResult(
                        success=True,
                        output=output,
                        execution_time_ms=execution_time,
                        memory_usage_mb=0.0  # TODO: 실제 메모리 사용량 측정
                    )
                else:
                    error = stderr.decode('utf-8')
                    return ExecutionResult(
                        success=False,
                        error=error,
                        execution_time_ms=execution_time
                    )

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    success=False,
                    error=f"실행 시간이 {self.RESOURCE_LIMITS['timeout']}초를 초과했습니다."
                )

        finally:
            # 임시 파일 정리
            if 'temp_file' in locals():
                try:
                    os.unlink(temp_file)
                except:
                    pass

    async def _execute_with_test_cases(self, code: str, test_cases: List[TestCase]) -> ExecutionResult:
        """테스트 케이스와 함께 코드 실행"""
        
        test_results = []
        total_execution_time = 0
        
        for i, test_case in enumerate(test_cases):
            result = await self._execute_single(code, test_case.input_data)
            
            if not result.success:
                return ExecutionResult(
                    success=False,
                    error=f"테스트 케이스 {i+1} 실행 실패: {result.error}",
                    test_results=test_results
                )
            
            total_execution_time += result.execution_time_ms
            actual_output = result.output.strip()
            expected_output = test_case.expected_output.strip()
            
            test_result = {
                'test_case': i + 1,
                'input': test_case.input_data,
                'expected_output': expected_output,
                'actual_output': actual_output,
                'passed': actual_output == expected_output,
                'description': test_case.description,
                'execution_time_ms': result.execution_time_ms
            }
            
            test_results.append(test_result)

        # 모든 테스트 통과 여부 확인
        all_passed = all(result['passed'] for result in test_results)
        
        return ExecutionResult(
            success=all_passed,
            output=f"테스트 케이스 {len([r for r in test_results if r['passed']])}/{len(test_cases)} 통과",
            execution_time_ms=total_execution_time,
            test_results=test_results
        )

# 전역 서비스 인스턴스
code_execution_service = CodeExecutionService()
