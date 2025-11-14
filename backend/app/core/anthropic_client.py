# -*- coding: utf-8 -*-
"""
Anthropic Claude API 클라이언트

Constitutional AI 구현을 위한 Claude API 통합
"""
import os
import anthropic
from typing import AsyncGenerator, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AnthropicClient:
    """
    Anthropic Claude API 클라이언트
    
    기능:
    - 텍스트 생성
    - 스트리밍 생성
    - Constitutional AI 프롬프트 지원
    """
    
    def __init__(self):
        """
        클라이언트 초기화
        
        환경변수:
            ANTHROPIC_API_KEY: Anthropic API 키
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not found. Claude API will not work.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
        
        # 기본 모델: Claude 3.5 Sonnet (최신)
        self.default_model = "claude-3-5-sonnet-20241022"
        
        # 대체 모델들
        self.models = {
            "sonnet": "claude-3-5-sonnet-20241022",  # 균형잡힌 성능 (추천)
            "opus": "claude-3-opus-20240229",        # 최고 성능 (비쌈)
            "haiku": "claude-3-haiku-20240307"       # 빠르고 저렴
        }
    
    def _check_client(self):
        """API 키 존재 여부 확인"""
        if not self.client:
            raise ValueError(
                "Anthropic API key not configured. "
                "Please set ANTHROPIC_API_KEY environment variable."
            )
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """
        Claude로 텍스트 생성 (일반)
        
        Args:
            prompt: 사용자 프롬프트
            system: 시스템 프롬프트 (Constitutional AI 원칙 등)
            max_tokens: 최대 토큰 수
            temperature: 온도 (0.0 ~ 1.0, 낮을수록 일관적)
            model: 사용할 모델 (기본값: sonnet)
        
        Returns:
            생성된 텍스트
        
        Example:
            >>> client = AnthropicClient()
            >>> result = await client.generate(
            ...     prompt="Python에서 리스트 컴프리헨션이 뭔가요?",
            ...     system="당신은 소크라테스식 교육자입니다."
            ... )
        """
        self._check_client()
        
        # 모델 선택
        selected_model = self.models.get(model, self.default_model) if model else self.default_model
        
        try:
            # Claude API 호출
            response = self.client.messages.create(
                model=selected_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system if system else "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 응답 텍스트 추출
            return response.content[0].text
            
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def stream_generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Claude로 스트리밍 텍스트 생성
        
        실시간으로 응답을 받아 SSE(Server-Sent Events)로 전송 가능
        
        Args:
            (generate()와 동일)
        
        Yields:
            생성된 텍스트 조각 (chunk)
        
        Example:
            >>> async for chunk in client.stream_generate(prompt="..."):
            ...     print(chunk, end="", flush=True)
        """
        self._check_client()
        
        # 모델 선택
        selected_model = self.models.get(model, self.default_model) if model else self.default_model
        
        try:
            # 스트리밍 API 호출
            with self.client.messages.stream(
                model=selected_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system if system else "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            ) as stream:
                # 텍스트 스트림 yield
                for text in stream.text_stream:
                    yield text
                    
        except anthropic.APIError as e:
            logger.error(f"Anthropic API streaming error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected streaming error: {e}")
            raise
    
    async def generate_with_constitutional_ai(
        self,
        user_code: str,
        language: str,
        user_level: str = "beginner",
        vulnerabilities: list = None,
        ethical_issues: list = None
    ) -> str:
        """
        Constitutional AI 원칙을 적용한 교육적 피드백 생성
        
        Args:
            user_code: 사용자가 작성한 코드
            language: 프로그래밍 언어 (python, javascript, sql 등)
            user_level: 학습자 레벨 (beginner, intermediate, advanced)
            vulnerabilities: 발견된 보안 취약점 리스트
            ethical_issues: 발견된 윤리적 문제 리스트
        
        Returns:
            교육적 피드백 텍스트
        """
        # Constitutional AI 시스템 프롬프트
        system_prompt = """당신은 Constitutional AI 원칙을 따르는 교육적 코드 리뷰어입니다.

핵심 원칙:
1. Safety (안전): 보안 취약점을 명확히 지적하고 안전한 대안을 제시
2. Educational (교육): 직접적인 답이 아닌 소크라테스식 질문으로 학습 유도
3. Ethical (윤리): 비윤리적 코드는 단호히 거부하며 윤리적 대안 제시
4. Helpful (도움): 학습자 레벨에 맞춰 긍정적인 톤으로 격려

응답 형식:
1. 먼저 코드의 좋은 점을 찾아 칭찬
2. 개선이 필요한 부분을 질문 형식으로 제시
3. 힌트를 점진적으로 제공
4. 보안/윤리 문제는 명확히 경고
"""
        
        # 사용자 프롬프트 구성
        user_prompt = f"""다음 {language} 코드를 리뷰해주세요.

학습자 레벨: {user_level}

코드:
```{language}
{user_code}
```
"""
        
        # 취약점이 발견된 경우
        if vulnerabilities:
            user_prompt += f"\n\n발견된 보안 취약점:\n"
            for vuln in vulnerabilities:
                user_prompt += f"- {vuln}\n"
        
        # 윤리적 문제가 발견된 경우
        if ethical_issues:
            user_prompt += f"\n\n발견된 윤리적 문제:\n"
            for issue in ethical_issues:
                user_prompt += f"- {issue}\n"
        
        # Claude에게 피드백 요청
        return await self.generate(
            prompt=user_prompt,
            system=system_prompt,
            max_tokens=2000,
            temperature=0.7
        )
    
    async def generate_socratic_question(
        self,
        student_question: str,
        context: Optional[str] = None
    ) -> str:
        """
        소크라테스식 질문 생성
        
        학생의 질문에 직접 답하지 않고,
        스스로 답을 찾도록 유도하는 질문 반환
        
        Args:
            student_question: 학생의 질문
            context: 학습 컨텍스트 (선택적)
        
        Returns:
            소크라테스식 역질문
        """
        system_prompt = """당신은 소크라테스입니다. 
        
직접적인 답을 주지 않습니다.
대신, 학습자가 스스로 답을 발견하도록 유도하는 질문을 합니다.

원칙:
1. "왜?"라고 묻기
2. 가정에 반례 제시
3. 더 간단한 문제로 분해
4. 학습자의 생각 먼저 물어보기
5. 힌트는 점진적으로
"""
        
        prompt = f"학생 질문: {student_question}"
        
        if context:
            prompt += f"\n\n학습 컨텍스트: {context}"
        
        return await self.generate(
            prompt=prompt,
            system=system_prompt,
            max_tokens=500,
            temperature=0.8
        )
    
    def get_usage_info(self) -> Dict[str, Any]:
        """
        API 사용 정보 반환
        
        Returns:
            모델 정보, 가격 정보 등
        """
        return {
            "default_model": self.default_model,
            "available_models": self.models,
            "api_configured": self.client is not None,
            "pricing_info": {
                "sonnet": {
                    "input": "$3 per million tokens",
                    "output": "$15 per million tokens"
                },
                "opus": {
                    "input": "$15 per million tokens",
                    "output": "$75 per million tokens"
                },
                "haiku": {
                    "input": "$0.25 per million tokens",
                    "output": "$1.25 per million tokens"
                }
            }
        }


# 싱글톤 인스턴스
anthropic_client = AnthropicClient()


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_basic():
        """기본 생성 테스트"""
        client = AnthropicClient()
        
        response = await client.generate(
            prompt="Python에서 for 루프를 설명해주세요.",
            system="당신은 친절한 프로그래밍 튜터입니다."
        )
        
        print("=== 기본 생성 ===")
        print(response)
    
    async def test_streaming():
        """스트리밍 테스트"""
        client = AnthropicClient()
        
        print("\n=== 스트리밍 생성 ===")
        async for chunk in client.stream_generate(
            prompt="Python 리스트 컴프리헨션을 예시와 함께 설명해주세요."
        ):
            print(chunk, end="", flush=True)
        print()
    
    async def test_constitutional():
        """Constitutional AI 테스트"""
        client = AnthropicClient()
        
        code = '''
query = f"SELECT * FROM users WHERE username = '{user_input}'"
cursor.execute(query)
'''
        
        feedback = await client.generate_with_constitutional_ai(
            user_code=code,
            language="python",
            user_level="beginner",
            vulnerabilities=["SQL Injection"]
        )
        
        print("\n=== Constitutional AI 피드백 ===")
        print(feedback)
    
    async def test_socratic():
        """소크라테스식 질문 테스트"""
        client = AnthropicClient()
        
        question = await client.generate_socratic_question(
            student_question="for 루프가 뭔가요?",
            context="Python 기초 과정 - 반복문 섹션"
        )
        
        print("\n=== 소크라테스식 질문 ===")
        print(question)
    
    # 테스트 실행
    async def run_all_tests():
        await test_basic()
        await test_streaming()
        await test_constitutional()
        await test_socratic()
    
    asyncio.run(run_all_tests())

