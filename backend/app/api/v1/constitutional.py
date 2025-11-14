# -*- coding: utf-8 -*-
"""
Constitutional AI API 엔드포인트

Safe Code Assistant 기능 제공
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.constitutional.safe_code_assistant import safe_code_assistant
from app.models.orm import User
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/api/v1/constitutional")


# ============================================================
# Pydantic 스키마
# ============================================================

class CodeReviewRequest(BaseModel):
    """코드 리뷰 요청"""
    code: str
    language: str  # python, javascript, sql 등
    user_level: Optional[str] = "beginner"  # beginner, intermediate, advanced


class VulnerabilityResponse(BaseModel):
    """보안 취약점 응답"""
    type: str
    severity: str
    line_number: Optional[int]
    description: str
    safe_alternative: str


class EthicalIssueResponse(BaseModel):
    """윤리적 문제 응답"""
    type: str
    description: str
    reason: str


class CodeReviewResponse(BaseModel):
    """코드 리뷰 응답"""
    safe_to_run: bool
    vulnerabilities: List[VulnerabilityResponse]
    ethical_issues: List[EthicalIssueResponse]
    educational_feedback: Optional[str]
    reviewed_at: datetime


class SocraticQuestionRequest(BaseModel):
    """소크라테스식 질문 요청"""
    student_question: str
    context: Optional[str] = None


# ============================================================
# API 엔드포인트
# ============================================================

@router.post("/review", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest,
    user: User = Depends(get_current_user)
):
    """
    코드 리뷰 (Constitutional AI 적용)
    
    **3단계 검증:**
    1. Safety - 보안 취약점 검사
    2. Ethics - 윤리적 문제 검사
    3. Education - 교육적 피드백 생성 (Claude)
    
    **요청 예시:**
    ```json
    {
      "code": "query = f\\"SELECT * FROM users WHERE id = {user_id}\\"",
      "language": "python",
      "user_level": "beginner"
    }
    ```
    
    **응답 예시:**
    ```json
    {
      "safe_to_run": false,
      "vulnerabilities": [
        {
          "type": "SQL_INJECTION",
          "severity": "critical",
          "line_number": 1,
          "description": "f-string in SQL query",
          "safe_alternative": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
        }
      ],
      "ethical_issues": [],
      "educational_feedback": "...",
      "reviewed_at": "2025-11-14T10:30:00Z"
    }
    ```
    """
    try:
        # Safe Code Assistant로 리뷰
        review = await safe_code_assistant.review_code(
            code=request.code,
            language=request.language,
            user_level=request.user_level
        )
        
        return review
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"코드 리뷰 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/socratic-question")
async def generate_socratic_question(
    request: SocraticQuestionRequest,
    user: User = Depends(get_current_user)
):
    """
    소크라테스식 질문 생성
    
    학생의 질문에 직접 답하지 않고,
    스스로 답을 찾도록 유도하는 역질문 생성
    
    **요청 예시:**
    ```json
    {
      "student_question": "for 루프가 뭔가요?",
      "context": "Python 기초 과정 - 반복문 섹션"
    }
    ```
    
    **응답 예시:**
    ```json
    {
      "question": "좋은 질문이에요! 먼저, 혹시 같은 작업을 여러 번 반복해야 했던 경험이 있나요?"
    }
    ```
    """
    try:
        from app.core.anthropic_client import anthropic_client
        
        question = await anthropic_client.generate_socratic_question(
            student_question=request.student_question,
            context=request.context
        )
        
        return {
            "question": question,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"소크라테스식 질문 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/principles")
async def get_constitutional_principles():
    """
    Constitutional AI 원칙 조회
    
    시스템이 따르는 4가지 핵심 원칙 반환
    """
    return {
        "principles": {
            "safety": {
                "title": "Safety (안전)",
                "description": "보안 취약점으로부터 학습자를 보호합니다",
                "checks": [
                    "SQL Injection",
                    "Command Injection",
                    "XSS",
                    "Unsafe Deserialization",
                    "Hardcoded Secrets",
                    "Weak Cryptography",
                    "Path Traversal"
                ]
            },
            "educational": {
                "title": "Educational (교육)",
                "description": "소크라테스식 질문으로 깊은 이해를 유도합니다",
                "methods": [
                    "직접적인 답 회피",
                    "질문으로 답하기",
                    "반례 제시",
                    "점진적 힌트",
                    "스스로 발견하도록 유도"
                ]
            },
            "ethical": {
                "title": "Ethical (윤리)",
                "description": "비윤리적 코드를 거부하고 대안을 제시합니다",
                "forbidden": [
                    "악성코드",
                    "무단 접근 도구",
                    "DDoS 공격",
                    "불법 크롤링",
                    "프라이버시 침해",
                    "저작권 침해",
                    "사기/기만 도구"
                ]
            },
            "helpful": {
                "title": "Helpful (도움)",
                "description": "학습자 레벨에 맞춰 긍정적으로 돕습니다",
                "features": [
                    "레벨별 맞춤 설명",
                    "긍정적 톤",
                    "격려와 성장 마인드셋",
                    "적응형 힌트"
                ]
            }
        },
        "version": "1.0.0",
        "documentation": "/docs/constitutional_principles.md"
    }


@router.get("/stats")
async def get_usage_stats(user: User = Depends(get_current_user)):
    """
    Constitutional AI 사용 통계
    
    (추후 구현: DB에 리뷰 로그 저장 후 통계 제공)
    """
    return {
        "message": "통계 기능은 추후 구현 예정입니다",
        "planned_metrics": [
            "총 코드 리뷰 횟수",
            "발견된 취약점 수 (타입별)",
            "윤리적 문제 차단 횟수",
            "학습자 레벨별 분포",
            "가장 많이 발견된 취약점 Top 5"
        ]
    }


@router.get("/health")
async def health_check():
    """
    Constitutional AI 시스템 상태 확인
    """
    from app.core.anthropic_client import anthropic_client
    
    status = {
        "status": "ok",
        "claude_api_configured": anthropic_client.client is not None,
        "default_model": anthropic_client.default_model,
        "available_models": list(anthropic_client.models.keys())
    }
    
    return status

