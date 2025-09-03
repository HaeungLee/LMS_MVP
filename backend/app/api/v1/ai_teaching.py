"""
Phase 9 Week 3: AI Teaching Session API
실시간 대화형 교육 세션 관리 API
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import json
import asyncio

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User
from app.models.ai_curriculum import AITeachingSession, AIGeneratedCurriculum
from app.services.syllabus_based_teaching_agent import syllabus_based_teaching_agent

router = APIRouter(prefix="/api/v1/ai-teaching", tags=["AI Teaching"])

# Pydantic 모델들
class TeachingSessionStartRequest(BaseModel):
    curriculum_id: int = Field(..., description="커리큘럼 ID")
    session_preferences: Optional[Dict[str, Any]] = Field(None, description="세션 선호도")


class TeachingMessage(BaseModel):
    session_id: int = Field(..., description="세션 ID")
    message: str = Field(..., description="사용자 메시지")
    message_type: str = Field(default="text", description="메시지 타입")


class TeachingSessionResponse(BaseModel):
    id: int
    curriculum_id: int
    session_title: str
    current_step: int
    total_steps: int
    completion_percentage: float
    session_status: str
    started_at: datetime
    last_activity_at: datetime
    conversation_preview: Optional[str] = None


class TeachingChatResponse(BaseModel):
    session_id: int
    message: str
    current_step: int
    step_title: str
    understanding_check: Optional[str]
    next_action: str
    progress_percentage: float
    learning_tips: Optional[List[str]]
    difficulty_adjustment: Optional[str]
    timestamp: datetime


# WebSocket 연결 관리자
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: int):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: int):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: dict, session_id: int):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)


manager = ConnectionManager()


# 누락된 API 엔드포인트들 추가


@router.post("/sessions/start", response_model=TeachingSessionResponse)
async def start_teaching_session(
    request: TeachingSessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI 교육 세션 시작"""
    try:
        session, first_message = await syllabus_based_teaching_agent.start_teaching_session(
            curriculum_id=request.curriculum_id,
            user_id=current_user.id,
            db=db
        )
        
        # 커리큘럼 정보 조회
        curriculum = db.query(AIGeneratedCurriculum).filter(
            AIGeneratedCurriculum.id == request.curriculum_id
        ).first()
        
        return TeachingSessionResponse(
            id=session.id,
            curriculum_id=session.curriculum_id,
            session_title=session.session_title,
            current_step=session.current_step,
            total_steps=session.total_steps,
            completion_percentage=session.completion_percentage,
            session_status=session.session_status,
            started_at=session.started_at,
            last_activity_at=session.last_activity_at,
            conversation_preview=first_message.get("message", "")[:100] + "..."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교육 세션 시작 실패: {str(e)}")


@router.post("/sessions/{session_id}/message", response_model=TeachingChatResponse)
async def send_teaching_message(
    session_id: int,
    request: TeachingMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """교육 세션 메시지 전송"""
    try:
        session, response = await syllabus_based_teaching_agent.continue_teaching(
            session_id=session_id,
            user_message=request.message,
            user_id=current_user.id,
            db=db
        )
        
        return TeachingChatResponse(
            session_id=session.id,
            message=response.get("message", ""),
            current_step=response.get("current_step", session.current_step),
            step_title=response.get("step_title", ""),
            understanding_check=response.get("understanding_check"),
            next_action=response.get("next_action", "continue"),
            progress_percentage=response.get("progress_percentage", session.completion_percentage),
            learning_tips=response.get("learning_tips"),
            difficulty_adjustment=response.get("difficulty_adjustment"),
            timestamp=datetime.fromisoformat(response.get("timestamp", datetime.utcnow().isoformat()))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메시지 처리 실패: {str(e)}")


@router.get("/sessions", response_model=List[TeachingSessionResponse])
async def get_user_teaching_sessions(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """사용자의 교육 세션 목록 조회"""
    try:
        query = db.query(AITeachingSession).filter(AITeachingSession.user_id == current_user.id)
        
        if status:
            query = query.filter(AITeachingSession.session_status == status)
        
        sessions = query.order_by(AITeachingSession.last_activity_at.desc()).all()
        
        results = []
        for session in sessions:
            # 대화 미리보기 생성
            conversation_preview = None
            if session.conversation_history:
                last_message = session.conversation_history[-1]
                if isinstance(last_message, dict):
                    preview_text = last_message.get("message", "")
                    conversation_preview = preview_text[:100] + "..." if len(preview_text) > 100 else preview_text
            
            results.append(TeachingSessionResponse(
                id=session.id,
                curriculum_id=session.curriculum_id,
                session_title=session.session_title,
                current_step=session.current_step,
                total_steps=session.total_steps,
                completion_percentage=session.completion_percentage,
                session_status=session.session_status,
                started_at=session.started_at,
                last_activity_at=session.last_activity_at,
                conversation_preview=conversation_preview
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 목록 조회 실패: {str(e)}")


@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_teaching_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    include_conversation: bool = True
):
    """교육 세션 상세 정보 조회"""
    try:
        session = db.query(AITeachingSession).filter(
            AITeachingSession.id == session_id,
            AITeachingSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="교육 세션을 찾을 수 없습니다")
        
        # 커리큘럼 정보 조회
        curriculum = db.query(AIGeneratedCurriculum).filter(
            AIGeneratedCurriculum.id == session.curriculum_id
        ).first()
        
        result = {
            "session": {
                "id": session.id,
                "curriculum_id": session.curriculum_id,
                "session_title": session.session_title,
                "current_step": session.current_step,
                "total_steps": session.total_steps,
                "completion_percentage": session.completion_percentage,
                "session_status": session.session_status,
                "started_at": session.started_at.isoformat(),
                "last_activity_at": session.last_activity_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            },
            "curriculum": {
                "title": curriculum.generated_syllabus.get("title") if curriculum else "알 수 없음",
                "description": curriculum.generated_syllabus.get("description") if curriculum else "",
                "steps": curriculum.generated_syllabus.get("steps", []) if curriculum else []
            }
        }
        
        if include_conversation:
            result["conversation_history"] = session.conversation_history or []
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 상세 조회 실패: {str(e)}")


@router.patch("/sessions/{session_id}/pause")
async def pause_teaching_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """교육 세션 일시정지"""
    try:
        success = await syllabus_based_teaching_agent.pause_session(
            session_id=session_id,
            user_id=current_user.id,
            db=db
        )
        
        if success:
            return {"message": "세션이 일시정지되었습니다"}
        else:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 일시정지 실패: {str(e)}")


@router.patch("/sessions/{session_id}/resume")
async def resume_teaching_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """교육 세션 재개"""
    try:
        success = await syllabus_based_teaching_agent.resume_session(
            session_id=session_id,
            user_id=current_user.id,
            db=db
        )
        
        if success:
            return {"message": "세션이 재개되었습니다"}
        else:
            raise HTTPException(status_code=404, detail="일시정지된 세션을 찾을 수 없습니다")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 재개 실패: {str(e)}")


@router.websocket("/sessions/{session_id}/ws")
async def websocket_teaching_session(
    websocket: WebSocket,
    session_id: int,
    user_id: int,  # 실제로는 토큰에서 파싱해야 함
    db: Session = Depends(get_db)
):
    """실시간 교육 세션 WebSocket"""
    await manager.connect(websocket, user_id, session_id)
    
    try:
        # 세션 존재 확인
        session = db.query(AITeachingSession).filter(
            AITeachingSession.id == session_id,
            AITeachingSession.user_id == user_id
        ).first()
        
        if not session:
            await websocket.close(code=4004, reason="Session not found")
            return
        
        # 연결 확인 메시지
        await manager.send_personal_message({
            "type": "connection_confirmed",
            "session_id": session_id,
            "message": "실시간 교육 세션에 연결되었습니다!"
        }, user_id)
        
        while True:
            # 사용자 메시지 수신
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat_message":
                user_message = message_data.get("message", "")
                
                # AI 강사 응답 생성
                updated_session, response = await syllabus_based_teaching_agent.continue_teaching(
                    session_id=session_id,
                    user_message=user_message,
                    user_id=user_id,
                    db=db
                )
                
                # 응답 전송
                await manager.send_personal_message({
                    "type": "ai_response",
                    "session_id": session_id,
                    "response": response,
                    "session_update": {
                        "current_step": updated_session.current_step,
                        "completion_percentage": updated_session.completion_percentage,
                        "session_status": updated_session.session_status
                    }
                }, user_id)
                
            elif message_data.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id, session_id)
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": f"오류가 발생했습니다: {str(e)}"
        }, user_id)
        manager.disconnect(user_id, session_id)


@router.get("/sessions/{session_id}/progress")
async def get_session_progress(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """교육 세션 진도 조회"""
    try:
        session = db.query(AITeachingSession).filter(
            AITeachingSession.id == session_id,
            AITeachingSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="교육 세션을 찾을 수 없습니다")
        
        # 커리큘럼 정보 조회
        curriculum = db.query(AIGeneratedCurriculum).filter(
            AIGeneratedCurriculum.id == session.curriculum_id
        ).first()
        
        steps = curriculum.generated_syllabus.get("steps", []) if curriculum else []
        
        # 진도 상세 정보
        progress_detail = []
        for i, step in enumerate(steps, 1):
            status = "completed" if i < session.current_step else "active" if i == session.current_step else "pending"
            progress_detail.append({
                "step_number": i,
                "title": step.get("title", f"{i}단계"),
                "status": status,
                "estimated_duration": step.get("estimated_duration", "미정"),
                "difficulty_level": step.get("difficulty_level", 5)
            })
        
        return {
            "session_id": session.id,
            "current_step": session.current_step,
            "total_steps": session.total_steps,
            "completion_percentage": session.completion_percentage,
            "session_status": session.session_status,
            "steps_detail": progress_detail,
            "learning_time": {
                "started_at": session.started_at.isoformat(),
                "last_activity_at": session.last_activity_at.isoformat(),
                "total_duration": str(session.last_activity_at - session.started_at)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"진도 조회 실패: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_teaching_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """교육 세션 삭제"""
    try:
        session = db.query(AITeachingSession).filter(
            AITeachingSession.id == session_id,
            AITeachingSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="교육 세션을 찾을 수 없습니다")
        
        db.delete(session)
        db.commit()
        
        return {"message": "교육 세션이 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 삭제 실패: {str(e)}")


@router.post("/sessions/{session_id}/message", response_model=TeachingChatResponse)
async def send_message(
    session_id: int,
    message_request: TeachingMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """교육 세션에 메시지 전송"""
    try:
        updated_session, ai_response = await syllabus_based_teaching_agent.continue_teaching(
            session_id=session_id,
            user_message=message_request.message,
            user_id=current_user.id,
            db=db
        )
        
        response = TeachingChatResponse(
            session_id=updated_session.id,
            message=ai_response.get('message', ''),
            current_step=updated_session.current_step,
            step_title=ai_response.get('step_title', ''),
            understanding_check=ai_response.get('understanding_check'),
            next_action=ai_response.get('next_action', ''),
            progress_percentage=ai_response.get('progress_percentage', 0.0),
            learning_tips=ai_response.get('learning_tips', []),
            difficulty_adjustment=ai_response.get('difficulty_adjustment'),
            timestamp=datetime.now()
        )
        
        # WebSocket으로 실시간 메시지 전송
        await manager.send_personal_message(
            {
                "type": "ai_response",
                "data": response.dict()
            },
            session_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메시지 전송 실패: {str(e)}")


@router.get("/sessions", response_model=List[TeachingSessionResponse])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """사용자의 교육 세션 목록 조회"""
    try:
        query = db.query(AITeachingSession).filter(
            AITeachingSession.user_id == current_user.id
        )
        
        if status:
            query = query.filter(AITeachingSession.session_status == status)
        
        sessions = query.order_by(AITeachingSession.started_at.desc()).all()
        
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
                last_activity_at=session.last_activity_at,
                conversation_preview=_get_conversation_preview(session.conversation_history)
            )
            for session in sessions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 목록 조회 실패: {str(e)}")


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: int,
    current_user: User = Depends(get_current_user)
):
    """WebSocket 실시간 교육 세션"""
    await manager.connect(websocket, session_id)
    
    try:
        await websocket.send_json({
            "type": "connection_established",
            "session_id": session_id,
            "message": "실시간 교육 세션이 연결되었습니다."
        })
        
        while True:
            # 클라이언트로부터 메시지 수신 대기
            data = await websocket.receive_json()
            
            if data.get("type") == "user_message":
                # 사용자 메시지 처리 (실제 구현에서는 send_message 엔드포인트 로직 활용)
                await websocket.send_json({
                    "type": "message_received",
                    "message": "메시지가 수신되었습니다."
                })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"WebSocket 오류: {str(e)}"
        })
        manager.disconnect(session_id)


def _get_conversation_preview(conversation_history):
    """대화 기록 미리보기 생성"""
    if not conversation_history or not isinstance(conversation_history, list):
        return None
    
    if len(conversation_history) > 0:
        last_message = conversation_history[-1]
        if isinstance(last_message, dict) and 'content' in last_message:
            return last_message['content'][:100] + "..." if len(last_message['content']) > 100 else last_message['content']
    
    return None
