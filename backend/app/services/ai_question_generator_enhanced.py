"""
Phase 10: AI 문제 생성 엔진 (강화 버전)
- 커리큘럼 기반 문제 자동 생성
- 적응형 난이도 조절
- 개인화된 문제 추천
- 스마트 문제 검토 시스템
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.ai_providers import AIProviderManager, AIRequest
from app.services.langchain_hybrid_provider import LangChainHybridProvider
from app.core.database import get_db
from app.models.orm import User, Subject, Question
from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """문제 유형"""
    MULTIPLE_CHOICE = "multiple_choice"
    CODING = "coding"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    FILL_BLANK = "fill_blank"
    TRUE_FALSE = "true_false"

class DifficultyLevel(Enum):
    """난이도 수준"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class QuestionGenerationRequest:
    """문제 생성 요청"""
    user_id: int
    subject_key: str
    topic: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    count: int = 1
    learning_goals: Optional[List[str]] = None
    user_weaknesses: Optional[List[str]] = None
    context: Optional[str] = None

@dataclass
class GeneratedQuestion:
    """생성된 문제"""
    question_text: str
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    options: Optional[List[str]] = None  # 객관식 선택지
    correct_answer: str = ""
    explanation: str = ""
    hints: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    estimated_time: Optional[int] = None  # 예상 소요 시간 (분)
    learning_objective: Optional[str] = None
    quality_score: float = 0.0  # AI 품질 평가 점수

