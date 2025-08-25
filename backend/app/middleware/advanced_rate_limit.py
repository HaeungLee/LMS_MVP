"""
고급 레이트리밋 시스템 - Phase 3
- 사용자별 개인화 제한
- 동적 임계값 조정
- 우선순위 기반 제한
- 분산 레이트리밋
"""

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import time
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from app.services.redis_service import get_redis_service
from app.models.orm import User

logger = logging.getLogger(__name__)

class UserTier(Enum):
    """사용자 등급"""
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"

class ActionPriority(Enum):
    """액션 우선순위"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class AdvancedRateLimiter:
    """고급 레이트리밋 시스템"""
    
    def __init__(self):
        self.redis_service = get_redis_service()
        
        # 사용자 등급별 기본 제한
        self.tier_multipliers = {
            UserTier.FREE: 1.0,
            UserTier.PREMIUM: 2.0,
            UserTier.ADMIN: 10.0
        }
        
        # 액션별 기본 제한 설정
        self.base_limits = {
            'submission': {
                'requests': 10,
                'window': 300,
                'priority': ActionPriority.NORMAL,
                'burst_allowance': 3
            },
            'feedback_request': {
                'requests': 20,
                'window': 300,
                'priority': ActionPriority.HIGH,
                'burst_allowance': 5
            },
            'ai_generation': {
                'requests': 5,
                'window': 600,
                'priority': ActionPriority.HIGH,
                'burst_allowance': 2
            },
            'recommendation_request': {
                'requests': 15,
                'window': 300,
                'priority': ActionPriority.NORMAL,
                'burst_allowance': 3
            },
            'login_attempt': {
                'requests': 5,
                'window': 300,
                'priority': ActionPriority.CRITICAL,
                'burst_allowance': 0
            },
            'api_call': {
                'requests': 100,
                'window': 60,
                'priority': ActionPriority.LOW,
                'burst_allowance': 20
            }
        }
        
        # 시간대별 가중치
        self.time_based_multipliers = {
            'peak_hours': 0.8,    # 피크 시간(9-18시) 제한 강화
            'normal_hours': 1.0,   # 일반 시간
            'off_hours': 1.5      # 오프 시간(23-6시) 제한 완화
        }
    
    def get_user_tier(self, user: Optional[User]) -> UserTier:
        """사용자 등급 확인"""
        if not user:
            return UserTier.FREE
        
        if hasattr(user, 'role'):
            if user.role == 'admin':
                return UserTier.ADMIN
            elif user.role == 'premium':
                return UserTier.PREMIUM
        
        return UserTier.FREE
    
    def get_time_multiplier(self) -> float:
        """시간대별 가중치 계산"""
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 18:
            return self.time_based_multipliers['peak_hours']
        elif 23 <= current_hour or current_hour <= 6:
            return self.time_based_multipliers['off_hours']
        else:
            return self.time_based_multipliers['normal_hours']
    
    def calculate_effective_limit(
        self, 
        action: str, 
        user_tier: UserTier,
        current_load: float = 1.0
    ) -> Tuple[int, int]:
        """효과적인 제한값 계산"""
        
        if action not in self.base_limits:
            # 기본 제한
            return 60, 60  # 1분에 60회
        
        base_config = self.base_limits[action]
        base_requests = base_config['requests']
        window = base_config['window']
        
        # 사용자 등급 적용
        tier_multiplier = self.tier_multipliers[user_tier]
        
        # 시간대 가중치 적용
        time_multiplier = self.get_time_multiplier()
        
        # 시스템 부하 고려
        load_multiplier = max(0.3, 1.0 - (current_load - 1.0) * 0.5)
        
        # 최종 제한값 계산
        effective_requests = int(
            base_requests * tier_multiplier * time_multiplier * load_multiplier
        )
        
        # 최소 제한값 보장
        effective_requests = max(1, effective_requests)
        
        return effective_requests, window
    
    async def check_rate_limit(
        self, 
        user_id: Optional[int], 
        action: str,
        user: Optional[User] = None,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """레이트리밋 확인"""
        
        try:
            # 사용자 식별
            identifier = f"user:{user_id}" if user_id else f"ip:{self._get_client_ip(request)}"
            
            # 사용자 등급 확인
            user_tier = self.get_user_tier(user)
            
            # 시스템 부하 확인 (간단한 구현)
            current_load = await self._get_system_load()
            
            # 효과적인 제한값 계산
            effective_requests, window = self.calculate_effective_limit(
                action, user_tier, current_load
            )
            
            # Redis 키 생성
            key = f"rate_limit:{identifier}:{action}"
            current_time = int(time.time())
            window_start = current_time - window
            
            # 레이트리밋 확인 및 업데이트
            if self.redis_service._is_connected():
                # Redis 슬라이딩 윈도우
                pipe = self.redis_service.redis_client.pipeline()
                
                # 만료된 요청 제거
                pipe.zremrangebyscore(key, 0, window_start)
                
                # 현재 요청 수 조회
                pipe.zcard(key)
                
                # 현재 요청 추가
                pipe.zadd(key, {str(current_time): current_time})
                
                # TTL 설정
                pipe.expire(key, window)
                
                results = pipe.execute()
                current_requests = results[1]
                
                # 버스트 허용량 확인
                burst_allowance = self.base_limits.get(action, {}).get('burst_allowance', 0)
                effective_limit_with_burst = effective_requests + burst_allowance
                
                if current_requests >= effective_limit_with_burst:
                    # 제한 초과
                    reset_time = window_start + window
                    return {
                        'allowed': False,
                        'current_requests': current_requests,
                        'limit': effective_requests,
                        'reset_time': reset_time,
                        'retry_after': reset_time - current_time,
                        'user_tier': user_tier.value,
                        'action': action
                    }
                
                return {
                    'allowed': True,
                    'current_requests': current_requests,
                    'limit': effective_requests,
                    'remaining': effective_requests - current_requests,
                    'reset_time': window_start + window,
                    'user_tier': user_tier.value,
                    'action': action
                }
            
            else:
                # Redis 없는 경우 기본 허용
                return {
                    'allowed': True,
                    'current_requests': 0,
                    'limit': effective_requests,
                    'remaining': effective_requests,
                    'fallback': True
                }
                
        except Exception as e:
            logger.error(f"레이트리밋 확인 실패: {str(e)}")
            # 오류 시 기본 허용 (가용성 우선)
            return {
                'allowed': True,
                'error': str(e),
                'fallback': True
            }
    
    async def _get_system_load(self) -> float:
        """시스템 부하 측정"""
        try:
            # Redis 연결 수 기반 간단한 부하 측정
            if self.redis_service._is_connected():
                info = self.redis_service.redis_client.info()
                connected_clients = info.get('connected_clients', 1)
                
                # 10개 연결 이상일 때 부하로 간주
                return min(2.0, connected_clients / 10.0)
            
            return 1.0
        except:
            return 1.0
    
    def _get_client_ip(self, request: Optional[Request]) -> str:
        """클라이언트 IP 추출"""
        if not request:
            return "unknown"
        
        # 프록시 헤더 확인
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 직접 연결
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"

# 컨텍스트별 레이트리밋 데코레이터
class RateLimitContext:
    """레이트리밋 컨텍스트 관리"""
    
    def __init__(self, action: str, error_message: Optional[str] = None):
        self.action = action
        self.error_message = error_message or f"Rate limit exceeded for {action}"
        self.rate_limiter = AdvancedRateLimiter()
    
    async def __call__(self, request: Request, user: Optional[User] = None) -> Optional[Response]:
        """레이트리밋 검사 실행"""
        
        user_id = getattr(user, 'id', None) if user else None
        
        # 레이트리밋 확인
        limit_result = await self.rate_limiter.check_rate_limit(
            user_id=user_id,
            action=self.action,
            user=user,
            request=request
        )
        
        if not limit_result['allowed']:
            # 제한 초과 응답
            headers = {
                'X-RateLimit-Limit': str(limit_result['limit']),
                'X-RateLimit-Remaining': str(0),
                'X-RateLimit-Reset': str(limit_result['reset_time']),
                'Retry-After': str(limit_result['retry_after'])
            }
            
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'Rate limit exceeded',
                    'message': self.error_message,
                    'limit': limit_result['limit'],
                    'retry_after': limit_result['retry_after'],
                    'user_tier': limit_result.get('user_tier')
                },
                headers=headers
            )
        
        # 성공 시 헤더 추가
        if hasattr(request, 'state'):
            request.state.rate_limit_headers = {
                'X-RateLimit-Limit': str(limit_result['limit']),
                'X-RateLimit-Remaining': str(limit_result.get('remaining', 0)),
                'X-RateLimit-Reset': str(limit_result.get('reset_time', 0))
            }
        
        return None  # 제한 없음

# 인스턴스 생성
advanced_rate_limiter = AdvancedRateLimiter()

# 액션별 컨텍스트
submission_rate_limit = RateLimitContext('submission', '제출 요청이 너무 많습니다. 잠시 후 다시 시도해주세요.')
feedback_rate_limit = RateLimitContext('feedback_request', '피드백 요청이 너무 많습니다. 잠시 후 다시 시도해주세요.')
ai_generation_rate_limit = RateLimitContext('ai_generation', 'AI 생성 요청이 너무 많습니다. 잠시 후 다시 시도해주세요.')
api_rate_limit = RateLimitContext('api_call', 'API 호출이 너무 많습니다. 잠시 후 다시 시도해주세요.')
recommendation_rate_limit = RateLimitContext('recommendation_request', '추천 요청이 너무 많습니다. 잠시 후 다시 시도해주세요.')
