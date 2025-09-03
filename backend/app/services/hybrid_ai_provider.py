"""
EduGPT 통합을 위한 하이브리드 AI 제공자 시스템
- OpenAI API 키가 있으면 OpenAI 사용
- 없으면 OpenRouter API 키로 무료/저비용 모델 사용
- Phase 9: EduGPT 통합 시 비용 효율적 운영
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any, Union, List
from enum import Enum
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

class EduGPTProvider(Enum):
    """EduGPT에서 사용할 AI 제공자"""
    OPENAI_DIRECT = "openai_direct"      # OpenAI API 직접 사용
    OPENROUTER_FALLBACK = "openrouter"   # OpenRouter 폴백

@dataclass
class EduGPTConfig:
    """EduGPT AI 설정"""
    provider: EduGPTProvider
    model_name: str
    api_key: str
    base_url: str
    temperature: float = 0.7
    max_tokens: int = 4096

@dataclass
class AIMessage:
    """AI 메시지 구조"""
    role: str
    content: str

class HybridAIProvider:
    """
    EduGPT용 하이브리드 AI 제공자
    OpenAI -> OpenRouter 순서로 폴백
    """
    
    def __init__(self):
        self.config = self._determine_provider()
        
        # 속성 추가 (테스트용)
        self.current_provider = self.config.provider.value if self.config else "none"
        self.openai_available = self.config and self.config.provider == EduGPTProvider.OPENAI_DIRECT
        self.openrouter_available = self.config and self.config.provider == EduGPTProvider.OPENROUTER_FALLBACK
        
    def _determine_provider(self) -> EduGPTConfig:
        """사용할 AI 제공자 결정"""
        
        # 1순위: OpenAI API 키 확인
        openai_key = os.getenv("OPENAI_API_KEY") or getattr(settings, 'OPENAI_API_KEY', None)
        
        if openai_key and openai_key.startswith("sk-"):
            logger.info("🔑 OpenAI API key detected - using OpenAI for EduGPT")
            return EduGPTConfig(
                provider=EduGPTProvider.OPENAI_DIRECT,
                model_name="gpt-3.5-turbo",
                api_key=openai_key,
                base_url="https://api.openai.com/v1",
                temperature=0.7,
                max_tokens=4096
            )
        
        # 2순위: OpenRouter API 키 사용
        openrouter_key = os.getenv("OPENROUTER_API_KEY") or getattr(settings, 'OPENROUTER_API_KEY', None)
        
        if openrouter_key:
            logger.info("🔄 No OpenAI key - using OpenRouter for EduGPT (cost-effective)")
            return EduGPTConfig(
                provider=EduGPTProvider.OPENROUTER_FALLBACK,
                model_name="mistralai/mistral-7b-instruct:free",
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.7,
                max_tokens=4096
            )
        
        raise ValueError("❌ No AI API keys found. Please set OPENAI_API_KEY or OPENROUTER_API_KEY")
    
    def chat_completion(self, messages: List[AIMessage], **kwargs) -> Dict[str, Any]:
        """채팅 완성 API 호출"""
        
        # 메시지 형식 변환
        formatted_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
        
        # API 요청 구성
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.config.provider == EduGPTProvider.OPENROUTER_FALLBACK:
            headers.update({
                "HTTP-Referer": "https://lms-mvp.com",
                "X-Title": "LMS MVP - EduGPT Integration"
            })
        
        payload = {
            "model": self.config.model_name,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
        }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ AI API call failed: {e}")
            raise
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """텍스트 생성 (간단한 인터페이스)"""
        
        messages = [AIMessage(role="user", content=prompt)]
        response = self.chat_completion(messages, **kwargs)
        
        return response["choices"][0]["message"]["content"]
    
    async def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """비동기 응답 생성 (EduGPT 통합용)"""
        return self.generate_text(prompt, temperature=temperature, max_tokens=max_tokens)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """현재 사용 중인 제공자 정보"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model_name,
            "is_free": self.config.provider == EduGPTProvider.OPENROUTER_FALLBACK,
            "cost_optimization": True if self.config.provider == EduGPTProvider.OPENROUTER_FALLBACK else False
        }
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """토큰 사용량 기반 비용 추정"""
        
        if self.config.provider == EduGPTProvider.OPENROUTER_FALLBACK:
            if "free" in self.config.model_name:
                return 0.0  # 무료 모델
            else:
                return (input_tokens + output_tokens) * 0.001 / 1000  # $0.001 per 1K tokens
        
        elif self.config.provider == EduGPTProvider.OPENAI_DIRECT:
            # OpenAI GPT-3.5-turbo 비용
            input_cost = input_tokens * 0.0015 / 1000   # $0.0015 per 1K input tokens
            output_cost = output_tokens * 0.002 / 1000  # $0.002 per 1K output tokens
            return input_cost + output_cost
        
        return 0.0

