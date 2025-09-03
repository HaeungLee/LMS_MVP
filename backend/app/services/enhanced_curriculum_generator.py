"""
Enhanced Curriculum Generator - Phase 9
EduGPT의 2-Agent 모델을 하이브리드 AI 시스템에 통합
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio

from app.services.hybrid_ai_provider import HybridAIProvider

logger = logging.getLogger(__name__)

class TwoAgentCurriculumGenerator:
    """
    EduGPT의 2-Agent 협력 모델을 활용한 커리큘럼 생성기
    - Instructor Agent: 전문적인 교육과정 설계
    - Teaching Assistant Agent: 학습자 관점에서 피드백 제공
    """
    
    def __init__(self):
        self.ai_provider = HybridAIProvider()
        self.conversation_history = []
        
    async def generate_curriculum(
        self,
        topic: str,
        difficulty_level: str = "beginner",
        duration_weeks: int = 8,
        learning_goals: List[str] = None,
        subject_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        2-Agent 협력을 통한 동적 커리큘럼 생성
        
        Args:
            topic: 학습 주제
            difficulty_level: 난이도 (beginner, intermediate, advanced)
            duration_weeks: 학습 기간 (주)
            learning_goals: 학습 목표 리스트
            subject_context: Phase 8 과목 시스템에서 가져온 컨텍스트
            
        Returns:
            생성된 커리큘럼 딕셔너리
        """
        try:
            logger.info(f"커리큘럼 생성 시작: {topic}, 난이도: {difficulty_level}")
            
            # 1. 작업 정의
            task = self._create_task_description(
                topic, difficulty_level, duration_weeks, learning_goals, subject_context
            )
            
            # 2. Agent 시스템 메시지 생성
            instructor_system_msg = self._create_instructor_system_message(task)
            assistant_system_msg = self._create_teaching_assistant_system_message(task)
            
            # 3. 2-Agent 대화 시작
            conversation_result = await self._conduct_agent_conversation(
                instructor_system_msg, assistant_system_msg, task
            )
            
            # 4. 커리큘럼 정리 및 구조화
            structured_curriculum = await self._structure_curriculum(
                conversation_result, topic, difficulty_level
            )
            
            # 5. Phase 8 과목 시스템과 연동
            if subject_context:
                structured_curriculum = self._align_with_subject_context(
                    structured_curriculum, subject_context
                )
            
            logger.info(f"커리큘럼 생성 완료: {topic}")
            return structured_curriculum
            
        except Exception as e:
            logger.error(f"커리큘럼 생성 실패: {str(e)}")
            raise
    
    def _create_task_description(
        self, 
        topic: str, 
        difficulty_level: str, 
        duration_weeks: int,
        learning_goals: List[str],
        subject_context: Dict[str, Any]
    ) -> str:
        """작업 설명 생성"""
        
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
- 학습자 중심의 단계적 학습 계획
- 각 주차별 명확한 학습 목표
- 실습과 이론의 균형잡힌 구성
- 평가 방법 및 과제 포함
{goals_text}{context_text}

최종 결과물: 체계적이고 실용적인 {duration_weeks}주 커리큘럼
"""
        return task
    
    def _create_instructor_system_message(self, task: str) -> str:
        """강사 에이전트 시스템 메시지"""
        return f"""당신은 경험이 풍부한 한국의 교육 전문가입니다. 
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

    def _create_teaching_assistant_system_message(self, task: str) -> str:
        """조교 에이전트 시스템 메시지"""
        return f"""당신은 한국의 학습자 관점을 잘 이해하는 Teaching Assistant입니다.
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
    
    async def _conduct_agent_conversation(
        self, 
        instructor_msg: str, 
        assistant_msg: str, 
        task: str
    ) -> List[str]:
        """2-Agent 대화 진행"""
        
        conversation_history = []
        chat_turn_limit = 5
        
        # 초기 메시지
        current_instructor_msg = "안녕하세요! 한국 학습자들을 위한 커리큘럼 설계를 시작하겠습니다. 구체적인 요구사항을 알려주세요."
        
        for turn in range(chat_turn_limit):
            # Teaching Assistant 턴
            assistant_prompt = f"""
{assistant_msg}

현재 상황: {current_instructor_msg}

한국 학습자들을 위한 다음 단계를 지시해주세요. 한국어로 답변하세요.
"""
            
            assistant_response = await self.ai_provider.generate_response(
                assistant_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            conversation_history.append(f"Teaching Assistant: {assistant_response}")
            logger.info(f"Teaching Assistant (턴 {turn+1}): {assistant_response}")
            
            if "<작업완료>" in assistant_response:
                break
            
            # Instructor 턴
            instructor_prompt = f"""
{instructor_msg}

Teaching Assistant 요청: {assistant_response}

위 요청에 대해 한국 학습자들을 위한 전문적인 솔루션을 한국어로 제시하세요.
"""
            
            instructor_response = await self.ai_provider.generate_response(
                instructor_prompt,
                temperature=0.8,
                max_tokens=1200
            )
            
            conversation_history.append(f"Instructor: {instructor_response}")
            logger.info(f"Instructor (턴 {turn+1}): {instructor_response}")
            
            current_instructor_msg = instructor_response
        
        return conversation_history
    
    async def _structure_curriculum(
        self, 
        conversation_history: List[str], 
        topic: str, 
        difficulty_level: str
    ) -> Dict[str, Any]:
        """대화 내용을 구조화된 커리큘럼으로 변환"""
        
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
        
        response = await self.ai_provider.generate_response(
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
            
            return structured_curriculum
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            # 기본 구조 반환 (한국어)
            return {
                "title": f"{topic} 학습 커리큘럼",
                "topic": topic,
                "difficulty_level": difficulty_level,
                "description": "AI가 한국 학습자를 위해 생성한 맞춤형 커리큘럼",
                "raw_content": response,
                "conversation_log": conversation_history,
                "generated_at": datetime.now().isoformat(),
                "status": "parsing_failed",
                "language": "korean"
            }
    
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


class EnhancedCurriculumManager:
    """
    기존 curriculum_manager.py를 확장한 고도화된 커리큘럼 관리자
    """
    
    def __init__(self):
        self.two_agent_generator = TwoAgentCurriculumGenerator()
        
    async def generate_dynamic_curriculum(
        self,
        subject_key: str,
        user_goals: List[str],
        difficulty_level: str = "beginner",
        duration_weeks: int = 8,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        동적 커리큘럼 생성 (EduGPT 2-Agent 모델 활용)
        """
        
        # Phase 8 과목 시스템에서 컨텍스트 가져오기
        subject_context = await self._get_subject_context(subject_key)
        
        # 2-Agent 모델로 커리큘럼 생성
        curriculum = await self.two_agent_generator.generate_curriculum(
            topic=subject_context.get('subject_name', subject_key),
            difficulty_level=difficulty_level,
            duration_weeks=duration_weeks,
            learning_goals=user_goals,
            subject_context=subject_context
        )
        
        # 사용자 정보 추가
        if user_id:
            curriculum['user_id'] = user_id
            curriculum['personalized'] = True
        
        return curriculum
    
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
