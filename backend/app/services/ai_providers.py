"""
AI 제공자 통합 시스템 - Phase 4
- OpenRouter 기본 지원 (무료/저비용 모델)
- OpenAI 호환 (필요시 쉬운 전환)
- 모델별 특성 최적화
- 비용 효율적 운영
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.redis_service import get_redis_service
from app.services.advanced_llm_optimizer import get_llm_optimizer

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """AI 제공자"""
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class ModelTier(Enum):
    """모델 등급 (비용 기준)"""
    FREE = "free"           # 무료 모델
    BASIC = "basic"         # 저비용 모델  
    PREMIUM = "premium"     # 고성능 모델
    ENTERPRISE = "enterprise"  # 최고급 모델

@dataclass
class ModelConfig:
    """모델 설정"""
    name: str
    provider: AIProvider
    tier: ModelTier
    cost_per_1k_tokens: float
    max_tokens: int
    context_window: int
    strengths: List[str]
    best_for: List[str]

@dataclass
class AIRequest:
    """AI 요청"""
    prompt: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    model_preference: Optional[ModelTier] = None
    task_type: str = "general"
    user_id: Optional[int] = None
    priority: str = "normal"

class AIProviderManager:
    """AI 제공자 통합 관리"""
    
    def __init__(self):
        self.redis_service = get_redis_service()
        self.llm_optimizer = get_llm_optimizer()
        
        # 사용 가능한 모델 정의
        self.models = {
            # OpenRouter 무료/저비용 모델
            "google/gemma-2-9b-it:free": ModelConfig(
                name="google/gemma-2-9b-it:free",
                provider=AIProvider.OPENROUTER,
                tier=ModelTier.FREE,
                cost_per_1k_tokens=0.0,
                max_tokens=8192,
                context_window=8192,
                strengths=["빠른 응답", "기본 추론", "코딩 지원"],
                best_for=["일반 피드백", "간단한 질문 답변", "기초 분석"]
            ),
            "meta-llama/llama-3.1-8b-instruct:free": ModelConfig(
                name="meta-llama/llama-3.1-8b-instruct:free",
                provider=AIProvider.OPENROUTER,
                tier=ModelTier.FREE,
                cost_per_1k_tokens=0.0,
                max_tokens=8192,
                context_window=128000,
                strengths=["긴 컨텍스트", "논리적 추론", "다국어"],
                best_for=["학습 분석", "패턴 인식", "요약"]
            ),
            "microsoft/phi-3-medium-128k-instruct:free": ModelConfig(
                name="microsoft/phi-3-medium-128k-instruct:free",
                provider=AIProvider.OPENROUTER,
                tier=ModelTier.FREE,
                cost_per_1k_tokens=0.0,
                max_tokens=4096,
                context_window=128000,
                strengths=["코드 이해", "수학", "논리"],
                best_for=["코딩 피드백", "문제 해결", "알고리즘 분석"]
            ),
            
            # OpenRouter 저비용 모델
            "anthropic/claude-3-haiku": ModelConfig(
                name="anthropic/claude-3-haiku",
                provider=AIProvider.OPENROUTER,
                tier=ModelTier.BASIC,
                cost_per_1k_tokens=0.25,
                max_tokens=4096,
                context_window=200000,
                strengths=["빠르고 정확", "안전한 응답", "분석적"],
                best_for=["상세 피드백", "멘토링", "학습 계획"]
            ),
            "google/gemini-flash-1.5": ModelConfig(
                name="google/gemini-flash-1.5",
                provider=AIProvider.OPENROUTER,
                tier=ModelTier.BASIC,
                cost_per_1k_tokens=0.075,
                max_tokens=8192,
                context_window=1000000,
                strengths=["매우 긴 컨텍스트", "멀티모달", "빠른 처리"],
                best_for=["프로젝트 분석", "코드 리뷰", "포트폴리오 평가"]
            ),
            
            # OpenAI 호환 (필요시 사용)
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                provider=AIProvider.OPENAI,
                tier=ModelTier.BASIC,
                cost_per_1k_tokens=0.5,
                max_tokens=4096,
                context_window=16385,
                strengths=["범용성", "안정성", "빠른 응답"],
                best_for=["일반 대화", "피드백", "질문 답변"]
            ),
            "gpt-4o-mini": ModelConfig(
                name="gpt-4o-mini",
                provider=AIProvider.OPENAI,
                tier=ModelTier.PREMIUM,
                cost_per_1k_tokens=0.15,
                max_tokens=16384,
                context_window=128000,
                strengths=["고품질 추론", "창의성", "복잡한 분석"],
                best_for=["심층 분석", "개인화 추천", "고급 멘토링"]
            ),
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                provider=AIProvider.OPENAI,
                tier=ModelTier.ENTERPRISE,
                cost_per_1k_tokens=2.5,
                max_tokens=4096,
                context_window=128000,
                strengths=["최고 품질", "복잡한 추론", "멀티모달"],
                best_for=["최고급 분석", "연구", "전문가 수준 피드백"]
            )
        }
        
        # 작업 유형별 최적 모델 매핑
        self.task_model_mapping = {
            "feedback": {
                ModelTier.FREE: "google/gemma-2-9b-it:free",
                ModelTier.BASIC: "anthropic/claude-3-haiku",
                ModelTier.PREMIUM: "gpt-4o-mini"
            },
            "analysis": {
                ModelTier.FREE: "meta-llama/llama-3.1-8b-instruct:free", 
                ModelTier.BASIC: "google/gemini-flash-1.5",
                ModelTier.PREMIUM: "gpt-4o-mini"
            },
            "coding": {
                ModelTier.FREE: "microsoft/phi-3-medium-128k-instruct:free",
                ModelTier.BASIC: "anthropic/claude-3-haiku",
                ModelTier.PREMIUM: "gpt-4o-mini"
            },
            "mentoring": {
                ModelTier.FREE: "google/gemma-2-9b-it:free",
                ModelTier.BASIC: "anthropic/claude-3-haiku", 
                ModelTier.PREMIUM: "gpt-4o-mini"
            },
            "project_review": {
                ModelTier.FREE: "meta-llama/llama-3.1-8b-instruct:free",
                ModelTier.BASIC: "google/gemini-flash-1.5",
                ModelTier.PREMIUM: "gpt-4o"
            }
        }
        
        # 클라이언트 초기화
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """AI 클라이언트 초기화"""
        try:
            # OpenRouter 클라이언트 (OpenAI 호환)
            if hasattr(settings, 'openrouter_api_key') and settings.openrouter_api_key:
                self.clients[AIProvider.OPENROUTER] = AsyncOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=settings.openrouter_api_key,
                )
                logger.info("OpenRouter 클라이언트 초기화 완료")
            
            # OpenAI 클라이언트
            if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                self.clients[AIProvider.OPENAI] = AsyncOpenAI(
                    api_key=settings.openai_api_key,
                )
                logger.info("OpenAI 클라이언트 초기화 완료")
                
        except Exception as e:
            logger.error(f"AI 클라이언트 초기화 실패: {str(e)}")
    
    def select_optimal_model(self, request: AIRequest) -> ModelConfig:
        """최적 모델 선택"""
        
        # 1. 사용자 선호도 또는 기본 등급 결정
        preferred_tier = request.model_preference or ModelTier.FREE
        
        # 2. 작업 유형별 최적 모델 찾기
        task_models = self.task_model_mapping.get(request.task_type, self.task_model_mapping["feedback"])
        
        # 3. 선호 등급의 모델 선택
        model_name = task_models.get(preferred_tier)
        if not model_name:
            # 폴백: FREE 등급 모델 사용
            model_name = task_models.get(ModelTier.FREE)
        
        # 4. 모델 설정 반환
        model_config = self.models.get(model_name)
        if not model_config:
            # 최종 폴백: 기본 무료 모델
            model_config = self.models["google/gemma-2-9b-it:free"]
        
        logger.info(f"선택된 모델: {model_config.name} (등급: {model_config.tier.value})")
        return model_config
    
    async def generate_completion(self, request: AIRequest) -> Dict[str, Any]:
        """AI 완성 생성"""
        
        try:
            # 최적 모델 선택
            model_config = self.select_optimal_model(request)
            
            # 캐시 확인
            cache_key = self._generate_cache_key(request.prompt, model_config.name)
            cached_response = self.redis_service.get_llm_cache(cache_key)
            
            if cached_response:
                logger.info(f"캐시 히트: {model_config.name}")
                return {
                    'success': True,
                    'response': cached_response,
                    'model': model_config.name,
                    'provider': model_config.provider.value,
                    'tier': model_config.tier.value,
                    'cached': True,
                    'cost_saved': model_config.cost_per_1k_tokens * (len(request.prompt) / 1000)
                }
            
            # AI 호출
            response = await self._call_ai_api(request, model_config)
            
            if response['success']:
                # 캐시 저장
                self.redis_service.set_llm_cache(cache_key, response['response'], 3600)
                
                # 비용 추적
                await self._track_usage(request.user_id, model_config, response.get('tokens_used', 0))
            
            return response
            
        except Exception as e:
            logger.error(f"AI 완성 생성 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_used': True
            }
    
    async def _call_ai_api(self, request: AIRequest, model_config: ModelConfig) -> Dict[str, Any]:
        """실제 AI API 호출"""
        
        client = self.clients.get(model_config.provider)
        if not client:
            raise Exception(f"클라이언트 없음: {model_config.provider}")
        
        try:
            # 토큰 수 제한 적용
            max_tokens = min(
                request.max_tokens or model_config.max_tokens,
                model_config.max_tokens
            )
            
            # API 호출 (OpenAI 호환 형식)
            completion = await client.chat.completions.create(
                model=model_config.name,
                messages=[
                    {"role": "user", "content": request.prompt}
                ],
                max_tokens=max_tokens,
                temperature=request.temperature,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            response_text = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens if completion.usage else 0
            
            return {
                'success': True,
                'response': response_text,
                'model': model_config.name,
                'provider': model_config.provider.value,
                'tier': model_config.tier.value,
                'tokens_used': tokens_used,
                'cost_estimate': (tokens_used / 1000) * model_config.cost_per_1k_tokens,
                'cached': False
            }
            
        except Exception as e:
            logger.error(f"AI API 호출 실패: {str(e)}")
            
            # 폴백 처리
            if model_config.tier != ModelTier.FREE:
                # 무료 모델로 재시도
                free_request = AIRequest(
                    prompt=request.prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    model_preference=ModelTier.FREE,
                    task_type=request.task_type,
                    user_id=request.user_id
                )
                return await self.generate_completion(free_request)
            
            raise e
    
    def _generate_cache_key(self, prompt: str, model_name: str) -> str:
        """캐시 키 생성"""
        import hashlib
        content = f"{model_name}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _track_usage(self, user_id: Optional[int], model_config: ModelConfig, tokens_used: int):
        """사용량 추적"""
        try:
            usage_data = {
                'user_id': user_id,
                'model': model_config.name,
                'provider': model_config.provider.value,
                'tier': model_config.tier.value,
                'tokens_used': tokens_used,
                'cost': (tokens_used / 1000) * model_config.cost_per_1k_tokens,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Redis에 사용량 기록
            usage_key = f"ai_usage:{datetime.utcnow().strftime('%Y-%m-%d')}"
            usage_list = self.redis_service.get_cache(usage_key) or []
            usage_list.append(usage_data)
            
            # 일일 사용량 유지 (최대 1000개 기록)
            if len(usage_list) > 1000:
                usage_list = usage_list[-1000:]
            
            self.redis_service.set_cache(usage_key, usage_list, 86400)  # 24시간
            
            logger.debug(f"사용량 추적: {model_config.name} - {tokens_used} 토큰")
            
        except Exception as e:
            logger.error(f"사용량 추적 실패: {str(e)}")
    
    def get_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """사용량 통계 조회"""
        try:
            from datetime import timedelta
            
            total_cost = 0
            total_tokens = 0
            provider_stats = {}
            tier_stats = {}
            
            # 지정된 일수만큼 조회
            for i in range(days):
                date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
                usage_key = f"ai_usage:{date}"
                daily_usage = self.redis_service.get_cache(usage_key) or []
                
                for usage in daily_usage:
                    total_cost += usage.get('cost', 0)
                    total_tokens += usage.get('tokens_used', 0)
                    
                    provider = usage.get('provider', 'unknown')
                    tier = usage.get('tier', 'unknown')
                    
                    provider_stats[provider] = provider_stats.get(provider, 0) + usage.get('cost', 0)
                    tier_stats[tier] = tier_stats.get(tier, 0) + usage.get('cost', 0)
            
            return {
                'period_days': days,
                'total_cost': round(total_cost, 4),
                'total_tokens': total_tokens,
                'avg_daily_cost': round(total_cost / days, 4),
                'cost_by_provider': provider_stats,
                'cost_by_tier': tier_stats,
                'cost_efficiency': 'excellent' if total_cost < 1.0 else 'good' if total_cost < 5.0 else 'review_needed'
            }
            
        except Exception as e:
            logger.error(f"사용량 통계 조회 실패: {str(e)}")
            return {'error': str(e)}
    
    def get_available_models(self, tier: Optional[ModelTier] = None) -> List[Dict[str, Any]]:
        """사용 가능한 모델 목록"""
        models = []
        
        for model_config in self.models.values():
            if tier is None or model_config.tier == tier:
                models.append({
                    'name': model_config.name,
                    'provider': model_config.provider.value,
                    'tier': model_config.tier.value,
                    'cost_per_1k_tokens': model_config.cost_per_1k_tokens,
                    'max_tokens': model_config.max_tokens,
                    'context_window': model_config.context_window,
                    'strengths': model_config.strengths,
                    'best_for': model_config.best_for
                })
        
        return sorted(models, key=lambda x: x['cost_per_1k_tokens'])

# 전역 인스턴스
ai_provider_manager = AIProviderManager()

def get_ai_provider_manager() -> AIProviderManager:
    """AI 제공자 관리자 인스턴스 반환"""
    return ai_provider_manager

# 편의 함수들
async def generate_ai_response(
    prompt: str,
    task_type: str = "general",
    model_preference: Optional[ModelTier] = None,
    user_id: Optional[int] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """AI 응답 생성 (편의 함수)"""
    
    request = AIRequest(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        model_preference=model_preference or ModelTier.FREE,
        task_type=task_type,
        user_id=user_id
    )
    
    return await ai_provider_manager.generate_completion(request)

async def generate_feedback(
    user_answer: str,
    correct_answer: str,
    question_context: str,
    user_id: Optional[int] = None,
    use_premium: bool = False
) -> str:
    """학습 피드백 생성 (특화 함수)"""
    
    prompt = f"""다음 학습자의 답안에 대해 건설적이고 구체적인 피드백을 제공해주세요.

