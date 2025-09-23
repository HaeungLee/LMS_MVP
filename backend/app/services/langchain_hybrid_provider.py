"""
LangChain 기반 개선된 하이브리드 AI 프로바이더
EduGPT와 완전 호환되는 LangChain 통합 버전
"""

import os
import logging
from typing import Optional, Dict, Any, Union, List
from enum import Enum
from dataclasses import dataclass

# LangChain 임포트
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

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

class LangChainHybridProvider:
    """
    LangChain 기반 하이브리드 AI 제공자
    EduGPT의 DiscussAgent와 완전 호환
    """
    
    def __init__(self):
        self.config = self._determine_provider()
        self.chat_model = self._create_chat_model()
        
        # 속성 추가 (기존 인터페이스 호환성)
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
                model_name="x-ai/grok-4-fast:free",
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.7,
                max_tokens=4096
            )
        
        raise ValueError("❌ No AI API keys found. Please set OPENAI_API_KEY or OPENROUTER_API_KEY")
    
    def _create_chat_model(self) -> BaseChatModel:
        """LangChain ChatModel 생성"""
        
        if self.config.provider == EduGPTProvider.OPENAI_DIRECT:
            # OpenAI 직접 연결
            return ChatOpenAI(
                model=self.config.model_name,
                openai_api_key=self.config.api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        
        elif self.config.provider == EduGPTProvider.OPENROUTER_FALLBACK:
            # OpenRouter를 통한 연결 (헤더 설정 수정)
            return ChatOpenAI(
                model=self.config.model_name,
                openai_api_key=self.config.api_key,
                openai_api_base=self.config.base_url,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                default_headers={
                    "HTTP-Referer": "https://lms-mvp.com",
                    "X-Title": "LMS MVP - EduGPT Integration"
                }
            )
        
        raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def get_llm(self) -> BaseChatModel:
        """일반 LLM 반환"""
        return self.chat_model
    
    def get_streaming_llm(self, callbacks: List = None) -> BaseChatModel:
        """스트리밍 가능한 LLM 반환"""
        if self.config.provider == EduGPTProvider.OPENAI_DIRECT:
            return ChatOpenAI(
                model=self.config.model_name,
                openai_api_key=self.config.api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                streaming=True,
                callbacks=callbacks or []
            )
        
        elif self.config.provider == EduGPTProvider.OPENROUTER_FALLBACK:
            return ChatOpenAI(
                model=self.config.model_name,
                openai_api_key=self.config.api_key,
                openai_api_base=self.config.base_url,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                streaming=True,
                callbacks=callbacks or [],
                default_headers={
                    "HTTP-Referer": "https://lms-mvp.com",
                    "X-Title": "LMS MVP - EduGPT Streaming"
                }
            )
        
        raise ValueError(f"Unsupported provider for streaming: {self.config.provider}")
    
    def invoke_with_messages(self, messages: List[BaseMessage]) -> AIMessage:
        """LangChain 메시지 리스트로 AI 호출 (EduGPT 호환)"""
        try:
            response = self.chat_model.invoke(messages)
            return response
        except Exception as e:
            logger.error(f"❌ LangChain AI invoke failed: {e}")
            raise
    
    def generate_with_system_and_human(self, system_content: str, human_content: str) -> str:
        """시스템 메시지와 인간 메시지로 응답 생성"""
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=human_content)
        ]
        
        response = self.invoke_with_messages(messages)
        return response.content
    
    async def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """기존 인터페이스 호환성을 위한 비동기 응답 생성"""
        
        # 일시적으로 온도 조절
        original_temp = self.chat_model.temperature
        self.chat_model.temperature = temperature
        
        try:
            human_message = HumanMessage(content=prompt)
            response = self.chat_model.invoke([human_message])
            return response.content
        finally:
            # 온도 복원
            self.chat_model.temperature = original_temp
    
    def get_provider_info(self) -> Dict[str, Any]:
        """현재 사용 중인 제공자 정보"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model_name,
            "framework": "langchain",
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


class EduGPTDiscussAgent:
    """
    EduGPT의 DiscussAgent를 LangChain 기반으로 재구현
    원본과 100% 호환
    """
    
    def __init__(
        self,
        system_message: SystemMessage,
        model: BaseChatModel,
    ) -> None:
        self.system_message = system_message
        self.model = model
        self.init_messages()

    def reset(self) -> List[BaseMessage]:
        """메시지 히스토리 리셋"""
        self.init_messages()
        return self.stored_messages

    def init_messages(self) -> None:
        """메시지 히스토리 초기화"""
        self.stored_messages = [self.system_message]

    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        """메시지 히스토리 업데이트"""
        self.stored_messages.append(message)
        return self.stored_messages

    def step(self, input_message: HumanMessage) -> AIMessage:
        """한 단계 대화 진행 (EduGPT 원본과 동일)"""
        messages = self.update_messages(input_message)
        
        output_message = self.model.invoke(messages)
        self.update_messages(output_message)
        
        return output_message


# 전역 인스턴스
_langchain_hybrid_provider = None

def get_langchain_hybrid_provider() -> LangChainHybridProvider:
    """LangChain 하이브리드 제공자 싱글톤"""
    global _langchain_hybrid_provider
    if _langchain_hybrid_provider is None:
        _langchain_hybrid_provider = LangChainHybridProvider()
    return _langchain_hybrid_provider

def create_discuss_agent(system_message_content: str) -> EduGPTDiscussAgent:
    """EduGPT 스타일 DiscussAgent 생성"""
    provider = get_langchain_hybrid_provider()
    system_message = SystemMessage(content=system_message_content)
    return EduGPTDiscussAgent(system_message, provider.chat_model)
