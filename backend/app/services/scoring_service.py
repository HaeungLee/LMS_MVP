import os
import asyncio
from typing import Dict, List
import json
from app.core.config import settings
from app.services.llm_providers import get_llm_provider
from app.services.llm_cache import feedback_cache, make_feedback_cache_key
from rapidfuzz import fuzz

class ScoringService:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "db.json")
        # 간단 동의어/정규화 사전 (v1)
        self.synonym_map: Dict[str, str] = {
            "dict": "dictionary",
            "딕트": "dictionary",
            "list": "list",
            "리스트": "list",
            "tuple": "tuple",
            "튜플": "tuple",
            "set": "set",
            "집합": "set",
            "string": "string",
            "문자열": "string",
            "true": "true",
            "false": "false",
        }
        
    def load_questions(self) -> Dict:
        """데이터베이스에서 문제 데이터를 로드"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_question_by_id(self, question_id: int) -> Dict:
        """ID로 특정 문제 조회"""
        data = self.load_questions()
        for question in data["questions"]:
            if question["id"] == question_id:
                return question
        return None
    
    def _normalize(self, text: str) -> str:
        t = (text or "").strip().lower()
        # 공백 축약
        parts = t.split()
        t = " ".join(parts)
        # 간단 동의어 치환(단어 단위)
        tokens = t.replace(',', ' ').replace(';', ' ').split()
        norm_tokens = [self.synonym_map.get(tok, tok) for tok in tokens]
        return " ".join(norm_tokens)

    def _unordered_token_match(self, a: str, b: str) -> bool:
        sa = set(a.split())
        sb = set(b.split())
        return bool(sa) and sa == sb

    def score_answer(self, question: Dict, user_answer: str) -> float:
        """답안 채점 (0, 0.5, 1점 시스템) - v1.5: 정규화/동의어/토큰무순서 + 토큰 유사도"""
        ua = self._normalize(user_answer)
        ca = self._normalize(question["answer"])

        # 완전 일치
        if ua == ca or self._unordered_token_match(ua, ca):
            return 1.0

        # 부분 정답: 빈칸형/키워드 포함 + 유사도 임계치
        if question.get("question_type") in {"fill_in_the_blank", "short_answer"}:
            if ca in ua:
                return 0.5
            # 의미적으로 근접(간단): 토큰 기반 유사도(부분 비율)
            try:
                ratio = max(
                    fuzz.partial_ratio(ua, ca),
                    fuzz.token_set_ratio(ua, ca)
                )
                if ratio >= 80:
                    return 0.5
            except Exception:
                pass

        return 0.0
    
    def analyze_by_topic(self, results: List[Dict]) -> Dict:
        """주제별 정답률 분석"""
        topic_stats = {}
        
        for result in results:
            topic = result["topic"]
            if topic not in topic_stats:
                topic_stats[topic] = {"total": 0, "correct": 0}
            
            topic_stats[topic]["total"] += 1
            if result["score"] >= 0.5:  # 0.5점 이상이면 정답으로 간주
                topic_stats[topic]["correct"] += 1
        
        # 정답률 계산
        topic_analysis = {}
        for topic, stats in topic_stats.items():
            percentage = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            topic_analysis[topic] = {
                "correct": stats["correct"],
                "total": stats["total"],
                "percentage": round(percentage, 1)
            }
            
        return topic_analysis
    
    async def generate_ai_feedback(self, question: Dict, user_answer: str, score: float) -> str:
        """AI 피드백 생성 (템플릿 폴백 + LLM 캐시 + 프로바이더 추상화)"""
        # 우선 템플릿
        template = None
        if score == 1.0:
            template = f"정답입니다! '{question['answer']}'를 정확히 입력하셨네요. 잘하셨습니다!"
        elif score == 0.5:
            template = f"거의 맞았습니다! 정답은 '{question['answer']}'입니다. 입력하신 '{user_answer}'와 비슷하지만 조금 다릅니다. 다시 한번 확인해보세요."
        else:
            template = f"아쉽게도 틀렸습니다. 정답은 '{question['answer']}'입니다. {question['topic']} 관련 내용을 다시 복습해보시는 것을 추천합니다."

        provider = get_llm_provider()
        if not provider:
            return template

        # 캐시 키 구성
        rubric_version = (question.get("rubric") or "v1").strip() or "v1"
        normalized_answer = self._normalize(user_answer)
        cache_key = make_feedback_cache_key(int(question.get("id", 0)), rubric_version, normalized_answer)
        cached = feedback_cache.get(cache_key)
        if cached:
            return cached

        system_prompt = "간결하고 친절한 튜터."
        user_prompt = (
            "다음 코딩 퀴즈 응답에 대해 2-3문장 피드백을 한국어로 작성하세요.\n"
            f"문항 주제: {question.get('topic','')}\n정답: {question.get('answer','')}\n사용자 답안: {user_answer}\n"
        )
        try:
            content = await provider.generate(system_prompt, user_prompt, max_tokens=160)
            if content:
                feedback_cache.set(cache_key, content)
                return content
        except Exception:
            pass
        return template

scoring_service = ScoringService()
