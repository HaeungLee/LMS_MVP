"""
24/7 AI 멘토링 시스템 - Phase 4
- 개인화된 AI 학습 코치
- 실시간 질문 답변
- 학습 동기 부여 및 격려
- 맞춤형 학습 가이드
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from app.models.orm import User, Submission, SubmissionItem, UserProgress, LearningGoal
from app.services.ai_providers import generate_ai_response, ModelTier, get_ai_provider_manager
from app.services.deep_learning_analyzer import get_deep_learning_analyzer, LearnerType
from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)

class MentorPersonality(Enum):
    """멘토 성격 유형"""
    ENCOURAGING = "encouraging"     # 격려형
    ANALYTICAL = "analytical"       # 분석형
    PRACTICAL = "practical"         # 실무형
    PATIENT = "patient"            # 인내형
    CHALLENGING = "challenging"     # 도전형

class ConversationMode(Enum):
    """대화 모드"""
    HELP_SEEKING = "help"          # 도움 요청
    MOTIVATION = "motivation"      # 동기 부여
    EXPLANATION = "explanation"    # 설명 요청
    GUIDANCE = "guidance"          # 학습 가이드
    REFLECTION = "reflection"      # 학습 성찰
    STRUCTURED_TEACHING = "structured_teaching"  # Phase 9: 구조화된 교육 모드

@dataclass
class MentorResponse:
    """멘토 응답"""
    content: str
    tone: str
    suggestions: List[str]
    follow_up_questions: List[str]
    resources: List[Dict[str, str]]
    confidence: float

@dataclass
class MentorSession:
    """멘토링 세션"""
    session_id: str
    user_id: int
    start_time: datetime
    conversation_history: List[Dict[str, Any]]
    mentor_personality: MentorPersonality
    current_mood: str
    session_goals: List[str]

class AIMentoringSystem:
    """AI 멘토링 시스템"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_service = get_redis_service()
        self.ai_provider = get_ai_provider_manager()
        self.learning_analyzer = get_deep_learning_analyzer(db)
        
        # 멘토 성격별 특성
        self.mentor_personalities = {
            MentorPersonality.ENCOURAGING: {
                'tone': '따뜻하고 격려적인',
                'style': '긍정적이고 지지적인 피드백을 제공하며 학습자의 성과를 칭찬',
                'response_pattern': '먼저 긍정적인 부분을 언급하고, 개선점을 부드럽게 제시',
                'catchphrases': ['잘하고 있어요!', '훌륭한 시도입니다!', '계속 이런 식으로 해보세요!']
            },
            MentorPersonality.ANALYTICAL: {
                'tone': '논리적이고 체계적인',
                'style': '데이터와 분석을 바탕으로 구체적이고 상세한 설명 제공',
                'response_pattern': '문제를 단계별로 분해하고 논리적 해결 방법 제시',
                'catchphrases': ['데이터를 보면...', '단계적으로 접근해보죠', '분석해보면...']
            },
            MentorPersonality.PRACTICAL: {
                'tone': '실무적이고 직접적인',
                'style': '실제 업무나 프로젝트에 바로 적용할 수 있는 실용적 조언',
                'response_pattern': '실무 예시와 함께 바로 활용 가능한 팁 제공',
                'catchphrases': ['실무에서는...', '실제로 해보세요', '바로 적용할 수 있는...']
            },
            MentorPersonality.PATIENT: {
                'tone': '인내심 있고 이해심 많은',
                'style': '학습자의 속도에 맞춰 차근차근 설명하고 반복 학습 지원',
                'response_pattern': '기초부터 천천히 설명하고 이해도를 확인하며 진행',
                'catchphrases': ['천천히 해봅시다', '이해할 때까지...', '괜찮습니다, 다시 한번...']
            },
            MentorPersonality.CHALLENGING: {
                'tone': '도전적이고 자극적인',
                'style': '더 높은 목표를 제시하고 학습자의 잠재력을 끌어내는 도전 제시',
                'response_pattern': '현재 수준보다 한 단계 높은 도전과제 제시',
                'catchphrases': ['더 도전해보세요!', '잠재력이 보입니다', '다음 레벨로...']
            }
        }
        
        # 학습자 유형별 최적 멘토 매칭
        self.learner_mentor_matching = {
            LearnerType.FAST_LEARNER: MentorPersonality.CHALLENGING,
            LearnerType.DEEP_THINKER: MentorPersonality.ANALYTICAL,
            LearnerType.PRACTICAL_LEARNER: MentorPersonality.PRACTICAL,
            LearnerType.STEADY_LEARNER: MentorPersonality.ENCOURAGING,
            LearnerType.STRUGGLING_LEARNER: MentorPersonality.PATIENT
        }
    
    async def start_mentoring_session(self, user_id: int, initial_question: Optional[str] = None) -> MentorSession:
        """멘토링 세션 시작"""
        
        try:
            # 사용자 학습 프로필 조회
            user_analysis = await self.learning_analyzer.analyze_user_deeply(user_id, use_ai=False)
            
            # 최적 멘토 성격 선택
            learner_type = LearnerType(user_analysis.get('learner_profile', {}).get('type', 'steady_learner'))
            mentor_personality = self.learner_mentor_matching.get(learner_type, MentorPersonality.ENCOURAGING)
            
            # 세션 생성
            session_id = f"mentor_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            session = MentorSession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.utcnow(),
                conversation_history=[],
                mentor_personality=mentor_personality,
                current_mood=await self._assess_user_mood(user_id),
                session_goals=await self._generate_session_goals(user_id, user_analysis)
            )
            
            # 세션 캐싱
            await self._cache_session(session)
            
            # 인사말 생성
            greeting = await self._generate_greeting(session, initial_question)
            
            # 첫 대화 기록
            session.conversation_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'mentor_greeting',
                'content': greeting.content,
                'tone': greeting.tone
            })
            
            await self._cache_session(session)
            
            logger.info(f"멘토링 세션 시작: {session_id} - 멘토: {mentor_personality.value}")
            return session
            
        except Exception as e:
            logger.error(f"멘토링 세션 시작 실패 user {user_id}: {str(e)}")
            raise
    
    async def continue_conversation(
        self, 
        session_id: str, 
        user_message: str,
        conversation_mode: ConversationMode = ConversationMode.HELP_SEEKING
    ) -> MentorResponse:
        """대화 계속하기"""
        
        try:
            # 세션 조회
            session = await self._get_session(session_id)
            if not session:
                raise ValueError(f"세션을 찾을 수 없습니다: {session_id}")
            
            # 사용자 메시지 기록
            session.conversation_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'user_message',
                'content': user_message,
                'mode': conversation_mode.value
            })
            
            # 컨텍스트 분석
            context = await self._analyze_conversation_context(session, user_message, conversation_mode)
            
            # 멘토 응답 생성
            mentor_response = await self._generate_mentor_response(session, context, conversation_mode)
            
            # 응답 기록
            session.conversation_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'mentor_response',
                'content': mentor_response.content,
                'tone': mentor_response.tone,
                'suggestions': mentor_response.suggestions,
                'confidence': mentor_response.confidence
            })
            
            # 세션 업데이트
            await self._cache_session(session)
            
            logger.info(f"멘토 응답 생성 완료: {session_id}")
            return mentor_response
            
        except Exception as e:
            logger.error(f"대화 계속하기 실패 {session_id}: {str(e)}")
            return await self._generate_fallback_response(user_message)
    
    async def _assess_user_mood(self, user_id: int) -> str:
        """사용자 기분 상태 평가"""
        
        try:
            # 최근 학습 성과 기반 기분 평가
            recent_time = datetime.utcnow() - timedelta(hours=24)
            # SubmissionItem에서 user_id를 얻기 위해 JOIN 사용
            recent_submissions = self.db.query(SubmissionItem).join(Submission).filter(
                Submission.user_id == user_id,
                Submission.submitted_at >= recent_time
            ).limit(10).all()
            
            if not recent_submissions:
                return "neutral"
            
            # 정확도 기반 기분 평가
            accuracy = sum(s.is_correct for s in recent_submissions) / len(recent_submissions)
            
            if accuracy >= 0.8:
                return "confident"
            elif accuracy >= 0.6:
                return "steady"
            elif accuracy >= 0.4:
                return "struggling"
            else:
                return "frustrated"
                
        except Exception:
            return "neutral"
    
    async def _generate_session_goals(self, user_id: int, user_analysis: Dict[str, Any]) -> List[str]:
        """세션 목표 생성"""
        
        goals = []
        
        # 약점 기반 목표
        weaknesses = user_analysis.get('learner_profile', {}).get('weaknesses', [])
        if weaknesses:
            goals.append(f"{weaknesses[0]} 영역 개선")
        
        # 학습 단계 기반 목표  
        phase = user_analysis.get('learner_profile', {}).get('phase', 'beginner')
        if phase == 'beginner':
            goals.append("기초 개념 정립")
        elif phase == 'intermediate':
            goals.append("응용 능력 향상")
        else:
            goals.append("전문성 확장")
        
        # 참여도 기반 목표
        engagement = user_analysis.get('learning_metrics', {}).get('engagement_level', 0.5)
        if engagement < 0.5:
            goals.append("학습 동기 향상")
        
        return goals or ["전반적인 학습 지원"]
    
    async def _generate_greeting(self, session: MentorSession, initial_question: Optional[str]) -> MentorResponse:
        """인사말 생성"""
        
        personality = self.mentor_personalities[session.mentor_personality]
        
        # 세션 고유 식별자 추가
        session_timestamp = int(datetime.utcnow().timestamp())

        greeting_prompt = f"""당신은 한국의 프로그래밍 교육 플랫폼의 따뜻하고 지식이 풍부한 AI 학습 멘토입니다.

세션 목표: {', '.join(session.session_goals)}
{f"학생의 첫 질문: {initial_question}" if initial_question else ""}

지침:
- 한국어로 따뜻하고 전문적으로 인사하세요
- 자연스럽고 환영하는 분위기로 (150-250자)
- 학습을 돕는 것에 대한 진심 어린 열정을 표현하세요
- 오늘 무엇을 도와드릴지 물어보세요
- 특수 토큰이나 포맷팅 마커를 사용하지 마세요
- 친근함을 위해 이모지 1개 사용
- 반드시 한국어로만 응답하세요

한국어로 따뜻하고 전문적인 인사말을 생성하세요."""

        response = await generate_ai_response(
            prompt=greeting_prompt,
            task_type="mentoring",
            model_preference=ModelTier.FREE,
            user_id=session.user_id,
            temperature=0.8
        )
        
        return MentorResponse(
            content=response.get('response', '안녕하세요! 학습 멘토입니다. 어떤 도움이 필요하신가요?'),
            tone=personality['tone'],
            suggestions=["궁금한 것을 자유롭게 물어보세요", "학습 계획을 함께 세워볼까요?"],
            follow_up_questions=["오늘 어떤 부분을 공부하고 계신가요?", "어려움을 겪고 있는 영역이 있나요?"],
            resources=[],
            confidence=0.8
        )
    
    async def _analyze_conversation_context(
        self, 
        session: MentorSession, 
        user_message: str, 
        mode: ConversationMode
    ) -> Dict[str, Any]:
        """대화 맥락 분석"""
        
        context = {
            'user_message': user_message,
            'conversation_mode': mode.value,
            'session_length': len(session.conversation_history),
            'mentor_personality': session.mentor_personality.value,
            'user_mood': session.current_mood,
            'session_goals': session.session_goals
        }
        
        # 최근 대화 히스토리 (최대 5개)
        recent_history = session.conversation_history[-5:] if session.conversation_history else []
        context['recent_conversation'] = [
            {'type': h['type'], 'content': h['content'][:100]} 
            for h in recent_history
        ]
        
        # 질문 유형 분류
        question_type = await self._classify_question_type(user_message)
        context['question_type'] = question_type
        
        # 감정 분석
        emotional_tone = await self._analyze_emotional_tone(user_message)
        context['emotional_tone'] = emotional_tone
        
        return context
    
    async def _classify_question_type(self, message: str) -> str:
        """질문 유형 분류"""
        
        # 간단한 키워드 기반 분류
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['왜', 'why', '이유', '원리']):
            return 'explanation'
        elif any(word in message_lower for word in ['어떻게', 'how', '방법']):
            return 'how_to'
        elif any(word in message_lower for word in ['뭐', 'what', '무엇']):
            return 'definition'
        elif any(word in message_lower for word in ['힘들', '어려', '모르겠', '이해 안']):
            return 'difficulty'
        elif any(word in message_lower for word in ['계획', '목표', '방향']):
            return 'guidance'
        else:
            return 'general'
    
    async def _analyze_emotional_tone(self, message: str) -> str:
        """감정 톤 분석"""
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['감사', '고마워', '좋아', '완벽']):
            return 'positive'
        elif any(word in message_lower for word in ['힘들', '어려워', '포기', '싫어']):
            return 'negative'
        elif any(word in message_lower for word in ['궁금', '질문', '도움']):
            return 'curious'
        elif any(word in message_lower for word in ['확신', '맞나', '의심']):
            return 'uncertain'
        else:
            return 'neutral'
    
    async def _generate_mentor_response(
        self, 
        session: MentorSession, 
        context: Dict[str, Any],
        mode: ConversationMode
    ) -> MentorResponse:
        """멘토 응답 생성"""
        
        personality = self.mentor_personalities[session.mentor_personality]
        
        # 고유한 대화 식별자 추가 (캐시 충돌 방지)
        conversation_id = f"{session.session_id}_{len(session.conversation_history)}_{int(datetime.utcnow().timestamp())}"

        # 프롬프트 구성 - 자세하고 친절하게
        response_prompt = f"""당신은 프로그래밍과 기술 교육을 위한 지식이 풍부하고 친근한 AI 학습 멘토입니다. 반드시 한국어로만 응답하세요.

Student's question: "{context['user_message']}"

Previous conversation:
{json.dumps(context['recent_conversation'][-2:], ensure_ascii=False) if len(context['recent_conversation']) > 0 else 'None'}

Session goals: {', '.join(session.session_goals)}

Instructions:
- Answer the student's question thoroughly and clearly in Korean
- Provide detailed explanations with examples when appropriate
- Keep response between 200-400 characters for balance
- Be friendly, encouraging, and show genuine interest in teaching
- Offer practical advice and actionable steps
- Use emojis sparingly (1-2 max) for friendliness
- Do NOT use special tokens, formatting markers, or meta-commentary
- Focus on being helpful and informative

Respond in Korean, naturally and conversationally with helpful details."""

        response = await generate_ai_response(
            prompt=response_prompt,
            task_type="mentoring",
            model_preference=ModelTier.FREE,
            user_id=session.user_id,
            temperature=0.8
        )
        
        # 응답 파싱 및 구조화
        content = response.get('response', '죄송합니다. 다시 말씀해 주시겠어요?')
        
        # 제안사항 추출 (간단한 파싱)
        suggestions = await self._extract_suggestions(content, context)
        
        # 후속 질문 생성
        follow_up_questions = await self._generate_follow_up_questions(context, session)
        
        # 학습 자료 추천
        resources = await self._recommend_resources(context, session)
        
        return MentorResponse(
            content=content,
            tone=personality['tone'],
            suggestions=suggestions,
            follow_up_questions=follow_up_questions,
            resources=resources,
            confidence=response.get('cost_estimate', 0) > 0 and 0.8 or 0.6
        )
    
    async def _extract_suggestions(self, content: str, context: Dict[str, Any]) -> List[str]:
        """제안사항 추출"""
        
        # 기본 제안사항
        suggestions = []
        
        question_type = context.get('question_type', 'general')
        
        if question_type == 'difficulty':
            suggestions.extend([
                "기초 개념부터 차근차근 복습해보세요",
                "비슷한 문제를 여러 번 풀어보세요",
                "이해되지 않는 부분은 언제든 질문하세요"
            ])
        elif question_type == 'explanation':
            suggestions.extend([
                "예시를 통해 개념을 이해해보세요",
                "관련 자료를 더 찾아보시는 것을 추천합니다",
                "다른 방식으로 접근해보면 어떨까요"
            ])
        else:
            suggestions.extend([
                "꾸준한 연습이 중요합니다",
                "오늘 배운 내용을 정리해보세요",
                "궁금한 점이 있으면 언제든 물어보세요"
            ])
        
        return suggestions[:3]
    
    async def _generate_follow_up_questions(self, context: Dict[str, Any], session: MentorSession) -> List[str]:
        """후속 질문 생성"""
        
        questions = []
        
        emotional_tone = context.get('emotional_tone', 'neutral')
        
        if emotional_tone == 'negative':
            questions.extend([
                "어떤 부분이 가장 어려우신가요?",
                "다른 방법으로 접근해볼까요?"
            ])
        elif emotional_tone == 'positive':
            questions.extend([
                "더 도전적인 문제를 시도해보시겠어요?",
                "이 개념을 어떻게 활용할 수 있을까요?"
            ])
        else:
            questions.extend([
                "이해가 잘 되시나요?",
                "다른 궁금한 점이 있으신가요?"
            ])
        
        return questions[:2]
    
    async def _recommend_resources(self, context: Dict[str, Any], session: MentorSession) -> List[Dict[str, str]]:
        """학습 자료 추천"""
        
        resources = []
        
        question_type = context.get('question_type', 'general')
        
        if question_type == 'explanation':
            resources.append({
                'type': 'article',
                'title': '개념 설명 자료',
                'description': '기초부터 차근차근 설명하는 자료입니다'
            })
        elif question_type == 'how_to':
            resources.append({
                'type': 'tutorial',
                'title': '단계별 실습 가이드',
                'description': '따라하며 배울 수 있는 실습 자료입니다'
            })
        
        return resources
    
    async def _cache_session(self, session: MentorSession):
        """세션 캐싱"""
        
        try:
            cache_key = f"mentor_session:{session.session_id}"
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'start_time': session.start_time.isoformat(),
                'conversation_history': session.conversation_history,
                'mentor_personality': session.mentor_personality.value,
                'current_mood': session.current_mood,
                'session_goals': session.session_goals
            }
            
            self.redis_service.set_cache(cache_key, session_data, 3600)  # 1시간
            
        except Exception as e:
            logger.error(f"세션 캐싱 실패: {str(e)}")
    
    async def _get_session(self, session_id: str) -> Optional[MentorSession]:
        """세션 조회"""
        
        try:
            cache_key = f"mentor_session:{session_id}"
            session_data = self.redis_service.get_cache(cache_key)
            
            if not session_data:
                return None
            
            return MentorSession(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                start_time=datetime.fromisoformat(session_data['start_time']),
                conversation_history=session_data['conversation_history'],
                mentor_personality=MentorPersonality(session_data['mentor_personality']),
                current_mood=session_data['current_mood'],
                session_goals=session_data['session_goals']
            )
            
        except Exception as e:
            logger.error(f"세션 조회 실패: {str(e)}")
            return None
    
    async def _generate_fallback_response(self, user_message: str) -> MentorResponse:
        """폴백 응답 생성"""
        
        return MentorResponse(
            content="죄송합니다. 일시적인 문제가 발생했습니다. 조금 더 구체적으로 질문해 주시겠어요?",
            tone="apologetic",
            suggestions=["다시 질문해 주세요", "구체적인 예시와 함께 말씀해 주세요"],
            follow_up_questions=["어떤 부분이 궁금하신가요?"],
            resources=[],
            confidence=0.3
        )
    
    async def get_daily_motivation(self, user_id: int) -> str:
        """일일 동기부여 메시지"""
        
        try:
            # 사용자 최근 성과 확인
            user_mood = await self._assess_user_mood(user_id)
            
            motivation_prompts = {
                'confident': "오늘도 훌륭한 성과를 보여주고 계시네요! 이 기세를 유지하며 더 도전적인 목표를 세워보시는 것은 어떨까요?",
                'steady': "꾸준히 잘 하고 계시는군요! 오늘도 한 걸음씩 전진해봅시다. 작은 성취도 큰 발전의 시작이에요.",
                'struggling': "학습이 어려우시겠지만 포기하지 마세요! 모든 전문가도 처음에는 초보였습니다. 천천히 기초부터 다져나가요.",
                'frustrated': "힘든 시간이지만 이것도 성장의 과정입니다. 잠시 휴식을 취하고 다른 접근 방식을 시도해보는 것은 어떨까요?",
                'neutral': "새로운 하루, 새로운 기회입니다! 오늘은 어떤 새로운 것을 배워볼까요?"
            }
            
            return motivation_prompts.get(user_mood, motivation_prompts['neutral'])
            
        except Exception as e:
            logger.error(f"일일 동기부여 메시지 생성 실패: {str(e)}")
            return "오늘도 화이팅! 조금씩이라도 배우고 성장하는 하루가 되시길 바라요."
    
    async def get_learning_tips(self, user_id: int, topic: Optional[str] = None) -> List[str]:
        """학습 팁 제공"""
        
        try:
            # 사용자 분석 데이터 기반 팁 생성
            user_analysis = await self.learning_analyzer.analyze_user_deeply(user_id, use_ai=False)
            
            learner_type = user_analysis.get('learner_profile', {}).get('type', 'steady_learner')
            
            type_specific_tips = {
                'fast_learner': [
                    "복습보다는 새로운 도전에 집중하세요",
                    "어려운 문제를 먼저 시도해보세요",
                    "학습한 내용을 다른 사람에게 설명해보세요"
                ],
                'deep_thinker': [
                    "충분한 시간을 두고 개념을 이해하세요",
                    "다양한 관점에서 문제를 분석해보세요",
                    "이론과 실제를 연결지어 생각해보세요"
                ],
                'practical_learner': [
                    "실제 프로젝트에 적용해보세요",
                    "구체적인 예시를 많이 찾아보세요",
                    "단계별로 직접 해보며 학습하세요"
                ],
                'steady_learner': [
                    "꾸준한 학습 스케줄을 유지하세요",
                    "작은 목표를 설정하고 달성해보세요",
                    "복습을 통해 기초를 탄탄히 하세요"
                ],
                'struggling_learner': [
                    "기초 개념부터 차근차근 시작하세요",
                    "이해되지 않는 부분은 반복 학습하세요",
                    "도움을 요청하는 것을 두려워하지 마세요"
                ]
            }
            
            return type_specific_tips.get(learner_type, type_specific_tips['steady_learner'])
            
        except Exception as e:
            logger.error(f"학습 팁 제공 실패: {str(e)}")
            return [
                "꾸준한 학습이 가장 중요합니다",
                "이해되지 않는 부분은 반복 학습하세요",
                "실습과 이론을 균형있게 학습하세요"
            ]

    # Phase 9: 구조화된 교육 모드 확장
    async def enter_structured_teaching_mode(
        self, 
        session: MentorSession, 
        curriculum_id: int,
        teaching_session_id: int
    ) -> MentorResponse:
        """구조화된 교육 모드 진입"""
        
        try:
            logger.info(f"구조화된 교육 모드 진입: session={session.session_id}, curriculum={curriculum_id}")
            
            # 세션에 구조화된 교육 정보 추가
            session.conversation_mode = ConversationMode.STRUCTURED_TEACHING
            session.structured_teaching_info = {
                'curriculum_id': curriculum_id,
                'teaching_session_id': teaching_session_id,
                'started_at': datetime.utcnow().isoformat(),
                'integration_mode': 'mentor_support'  # 멘토가 교육 세션을 지원하는 모드
            }
            
            # 구조화된 교육 안내 메시지 생성
            guidance_prompt = f"""당신은 이제 구조화된 AI 교육 세션을 지원하는 멘토입니다.

역할 변화:
- 기존: 일반적인 학습 멘토링
- 현재: 체계적인 커리큘럼 기반 교육 지원

지원 방식:
1. 학습자가 교육 중 막히는 부분에 대한 추가 설명 제공
2. 동기 부여 및 격려를 통한 학습 지속성 향상  
3. 교육 내용에 대한 보충 자료나 예시 제안
4. 학습자의 이해도 체크 및 복습 가이드

현재 학습자가 구조화된 AI 교육 세션을 시작했습니다.
멘토로서 이 새로운 학습 방식을 격려하고, 필요시 언제든 도움을 요청하라고 안내해주세요.
따뜻하고 지원적인 톤으로 200자 이내로 작성해주세요."""

            response = await generate_ai_response(
                prompt=guidance_prompt,
                task_type="mentoring",
                model_preference=ModelTier.STANDARD,
                user_id=session.user_id,
                temperature=0.7
            )
            
            mentor_response = MentorResponse(
                content=response.get('response', '구조화된 학습 세션을 시작하시는군요! 체계적인 커리큘럼으로 더욱 효과적인 학습이 될 것입니다. 궁금한 점이나 추가 설명이 필요하면 언제든 말씀해주세요!'),
                tone="supportive",
                suggestions=[
                    "교육 중 이해가 안 되는 부분이 있으면 바로 질문하세요",
                    "각 단계별로 충분히 이해한 후 다음으로 넘어가세요",
                    "실습할 때 막히면 힌트를 요청해보세요"
                ],
                follow_up_questions=[
                    "현재 학습하고 있는 주제에 대해 이전에 경험이 있으신가요?",
                    "특별히 중점적으로 배우고 싶은 부분이 있나요?"
                ],
                resources=[
                    {
                        "type": "tip",
                        "title": "구조화된 학습 팁",
                        "content": "각 단계의 학습 목표를 명확히 파악하고 진행하세요"
                    }
                ],
                confidence=0.9
            )
            
            # 대화 기록 업데이트
            session.conversation_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'structured_teaching_entry',
                'content': mentor_response.content,
                'tone': mentor_response.tone,
                'curriculum_id': curriculum_id,
                'teaching_session_id': teaching_session_id
            })
            
            await self._cache_session(session)
            
            return mentor_response
            
        except Exception as e:
            logger.error(f"구조화된 교육 모드 진입 실패: {str(e)}")
            return await self._generate_fallback_response("구조화된 학습을 시작하겠습니다.")

    async def support_structured_teaching(
        self, 
        session: MentorSession, 
        user_question: str,
        current_step_info: Dict[str, Any] = None
    ) -> MentorResponse:
        """구조화된 교육 중 멘토 지원"""
        
        try:
            if not hasattr(session, 'structured_teaching_info') or not session.structured_teaching_info:
                # 구조화된 교육 모드가 아닌 경우 일반 모드로 처리
                return await self.continue_conversation(session, user_question, ConversationMode.HELP_SEEKING)
            
            teaching_info = session.structured_teaching_info
            
            # 현재 교육 단계 정보 포함한 프롬프트 생성
            support_prompt = f"""당신은 구조화된 AI 교육을 지원하는 멘토입니다.

현재 교육 상황:
- 커리큘럼 ID: {teaching_info.get('curriculum_id')}
- 교육 세션 ID: {teaching_info.get('teaching_session_id')}
{f"- 현재 단계: {current_step_info.get('title')}" if current_step_info else ""}
{f"- 학습 목표: {', '.join(current_step_info.get('learning_objectives', []))}" if current_step_info else ""}

학습자 질문: {user_question}

멘토 역할:
1. AI 교육 강사를 보완하는 추가 설명 제공
2. 다른 관점에서의 설명이나 예시 제공
3. 학습자의 이해도 향상을 위한 맞춤형 가이드
4. 동기 부여 및 격려

AI 교육 강사와 겹치지 않으면서도 도움이 되는 멘토링을 제공해주세요.
친근하고 격려하는 톤으로 300자 이내로 작성해주세요."""

            response = await generate_ai_response(
                prompt=support_prompt,
                task_type="mentoring",
                model_preference=ModelTier.STANDARD,
                user_id=session.user_id,
                temperature=0.7
            )
            
            mentor_response = MentorResponse(
                content=response.get('response', '좋은 질문이네요! 이 부분을 다른 방식으로 설명드려볼게요.'),
                tone="supportive",
                suggestions=[
                    "이해되지 않으면 더 자세히 설명드릴게요",
                    "비슷한 예시를 더 들어드릴까요?",
                    "다른 접근 방법도 시도해보세요"
                ],
                follow_up_questions=[
                    "이 설명이 도움이 되셨나요?",
                    "추가로 궁금한 부분이 있으신가요?"
                ],
                resources=[],
                confidence=0.8
            )
            
            # 대화 기록 업데이트
            session.conversation_history.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'structured_teaching_support',
                'user_question': user_question,
                'mentor_response': mentor_response.content,
                'current_step': current_step_info.get('title') if current_step_info else None
            })
            
            await self._cache_session(session)
            
            return mentor_response
            
        except Exception as e:
            logger.error(f"구조화된 교육 지원 실패: {str(e)}")
            return await self._generate_fallback_response(user_question)

    async def exit_structured_teaching_mode(self, session: MentorSession) -> MentorResponse:
        """구조화된 교육 모드 종료"""
        
        try:
            if hasattr(session, 'structured_teaching_info') and session.structured_teaching_info:
                teaching_duration = datetime.utcnow() - datetime.fromisoformat(
                    session.structured_teaching_info['started_at']
                )
                
                # 구조화된 교육 완료 격려 메시지
                completion_prompt = f"""학습자가 구조화된 AI 교육 세션을 완료했습니다.

교육 정보:
- 소요 시간: {str(teaching_duration)}
- 교육 모드: 체계적 커리큘럼 기반 학습

멘토로서:
1. 구조화된 학습 완료를 축하
2. 학습 성과에 대한 격려
3. 향후 학습 방향 제안
4. 언제든 멘토링 지원 가능함을 안내

따뜻하고 축하하는 톤으로 250자 이내로 작성해주세요."""

                response = await generate_ai_response(
                    prompt=completion_prompt,
                    task_type="mentoring",
                    model_preference=ModelTier.STANDARD,
                    user_id=session.user_id,
                    temperature=0.8
                )
                
                # 구조화된 교육 정보 제거
                session.structured_teaching_info = None
                session.conversation_mode = ConversationMode.MOTIVATION
                
                mentor_response = MentorResponse(
                    content=response.get('response', '구조화된 학습 세션을 완료하신 것을 축하합니다! 체계적으로 학습하신 모습이 인상적이었어요. 앞으로도 꾸준히 학습하시길 응원하며, 언제든 도움이 필요하면 말씀해주세요!'),
                    tone="celebratory",
                    suggestions=[
                        "학습한 내용을 복습해보세요",
                        "다음 단계 학습을 계획해보세요",
                        "배운 내용을 실제 프로젝트에 적용해보세요"
                    ],
                    follow_up_questions=[
                        "이번 학습에서 가장 인상깊었던 부분은 무엇인가요?",
                        "다음에는 어떤 주제를 학습하고 싶으신가요?"
                    ],
                    resources=[],
                    confidence=0.9
                )
                
                # 대화 기록 업데이트
                session.conversation_history.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'structured_teaching_exit',
                    'content': mentor_response.content,
                    'duration': str(teaching_duration)
                })
                
                await self._cache_session(session)
                
                return mentor_response
            
            else:
                # 구조화된 교육 모드가 아닌 경우
                return MentorResponse(
                    content="현재 구조화된 교육 모드가 아닙니다. 일반 멘토링을 계속 진행하겠습니다.",
                    tone="neutral",
                    suggestions=["궁금한 것을 자유롭게 질문해주세요"],
                    follow_up_questions=["어떤 도움이 필요하신가요?"],
                    resources=[],
                    confidence=0.7
                )
                
        except Exception as e:
            logger.error(f"구조화된 교육 모드 종료 실패: {str(e)}")
            return await self._generate_fallback_response("학습을 완료하셨군요!")


# 전역 인스턴스 생성 함수
def get_ai_mentoring_system(db: Session) -> AIMentoringSystem:
    """AI 멘토링 시스템 인스턴스 반환"""
    return AIMentoringSystem(db)
