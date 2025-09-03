"""
Phase 9 Week 3: Syllabus-Based Teaching Agent
생성된 커리큘럼을 기반으로 실제 교육을 진행하는 AI 강사 시스템
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory  # langchain.memory에서 import
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.models.ai_curriculum import AIGeneratedCurriculum, AITeachingSession, AIContentGenerationLog
from app.services.langchain_hybrid_provider import LangChainHybridProvider

logger = logging.getLogger(__name__)


class TeachingResponse(BaseModel):
    """AI 강사 응답 모델"""
    message: str = Field(..., description="AI 강사의 메시지")
    current_step: int = Field(..., description="현재 단계")
    step_title: str = Field(..., description="현재 단계 제목")
    understanding_check: Optional[str] = Field(None, description="이해도 확인 질문")
    next_action: str = Field(..., description="다음 액션 (continue, quiz, review, next_step)")
    progress_percentage: float = Field(..., description="진도율 (0-100)")
    learning_tips: Optional[List[str]] = Field(None, description="학습 팁")
    difficulty_adjustment: Optional[str] = Field(None, description="난이도 조정 제안")


class SyllabusBasedTeachingAgent:
    """
    커리큘럼 기반 AI 강사 시스템
    생성된 커리큘럼을 바탕으로 단계별 교육을 진행하며 학습자와 대화
    """
    
    def __init__(self):
        self.ai_provider = LangChainHybridProvider()
        self.response_parser = JsonOutputParser(pydantic_object=TeachingResponse)
        
        # AI 강사 시스템 메시지 (한국어 최적화)
        self.teacher_system_message = """당신은 경험이 풍부한 프로그래밍 강사입니다.
학습자의 커리큘럼을 바탕으로 단계별로 체계적인 교육을 진행합니다.

**교육 원칙:**
1. 학습자 중심: 개별 학습자의 이해도와 속도에 맞춤
2. 단계적 진행: 커리큘럼의 각 단계를 체계적으로 진행
3. 상호작용: 지속적인 질문과 피드백으로 참여 유도
4. 실습 중심: 이론 설명 후 즉시 실습 기회 제공
5. 격려와 동기부여: 긍정적이고 격려하는 분위기 조성

**교육 방식:**
- 한국어로 친근하고 이해하기 쉽게 설명
- 복잡한 개념은 단순한 예시로 설명
- 학습자의 질문에 인내심을 갖고 답변
- 실습 코드는 주석과 함께 제공
- 이해도 확인을 위한 중간 점검 질문
- 필요시 이전 단계 복습 제안