문제 맥락: {question_context}

정답: {correct_answer}

학습자 답안: {user_answer}

피드백 지침:
1. 긍정적인 부분을 먼저 언급
2. 개선할 점을 구체적으로 설명
3. 학습자 수준에 맞는 추가 학습 방향 제시
4. 격려와 동기부여 포함

한국어로 친근하고 도움이 되는 톤으로 작성해주세요."""

    tier = ModelTier.BASIC if use_premium else ModelTier.FREE
    
    response = await generate_ai_response(
        prompt=prompt,
        task_type="feedback",
        model_preference=tier,
        user_id=user_id,
        temperature=0.7
    )
    
    return response.get('response', '피드백 생성에 실패했습니다.')

async def analyze_learning_pattern(
    user_submissions: List[Dict],
    user_id: int,
    use_premium: bool = False
) -> Dict[str, Any]:
    """학습 패턴 분석 (특화 함수)"""
    
    # 제출 데이터 요약
    submissions_summary = []
    for submission in user_submissions[-10:]:  # 최근 10개
        submissions_summary.append({
            'topic': submission.get('topic', ''),
            'correct': submission.get('is_correct', False),
            'response_time': submission.get('response_time', 0),
            'difficulty': submission.get('difficulty', 1)
        })
    
    prompt = f"""다음 학습자의 최근 학습 데이터를 분석하여 학습 패턴과 개선 방향을 제시해주세요.