# 전역 인스턴스
_hybrid_provider = None

def get_hybrid_ai_provider() -> HybridAIProvider:
    """하이브리드 AI 제공자 싱글톤"""
    global _hybrid_provider
    if _hybrid_provider is None:
        _hybrid_provider = HybridAIProvider()
    return _hybrid_provider

def generate_curriculum(subject: str, level: str, weeks: int = 12) -> str:
    """커리큘럼 생성 (EduGPT 통합용)"""
    
    prompt = f"""
    다음 조건에 맞는 {weeks}주차 커리큘럼을 생성해주세요:
    
    과목: {subject}
    수준: {level}
    기간: {weeks}주
    
    각 주차별로 다음을 포함해주세요:
    - 주차 제목
    - 학습 목표
    - 주요 내용
    - 실습 활동
    - 평가 방법
    
    JSON 형식으로 응답해주세요.
    """
    
    provider = get_hybrid_ai_provider()
    return provider.generate_text(prompt, temperature=0.7, max_tokens=3000)

def generate_teaching_response(context: str, student_question: str) -> str:
    """교수 응답 생성 (EduGPT 티칭 에이전트용)"""
    
    prompt = f"""
    다음 맥락에서 학생의 질문에 답변해주세요:
    
    맥락: {context}
    학생 질문: {student_question}
    
    교육적이고 이해하기 쉬운 답변을 제공해주세요.
    """
    
    provider = get_hybrid_ai_provider()
    return provider.generate_text(prompt, temperature=0.8, max_tokens=1500)

def log_ai_usage(operation: str, tokens_used: int = 0):
    """AI 사용량 로깅"""
    provider = get_hybrid_ai_provider()
    info = provider.get_provider_info()
    
    logger.info(f"🤖 EduGPT AI Usage - Operation: {operation}, "
                f"Provider: {info['provider']}, Model: {info['model']}, "
                f"Tokens: {tokens_used}, Cost-Optimized: {info['cost_optimization']}")

# Phase 9 통합을 위한 유틸리티 함수들
def check_ai_availability() -> Dict[str, Any]:
    """AI 제공자 가용성 체크"""
    try:
        provider = get_hybrid_ai_provider()
        info = provider.get_provider_info()
        return {
            "available": True,
            "provider": info["provider"],
            "model": info["model"],
            "is_free": info["is_free"],
            "status": "ready"
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "status": "error"
        }

def get_recommended_settings() -> Dict[str, Any]:
    """EduGPT 통합을 위한 권장 설정"""
    provider = get_hybrid_ai_provider()
    
    if provider.config.provider == EduGPTProvider.OPENAI_DIRECT:
        return {
            "curriculum_generation": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 3000
            },
            "teaching_agent": {
                "model": "gpt-3.5-turbo", 
                "temperature": 0.8,
                "max_tokens": 1500
            }
        }
    else:
        return {
            "curriculum_generation": {
                "model": "mistralai/mistral-7b-instruct:free",
                "temperature": 0.6,
                "max_tokens": 2000
            },
            "teaching_agent": {
                "model": "mistralai/mistral-7b-instruct:free",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
