"""
LangChain 기반 개선된 커리큘럼 생성기
EduGPT의 2-Agent 모델을 LangChain으로 완전 재구현
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import asyncio

# LangChain 임포트
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from sqlalchemy.orm import Session

from app.services.langchain_hybrid_provider import (
    get_langchain_hybrid_provider, 
    create_discuss_agent,
    EduGPTDiscussAgent
)
from app.models.ai_curriculum import AIGeneratedCurriculum

logger = logging.getLogger(__name__)

class LangChainTwoAgentCurriculumGenerator:
    """
    LangChain 기반 2-Agent 협력 커리큘럼 생성기
    EduGPT의 원본 구조를 LangChain으로 완전히 재구현
    """
    
    def __init__(self):
        self.provider = get_langchain_hybrid_provider()
        self.instructor_agent: Optional[EduGPTDiscussAgent] = None
        self.assistant_agent: Optional[EduGPTDiscussAgent] = None
        
    async def generate_curriculum(
        self,
        topic: str,
        difficulty_level: str = "beginner",
        duration_weeks: int = 8,
        learning_goals: List[str] = None,
        subject_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        LangChain 2-Agent 협력을 통한 동적 커리큘럼 생성
        """
        try:
            logger.info(f"LangChain 커리큘럼 생성 시작: {topic}, 난이도: {difficulty_level}")
            
            # 1. 작업 정의
            task = self._create_task_description(
                topic, difficulty_level, duration_weeks, learning_goals, subject_context
            )
            
            # 2. LangChain Agent 생성
            self._create_agents(task)
            
            # 3. 2-Agent 대화 진행
            conversation_result = await self._conduct_langchain_conversation(task)
            
            # 4. 커리큘럼 구조화
            structured_curriculum = await self._structure_curriculum_with_langchain(
                conversation_result, topic, difficulty_level
            )
            
            # 5. Phase 8 과목 시스템과 연동
            if subject_context:
                structured_curriculum = self._align_with_subject_context(
                    structured_curriculum, subject_context
                )
            
            # LangChain 정보 추가
            structured_curriculum['generation_framework'] = 'langchain'
            structured_curriculum['ai_provider'] = self.provider.current_provider
            
            logger.info(f"LangChain 커리큘럼 생성 완료: {topic}")
            return structured_curriculum
            
        except Exception as e:
            logger.error(f"LangChain 커리큘럼 생성 실패: {str(e)}")
            raise
    
    def _create_task_description(
        self, 
        topic: str, 
        difficulty_level: str, 
        duration_weeks: int,
        learning_goals: List[str],
        subject_context: Dict[str, Any]
    ) -> str:
        """작업 설명 생성 (한국어)"""
        
        goals_text = ""
        if learning_goals:
            goals_text = f"\n학습 목표:\n" + "\n".join([f"- {goal}" for goal in learning_goals])
        
        context_text = ""
        if subject_context and subject_context.get('existing_topics'):
            topics = [topic['topic_key'] for topic in subject_context['existing_topics']]
            context_text = f"\n기존 과목 토픽들: {', '.join(topics)}"
        
        task = f"""
{topic}에 대한 {difficulty_level} 레벨의 {duration_weeks}주 학습 커리큘럼을 설계해주세요.

요구사항:
- 한국 학습자 중심의 단계적 학습 계획
- 각 주차별 명확한 학습 목표
- 실습과 이론의 균형잡힌 구성
- 평가 방법 및 과제 포함
- 모든 내용은 한국어로 작성
{goals_text}{context_text}

최종 결과물: 체계적이고 실용적인 {duration_weeks}주 한국어 커리큘럼
"""
        return task
    
    def _create_agents(self, task: str) -> None:
        """LangChain 기반 Agent 생성"""
        
        # Instructor Agent 시스템 메시지
        instructor_system = f"""당신은 경험이 풍부한 한국의 교육 전문가입니다. 
교육과정 설계와 커리큘럼 개발에 특화되어 있으며, 한국의 교육 환경과 학습자들의 특성을 잘 이해하고 있습니다.

역할:
- 체계적이고 효과적인 학습 커리큘럼 설계
- 한국 학습자의 수준과 목표에 맞는 단계적 학습 계획 수립
- 이론과 실습의 균형잡힌 구성
- 한국어로 명확하고 이해하기 쉬운 설명

작업: {task}

당신은 Teaching Assistant와 협력하여 최고의 커리큘럼을 만들어야 합니다.
Teaching Assistant의 질문과 제안에 전문적으로 답변하고, 
구체적이고 실행 가능한 솔루션을 제시하세요.

**중요: 모든 답변은 한국어로 작성하세요.**

항상 다음 형식으로 답변하세요:
Solution: <구체적인 해결책>

<구체적인 해결책>은 한국어로 명확하고 실행 가능해야 하며, 
반드시 "다음 요청을 기다리겠습니다."로 끝나야 합니다."""

        # Teaching Assistant Agent 시스템 메시지
        assistant_system = f"""당신은 한국의 학습자 관점을 잘 이해하는 Teaching Assistant입니다.
한국 학습자들의 어려움과 필요사항을 파악하여 더 나은 교육과정을 만드는 것이 목표입니다.

역할:
- 한국 학습자 관점에서 커리큘럼의 실용성 검토
- 학습 진도와 난이도 조절에 대한 피드백 제공
- 한국 교육 환경에 맞는 효과적인 학습 방법과 평가 방식 제안
- 한국어로 명확하고 친근한 소통

작업: {task}

당신은 Instructor와 협력하여 한국 학습자 중심의 커리큘럼을 만들어야 합니다.
Instructor에게 구체적인 질문을 하고, 학습자 관점에서 개선점을 제안하세요.

**중요: 모든 대화는 한국어로 진행하세요.**

다음 두 가지 방식으로만 지시하세요:

1. 입력이 필요한 지시:
Instruction: <지시사항>
Input: <입력내용>

2. 입력이 없는 지시:
Instruction: <지시사항>
Input: None

작업이 완료되면 <작업완료>을 포함하여 답변하세요."""

        # LangChain Agent 생성
        self.instructor_agent = create_discuss_agent(instructor_system)
        self.assistant_agent = create_discuss_agent(assistant_system)
    
    async def _conduct_langchain_conversation(self, task: str) -> List[str]:
        """LangChain 기반 2-Agent 대화 진행"""
        
        conversation_history = []
        chat_turn_limit = 5
        
        # 초기 상황 설정
        current_situation = "안녕하세요! 한국 학습자들을 위한 커리큘럼 설계를 시작하겠습니다. 구체적인 요구사항을 알려주세요."
        
        for turn in range(chat_turn_limit):
            # Teaching Assistant 턴
            assistant_prompt = f"""
현재 상황: {current_situation}

한국 학습자들을 위한 다음 단계를 지시해주세요. 한국어로 답변하세요.
"""
            
            assistant_input = HumanMessage(content=assistant_prompt)
            # ✅ 올바른 LangChain Agent 호출
            assistant_response = await self.assistant_agent.ainvoke({"messages": [assistant_input]})
            response_content = assistant_response.get("messages", [{}])[-1].get("content", "") if isinstance(assistant_response, dict) else assistant_response.content
            
            conversation_history.append(f"Teaching Assistant: {response_content}")
            logger.info(f"Teaching Assistant (턴 {turn+1}): {response_content}")
            
            if "<작업완료>" in response_content:
                break
            
            # Instructor 턴
            instructor_prompt = f"""
Teaching Assistant 요청: {response_content}

위 요청에 대해 한국 학습자들을 위한 전문적인 솔루션을 한국어로 제시하세요.
"""
            
            instructor_input = HumanMessage(content=instructor_prompt)
            # ✅ 올바른 LangChain Agent 호출
            instructor_response = await self.instructor_agent.ainvoke({"messages": [instructor_input]})
            instructor_content = instructor_response.get("messages", [{}])[-1].get("content", "") if isinstance(instructor_response, dict) else instructor_response.content
            
            conversation_history.append(f"Instructor: {instructor_content}")
            logger.info(f"Instructor (턴 {turn+1}): {instructor_content}")
            
            current_situation = instructor_content
        
        return conversation_history
    
    async def _structure_curriculum_with_langchain(
        self, 
        conversation_history: List[str], 
        topic: str, 
        difficulty_level: str
    ) -> Dict[str, Any]:
        """LangChain을 사용한 대화 내용 구조화"""
        
        conversation_text = "\n\n".join(conversation_history)
        
        structure_prompt = f"""
다음은 한국 학습자들을 위한 {topic} 커리큘럼 설계에 대한 전문가 대화 내용입니다:

{conversation_text}

이 대화를 바탕으로 한국 학습자들에게 최적화된 다음 JSON 형식의 구조화된 커리큘럼을 한국어로 생성해주세요:

{{
    "title": "한국어 커리큘럼 제목",
    "topic": "{topic}",
    "difficulty_level": "{difficulty_level}",
    "description": "한국어 커리큘럼 설명",
    "duration_weeks": 8,
    "total_hours": 60,
    "weekly_schedule": [
        {{
            "week": 1,
            "title": "한국어 주차 제목",
            "learning_objectives": ["한국어 학습목표1", "한국어 학습목표2"],
            "topics": ["한국어 토픽1", "한국어 토픽2"],
            "activities": ["한국어 활동1", "한국어 활동2"],
            "assignments": ["한국어 과제1"],
            "estimated_hours": 8
        }}
    ],
    "assessment_methods": ["한국어 평가방법1", "한국어 평가방법2"],
    "required_resources": ["한국어 학습자료1", "한국어 학습자료2"],
    "learning_outcomes": ["한국어 학습성과1", "한국어 학습성과2"]
}}

**중요사항:**
- 모든 텍스트는 한국어로 작성
- 한국 학습자의 특성과 교육 환경 고려
- 실용적이고 체계적인 내용 구성

JSON 형식으로만 답변하세요:
"""
        
        # LangChain으로 구조화 요청
        response = await self.provider.generate_response(
            structure_prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        try:
            # JSON 응답에서 실제 JSON 부분만 추출
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            structured_curriculum = json.loads(json_str)
            structured_curriculum['generated_at'] = datetime.now().isoformat()
            structured_curriculum['conversation_log'] = conversation_history
            structured_curriculum['framework'] = 'langchain'
            
            return structured_curriculum
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            # 기본 구조 반환 (한국어)
            return {
                "title": f"{topic} 학습 커리큘럼",
                "topic": topic,
                "difficulty_level": difficulty_level,
                "description": "LangChain AI가 한국 학습자를 위해 생성한 맞춤형 커리큘럼",
                "raw_content": response,
                "conversation_log": conversation_history,
                "generated_at": datetime.now().isoformat(),
                "status": "parsing_failed",
                "language": "korean",
                "framework": "langchain"
            }
    
    async def generate_curriculum_streaming(
        self,
        topic: str,
        difficulty_level: str = "beginner",
        duration_weeks: int = 8,
        learning_goals: List[str] = None,
        subject_context: Dict[str, Any] = None,
        streaming_handler = None
    ) -> Dict[str, Any]:
        """
        스트리밍 방식으로 LangChain 커리큘럼 생성
        """
        try:
            print(f"🔥 스트리밍 생성 시작: {topic}")  # 디버그 로그
            logger.info(f"스트리밍 커리큘럼 생성 시작: {topic}")
            
            # 기본 컨텍스트 설정
            context = self._prepare_generation_context(
                topic, difficulty_level, duration_weeks, learning_goals, subject_context
            )
            
            # 스트리밍 프롬프트 준비 
            system_prompt = f"""당신은 한국 학습자를 위한 경험 많은 교육 전문가입니다. 
            
            주제: {topic}
            난이도: {difficulty_level}
            기간: {duration_weeks}주
            학습목표: {', '.join(learning_goals or [])}
            
            다음 구조로 체계적인 커리큘럼을 한국어로 생성해주세요:
            
            1. **커리큘럼 개요**
               - 과정 소개
               - 학습 목표
               - 예상 학습 시간
            
            2. **주차별 학습 계획**
               - 각 주차의 제목과 목표
               - 학습할 주요 개념
               - 실습 활동
               - 과제
            
            3. **평가 방법**
               - 중간 평가
               - 최종 평가
               - 과제 평가
            
            4. **필요 자료 및 도구**
               - 교재 및 참고자료
               - 개발 도구
               - 온라인 리소스
            
            한국 학습자의 특성을 고려하여 상세하고 실용적으로 작성해주세요."""
            
            user_prompt = f"{topic}에 대한 {difficulty_level} 수준의 {duration_weeks}주 완성 커리큘럼을 생성해주세요."
            
            # 스트리밍 LLM 가져오기
            if streaming_handler:
                print(f"🔥 스트리밍 핸들러 있음, LLM 생성")  # 디버그 로그
                llm = self.provider.get_streaming_llm(callbacks=[streaming_handler])
            else:
                print(f"🔥 스트리밍 핸들러 없음, 일반 LLM 생성")  # 디버그 로그
                llm = self.provider.get_llm()
            
            # 스트리밍 생성 실행
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # ✅ 진짜 스트리밍: astream() 사용
            full_response = ""
            async for chunk in llm.astream(messages):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if content:
                    full_response += content
                    # 스트리밍 핸들러가 있으면 직접 토큰 전달
                    if streaming_handler:
                        await streaming_handler.on_llm_new_token(content)
            
            # 응답을 구조화된 커리큘럼으로 파싱
            curriculum_content = full_response
            
            # 기본 구조화된 커리큘럼 생성
            curriculum = {
                "title": f"{topic} {difficulty_level.title()} 과정 ({duration_weeks}주 완성)",
                "topic": topic,
                "difficulty_level": difficulty_level,
                "duration_weeks": duration_weeks,
                "learning_goals": learning_goals or [],
                "content": curriculum_content,
                "generated_at": datetime.utcnow().isoformat(),
                "method": "langchain_streaming",
                "personalized": True,
                "language": "korean"
            }
            
            # Subject context와 정렬
            if subject_context:
                curriculum = self._align_with_subject_context(curriculum, subject_context)
            
            return curriculum
            
        except Exception as e:
            logger.error(f"스트리밍 커리큘럼 생성 실패: {str(e)}")
            raise
    
    def _align_with_subject_context(
        self, 
        curriculum: Dict[str, Any], 
        subject_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 8 과목 시스템과 연동하여 일관성 확보"""
        
        if subject_context.get('existing_topics'):
            existing_topics = [t['topic_key'] for t in subject_context['existing_topics']]
            curriculum['aligned_topics'] = existing_topics
            curriculum['subject_integration'] = {
                "subject_key": subject_context.get('subject_key'),
                "category": subject_context.get('category'),
                "existing_topics_count": len(existing_topics)
            }
        
        return curriculum
    
    def _prepare_generation_context(
        self,
        topic: str,
        difficulty_level: str,
        duration_weeks: int,
        learning_goals: List[str],
        subject_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """생성을 위한 컨텍스트 준비"""
        context = {
            "topic": topic,
            "difficulty_level": difficulty_level,
            "duration_weeks": duration_weeks,
            "learning_goals": learning_goals or [],
            "subject_context": subject_context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 기존 토픽 정보가 있으면 추가
        if subject_context and subject_context.get('existing_topics'):
            context["existing_topics"] = [
                topic['topic_key'] for topic in subject_context['existing_topics']
            ]
        
        return context


class LangChainEnhancedCurriculumManager:
    """
    LangChain 기반 고도화된 커리큘럼 관리자
    """
    
    def __init__(self):
        self.langchain_generator = LangChainTwoAgentCurriculumGenerator()
        
    async def generate_dynamic_curriculum(
        self,
        subject_key: str,
        user_goals: List[str],
        difficulty_level: int,  # 1-10 난이도 스케일
        user_id: int,
        db: Session,
        duration_weeks: int = 8
    ) -> Tuple[AIGeneratedCurriculum, Dict[str, Any]]:
        """
        LangChain 기반 동적 커리큘럼 생성 및 데이터베이스 저장
        """
        try:
            # 1. 데이터베이스에 초기 레코드 생성
            curriculum_record = AIGeneratedCurriculum(
                user_id=user_id,
                subject_key=subject_key,
                learning_goals=user_goals,
                difficulty_level=difficulty_level,
                status="generating"
            )
            db.add(curriculum_record)
            db.commit()
            db.refresh(curriculum_record)
            
            # 2. Phase 8 과목 시스템에서 컨텍스트 가져오기
            subject_context = await self._get_subject_context(subject_key)
            
            # 3. 난이도를 문자열로 변환 (1-3: beginner, 4-6: intermediate, 7-10: advanced)
            difficulty_str = "beginner" if difficulty_level <= 3 else "intermediate" if difficulty_level <= 6 else "advanced"
            
            # 4. LangChain 2-Agent 모델로 커리큘럼 생성
            curriculum_data = await self.langchain_generator.generate_curriculum(
                topic=subject_context.get('subject_name', subject_key),
                difficulty_level=difficulty_str,
                duration_weeks=duration_weeks,
                learning_goals=user_goals,
                subject_context=subject_context
            )
            
            # 5. 사용자 정보 추가
            curriculum_data['user_id'] = user_id
            curriculum_data['personalized'] = True
            
            # 6. 데이터베이스 레코드 업데이트
            curriculum_record.generated_syllabus = curriculum_data
            curriculum_record.status = "completed"
            curriculum_record.generation_metadata = {
                "framework": "langchain",
                "ai_provider": self.langchain_generator.provider.current_provider,
                "generation_time": datetime.utcnow().isoformat(),
                "difficulty_level": difficulty_level,
                "duration_weeks": duration_weeks
            }
            
            db.commit()
            db.refresh(curriculum_record)
            
            return curriculum_record, curriculum_data
            
        except Exception as e:
            # 에러 발생 시 상태 업데이트
            if 'curriculum_record' in locals():
                curriculum_record.status = "failed"
                curriculum_record.generation_metadata = {
                    "error": str(e),
                    "error_time": datetime.utcnow().isoformat()
                }
                db.commit()
            
            logger.error(f"LangChain 커리큘럼 생성 실패: {str(e)}")
            raise
    
    async def generate_dynamic_curriculum_streaming(
        self,
        subject_key: str,
        user_goals: List[str],
        difficulty_level: int,
        user_id: int,
        db: Session,
        streaming_handler,
        duration_weeks: int = 8
    ) -> Dict[str, Any]:
        """
        스트리밍 방식으로 LangChain 커리큘럼 생성
        """
        try:
            # Phase 8 과목 시스템에서 컨텍스트 가져오기
            subject_context = await self._get_subject_context(subject_key)
            
            # 난이도를 문자열로 변환
            difficulty_str = "beginner" if difficulty_level <= 3 else "intermediate" if difficulty_level <= 6 else "advanced"
            
            # LangChain 스트리밍으로 커리큘럼 생성
            curriculum_data = await self.langchain_generator.generate_curriculum_streaming(
                topic=subject_context.get('subject_name', subject_key),
                difficulty_level=difficulty_str,
                duration_weeks=duration_weeks,
                learning_goals=user_goals,
                subject_context=subject_context,
                streaming_handler=streaming_handler
            )
            
            # 사용자 정보 추가
            curriculum_data['user_id'] = user_id
            curriculum_data['personalized'] = True
            
            return curriculum_data
            
        except Exception as e:
            logger.error(f"스트리밍 커리큘럼 생성 실패: {str(e)}")
            raise
    
    async def _get_subject_context(self, subject_key: str) -> Dict[str, Any]:
        """Phase 8 동적 과목 시스템에서 컨텍스트 조회"""
        # TODO: Phase 8 API 호출하여 과목 정보 가져오기
        # 현재는 Mock 데이터 반환
        return {
            "subject_key": subject_key,
            "subject_name": subject_key.replace('_', ' ').title(),
            "category": "Programming",
            "existing_topics": [
                {"topic_key": "basics", "weight": 1.0},
                {"topic_key": "advanced", "weight": 1.5}
            ]
        }
    
    async def get_user_curricula(self, user_id: int, db: Session) -> List[AIGeneratedCurriculum]:
        """사용자의 커리큘럼 목록 조회"""
        try:
            curricula = db.query(AIGeneratedCurriculum).filter(
                AIGeneratedCurriculum.user_id == user_id
            ).order_by(AIGeneratedCurriculum.created_at.desc()).all()
            
            return curricula
        except Exception as e:
            logger.error(f"커리큘럼 목록 조회 실패: {str(e)}")
            raise
    
    async def get_curriculum_by_id(self, curriculum_id: int, db: Session) -> AIGeneratedCurriculum:
        """특정 커리큘럼 조회"""
        try:
            curriculum = db.query(AIGeneratedCurriculum).filter(
                AIGeneratedCurriculum.id == curriculum_id
            ).first()
            
            if not curriculum:
                raise ValueError(f"커리큘럼 ID {curriculum_id}를 찾을 수 없습니다")
            
            return curriculum
        except Exception as e:
            logger.error(f"커리큘럼 상세 조회 실패: {str(e)}")
            raise