**응답 형식:**
항상 JSON 형식으로 구조화된 응답을 제공합니다."""

    async def start_teaching_session(
        self,
        curriculum_id: int,
        user_id: int,
        db: Session
    ) -> Tuple[AITeachingSession, Dict[str, Any]]:
        """교육 세션 시작"""
        
        try:
            # 커리큘럼 조회
            curriculum = db.query(AIGeneratedCurriculum).filter(
                AIGeneratedCurriculum.id == curriculum_id,
                AIGeneratedCurriculum.user_id == user_id
            ).first()
            
            if not curriculum or curriculum.status != "completed":
                raise ValueError("완성된 커리큘럼을 찾을 수 없습니다")
            
            # 기존 활성 세션 확인
            existing_session = db.query(AITeachingSession).filter(
                AITeachingSession.curriculum_id == curriculum_id,
                AITeachingSession.user_id == user_id,
                AITeachingSession.session_status == "active"
            ).first()
            
            if existing_session:
                # 기존 세션 재개
                return existing_session, await self._generate_session_resume_message(existing_session)
            
            # 새 세션 생성
            curriculum_data = curriculum.generated_syllabus
            steps = curriculum_data.get("steps", [])
            
            session = AITeachingSession(
                curriculum_id=curriculum_id,
                user_id=user_id,
                session_title=f"{curriculum_data.get('title', '커리큘럼')} 학습",
                conversation_history=[],
                current_step=1,
                total_steps=len(steps),
                completion_percentage=0.0,
                session_status="active"
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # 첫 교육 메시지 생성
            first_message = await self._generate_welcome_message(curriculum_data, session)
            
            # 대화 기록 저장
            session.conversation_history = [first_message]
            session.last_activity_at = datetime.utcnow()
            db.commit()
            
            return session, first_message
            
        except Exception as e:
            logger.error(f"Teaching session start failed: {str(e)}")
            raise

    async def continue_teaching(
        self,
        session_id: int,
        user_message: str,
        user_id: int,
        db: Session
    ) -> Tuple[AITeachingSession, Dict[str, Any]]:
        """교육 세션 계속"""
        
        try:
            # 세션 조회
            session = db.query(AITeachingSession).filter(
                AITeachingSession.id == session_id,
                AITeachingSession.user_id == user_id,
                AITeachingSession.session_status == "active"
            ).first()
            
            if not session:
                raise ValueError("활성 교육 세션을 찾을 수 없습니다")
            
            # 커리큘럼 정보 조회
            curriculum = db.query(AIGeneratedCurriculum).filter(
                AIGeneratedCurriculum.id == session.curriculum_id
            ).first()
            
            curriculum_data = curriculum.generated_syllabus
            current_step_data = curriculum_data.get("steps", [])[session.current_step - 1]
            
            # AI 강사 응답 생성
            response = await self._generate_teaching_response(
                session, user_message, curriculum_data, current_step_data
            )
            
            # 대화 기록 업데이트
            conversation = session.conversation_history or []
            conversation.extend([
                {
                    "role": "user",
                    "message": user_message,
                    "timestamp": datetime.utcnow().isoformat()
                },
                response
            ])
            
            # 진도 업데이트
            if response.get("next_action") == "next_step":
                session.current_step = min(session.current_step + 1, session.total_steps)
                session.completion_percentage = (session.current_step / session.total_steps) * 100
                
                # 모든 단계 완료 시 세션 완료
                if session.current_step >= session.total_steps:
                    session.session_status = "completed"
                    session.completed_at = datetime.utcnow()
                    session.completion_percentage = 100.0
            
            session.conversation_history = conversation
            session.last_activity_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            return session, response
            
        except Exception as e:
            logger.error(f"Teaching session continue failed: {str(e)}")
            raise

    async def _generate_welcome_message(
        self,
        curriculum_data: Dict[str, Any],
        session: AITeachingSession
    ) -> Dict[str, Any]:
        """환영 메시지 생성"""
        
        curriculum_title = curriculum_data.get("title", "커리큘럼")
        first_step = curriculum_data.get("steps", [])[0] if curriculum_data.get("steps") else {}
        
        welcome_prompt = f"""
**새로운 학습 시작!**

안녕하세요! 🎉 
'{curriculum_title}' 학습을 시작하신 것을 축하합니다!

**학습 개요:**
- 📚 커리큘럼: {curriculum_title}
- 🎯 총 {session.total_steps}단계로 구성
- ⏰ 예상 소요시간: {curriculum_data.get('total_duration', '미정')}

**첫 번째 단계:**
📖 {first_step.get('title', '첫 단계')}

{first_step.get('description', '첫 단계를 시작합니다!')}

**학습 목표:**
{chr(10).join([f'• {obj}' for obj in first_step.get('learning_objectives', [])])}

준비되셨나요? 궁금한 것이 있으시면 언제든지 질문해주세요! 
함께 차근차근 배워나가겠습니다. 💪

어떤 부분부터 시작하고 싶으신가요?
"""
        
        return {
            "role": "assistant",
            "message": welcome_prompt,
            "current_step": 1,
            "step_title": first_step.get('title', '첫 단계'),
            "understanding_check": "학습을 시작하기 전에 이 주제에 대해 어느 정도 알고 계신가요?",
            "next_action": "continue",
            "progress_percentage": 0.0,
            "learning_tips": [
                "모르는 것이 있으면 언제든지 질문하세요",
                "실습을 통해 직접 코딩해보세요",
                "이해가 안 되면 다시 설명드릴게요"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _generate_session_resume_message(
        self,
        session: AITeachingSession
    ) -> Dict[str, Any]:
        """세션 재개 메시지 생성"""
        
        return {
            "role": "assistant",
            "message": f"""
안녕하세요! 👋

이전 학습을 이어서 진행하겠습니다.

**현재 진행 상황:**
- 📊 진도: {session.completion_percentage:.1f}% 완료
- 📖 현재 단계: {session.current_step}/{session.total_steps}단계
- ⏰ 마지막 학습: {session.last_activity_at.strftime('%Y-%m-%d %H:%M')}

