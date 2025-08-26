import asyncio
import pytest

from app.services import scoring_service as sc_mod
from app.services.scoring_service import scoring_service


class FakeProvider:
    def __init__(self):
        self.calls = []

    async def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 160):
        # 기록 후 고유한 문자열 반환
        self.calls.append({
            "system": system_prompt,
            "user": user_prompt,
            "max_tokens": max_tokens,
        })
        return "[LLM] 리스트에 값을 추가하려면 append를 사용하세요."


@pytest.mark.asyncio
async def test_generate_ai_feedback_uses_llm(monkeypatch):
    # 1) LLM provider를 가짜로 주입
    fake = FakeProvider()
    monkeypatch.setattr(sc_mod, "get_llm_provider", lambda: fake)

    # 2) 리스트/append 문제 맥락의 질문 구성
    question = {
        "id": 123,
        "question_type": "short_answer",
        "topic": "리스트",
        "difficulty": "easy",
        "code_snippet": "list = ['apple', 'banana', 'tomato']\n# list에 potato를 추가하시오\nlist.______[potato]",
        "correct_answer": "append",
    }

    user_answer = "append"
    score = 1.0

    # 3) 호출
    feedback = await scoring_service.generate_ai_feedback(question, user_answer, score)

    # 4) 검증: LLM이 호출되었고, 반환 텍스트가 LLM에서 온 것인지 확인
    assert fake.calls, "LLM provider was not called"
    assert feedback.startswith("[LLM]"), f"Unexpected feedback source: {feedback}"

    # 5) 템플릿성 딕셔너리 힌트가 섞이지 않았는지 (거친 차단)
    assert "딕셔너리는 키-값" not in feedback


@pytest.mark.asyncio
async def test_template_when_llm_disabled(monkeypatch):
    # LLM을 비활성화하여 템플릿 경로로 가게 함
    monkeypatch.setattr(sc_mod, "get_llm_provider", lambda: None)

    question = {
        "id": 456,
        "question_type": "short_answer",
        "topic": "리스트",
        "difficulty": "easy",
        "code_snippet": "list.______[potato]",
        "correct_answer": "append",
    }
    user_answer = "insert"
    score = 0.0

    feedback = await scoring_service.generate_ai_feedback(question, user_answer, score)

    # 템플릿 경로 동작 확인 (LLM prefix가 없어야 함)
    assert not feedback.startswith("[LLM]"), "Feedback should come from template when LLM disabled"
    # 리스트 관련 힌트가 포함될 가능성 (딕셔너리 힌트 방지용 간단 체크)
    assert "딕셔너리는 키-값" not in feedback
