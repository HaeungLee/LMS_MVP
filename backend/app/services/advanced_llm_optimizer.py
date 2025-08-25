"""
LLM 최적화 시스템 - Phase 3
- 지능형 캐싱
- 지수 백오프
- 요청 큐잉
- 장애 복구
"""

import asyncio
import random
import hashlib
import json
import time
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from enum import Enum

from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """LLM 프로바이더"""
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class RequestPriority(Enum):
    """요청 우선순위"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class AdvancedLLMOptimizer:
    """고급 LLM 최적화 시스템"""
    
    def __init__(self):
        self.redis_service = get_redis_service()
        self.request_queue = asyncio.Queue(maxsize=100)
        self.processing = False
        
        # 프로바이더별 상태
        self.provider_status = {
            LLMProvider.OPENROUTER: {
                'failure_count': 0,
                'last_failure_time': 0,
                'consecutive_failures': 0,
                'circuit_breaker_open': False,
                'total_requests': 0,
                'successful_requests': 0
            }
        }
        
        # 백오프 설정
        self.backoff_config = {
            'base_delay': 1.0,
            'max_delay': 60.0,
            'multiplier': 2.0,
            'jitter': True
        }
        
        # 캐시 설정
        self.cache_config = {
            'default_ttl': 3600,  # 1시간
            'max_prompt_length': 10000,
            'hit_ratio_threshold': 0.7
        }
        
        # 회로 차단기 설정
        self.circuit_breaker_config = {
            'failure_threshold': 5,
            'recovery_time': 300,
            'half_open_max_calls': 3
        }
    
    async def execute_optimized_llm_call(
        self,
        llm_call: Callable,
        prompt: str,
        provider: LLMProvider = LLMProvider.OPENROUTER,
        priority: RequestPriority = RequestPriority.NORMAL,
        cache_ttl: Optional[int] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Optional[str]:
        """최적화된 LLM 호출"""
        
        # 1. 캐시 확인
        cache_result = await self._check_cache(prompt, provider)
        if cache_result:
            logger.info(f"캐시 히트: {provider.value}")
            return cache_result
        
        # 2. 회로 차단기 확인
        if self._is_circuit_breaker_open(provider):
            logger.warning(f"회로 차단기 열림: {provider.value}")
            return await self._handle_circuit_breaker_open(prompt, provider)
        
        # 3. 지수 백오프로 재시도
        for attempt in range(max_retries):
            try:
                # 백오프 지연
                if attempt > 0:
                    delay = await self._calculate_backoff_delay(provider, attempt)
                    await asyncio.sleep(delay)
                
                # LLM 호출
                self._update_request_metrics(provider, attempt=True)
                
                result = await llm_call(**kwargs)
                
                if result:
                    # 성공 처리
                    self._update_provider_success(provider)
                    
                    # 캐시 저장
                    await self._save_to_cache(prompt, result, provider, cache_ttl or self.cache_config['default_ttl'])
                    
                    return result
                
            except Exception as e:
                logger.error(f"LLM 호출 실패 (시도 {attempt + 1}/{max_retries}): {str(e)}")
                self._update_provider_failure(provider, str(e))
                
                if attempt == max_retries - 1:
                    return None
        
        return None
    
    async def _check_cache(self, prompt: str, provider: LLMProvider) -> Optional[str]:
        """캐시 확인"""
        
        if len(prompt) > self.cache_config['max_prompt_length']:
            return None
        
        try:
            prompt_hash = self._generate_prompt_hash(prompt, provider)
            cached_response = self.redis_service.get_llm_cache(prompt_hash)
            
            if cached_response:
                await self._update_cache_metrics(provider, hit=True)
                return cached_response
            
            await self._update_cache_metrics(provider, hit=False)
            return None
            
        except Exception as e:
            logger.error(f"캐시 확인 실패: {str(e)}")
            return None
    
    async def _calculate_backoff_delay(self, provider: LLMProvider, attempt: int) -> float:
        """백오프 지연 시간 계산"""
        
        provider_info = self.provider_status[provider]
        base_delay = self.backoff_config['base_delay']
        multiplier = self.backoff_config['multiplier']
        max_delay = self.backoff_config['max_delay']
        
        # 지수 백오프
        delay = min(max_delay, base_delay * (multiplier ** attempt))
        
        # 연속 실패 시 추가 지연
        if provider_info['consecutive_failures'] > 3:
            delay *= 1.5
        
        # 지터 추가
        if self.backoff_config['jitter']:
            delay += random.uniform(0, delay * 0.1)
        
        return delay
    
    def _generate_prompt_hash(self, prompt: str, provider: LLMProvider) -> str:
        """프롬프트 해시 생성"""
        content = f"{provider.value}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _save_to_cache(self, prompt: str, response: str, provider: LLMProvider, ttl: int):
        """캐시에 응답 저장"""
        
        if len(prompt) > self.cache_config['max_prompt_length']:
            return
        
        try:
            prompt_hash = self._generate_prompt_hash(prompt, provider)
            self.redis_service.set_llm_cache(prompt_hash, response, ttl)
            logger.debug(f"LLM 응답 캐시 저장: {provider.value}")
        except Exception as e:
            logger.error(f"캐시 저장 실패: {str(e)}")
    
    def _is_circuit_breaker_open(self, provider: LLMProvider) -> bool:
        """회로 차단기 상태 확인"""
        
        provider_info = self.provider_status[provider]
        
        if not provider_info['circuit_breaker_open']:
            return False
        
        # 복구 시간 확인
        current_time = time.time()
        if (current_time - provider_info['last_failure_time']) > self.circuit_breaker_config['recovery_time']:
            provider_info['circuit_breaker_open'] = False
            provider_info['consecutive_failures'] = 0
            logger.info(f"회로 차단기 Half-Open 상태로 전환: {provider.value}")
            return False
        
        return True
    
    async def _handle_circuit_breaker_open(self, prompt: str, provider: LLMProvider) -> Optional[str]:
        """회로 차단기 열림 상태 처리"""
        
        fallback_responses = {
            LLMProvider.OPENROUTER: "죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.",
        }
        
        logger.warning(f"회로 차단기 열림 - 폴백 응답 사용: {provider.value}")
        return fallback_responses.get(provider, "서비스를 사용할 수 없습니다.")
    
    def _update_provider_success(self, provider: LLMProvider):
        """프로바이더 성공 메트릭 업데이트"""
        provider_info = self.provider_status[provider]
        provider_info['successful_requests'] += 1
        provider_info['consecutive_failures'] = 0
        provider_info['circuit_breaker_open'] = False
    
    def _update_provider_failure(self, provider: LLMProvider, error: str):
        """프로바이더 실패 메트릭 업데이트"""
        provider_info = self.provider_status[provider]
        provider_info['failure_count'] += 1
        provider_info['consecutive_failures'] += 1
        provider_info['last_failure_time'] = time.time()
        
        # 회로 차단기 활성화 확인
        if provider_info['consecutive_failures'] >= self.circuit_breaker_config['failure_threshold']:
            provider_info['circuit_breaker_open'] = True
            logger.warning(f"회로 차단기 활성화: {provider.value}")
    
    def _update_request_metrics(self, provider: LLMProvider, attempt: bool = True):
        """요청 메트릭 업데이트"""
        provider_info = self.provider_status[provider]
        if attempt:
            provider_info['total_requests'] += 1
    
    async def _update_cache_metrics(self, provider: LLMProvider, hit: bool):
        """캐시 메트릭 업데이트"""
        try:
            key = f"cache_metrics:{provider.value}"
            metrics = self.redis_service.get_cache(key) or {'hits': 0, 'misses': 0}
            
            if hit:
                metrics['hits'] += 1
            else:
                metrics['misses'] += 1
            
            self.redis_service.set_cache(key, metrics, 86400)
            
        except Exception as e:
            logger.error(f"캐시 메트릭 업데이트 실패: {str(e)}")
    
    def get_provider_stats(self, provider: LLMProvider) -> Dict[str, Any]:
        """프로바이더 통계 조회"""
        provider_info = self.provider_status[provider]
        total_requests = provider_info['total_requests']
        
        return {
            'provider': provider.value,
            'total_requests': total_requests,
            'successful_requests': provider_info['successful_requests'],
            'failure_count': provider_info['failure_count'],
            'success_rate': (provider_info['successful_requests'] / total_requests) if total_requests > 0 else 0,
            'consecutive_failures': provider_info['consecutive_failures'],
            'circuit_breaker_open': provider_info['circuit_breaker_open'],
            'last_failure_time': provider_info['last_failure_time']
        }
    
    async def get_cache_stats(self, provider: LLMProvider) -> Dict[str, Any]:
        """캐시 통계 조회"""
        try:
            key = f"cache_metrics:{provider.value}"
            metrics = self.redis_service.get_cache(key) or {'hits': 0, 'misses': 0}
            
            total_requests = metrics['hits'] + metrics['misses']
            hit_rate = (metrics['hits'] / total_requests) if total_requests > 0 else 0
            
            return {
                'provider': provider.value,
                'cache_hits': metrics['hits'],
                'cache_misses': metrics['misses'],
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'hit_rate_percentage': f"{hit_rate * 100:.1f}%"
            }
            
        except Exception as e:
            logger.error(f"캐시 통계 조회 실패: {str(e)}")
            return {'error': str(e)}

# 전역 인스턴스
llm_optimizer = AdvancedLLMOptimizer()

def get_llm_optimizer() -> AdvancedLLMOptimizer:
    """LLM 최적화 인스턴스 반환"""
    return llm_optimizer