이전에 어디까지 학습했는지 기억하시나요? 
복습이 필요하시면 말씀해주세요!

어떻게 진행하고 싶으신가요?
1. 현재 단계 계속하기
2. 이전 단계 복습하기  
3. 질문하기
""",
            "current_step": session.current_step,
            "step_title": f"{session.current_step}단계",
            "understanding_check": None,
            "next_action": "continue",
            "progress_percentage": session.completion_percentage,
            "learning_tips": ["이전 내용이 기억나지 않으면 복습부터 시작하세요"],
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _generate_teaching_response(
        self,
        session: AITeachingSession,
        user_message: str,
        curriculum_data: Dict[str, Any],
        current_step_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI 강사 응답 생성"""
        
        # 대화 컨텍스트 준비
        conversation_context = self._prepare_conversation_context(session, curriculum_data, current_step_data)
        
        # 프롬프트 생성
        teaching_prompt = f"""
**현재 교육 상황:**
- 커리큘럼: {curriculum_data.get('title')}
- 현재 단계: {session.current_step}/{session.total_steps} - {current_step_data.get('title')}
- 단계 목표: {', '.join(current_step_data.get('learning_objectives', []))}
- 핵심 개념: {', '.join(current_step_data.get('key_concepts', []))}

**학습자 메시지:** {user_message}

**교육 지침:**
1. 학습자의 메시지를 분석하여 이해도 파악
2. 현재 단계의 학습 목표에 맞는 설명 제공
3. 필요시 실습 예제나 코드 제공
4. 다음 단계로 진행할 준비가 되었는지 판단
5. 학습자의 동기를 유지하는 격려 메시지

현재 단계의 내용을 바탕으로 학습자에게 도움이 되는 응답을 생성해주세요.

{self.response_parser.get_format_instructions()}
"""
        
        start_time = datetime.now()
        
        response = await self.ai_provider.generate_structured_response(
            messages=[
                SystemMessage(content=self.teacher_system_message),
                HumanMessage(content=teaching_prompt)
            ],
            parser=self.response_parser,
            model_name="gpt-4"
        )
        
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # 응답에 메타데이터 추가
        response_dict = response.dict()
        response_dict.update({
            "role": "assistant",
            "timestamp": datetime.utcnow().isoformat(),
            "generation_time_ms": generation_time
        })
        
        return response_dict

    def _prepare_conversation_context(
        self,
        session: AITeachingSession,
        curriculum_data: Dict[str, Any],
        current_step_data: Dict[str, Any]
    ) -> str:
        """대화 컨텍스트 준비"""
        
        recent_messages = (session.conversation_history or [])[-5:]  # 최근 5개 메시지
        
        context = f"""
**커리큘럼 정보:**
- 제목: {curriculum_data.get('title')}
- 대상: {curriculum_data.get('target_audience')}
- 전체 소요시간: {curriculum_data.get('total_duration')}

**현재 단계 정보:**
- 제목: {current_step_data.get('title')}
- 설명: {current_step_data.get('description')}
- 난이도: {current_step_data.get('difficulty_level')}/10
- 예상 시간: {current_step_data.get('estimated_duration')}

**최근 대화:**
"""
        for msg in recent_messages:
            role = "학습자" if msg.get("role") == "user" else "강사"
            context += f"- {role}: {msg.get('message', '')[:100]}...\n"
        
        return context

    async def pause_session(self, session_id: int, user_id: int, db: Session) -> bool:
        """세션 일시정지"""
        try:
            session = db.query(AITeachingSession).filter(
                AITeachingSession.id == session_id,
                AITeachingSession.user_id == user_id
            ).first()
            
            if session:
                session.session_status = "paused"
                session.last_activity_at = datetime.utcnow()
                db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Session pause failed: {str(e)}")
            return False

    async def resume_session(self, session_id: int, user_id: int, db: Session) -> bool:
        """세션 재개"""
        try:
            session = db.query(AITeachingSession).filter(
                AITeachingSession.id == session_id,
                AITeachingSession.user_id == user_id,
                AITeachingSession.session_status == "paused"
            ).first()
            
            if session:
                session.session_status = "active"
                session.last_activity_at = datetime.utcnow()
                db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Session resume failed: {str(e)}")
            return False


# 싱글톤 인스턴스
syllabus_based_teaching_agent = SyllabusBasedTeachingAgent()
