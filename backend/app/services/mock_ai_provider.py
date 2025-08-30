"""
모의 AI 제공자 - 실제 API 없이 LMS 테스트용
"""
import json
import random
from typing import Dict, Any, List
from datetime import datetime
from app.services.ai_providers import AIProviderManager, AIRequest, ModelTier, ModelConfig, AIProvider

class MockAIProviderManager(AIProviderManager):
    """모의 AI 제공자 관리자"""

    def __init__(self):
        # 부모 클래스 초기화 생략 (실제 API 호출 방지)
        self.models = {
            "mock-gpt": ModelConfig(
                name="mock-gpt",
                provider=AIProvider.OPENAI,
                tier=ModelTier.FREE,
                cost_per_1k_tokens=0.0,
                max_tokens=1000,
                context_window=4000,
                strengths=["빠른 응답", "교육적 콘텐츠", "프로그래밍 지원"],
                best_for=["문제 생성", "피드백", "학습 지원"]
            )
        }

    def select_optimal_model(self, request: AIRequest) -> ModelConfig:
        """항상 모의 모델 선택"""
        return self.models["mock-gpt"]

    async def generate_completion(self, request: AIRequest) -> Dict[str, Any]:
        """모의 AI 응답 생성"""
        try:
            # 요청 타입에 따른 모의 응답 생성
            if "coding" in request.task_type:
                response_text = self._generate_mock_coding_response(request.prompt)
            elif "feedback" in request.task_type:
                response_text = self._generate_mock_feedback_response(request.prompt)
            elif "analysis" in request.task_type:
                response_text = self._generate_mock_analysis_response(request.prompt)
            else:
                response_text = self._generate_mock_general_response(request.prompt)

            return {
                'success': True,
                'response': response_text,
                'model': 'mock-gpt',
                'provider': 'openai',
                'tier': 'free',
                'tokens_used': len(request.prompt.split()) * 2,  # 대략적 토큰 계산
                'cost_estimate': 0.0,
                'cached': False,
                'mock_response': True  # 모의 응답 표시
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mock_response': True
            }

    def _generate_mock_coding_response(self, prompt: str) -> str:
        """모의 코딩 응답 생성"""
        if "객관식" in prompt or "multiple choice" in prompt.lower():
            return '''{
  "question_type": "multiple_choice",
  "question": "다음 중 파이썬에서 'Hello, World!'를 출력하는 올바른 코드는?",
  "options": [
    "A) print('Hello, World!')",
    "B) console.log('Hello, World!')",
    "C) echo 'Hello, World!'",
    "D) printf('Hello, World!')"
  ],
  "correct_answer": "A",
  "explanation": "파이썬에서는 print() 함수를 사용하여 텍스트를 출력합니다.",
  "difficulty": "easy",
  "topic": "python_basics"
}'''

        elif "빈칸" in prompt or "fill_in_the_blank" in prompt.lower():
            return '''{
  "question_type": "fill_in_the_blank",
  "question": "파이썬에서 텍스트를 출력하려면 ____('Hello, World!')와 같이 작성합니다.",
  "answer": "print",
  "explanation": "print() 함수는 파이썬의 기본 출력 함수입니다.",
  "difficulty": "easy",
  "topic": "python_basics"
}'''

        else:
            return '''{
  "question_type": "short_answer",
  "question": "파이썬에서 'Hello, World!'를 출력하는 코드를 작성하세요.",
  "sample_answer": "print('Hello, World!')",
  "explanation": "print() 함수를 사용하여 문자열을 출력할 수 있습니다.",
  "difficulty": "easy",
  "topic": "python_basics"
}'''

    def _generate_mock_feedback_response(self, prompt: str) -> str:
        """모의 피드백 응답 생성"""
        if "잘못" in prompt or "틀렸" in prompt:
            return """좋은 시도였습니다! 다음 사항들을 고려해보세요:

**강점:**
- 문제 이해도가 좋습니다
- 적절한 접근 방법을 선택했습니다

**개선할 점:**
- print() 함수의 사용법을 다시 확인해보세요
- 따옴표의 종류(작은따옴표 vs 큰따옴표)에 주의하세요

**다음 단계:**
- 파이썬 기본 문법을 복습해보세요
- 간단한 출력 예제들을 직접 실행해보세요

계속 도전해보세요! 💪"""

        else:
            return """잘하셨습니다! 🎉

**우수한 점:**
- 정확한 코드를 작성했습니다
- 올바른 파이썬 문법을 사용했습니다

**더 발전시키기:**
- 다른 출력 방법들도 공부해보세요
- 변수와 함께 출력하는 방법을 연습해보세요

다음 문제도 도전해보세요!"""

    def _generate_mock_analysis_response(self, prompt: str) -> str:
        """모의 분석 응답 생성"""
        return '''{
  "strengths": [
    "기초 개념 이해도가 좋음",
    "문제 해결 능력이 우수함",
    "꾸준한 학습 태도를 보임"
  ],
  "weaknesses": [
    "실행 결과 예측력이 부족함",
    "디버깅 능력이 더 필요함"
  ],
  "learning_speed": "normal",
  "preferred_difficulty": 2,
  "recommendations": [
    "더 많은 실습 문제를 풀어보세요",
    "코드 실행 결과를 미리 예측하는 연습을 하세요",
    "에러 메시지를 주의 깊게 읽어보세요"
  ],
  "next_focus_areas": [
    "변수와 데이터 타입",
    "조건문과 반복문",
    "함수 정의와 호출"
  ]
}'''

    def _generate_mock_general_response(self, prompt: str) -> str:
        """모의 일반 응답 생성"""
        responses = [
            "파이썬은 강력하고 배우기 쉬운 프로그래밍 언어입니다.",
            "프로그래밍 학습에서 꾸준한 연습이 가장 중요합니다.",
            "코드를 작성하고 실행해보며 배우는 것이 효과적입니다.",
            "질문이 있으시면 언제든지 물어보세요!",
            "학습은 즐거운 과정이 되어야 합니다."
        ]
        return random.choice(responses)

# 전역 모의 인스턴스
mock_ai_provider_manager = MockAIProviderManager()

def get_mock_ai_provider():
    """모의 AI 제공자 인스턴스 반환"""
    return mock_ai_provider_manager