class AIQuestionGeneratorEnhanced:
    """Phase 10: 강화된 AI 문제 생성기"""
    
    def __init__(self):
        self.ai_provider = AIProviderManager()
        self.langchain_provider = LangChainHybridProvider()
        self.redis_service = get_redis_service()
        
        # 문제 생성 템플릿
        self.question_templates = {
            QuestionType.MULTIPLE_CHOICE: self._get_multiple_choice_template(),
            QuestionType.CODING: self._get_coding_template(),
            QuestionType.SHORT_ANSWER: self._get_short_answer_template(),
            QuestionType.ESSAY: self._get_essay_template(),
            QuestionType.FILL_BLANK: self._get_fill_blank_template(),
            QuestionType.TRUE_FALSE: self._get_true_false_template(),
        }
    
    async def generate_questions(
        self, 
        request: QuestionGenerationRequest,
        db: Session
    ) -> List[GeneratedQuestion]:
        """메인 문제 생성 함수"""
        
        try:
            logger.info(f"문제 생성 시작: {request.subject_key}/{request.topic} ({request.count}개)")
            
            # 1. 사용자 컨텍스트 분석
            user_context = await self._analyze_user_context(request.user_id, db)
            
            # 2. 커리큘럼 기반 컨텍스트 구성
            curriculum_context = await self._get_curriculum_context(
                request.subject_key, 
                request.topic,
                db
            )
            
            # 3. 문제 생성 프롬프트 구성
            generation_prompt = await self._build_generation_prompt(
                request, 
                user_context, 
                curriculum_context
            )
            
            # 4. AI를 통한 문제 생성
            ai_request = AIRequest(
                prompt=generation_prompt,
                task_type="question_generation",
                user_id=request.user_id,
                priority="high"
            )
            
            ai_response = await self.ai_provider.generate_completion(ai_request)
            
            if not ai_response.get('success'):
                raise Exception(f"AI 문제 생성 실패: {ai_response.get('error')}")
            
            # 5. 응답 파싱 및 구조화
            questions = await self._parse_ai_response(
                ai_response['response'],
                request
            )
            
            # 6. 문제 품질 검증
            validated_questions = await self._validate_questions(questions, db)
            
            # 7. 캐싱 및 로깅
            await self._cache_generated_questions(request, validated_questions)
            await self._log_generation_metrics(request, validated_questions)
            
            logger.info(f"문제 생성 완료: {len(validated_questions)}개")
            return validated_questions
            
        except Exception as e:
            logger.error(f"문제 생성 실패: {str(e)}")
            # 폴백: 기본 문제 생성
            return await self._generate_fallback_questions(request, db)
    
    async def generate_adaptive_questions(
        self,
        user_id: int,
        subject_key: str,
        current_performance: Dict[str, Any],
        db: Session
    ) -> List[GeneratedQuestion]:
        """적응형 문제 생성 (사용자 성과 기반)"""
        
        try:
            # 사용자 성과 분석
            performance_analysis = await self._analyze_performance(
                user_id, 
                current_performance,
                db
            )
            
            # 최적 난이도 계산
            optimal_difficulty = await self._calculate_optimal_difficulty(
                performance_analysis
            )
            
            # 약점 토픽 식별
            weak_topics = await self._identify_weak_topics(
                user_id,
                subject_key,
                db
            )
            
            # 적응형 문제 생성 요청 구성
            adaptive_requests = []
            for topic in weak_topics[:3]:  # 상위 3개 약점 토픽
                request = QuestionGenerationRequest(
                    user_id=user_id,
                    subject_key=subject_key,
                    topic=topic['name'],
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    difficulty_level=optimal_difficulty,
                    count=2,
                    user_weaknesses=topic.get('weaknesses', [])
                )
                adaptive_requests.append(request)
            
            # 병렬 문제 생성
            all_questions = []
            for request in adaptive_requests:
                questions = await self.generate_questions(request, db)
                all_questions.extend(questions)
            
            return all_questions
            
        except Exception as e:
            logger.error(f"적응형 문제 생성 실패: {str(e)}")
            return []
    
    async def review_generated_question(
        self,
        question: GeneratedQuestion,
        review_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """생성된 문제 AI 검토"""
        
        review_prompt = f"""
        다음 생성된 문제를 교육 전문가 관점에서 검토해주세요:

        **문제**: {question.question_text}
        **정답**: {question.correct_answer}
        **설명**: {question.explanation}
        **난이도**: {question.difficulty_level.value}

        **검토 기준**:
        1. 교육적 가치 (1-10점)
        2. 문제 명확성 (1-10점)
        3. 난이도 적정성 (1-10점)
        4. 정답 정확성 (1-10점)
        5. 설명 충분성 (1-10점)

        **출력 형식** (JSON):
        {{
            "overall_score": 8.5,
            "criteria_scores": {{
                "educational_value": 9,
                "clarity": 8,
                "difficulty_appropriateness": 8,
                "answer_accuracy": 9,
                "explanation_quality": 8
            }},
            "strengths": ["문제가 명확함", "실용적인 예시"],
            "improvements": ["설명을 더 자세히", "힌트 추가 필요"],
            "approval_status": "approved",
            "reviewer_notes": "전반적으로 좋은 문제입니다."
        }}
        """
        
        ai_request = AIRequest(
            prompt=review_prompt,
            task_type="question_review",
            priority="normal"
        )
        
        response = await self.ai_provider.generate_completion(ai_request)
        
        if response.get('success'):
            try:
                return json.loads(response['response'])
            except json.JSONDecodeError:
                return {"error": "검토 결과 파싱 실패"}
        
        return {"error": "AI 검토 실패"}
    
    # ========== 내부 도우미 메서드들 ==========
    
    async def _analyze_user_context(self, user_id: int, db: Session) -> Dict[str, Any]:
        """사용자 학습 컨텍스트 분석"""
        
        # 사용자 정보 조회
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Redis에서 최근 학습 이력 조회
        learning_history = self.redis_service.get_cache(f"user_learning_history:{user_id}")
        performance_data = self.redis_service.get_cache(f"user_performance:{user_id}")
        
        return {
            "user_level": user.role,
            "learning_history": learning_history or [],
            "performance_data": performance_data or {},
            "preferences": getattr(user, 'learning_preferences', {})
        }
    
    async def _get_curriculum_context(
        self, 
        subject_key: str, 
        topic: str, 
        db: Session
    ) -> Dict[str, Any]:
        """커리큘럼 기반 컨텍스트 구성"""
        
        # 과목 정보 조회
        subject = db.query(Subject).filter(Subject.key == subject_key).first()
        
        # 관련 문제 샘플 조회
        existing_questions = db.query(Question).filter(
            Question.subject == subject_key,
            Question.topic == topic
        ).limit(3).all()
        
        return {
            "subject_info": {
                "name": subject.name if subject else subject_key,
                "description": subject.description if subject else ""
            },
            "topic_name": topic,
            "existing_questions_samples": [
                {
                    "text": q.question_text,
                    "difficulty": q.difficulty,
                    "type": getattr(q, 'question_type', 'unknown')
                }
                for q in existing_questions
            ]
        }
    
    async def _build_generation_prompt(
        self,
        request: QuestionGenerationRequest,
        user_context: Dict[str, Any],
        curriculum_context: Dict[str, Any]
    ) -> str:
        """문제 생성 프롬프트 구성"""
        
        template = self.question_templates[request.question_type]
        
        # 개인화 요소 추가
        personalization = ""
        if request.user_weaknesses:
            personalization += f"사용자 약점 영역: {', '.join(request.user_weaknesses)}\n"
        
        if request.learning_goals:
            personalization += f"학습 목표: {', '.join(request.learning_goals)}\n"
        
        # 컨텍스트 정보 통합
        context_info = f"""
        **과목**: {curriculum_context['subject_info']['name']}
        **토픽**: {curriculum_context['topic_name']}
        **난이도**: {request.difficulty_level.value}
        **문제 유형**: {request.question_type.value}
        **생성 개수**: {request.count}

        {personalization}

        **기존 문제 참고**:
        {json.dumps(curriculum_context['existing_questions_samples'], ensure_ascii=False, indent=2)}
        """
        
        return template.format(
            context=context_info,
            specific_requirements=request.context or ""
        )
    
    async def _parse_ai_response(
        self,
        ai_response: str,
        request: QuestionGenerationRequest
    ) -> List[GeneratedQuestion]:
        """AI 응답을 구조화된 문제로 파싱"""
        
        try:
            # JSON 형태로 파싱 시도
            if ai_response.strip().startswith('{') or ai_response.strip().startswith('['):
                parsed_data = json.loads(ai_response)
            else:
                # 텍스트 형태인 경우 구조화
                parsed_data = await self._structure_text_response(ai_response, request)
            
            questions = []
            if isinstance(parsed_data, list):
                for item in parsed_data:
                    question = self._create_question_from_data(item, request)
                    if question:
                        questions.append(question)
            elif isinstance(parsed_data, dict):
                question = self._create_question_from_data(parsed_data, request)
                if question:
                    questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"AI 응답 파싱 실패: {str(e)}")
            return []
    
    def _create_question_from_data(
        self, 
        data: Dict[str, Any], 
        request: QuestionGenerationRequest
    ) -> Optional[GeneratedQuestion]:
        """데이터에서 GeneratedQuestion 객체 생성"""
        
        try:
            return GeneratedQuestion(
                question_text=data.get('question', ''),
                question_type=request.question_type,
                difficulty_level=request.difficulty_level,
                options=data.get('options', []),
                correct_answer=data.get('answer', ''),
                explanation=data.get('explanation', ''),
                hints=data.get('hints', []),
                tags=data.get('tags', []),
                estimated_time=data.get('estimated_time', 5),
                learning_objective=data.get('learning_objective', ''),
                quality_score=data.get('quality_score', 7.0)
            )
        except Exception as e:
            logger.error(f"문제 객체 생성 실패: {str(e)}")
            return None
    
    async def _validate_questions(
        self, 
        questions: List[GeneratedQuestion],
        db: Session
    ) -> List[GeneratedQuestion]:
        """생성된 문제들의 품질 검증"""
        
        validated = []
        for question in questions:
            # 기본 검증
            if len(question.question_text) < 10:
                continue
            
            if not question.correct_answer:
                continue
            
            # 중복 검사
            if await self._is_duplicate_question(question, db):
                continue
            
            validated.append(question)
        
        return validated
    
    async def _is_duplicate_question(
        self, 
        question: GeneratedQuestion, 
        db: Session
    ) -> bool:
        """중복 문제 검사"""
        
        # 기존 문제와 유사성 검사 (간단한 버전)
        existing = db.query(Question).filter(
            Question.question_text.ilike(f"%{question.question_text[:50]}%")
        ).first()
        
        return existing is not None
    
    async def _generate_fallback_questions(
        self,
        request: QuestionGenerationRequest,
        db: Session
    ) -> List[GeneratedQuestion]:
        """폴백 문제 생성 (AI 실패 시)"""
        
        # 기본 템플릿 기반 문제 생성
        fallback_question = GeneratedQuestion(
            question_text=f"{request.topic}에 대한 기본 문제입니다.",
            question_type=request.question_type,
            difficulty_level=request.difficulty_level,
            correct_answer="기본 답변",
            explanation="폴백 모드에서 생성된 문제입니다.",
            quality_score=5.0
        )
        
        return [fallback_question]
    
    # ========== 문제 템플릿들 ==========
    
    def _get_multiple_choice_template(self) -> str:
        return """
        {context}

        다음 조건에 맞는 객관식 문제를 생성해주세요:

        1. 명확하고 구체적인 문제 출제
        2. 4개의 선택지 (정답 1개, 오답 3개)
        3. 정답에 대한 상세한 설명
        4. 학습 목표와 연관된 내용

        {specific_requirements}

        **출력 형식** (JSON):
        {{
            "question": "문제 내용",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
            "answer": "정답",
            "explanation": "정답 설명",
            "hints": ["힌트1", "힌트2"],
            "estimated_time": 3,
            "learning_objective": "학습 목표"
        }}
        """
    
    def _get_coding_template(self) -> str:
        return """
        {context}

        다음 조건에 맞는 코딩 문제를 생성해주세요:

        1. 실용적이고 교육적인 프로그래밍 문제
        2. 명확한 입출력 예시
        3. 예상 코드 솔루션
        4. 단계별 해결 과정 설명

        {specific_requirements}

        **출력 형식** (JSON):
        {{
            "question": "문제 설명",
            "input_format": "입력 형식",
            "output_format": "출력 형식",
            "examples": [
                {{"input": "예시 입력", "output": "예시 출력"}}
            ],
            "answer": "샘플 코드 솔루션",
            "explanation": "해결 과정 설명",
            "estimated_time": 15,
            "difficulty_hints": ["힌트1", "힌트2"]
        }}
        """
    
    def _get_short_answer_template(self) -> str:
        return """
        {context}

        다음 조건에 맞는 단답형 문제를 생성해주세요:

        1. 핵심 개념을 묻는 간결한 문제
        2. 명확한 정답 기준
        3. 부분 점수 기준 제시

        {specific_requirements}

        **출력 형식** (JSON):
        {{
            "question": "문제 내용",
            "answer": "모범 답안",
            "answer_keywords": ["핵심키워드1", "핵심키워드2"],
            "explanation": "답안 설명",
            "estimated_time": 5
        }}
        """
    
    def _get_essay_template(self) -> str:
        return """
        {context}

        다음 조건에 맞는 서술형 문제를 생성해주세요:

        1. 깊이 있는 사고를 요구하는 문제
        2. 구체적인 평가 기준
        3. 예시 답안 제시

        {specific_requirements}

        **출력 형식** (JSON):
        {{
            "question": "문제 내용",
            "answer": "예시 답안",
            "evaluation_criteria": ["평가기준1", "평가기준2"],
            "explanation": "출제 의도 및 핵심 포인트",
            "estimated_time": 20
        }}
        """
    
    def _get_fill_blank_template(self) -> str:
        return """
        {context}

        다음 조건에 맞는 빈칸 채우기 문제를 생성해주세요:

        1. 핵심 용어나 개념을 묻는 문제
        2. 문맥상 자연스러운 빈칸 배치
        3. 정확한 정답과 설명

        {specific_requirements}

        **출력 형식** (JSON):
        {{
            "question": "빈칸이 포함된 문제 (___ 로 표시)",
            "answer": "빈칸에 들어갈 정답",
            "explanation": "정답 설명",
            "estimated_time": 3
        }}
        """
    
    def _get_true_false_template(self) -> str:
        return """
        {context}

        다음 조건에 맞는 참/거짓 문제를 생성해주세요:

        1. 명확하게 참 또는 거짓을 판단할 수 있는 진술
        2. 상세한 근거와 설명
        3. 일반적인 오해나 헷갈리는 개념 활용

        {specific_requirements}

        **출력 형식** (JSON):
        {{
            "question": "참/거짓을 판단할 진술",
            "answer": "참 또는 거짓",
            "explanation": "정답 근거 및 설명",
            "estimated_time": 2
        }}
        """
    
    # ========== 적응형 학습 관련 메서드들 ==========
    
    async def _analyze_performance(
        self,
        user_id: int,
        current_performance: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """사용자 성과 분석"""
        
        # 기본 성과 분석 로직
        accuracy = current_performance.get('accuracy', 0.7)
        response_time = current_performance.get('avg_response_time', 60)
        consistency = current_performance.get('consistency', 0.8)
        
        return {
            "accuracy": accuracy,
            "response_time": response_time,
            "consistency": consistency,
            "performance_trend": "improving" if accuracy > 0.75 else "needs_support"
        }
    
    async def _calculate_optimal_difficulty(
        self,
        performance_analysis: Dict[str, Any]
    ) -> DifficultyLevel:
        """최적 난이도 계산"""
        
        accuracy = performance_analysis.get('accuracy', 0.7)
        
        if accuracy >= 0.85:
            return DifficultyLevel.ADVANCED
        elif accuracy >= 0.70:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER
    
    async def _identify_weak_topics(
        self,
        user_id: int,
        subject_key: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """약점 토픽 식별"""
        
        # 임시 구현 - 실제로는 더 정교한 분석 필요
        return [
            {"name": "변수와 자료형", "accuracy": 0.65, "weaknesses": ["타입 변환", "스코프"]},
            {"name": "제어문", "accuracy": 0.72, "weaknesses": ["조건문", "반복문"]},
            {"name": "함수", "accuracy": 0.58, "weaknesses": ["매개변수", "반환값"]}
        ]
    
    async def _cache_generated_questions(
        self,
        request: QuestionGenerationRequest,
        questions: List[GeneratedQuestion]
    ):
        """생성된 문제 캐싱"""
        
        cache_key = f"generated_questions:{request.user_id}:{request.subject_key}:{request.topic}"
        cache_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "request": {
                "subject_key": request.subject_key,
                "topic": request.topic,
                "difficulty": request.difficulty_level.value,
                "type": request.question_type.value
            },
            "questions": [
                {
                    "text": q.question_text,
                    "answer": q.correct_answer,
                    "quality_score": q.quality_score
                }
                for q in questions
            ]
        }
        
        self.redis_service.set_cache(cache_key, cache_data, 3600)  # 1시간 캐시
    
    async def _log_generation_metrics(
        self,
        request: QuestionGenerationRequest,
        questions: List[GeneratedQuestion]
    ):
        """문제 생성 지표 로깅"""
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": request.user_id,
            "subject_key": request.subject_key,
            "requested_count": request.count,
            "generated_count": len(questions),
            "avg_quality_score": sum(q.quality_score for q in questions) / len(questions) if questions else 0,
            "success_rate": len(questions) / request.count if request.count > 0 else 0
        }
        
        logger.info(f"문제 생성 지표: {json.dumps(metrics, ensure_ascii=False)}")
    
    async def _structure_text_response(
        self,
        text_response: str,
        request: QuestionGenerationRequest
    ) -> Dict[str, Any]:
        """텍스트 응답을 구조화"""
        
        # 간단한 텍스트 파싱 로직
        # 실제로는 더 정교한 NLP 파싱이 필요
        return {
            "question": text_response[:200] + "...",
            "answer": "파싱된 답변",
            "explanation": "텍스트에서 추출한 설명",
            "quality_score": 6.0
        }


# 의존성 주입을 위한 함수
def get_ai_question_generator() -> AIQuestionGeneratorEnhanced:
    """AI 문제 생성기 인스턴스 반환"""
    return AIQuestionGeneratorEnhanced()
