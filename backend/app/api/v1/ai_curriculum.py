"""
Phase 9: AI 커리큘럼 생성 API 엔드포인트
Enhanced Curriculum Generator와 Teaching Session 관리
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
import asyncio

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User
from app.models.ai_curriculum import AIGeneratedCurriculum, AITeachingSession
from app.services.enhanced_curriculum_generator import TwoAgentCurriculumGenerator
from app.services.langchain_curriculum_generator import LangChainTwoAgentCurriculumGenerator, LangChainEnhancedCurriculumManager
from app.services.streaming_handler import CurriculumStreamingHandler, SimpleStreamingHandler

router = APIRouter(prefix="/api/v1/ai-curriculum", tags=["AI Curriculum"])

# Pydantic 모델들
class CurriculumGenerationRequest(BaseModel):
    subject_key: str = Field(..., description="Phase 8 과목 키")
    learning_goals: List[str] = Field(..., description="학습 목표 리스트")
    difficulty_level: int = Field(..., ge=1, le=10, description="난이도 (1-10)")
    duration_preference: Optional[str] = Field(None, description="선호 학습 기간")
    special_requirements: Optional[List[str]] = Field(None, description="특별 요구사항")


class CurriculumResponse(BaseModel):
    id: int
    status: str
    subject_key: str
    learning_goals: List[str]
    difficulty_level: int
    generated_syllabus: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class TeachingSessionStartRequest(BaseModel):
    curriculum_id: int = Field(..., description="커리큘럼 ID")
    session_title: Optional[str] = Field(None, description="세션 제목")
    learning_preferences: Optional[Dict[str, Any]] = Field(None, description="학습 선호도")


class TeachingSessionResponse(BaseModel):
    id: int
    curriculum_id: int
    session_title: Optional[str]
    current_step: int
    total_steps: Optional[int]
    completion_percentage: float
    session_status: str
    started_at: datetime
    last_activity_at: datetime


# 의존성
def get_curriculum_generator():
    """커리큘럼 생성기 의존성"""
    return LangChainEnhancedCurriculumManager()


@router.post("/generate-curriculum", response_model=CurriculumResponse)
async def generate_dynamic_curriculum(
    request: CurriculumGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    generator: LangChainEnhancedCurriculumManager = Depends(get_curriculum_generator)
):
    """
    동적 커리큘럼 생성 API
    Phase 8 동적 과목 시스템과 연동하여 개인화된 커리큘럼 생성
    """
    try:
        # 백그라운드에서 커리큘럼 생성 시작
        curriculum_record, curriculum_data = await generator.generate_dynamic_curriculum(
            subject_key=request.subject_key,
            user_goals=request.learning_goals,
            difficulty_level=request.difficulty_level,
            user_id=current_user.id,
            db=db
        )
        
        return CurriculumResponse(
            id=curriculum_record.id,
            status=curriculum_record.status,
            subject_key=curriculum_record.subject_key,
            learning_goals=curriculum_record.learning_goals,
            difficulty_level=curriculum_record.difficulty_level,
            generated_syllabus=curriculum_record.generated_syllabus,
            created_at=curriculum_record.created_at,
            updated_at=curriculum_record.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커리큘럼 생성 실패: {str(e)}")


@router.post("/generate-curriculum-stream")
async def generate_curriculum_stream(
    request: CurriculumGenerationRequest,
    # current_user: User = Depends(get_current_user),  # 임시로 인증 제거
    db: Session = Depends(get_db)
):
    """실시간 스트리밍으로 AI 커리큘럼 생성"""
    
    async def curriculum_stream():
        """스트리밍 생성기"""
        streaming_handler = CurriculumStreamingHandler()
        
        try:
            # LangChain 생성기 가져오기
            generator = LangChainEnhancedCurriculumManager()
            
            # 데이터베이스에 초기 레코드 생성
            curriculum_record = AIGeneratedCurriculum(
                user_id=1,  # 임시로 test@test.com 사용자 ID
                subject_key=request.subject_key,
                learning_goals=request.learning_goals,
                difficulty_level=request.difficulty_level,
                status="generating"
            )
            db.add(curriculum_record)
            db.commit()
            db.refresh(curriculum_record)
            
            # 초기 응답 전송
            yield f"data: {json.dumps({'type': 'started', 'curriculum_id': curriculum_record.id, 'message': 'AI 커리큘럼 생성을 시작합니다...'})}\n\n"
            
            # LangChain 스트리밍으로 커리큘럼 생성
            print(f"🔥 LangChain 호출 시작 - curriculum_id: {curriculum_record.id}")
            yield f"data: {json.dumps({'type': 'token', 'content': '🔥 LangChain 연결 중...'})}\n\n"
            
            curriculum_result = await generator.generate_dynamic_curriculum_streaming(
                subject_key=request.subject_key,
                user_goals=request.learning_goals,
                difficulty_level=request.difficulty_level,
                user_id=1,  # 임시로 test@test.com 사용자 ID
                db=db,
                streaming_handler=streaming_handler
            )
            
            print(f"🎯 LangChain 호출 완료 - 결과: {type(curriculum_result)}")
            yield f"data: {json.dumps({'type': 'token', 'content': '✅ 커리큘럼 생성 완료!'})}\n\n"
            
            # 커리큘럼 결과를 토큰으로 분할하여 스트리밍 전송
            if curriculum_result and isinstance(curriculum_result, dict):
                curriculum_text = json.dumps(curriculum_result, ensure_ascii=False, indent=2)
                
                # 텍스트를 작은 청크로 분할하여 스트리밍
                chunk_size = 50  # 50자씩 분할
                for i in range(0, len(curriculum_text), chunk_size):
                    chunk = curriculum_text[i:i+chunk_size]
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.1)  # 0.1초 간격
                    
                # 완료 신호
                yield f"data: {json.dumps({'type': 'completed', 'message': '커리큘럼 생성이 완료되었습니다!'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': '커리큘럼 데이터를 가져올 수 없습니다.'})}\n\n"
            
            # 기존 스트리밍 핸들러 코드 (임시 비활성화)
            # 스트리밍 데이터 전송
            # async for chunk in streaming_handler.get_stream():
            #     yield f"data: {json.dumps(chunk)}\n\n"
            #     
            #     # 완료 시 데이터베이스 업데이트
            #     if chunk.get("type") == "completed":
            #         curriculum_record.generated_syllabus = curriculum_result
            #         curriculum_record.status = "completed"
            #         db.commit()
            #         
            #         # 최종 완료 메시지
            #         yield f"data: {json.dumps({'type': 'final_complete', 'curriculum_id': curriculum_record.id, 'message': '커리큘럼이 성공적으로 생성되었습니다!'})}\n\n"
            #         break
            
            # 데이터베이스 업데이트
            curriculum_record.generated_syllabus = curriculum_result
            curriculum_record.status = "completed"
            db.commit()
                    
        except Exception as e:
            # 에러 발생 시
            error_message = f"커리큘럼 생성 중 오류: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_message})}\n\n"
            
            if 'curriculum_record' in locals():
                curriculum_record.status = "failed"
                curriculum_record.generation_metadata = {"error": str(e)}
                db.commit()
    
    return StreamingResponse(
        curriculum_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )


@router.get("/curricula", response_model=List[CurriculumResponse])
async def get_user_curricula(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    generator: LangChainEnhancedCurriculumManager = Depends(get_curriculum_generator)
):
    """사용자의 커리큘럼 목록 조회"""
    try:
        curricula = await generator.get_user_curricula(current_user.id, db)
        
        return [
            CurriculumResponse(
                id=curriculum.id,
                status=curriculum.status,
                subject_key=curriculum.subject_key,
                learning_goals=curriculum.learning_goals,
                difficulty_level=curriculum.difficulty_level,
                generated_syllabus=curriculum.generated_syllabus,
                created_at=curriculum.created_at,
                updated_at=curriculum.updated_at
            )
            for curriculum in curricula
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커리큘럼 목록 조회 실패: {str(e)}")


@router.get("/curricula/{curriculum_id}", response_model=CurriculumResponse)
async def get_curriculum_detail(
    curriculum_id: int,
    # current_user: User = Depends(get_current_user),  # 임시로 인증 제거
    db: Session = Depends(get_db),
    generator: LangChainEnhancedCurriculumManager = Depends(get_curriculum_generator)
):
    """커리큘럼 상세 정보 조회"""
    try:
        curriculum = await generator.get_curriculum_by_id(curriculum_id, db)
        
        if not curriculum:
            raise HTTPException(status_code=404, detail="커리큘럼을 찾을 수 없습니다")
        
        # 권한 확인 (본인 커리큘럼만 조회 가능) - 임시로 비활성화
        # if curriculum.user_id != current_user.id and current_user.role != "admin":
        #     raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
        
        return CurriculumResponse(
            id=curriculum.id,
            status=curriculum.status,
            subject_key=curriculum.subject_key,
            learning_goals=curriculum.learning_goals,
            difficulty_level=curriculum.difficulty_level,
            generated_syllabus=curriculum.generated_syllabus,
            created_at=curriculum.created_at,
            updated_at=curriculum.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커리큘럼 조회 실패: {str(e)}")


@router.post("/teaching-sessions", response_model=TeachingSessionResponse)
async def start_teaching_session(
    request: TeachingSessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI 교육 세션 시작"""
    try:
        # 커리큘럼 존재 확인 및 권한 검증
        curriculum = db.query(AIGeneratedCurriculum).filter(
            AIGeneratedCurriculum.id == request.curriculum_id,
            AIGeneratedCurriculum.user_id == current_user.id
        ).first()
        
        if not curriculum:
            raise HTTPException(status_code=404, detail="커리큘럼을 찾을 수 없거나 권한이 없습니다")
        
        if curriculum.status != "completed":
            raise HTTPException(status_code=400, detail="완성되지 않은 커리큘럼입니다")
        
        # 교육 세션 생성
        session = AITeachingSession(
            curriculum_id=request.curriculum_id,
            user_id=current_user.id,
            session_title=request.session_title or f"{curriculum.subject_key} 학습 세션",
            conversation_history=[],
            current_step=1,
            total_steps=len(curriculum.generated_syllabus.get("steps", [])) if curriculum.generated_syllabus else None,
            completion_percentage=0.0,
            session_status="active",
            teaching_metadata=request.learning_preferences
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return TeachingSessionResponse(
            id=session.id,
            curriculum_id=session.curriculum_id,
            session_title=session.session_title,
            current_step=session.current_step,
            total_steps=session.total_steps,
            completion_percentage=session.completion_percentage,
            session_status=session.session_status,
            started_at=session.started_at,
            last_activity_at=session.last_activity_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교육 세션 시작 실패: {str(e)}")


@router.get("/teaching-sessions", response_model=List[TeachingSessionResponse])
async def get_user_teaching_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """사용자의 교육 세션 목록 조회"""
    try:
        query = db.query(AITeachingSession).filter(AITeachingSession.user_id == current_user.id)
        
        if status:
            query = query.filter(AITeachingSession.session_status == status)
        
        sessions = query.order_by(AITeachingSession.last_activity_at.desc()).all()
        
        return [
            TeachingSessionResponse(
                id=session.id,
                curriculum_id=session.curriculum_id,
                session_title=session.session_title,
                current_step=session.current_step,
                total_steps=session.total_steps,
                completion_percentage=session.completion_percentage,
                session_status=session.session_status,
                started_at=session.started_at,
                last_activity_at=session.last_activity_at
            )
            for session in sessions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교육 세션 목록 조회 실패: {str(e)}")


@router.get("/teaching-sessions/{session_id}", response_model=TeachingSessionResponse)
async def get_teaching_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """교육 세션 상세 정보 조회"""
    try:
        session = db.query(AITeachingSession).filter(
            AITeachingSession.id == session_id,
            AITeachingSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="교육 세션을 찾을 수 없습니다")
        
        return TeachingSessionResponse(
            id=session.id,
            curriculum_id=session.curriculum_id,
            session_title=session.session_title,
            current_step=session.current_step,
            total_steps=session.total_steps,
            completion_percentage=session.completion_percentage,
            session_status=session.session_status,
            started_at=session.started_at,
            last_activity_at=session.last_activity_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교육 세션 조회 실패: {str(e)}")


@router.delete("/curricula/{curriculum_id}")
async def delete_curriculum(
    curriculum_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """커리큘럼 삭제"""
    try:
        curriculum = db.query(AIGeneratedCurriculum).filter(
            AIGeneratedCurriculum.id == curriculum_id,
            AIGeneratedCurriculum.user_id == current_user.id
        ).first()
        
        if not curriculum:
            raise HTTPException(status_code=404, detail="커리큘럼을 찾을 수 없습니다")
        
        # 관련 교육 세션들도 함께 삭제
        db.query(AITeachingSession).filter(
            AITeachingSession.curriculum_id == curriculum_id
        ).delete()
        
        db.delete(curriculum)
        db.commit()
        
        return {"message": "커리큘럼이 성공적으로 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커리큘럼 삭제 실패: {str(e)}")