학습 데이터: {json.dumps(submissions_summary, ensure_ascii=False, indent=2)}

분석해야 할 요소:
1. 강점 영역과 약점 영역 식별
2. 학습 속도와 난이도 선호도 분석
3. 개선이 필요한 학습 습관
4. 다음 학습 단계 추천
5. 개인화된 학습 전략 제안

결과를 JSON 형태로 구조화하여 다음 형식으로 제공해주세요:
{{
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["약점1", "약점2"],
  "learning_speed": "fast/normal/slow",
  "preferred_difficulty": 1-5,
  "recommendations": ["추천1", "추천2"],
  "next_focus_areas": ["영역1", "영역2"]
}}"""

    tier = ModelTier.BASIC if use_premium else ModelTier.FREE
    
    response = await generate_ai_response(
        prompt=prompt,
        task_type="analysis",
        model_preference=tier,
        user_id=user_id,
        temperature=0.3
    )
    
    try:
        # JSON 파싱 시도
        result = json.loads(response.get('response', '{}'))
        result['analysis_model'] = response.get('model', 'unknown')
        result['analysis_cost'] = response.get('cost_estimate', 0)
        return result
    except:
        # 파싱 실패시 기본 구조 반환
        return {
            'strengths': ['분석 데이터 부족'],
            'weaknesses': ['더 많은 학습 필요'],
            'learning_speed': 'normal',
            'preferred_difficulty': 3,
            'recommendations': ['꾸준한 학습 지속'],
            'next_focus_areas': ['기초 개념 강화'],
            'raw_response': response.get('response', ''),
            'analysis_error': 'JSON 파싱 실패'
        }
