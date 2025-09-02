"""
Redis 서비스 - Phase 3
- 캐싱 시스템
- 세션 관리
- 레이트리밋 데이터
- 비동기 작업 상태 관리
"""

import redis
import json
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Redis 동기 서비스"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=getattr(settings, 'redis_host', 'localhost'),
                port=getattr(settings, 'redis_port', 6379),
                db=0,
                decode_responses=True,
                socket_timeout=1,  # 빠른 타임아웃
                socket_connect_timeout=1,  # 빠른 연결 타임아웃
                retry_on_timeout=False  # 재시도 비활성화
            )
            # 연결 테스트 (더 안전하게)
            self.redis_client.ping()
            logger.info("Redis 연결 성공")
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {str(e)}, 메모리 캐시로 폴백")
            self.redis_client = None
            self._memory_cache = {}
    
    def _is_connected(self) -> bool:
        """Redis 연결 상태 확인"""
        if self.redis_client is None:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set_cache(self, key: str, value: Any, expiry_seconds: int = 3600) -> bool:
        """캐시 데이터 저장"""
        try:
            if self._is_connected():
                # JSON 직렬화 시도
                try:
                    json_value = json.dumps(value, ensure_ascii=False)
                    return self.redis_client.setex(key, expiry_seconds, json_value)
                except (TypeError, ValueError):
                    # JSON 직렬화 실패시 pickle 사용
                    pickle_value = pickle.dumps(value)
                    return self.redis_client.setex(f"pickle:{key}", expiry_seconds, pickle_value)
            else:
                # 메모리 캐시 폴백
                self._memory_cache[key] = {
                    'value': value,
                    'expires_at': datetime.utcnow() + timedelta(seconds=expiry_seconds)
                }
                return True
        except Exception as e:
            logger.error(f"캐시 저장 실패 {key}: {str(e)}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """캐시 데이터 조회"""
        try:
            if self._is_connected():
                # JSON 데이터 조회 시도
                value = self.redis_client.get(key)
                if value is not None:
                    try:
                        return json.loads(value)
                    except (TypeError, ValueError):
                        pass
                
                # Pickle 데이터 조회 시도
                pickle_value = self.redis_client.get(f"pickle:{key}")
                if pickle_value is not None:
                    try:
                        return pickle.loads(pickle_value)
                    except:
                        pass
                
                return None
            else:
                # 메모리 캐시 폴백
                if key in self._memory_cache:
                    cache_item = self._memory_cache[key]
                    if datetime.utcnow() < cache_item['expires_at']:
                        return cache_item['value']
                    else:
                        del self._memory_cache[key]
                return None
        except Exception as e:
            logger.error(f"캐시 조회 실패 {key}: {str(e)}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """캐시 데이터 삭제"""
        try:
            if self._is_connected():
                deleted = self.redis_client.delete(key) > 0
                # Pickle 버전도 삭제 시도
                self.redis_client.delete(f"pickle:{key}")
                return deleted
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"캐시 삭제 실패 {key}: {str(e)}")
            return False
    
    def set_user_session(self, user_id: int, session_data: Dict[str, Any], ttl: int = 86400) -> bool:
        """사용자 세션 저장 (24시간 기본)"""
        key = f"session:user:{user_id}"
        return self.set_cache(key, session_data, ttl)
    
    def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """사용자 세션 조회"""
        key = f"session:user:{user_id}"
        return self.get_cache(key)
    
    def set_submission_status(self, submission_id: str, status: str, result: Optional[Dict] = None) -> bool:
        """제출 상태 저장"""
        key = f"submission:{submission_id}"
        data = {
            'status': status,
            'result': result,
            'updated_at': datetime.utcnow().isoformat()
        }
        return self.set_cache(key, data, 86400)  # 24시간
    
    def get_submission_status(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """제출 상태 조회"""
        key = f"submission:{submission_id}"
        return self.get_cache(key)
    
    def set_rate_limit_data(self, user_id: int, action: str, window_seconds: int = 300) -> bool:
        """레이트리밋 데이터 설정"""
        if not self._is_connected():
            return True  # Redis 없으면 레이트리밋 비활성화
        
        try:
            key = f"rate_limit:{user_id}:{action}"
            current_time = datetime.utcnow().timestamp()
            
            # Sorted Set에 현재 시간 추가
            self.redis_client.zadd(key, {str(current_time): current_time})
            
            # 윈도우 이전 데이터 제거
            cutoff_time = current_time - window_seconds
            self.redis_client.zremrangebyscore(key, 0, cutoff_time)
            
            # TTL 설정
            self.redis_client.expire(key, window_seconds)
            
            return True
        except Exception as e:
            logger.error(f"레이트리밋 설정 실패 {user_id}:{action}: {str(e)}")
            return False
    
    def get_rate_limit_count(self, user_id: int, action: str) -> int:
        """레이트리밋 현재 카운트 조회"""
        if not self._is_connected():
            return 0
        
        try:
            key = f"rate_limit:{user_id}:{action}"
            return self.redis_client.zcard(key)
        except Exception as e:
            logger.error(f"레이트리밋 카운트 조회 실패 {user_id}:{action}: {str(e)}")
            return 0
    
    def set_llm_cache(self, prompt_hash: str, response: str, ttl: int = 3600) -> bool:
        """LLM 응답 캐싱 (1시간 기본)"""
        key = f"llm_cache:{prompt_hash}"
        return self.set_cache(key, response, ttl)
    
    def get_llm_cache(self, prompt_hash: str) -> Optional[str]:
        """LLM 캐시 조회"""
        key = f"llm_cache:{prompt_hash}"
        return self.get_cache(key)
    
    def set_recommendation_cache(self, user_id: int, rec_type: str, recommendations: List[Dict], ttl: int = 1800) -> bool:
        """추천 결과 캐싱 (30분 기본)"""
        key = f"recommendations:{user_id}:{rec_type}"
        return self.set_cache(key, recommendations, ttl)
    
    def get_recommendation_cache(self, user_id: int, rec_type: str) -> Optional[List[Dict]]:
        """추천 캐시 조회"""
        key = f"recommendations:{user_id}:{rec_type}"
        return self.get_cache(key)
    
    def clear_user_cache(self, user_id: int) -> bool:
        """사용자 관련 모든 캐시 삭제"""
        if not self._is_connected():
            return True
        
        try:
            # 패턴 매칭으로 사용자 관련 키 찾기
            patterns = [
                f"session:user:{user_id}",
                f"recommendations:{user_id}:*",
                f"rate_limit:{user_id}:*"
            ]
            
            deleted_count = 0
            for pattern in patterns:
                if "*" in pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        deleted_count += self.redis_client.delete(*keys)
                else:
                    deleted_count += self.redis_client.delete(pattern)
            
            logger.info(f"사용자 {user_id} 캐시 {deleted_count}개 항목 삭제")
            return True
        except Exception as e:
            logger.error(f"사용자 캐시 삭제 실패 {user_id}: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        if not self._is_connected():
            return {
                'connected': False,
                'type': 'memory_fallback',
                'memory_items': len(getattr(self, '_memory_cache', {}))
            }
        
        try:
            info = self.redis_client.info()
            return {
                'connected': True,
                'type': 'redis',
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except Exception as e:
            logger.error(f"캐시 통계 조회 실패: {str(e)}")
            return {'connected': False, 'error': str(e)}


class AsyncRedisService:
    """Redis 비동기 서비스 (동기식 fallback)"""
    
    def __init__(self):
        self.redis_service = None
        self._initialized = False
    
    async def initialize(self):
        """비동기 Redis 연결 초기화 (동기식 fallback)"""
        if self._initialized:
            return
        
        try:
            self.redis_service = get_redis_service()
            self._initialized = True
            logger.info("Async Redis 연결 성공 (동기식 fallback)")
        except Exception as e:
            logger.warning(f"Async Redis 연결 실패: {str(e)}")
            self.redis_service = None
    
    async def close(self):
        """Redis 연결 종료"""
        pass  # 동기식 연결은 별도 종료 불필요
    
    async def set_async_cache(self, key: str, value: Any, expiry_seconds: int = 3600) -> bool:
        """비동기 캐시 저장 (동기식 fallback)"""
        if not self._initialized or self.redis_service is None:
            return False
        
        try:
            return self.redis_service.set_cache(key, value, expiry_seconds)
        except Exception as e:
            logger.error(f"비동기 캐시 저장 실패 {key}: {str(e)}")
            return False
    
    async def get_async_cache(self, key: str) -> Optional[Any]:
        """비동기 캐시 조회 (동기식 fallback)"""
        if not self._initialized or self.redis_service is None:
            return None
        
        try:
            return self.redis_service.get_cache(key)
        except Exception as e:
            logger.error(f"비동기 캐시 조회 실패 {key}: {str(e)}")
            return None
    
    async def publish_task_update(self, task_id: str, status: str, result: Optional[Dict] = None):
        """작업 상태 업데이트 발행 (동기식 fallback)"""
        if not self._initialized or self.redis_service is None:
            return
        
        try:
            message = {
                'task_id': task_id,
                'status': status,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            # 동기식으로 상태 저장
            status_key = f"task_status:{task_id}"
            self.redis_service.set_cache(status_key, message, 3600)
            logger.debug(f"작업 상태 업데이트 저장: {task_id}")
        except Exception as e:
            logger.error(f"작업 업데이트 발행 실패 {task_id}: {str(e)}")


# 전역 인스턴스
redis_service = RedisService()
async_redis_service = AsyncRedisService()

def get_redis_service() -> RedisService:
    """Redis 서비스 인스턴스 반환"""
    return redis_service

def get_async_redis_service() -> AsyncRedisService:
    """비동기 Redis 서비스 인스턴스 반환"""
    return async_redis_service
