import os
import asyncio
from typing import Dict, List, Tuple, Optional
import json
import ast
import re
from app.core.config import settings
from app.services.llm_providers import get_llm_provider
from app.services.llm_cache import feedback_cache, make_feedback_cache_key
from app.models.question_types import QuestionType
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
    
    async def evaluate_with_llm(self, question: Dict, user_answer: str) -> Dict[str, object]:
        """LLM을 사용해 직접 채점(점수)과 피드백을 동시에 생성한다.
        반환: { "score": float (0.0~1.0), "feedback": str }
        실패 시 기존 스코어링과 템플릿 피드백으로 폴백한다.
        """
        provider = get_llm_provider()
        if not provider:
            # LLM 비활성 → 기존 로직 폴백
            score = self.score_answer(question, user_answer)
            feedback = await self.generate_ai_feedback(question, user_answer, score)
            return {"score": float(score), "feedback": feedback}

        # 문제/정답/사용자 답안을 맥락으로 제공하고 JSON으로 결과 요구
        system_prompt = (
            "당신은 프로그래밍 튜터 겸 채점자입니다. 문제, 정답, 학습자 답안을 바탕으로"
            " 정밀하게 채점하고, JSON으로만 응답하세요."
            " 반환 JSON 스키마: {\"score\": 0|0.5|1, \"feedback\": string }"
            " feedback은 한국어로 2~4문장, 구체적이며 주제에 맞는 설명만 포함하세요."
        )
        correct_answer = question.get("correct_answer") or question.get("answer", "")
        user_prompt = (
            f"문제 유형: {question.get('question_type', 'short_answer')}\n"
            f"주제: {question.get('topic', '')}\n"
            f"난이도: {question.get('difficulty', 'easy')}\n"
            f"코드:\n{question.get('code_snippet', '')}\n\n"
            f"정답: {correct_answer}\n"
            f"학습자 답안: {user_answer}\n\n"
            "점수는 0, 0.5, 1 중 하나만 선택해 주세요. JSON 외 텍스트 금지."
        )

        try:
            content = await provider.generate(system_prompt, user_prompt, max_tokens=220)
            # JSON 파싱 시도
            data = json.loads((content or "").strip())
            score = float(data.get("score", 0))
            # 허용 범위 제한
            if score not in (0.0, 0.5, 1.0):
                score = 0.0
            feedback = str(data.get("feedback", ""))
            if not feedback:
                raise ValueError("empty feedback")
            return {"score": score, "feedback": feedback}
        except Exception as e:
            # 실패 시 폴백
            try:
                score = self.score_answer(question, user_answer)
                feedback = await self.generate_ai_feedback(question, user_answer, score)
                return {"score": float(score), "feedback": feedback}
            except Exception:
                # 최종 폴백
                return {"score": 0.0, "feedback": "피드백 생성에 실패했습니다. 잠시 후 다시 시도해주세요."}
    
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
        """고도화된 답안 채점 (0, 0.5, 1점 시스템) - AI 의미 분석 포함"""
        # 새로운 문제 유형별 채점 시스템
        question_type = question.get("question_type")
        if question_type:
            return self.score_by_question_type(question, user_answer, question_type)
        
        # 기존 레거시 채점 로직 (하위 호환성)
        return self._legacy_score_answer(question, user_answer)

    def score_by_question_type(self, question: Dict, user_answer: str, question_type: str) -> float:
        """문제 유형별 특화 채점 로직"""
        try:
            if question_type == QuestionType.MULTIPLE_CHOICE.value:
                return self._score_multiple_choice(question, user_answer)
            elif question_type == QuestionType.SHORT_ANSWER.value:
                return self._score_short_answer(question, user_answer)
            elif question_type == QuestionType.CODE_COMPLETION.value:
                return self._score_code_completion(question, user_answer)
            elif question_type == QuestionType.DEBUG_CODE.value:
                return self._score_debug_code(question, user_answer)
            elif question_type == QuestionType.TRUE_FALSE.value:
                return self._score_true_false(question, user_answer)
            else:
                # 알 수 없는 타입은 기존 로직 사용
                return self._legacy_score_answer(question, user_answer)
        except Exception as e:
            print(f"Error in type-specific scoring: {e}")
            return self._legacy_score_answer(question, user_answer)

    def _score_multiple_choice(self, question: Dict, user_answer: str) -> float:
        """객관식 문제 채점: 완전 일치만 정답"""
        correct_answer = question.get("correct_answer", "").strip().upper()
        user_answer_normalized = user_answer.strip().upper()
        
        # 완전 일치만 정답 (1점)
        if user_answer_normalized == correct_answer:
            return 1.0
        
        # 객관식은 부분 점수 없음
        return 0.0

    def _score_short_answer(self, question: Dict, user_answer: str) -> float:
        """단답형 문제 채점: 키워드 매칭 + 유사도"""
        ua = self._normalize(user_answer)
        ca = self._normalize(question.get("correct_answer", ""))

        # 1. 완전 일치 (1.0점)
        if ua == ca or self._unordered_token_match(ua, ca):
            return 1.0

        # 2. 의미적 유사도 검사
        semantic_score = self._check_semantic_similarity(question, ua, ca)
        if semantic_score >= 0.9:
            return 1.0
        elif semantic_score >= 0.6:
            return 0.5
        elif semantic_score >= 0.3:
            return 0.3

        # 3. 부분 정답 검사
        partial_score = self._check_partial_correctness(question, ua, ca)
        return partial_score

    def _score_code_completion(self, question: Dict, user_answer: str) -> float:
        """코드 완성 문제 채점: 문법 + 로직 + 키워드"""
        score = 0.0
        
        # 1. Python 문법 검사 (40%)
        if self._check_python_syntax(user_answer):
            score += 0.4
        
        # 2. 핵심 키워드 포함 검사 (30%)
        required_keywords = question.get("required_keywords", [])
        if required_keywords:
            keyword_score = self._calculate_keyword_match(user_answer, required_keywords)
            score += keyword_score * 0.3
        
        # 3. 로직 정확성 검사 (30%)
        correct_answer = question.get("correct_answer", "")
        if self._check_code_logic_similarity(user_answer, correct_answer):
            score += 0.3
        
        return min(score, 1.0)

    def _score_debug_code(self, question: Dict, user_answer: str) -> float:
        """디버깅 문제 채점: 버그 식별 + 수정 방법"""
        correct_bugs = question.get("bugs", [])
        correct_solution = question.get("correct_answer", "")
        
        score = 0.0
        
        # 1. 버그 식별 정확성 (50%)
        identified_bugs = self._extract_identified_bugs(user_answer)
        bug_score = self._calculate_bug_identification_score(identified_bugs, correct_bugs)
        score += bug_score * 0.5
        
        # 2. 수정 방법의 적절성 (50%)
        solution_score = self._evaluate_debug_solution(user_answer, correct_solution)
        score += solution_score * 0.5
        
        return min(score, 1.0)

    def _score_true_false(self, question: Dict, user_answer: str) -> float:
        """OX 문제 채점: 정답 + 이유 설명"""
        # 답안에서 OX와 이유 분리
        tf_answer, reasoning = self._parse_true_false_answer(user_answer)
        correct_answer = question.get("correct_answer", "").lower()
        
        score = 0.0
        
        # 1. OX 정답 여부 (60%)
        if tf_answer and tf_answer.lower() in correct_answer:
            score += 0.6
        
        # 2. 이유 설명 품질 (40%)
        if reasoning:
            reasoning_score = self._evaluate_reasoning_quality(reasoning, question)
            score += reasoning_score * 0.4
        
        return min(score, 1.0)

    # === 헬퍼 메서드들 ===
    def _check_python_syntax(self, code: str) -> bool:
        """Python 코드 문법 검사"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False

    def _calculate_keyword_match(self, user_answer: str, required_keywords: List[str]) -> float:
        """필수 키워드 매칭 점수 계산"""
        if not required_keywords:
            return 1.0
        
        user_text = user_answer.lower()
        matched_keywords = sum(1 for keyword in required_keywords if keyword.lower() in user_text)
        
        return matched_keywords / len(required_keywords)

    def _check_code_logic_similarity(self, user_code: str, correct_code: str) -> bool:
        """코드 로직 유사성 검사 (간단한 패턴 매칭)"""
        # 공백 및 주석 제거 후 비교
        user_clean = re.sub(r'#.*', '', user_code).replace(' ', '').replace('\n', '')
        correct_clean = re.sub(r'#.*', '', correct_code).replace(' ', '').replace('\n', '')
        
        # 80% 이상 유사하면 로직이 비슷하다고 판단
        try:
            similarity = fuzz.ratio(user_clean, correct_clean)
            return similarity >= 80
        except:
            return user_clean == correct_clean

    def _extract_identified_bugs(self, user_answer: str) -> List[str]:
        """사용자 답안에서 식별된 버그 목록 추출"""
        # 간단한 패턴 매칭으로 버그 키워드 추출
        bug_patterns = [
            r'오타|typo|철자',
            r'인덴트|indent|들여쓰기',
            r'세미콜론|semicolon|;',
            r'변수명|variable|name',
            r'함수명|function|def',
            r'괄호|bracket|parenthesis',
            r'등호|equal|=',
            r'비교|comparison|==',
        ]
        
        identified = []
        user_text = user_answer.lower()
        
        for pattern in bug_patterns:
            if re.search(pattern, user_text):
                identified.append(pattern.split('|')[0])  # 첫 번째 키워드 사용
        
        return identified

    def _calculate_bug_identification_score(self, identified: List[str], correct: List[str]) -> float:
        """버그 식별 정확도 점수 계산"""
        if not correct:
            return 1.0 if not identified else 0.5
        
        if not identified:
            return 0.0
        
        # 간단한 키워드 매칭 (정확한 구현은 실제 버그 데이터에 따라 조정)
        matches = 0
        for bug in correct:
            for identified_bug in identified:
                if identified_bug.lower() in bug.lower() or bug.lower() in identified_bug.lower():
                    matches += 1
                    break
        
        return min(matches / len(correct), 1.0)

    def _evaluate_debug_solution(self, user_answer: str, correct_solution: str) -> float:
        """디버깅 해결책 평가"""
        # 키워드 기반 유사도 검사
        try:
            similarity = fuzz.token_sort_ratio(user_answer.lower(), correct_solution.lower())
            if similarity >= 80:
                return 1.0
            elif similarity >= 60:
                return 0.7
            elif similarity >= 40:
                return 0.4
            else:
                return 0.0
        except:
            return 0.5 if user_answer.strip() else 0.0

    def _parse_true_false_answer(self, user_answer: str) -> Tuple[Optional[str], Optional[str]]:
        """OX 답안에서 정답과 이유 분리"""
        text = user_answer.strip()
        
        # OX, True/False, 참/거짓 패턴 검색
        tf_patterns = [
            r'\b(O|X)\b',
            r'\b(True|False)\b',
            r'\b(참|거짓)\b',
            r'\b(맞|틀)\b',
        ]
        
        tf_answer = None
        reasoning = text
        
        for pattern in tf_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tf_answer = match.group(1)
                # 매칭된 부분을 제거하고 나머지를 이유로 간주
                reasoning = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
                break
        
        return tf_answer, reasoning if reasoning else None

    def _evaluate_reasoning_quality(self, reasoning: str, question: Dict) -> float:
        """이유 설명의 품질 평가"""
        if not reasoning or len(reasoning.strip()) < 10:
            return 0.0
        
        # 기본 점수: 설명이 있으면 0.5점
        score = 0.5
        
        # 주요 키워드 포함 시 가산점
        topic_keywords = question.get("topic", "").split()
        for keyword in topic_keywords:
            if keyword.lower() in reasoning.lower():
                score += 0.1
        
        # 논리적 접속사 사용 시 가산점
        logical_connectors = ['because', 'since', 'therefore', '왜냐하면', '따라서', '그러므로']
        for connector in logical_connectors:
            if connector in reasoning.lower():
                score += 0.1
                break
        
        return min(score, 1.0)

    def _legacy_score_answer(self, question: Dict, user_answer: str) -> float:
        """고도화된 답안 채점 (0, 0.5, 1점 시스템) - AI 의미 분석 포함"""
        ua = self._normalize(user_answer)
        ca = self._normalize(question["answer"])

        # 1. 완전 일치 (1.0점)
        if ua == ca or self._unordered_token_match(ua, ca):
            return 1.0

        # 2. 의미적 유사도 검사 (프로그래밍 코드 특화)
        semantic_score = self._check_semantic_similarity(question, ua, ca)
        if semantic_score >= 0.9:
            return 1.0
        elif semantic_score >= 0.6:
            return 0.5

        # 3. 부분 정답 검사 (기존 로직 강화)
        if question.get("question_type") in {"fill_in_the_blank", "short_answer"}:
            partial_score = self._check_partial_correctness(question, ua, ca)
            if partial_score > 0:
                return partial_score

        return 0.0

    def _check_semantic_similarity(self, question: Dict, user_answer: str, correct_answer: str) -> float:
        """프로그래밍 답안의 의미적 유사도 검사"""
        topic = question.get('topic', '').lower()
        
        # 프로그래밍 키워드 매핑
        programming_synonyms = {
            'dictionary': ['dict', '딕셔너리', '딕트', 'Dictionary'],
            'list': ['리스트', 'List', 'array', '배열'],
            'tuple': ['튜플', 'Tuple'],
            'set': ['집합', 'Set'],
            'string': ['문자열', 'str', 'String'],
            'append': ['추가', 'add'],
            'remove': ['제거', 'delete', 'del'],
            'pop': ['팝', '제거'],
            'get': ['가져오기', '얻기'],
            'strip': ['공백제거', 'trim'],
            'split': ['분할', '나누기'],
            'join': ['합치기', '결합'],
            'range': ['범위', '레인지'],
            'len': ['길이', 'length'],
            'while': ['반복', '와일'],
            'for': ['포', '반복'],
            'if': ['만약', '조건'],
            'true': ['참', 'True', '트루'],
            'false': ['거짓', 'False', '폴스'],
        }
        
        # 정답 키워드 추출
        correct_keywords = set(correct_answer.split())
        user_keywords = set(user_answer.split())
        
        # 동의어 매핑으로 확장
        expanded_correct = correct_keywords.copy()
        expanded_user = user_keywords.copy()
        
        for keyword in correct_keywords:
            for canonical, synonyms in programming_synonyms.items():
                if keyword.lower() in [canonical] + synonyms:
                    expanded_correct.update(synonyms)
                    expanded_correct.add(canonical)
        
        for keyword in user_keywords:
            for canonical, synonyms in programming_synonyms.items():
                if keyword.lower() in [canonical] + synonyms:
                    expanded_user.update(synonyms)
                    expanded_user.add(canonical)
        
        # 교집합 비율 계산
        if not expanded_correct:
            return 0.0
            
        intersection = expanded_correct & expanded_user
        similarity = len(intersection) / len(expanded_correct)
        
        return similarity

    def _check_partial_correctness(self, question: Dict, user_answer: str, correct_answer: str) -> float:
        """부분 정답 검사 (기존 로직 강화)"""
        # 키워드 포함 검사
        if correct_answer in user_answer:
            return 0.5
            
        # 문자열 유사도 검사 (더 엄격한 기준)
        try:
            ratio = max(
                fuzz.partial_ratio(user_answer, correct_answer),
                fuzz.token_set_ratio(user_answer, correct_answer)
            )
            if ratio >= 85:  # 기준을 80에서 85로 상향
                return 0.5
            elif ratio >= 70:  # 새로운 부분 점수 구간
                return 0.3
        except Exception:
            pass
            
        # 프로그래밍 특화 패턴 매칭
        return self._check_programming_patterns(question, user_answer, correct_answer)

    def _check_programming_patterns(self, question: Dict, user_answer: str, correct_answer: str) -> float:
        """프로그래밍 특화 패턴 매칭"""
        topic = question.get('topic', '').lower()
        
        # 주제별 특화 검사
        if '딕셔너리' in topic or 'dict' in topic.lower():
            if any(word in user_answer.lower() for word in ['get', 'key', 'value']):
                return 0.3
                
        elif '리스트' in topic or 'list' in topic.lower():
            if any(word in user_answer.lower() for word in ['append', 'pop', 'insert', 'remove']):
                return 0.3
                
        elif '문자열' in topic or 'string' in topic.lower():
            if any(word in user_answer.lower() for word in ['strip', 'split', 'join', 'replace']):
                return 0.3
                
        elif '반복' in topic or 'loop' in topic.lower():
            if any(word in user_answer.lower() for word in ['for', 'while', 'range']):
                return 0.3
        
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
    
    async def generate_ai_feedback(self, question: Dict, user_answer: str, score: float, user_id: Optional[int] = None) -> str:
        """고도화된 AI 피드백 생성 (문제 유형별 특화)"""
        provider = get_llm_provider()
        
        # LLM 사용 불가능한 경우 개선된 템플릿 사용
        if not provider:
            return self._generate_enhanced_template_feedback(question, user_answer, score)

        # 캐시 키 구성 (문제 유형 포함)
        question_type = question.get("question_type", "legacy")
        cache_key = make_feedback_cache_key(
            int(question.get("id", 0)), 
            question_type, 
            self._normalize(user_answer),
            user_id
        )
        cached = feedback_cache.get(cache_key)
        if cached:
            return cached

        # 문제 유형별 AI 프롬프트 생성
        system_prompt = self._create_contextual_system_prompt(question_type)
        user_prompt = self._create_contextual_user_prompt(question, user_answer, score, question_type)
        
        try:
            content = await provider.generate(system_prompt, user_prompt, max_tokens=250)
            if content and len(content.strip()) > 10:  # 최소 품질 검증
                feedback_cache.set(cache_key, content)
                return content
        except Exception as e:
            print(f"AI feedback generation failed: {e}")
        
        # AI 실패 시 강화된 템플릿 폴백
        return self._generate_enhanced_template_feedback(question, user_answer, score)

    def _create_contextual_system_prompt(self, question_type: str) -> str:
        """문제 유형별 맞춤 시스템 프롬프트"""
        base_prompt = """당신은 친절하고 전문적인 프로그래밍 튜터입니다. 
학습자의 답안을 분석하여 다음 요소를 포함한 피드백을 제공하세요:

1. 답안 평가 (정답/부분정답/오답)
2. 구체적인 설명 또는 힌트
3. 학습 방향 제시 (다음에 공부할 내용)
4. 격려의 말

응답은 한국어로 3-4문장, 친근하고 격려하는 톤으로 작성하세요."""
        
        type_specific_prompts = {
            "multiple_choice": base_prompt + "\n\n객관식 문제의 경우, 왜 해당 선택지가 정답인지 또는 틀린 선택지를 선택한 이유를 설명해주세요.",
            
            "short_answer": base_prompt + "\n\n단답형 문제의 경우, 핵심 키워드를 명확히 하고 관련 개념을 확장해서 설명해주세요.",
            
            "code_completion": base_prompt + "\n\n코드 완성 문제의 경우, 문법 오류나 로직 개선점을 구체적으로 지적하고 올바른 코드 작성법을 안내해주세요.",
            
            "debug_code": base_prompt + "\n\n디버깅 문제의 경우, 버그를 찾는 체계적인 방법과 예방법을 알려주고, 올바른 수정 방법을 제시해주세요.",
            
            "true_false": base_prompt + "\n\nOX 문제의 경우, 논리적 근거의 타당성을 평가하고 더 나은 논증 방법을 제시해주세요."
        }
        
        return type_specific_prompts.get(question_type, base_prompt)

    def _create_contextual_user_prompt(self, question: Dict, user_answer: str, score: float, question_type: str) -> str:
        """문제 유형별 맞춤 사용자 프롬프트"""
        difficulty = question.get('difficulty', 'easy')
        topic = question.get('topic', '')
        code_snippet = question.get('code_snippet', '')
        correct_answer = question.get('correct_answer', '')
        
        # 점수별 상황 분석
        if score == 1.0:
            situation = "정답"
        elif score >= 0.5:
            situation = "부분정답"
        else:
            situation = "오답"
        
        # 기본 프롬프트
        base_info = f"""다음 프로그래밍 문제에 대한 학습자의 답안을 분석해주세요:

【문제 정보】
- 유형: {question_type}
- 주제: {topic}
- 난이도: {difficulty}
- 코드: {code_snippet}

【답안 분석】
- 정답: {correct_answer}
- 학습자 답안: {user_answer}
- 결과: {situation} (점수: {score})"""

        # 문제 유형별 추가 정보
        type_specific_info = {
            "multiple_choice": f"\n- 선택지: {question.get('choices', [])}",
            "short_answer": f"\n- 핵심 키워드: {question.get('required_keywords', [])}",
            "code_completion": f"\n- 필수 키워드: {question.get('required_keywords', [])}\n- 문법 검사 결과: {'통과' if score >= 0.4 else '실패'}",
            "debug_code": f"\n- 예상 버그: {question.get('bugs', [])}\n- 버그 식별 정확도: {score * 100:.0f}%",
            "true_false": f"\n- 추론 품질: {'우수' if score >= 0.8 else '보통' if score >= 0.5 else '부족'}"
        }
        
        additional_info = type_specific_info.get(question_type, "")
        
        return base_info + additional_info + "\n\n위 정보를 바탕으로 학습자에게 도움이 되는 피드백을 작성해주세요."

    def _generate_enhanced_template_feedback(self, question: Dict, user_answer: str, score: float) -> str:
        """문제 유형별 강화된 템플릿 피드백"""
        question_type = question.get("question_type", "legacy")
        topic = question.get('topic', '')
        correct_answer = question.get('correct_answer', '')
        difficulty = question.get('difficulty', 'easy')
        
        if question_type == "multiple_choice":
            return self._generate_multiple_choice_feedback(score, correct_answer, user_answer, topic)
        elif question_type == "short_answer":
            return self._generate_short_answer_feedback(score, correct_answer, user_answer, topic)
        elif question_type == "fill_in_the_blank":
            return self._generate_fill_in_the_blank_feedback(score, correct_answer, user_answer, topic)
        elif question_type == "code_completion":
            return self._generate_code_completion_feedback(score, correct_answer, user_answer, topic)
        elif question_type == "debug_code":
            return self._generate_debug_code_feedback(score, correct_answer, user_answer, topic)
        elif question_type == "true_false":
            return self._generate_true_false_feedback(score, correct_answer, user_answer, topic)
        else:
            # 기존 레거시 피드백
            return self._generate_legacy_feedback(score, correct_answer, user_answer, topic)

    def _generate_multiple_choice_feedback(self, score: float, correct_answer: str, user_answer: str, topic: str) -> str:
        """객관식 문제 피드백"""
        # correct_answer가 비어있거나 None인 경우 안전하게 처리
        display_answer = correct_answer if correct_answer and correct_answer.strip() else "정답"
        display_user_answer = user_answer if user_answer and user_answer.strip() else "선택하신 답"
        
        if score == 1.0:
            return f"🎉 정답입니다! '{display_answer}' 선택지가 맞습니다. {topic} 개념을 정확히 이해하고 계시네요. 다른 선택지가 왜 틀렸는지도 한번 생각해보시면 더 도움이 될 거예요!"
        else:
            return f"❌ 아쉽게도 틀렸습니다. 정답은 '{display_answer}'입니다. 선택하신 '{display_user_answer}'는 {self._get_wrong_choice_hint(topic)}. {topic} 개념을 다시 한 번 정리해보시고 비슷한 문제를 더 풀어보세요!"

    def _generate_short_answer_feedback(self, score: float, correct_answer: str, user_answer: str, topic: str) -> str:
        """단답형 문제 피드백"""
        # correct_answer가 비어있거나 None인 경우 안전하게 처리
        display_answer = correct_answer if correct_answer and correct_answer.strip() else "정답"
        display_user_answer = user_answer if user_answer and user_answer.strip() else "입력하신 답"
        
        if score == 1.0:
            return f"🎉 완벽합니다! '{display_answer}'를 정확히 입력하셨네요. {topic} 개념을 잘 이해하고 계시는 것 같습니다. 이제 이 개념을 실제 코드에 적용해보는 연습을 해보세요!"
        elif score >= 0.5:
            return f"👍 거의 맞았습니다! 정답은 '{display_answer}'입니다. 입력하신 '{display_user_answer}'와 의미상 비슷하지만 정확한 키워드나 표현이 조금 다릅니다. {topic} 관련 용어를 정확히 기억해보세요."
        else:
            return f"🤔 아쉽게도 틀렸습니다. 정답은 '{display_answer}'입니다. {self._get_topic_hints(topic, '')} {topic} 개념을 다시 한번 정리하고 관련 예제를 더 풀어보시면 도움이 될 거예요!"

    def _generate_fill_in_the_blank_feedback(self, score: float, correct_answer: str, user_answer: str, topic: str) -> str:
        """빈칸 채우기 문제 피드백"""
        # correct_answer가 비어있거나 None인 경우 안전하게 처리
        display_answer = correct_answer if correct_answer and correct_answer.strip() else "정답"
        display_user_answer = user_answer if user_answer and user_answer.strip() else "입력하신 답"
        
        if score == 1.0:
            return f"🎉 정답입니다! 빈칸에 '{display_answer}'를 정확히 입력하셨네요. {topic} 개념을 잘 이해하고 계시는 것 같습니다. 이런 패턴을 기억해두시면 비슷한 문제에서도 도움이 될 거예요!"
        elif score >= 0.5:
            return f"👍 거의 맞았습니다! 정답은 '{display_answer}'입니다. 입력하신 '{display_user_answer}'와 의미상 비슷하지만 정확한 문법이나 키워드가 조금 다릅니다. {topic} 관련 문법을 다시 한번 확인해보세요."
        else:
            return f"🤔 아쉽게도 틀렸습니다. 정답은 '{display_answer}'입니다. {self._get_topic_hints(topic, '')} {topic}의 기본 문법과 함수들을 다시 정리해보시고 비슷한 예제를 더 풀어보세요!"

    def _generate_code_completion_feedback(self, score: float, correct_answer: str, user_answer: str, topic: str) -> str:
        """코드 완성 문제 피드백"""
        if score >= 0.8:
            return f"💻 훌륭한 코드입니다! 문법도 정확하고 로직도 올바릅니다. {topic} 개념을 코드로 잘 구현하셨네요. 이제 더 복잡한 상황에서도 응용해보세요!"
        elif score >= 0.4:
            syntax_ok = score >= 0.4
            if syntax_ok:
                return f"📝 문법은 맞지만 로직을 다시 확인해보세요. 정답 코드: {correct_answer}. {topic}에서 핵심은 올바른 메서드 사용과 변수 처리입니다. 한 단계씩 차근차근 접근해보세요!"
            else:
                return f"⚠️ 문법 오류가 있습니다. Python 기본 문법을 다시 확인하고, {topic} 관련 메서드 사용법을 복습해보세요. 정답 코드: {correct_answer}"
        else:
            return f"💡 코드 작성이 어려우셨나요? {topic} 기본 문법부터 차근차근 연습해보세요. 예시 코드: {correct_answer}. 이 코드를 따라 타이핑해보면서 패턴을 익혀보시길 권장합니다!"

    def _generate_debug_code_feedback(self, score: float, correct_answer: str, user_answer: str, topic: str) -> str:
        """디버깅 문제 피드백"""
        if score >= 0.8:
            return f"🕵️ 훌륭한 디버깅입니다! 버그를 정확히 찾고 올바른 해결책도 제시하셨네요. 이런 체계적인 접근법을 계속 유지하시면 실무에서도 도움이 많이 될 거예요!"
        elif score >= 0.4:
            return f"🔍 버그는 어느 정도 찾으셨지만 수정 방법을 다시 생각해보세요. 올바른 해결책: {correct_answer}. 디버깅할 때는 항상 에러 메시지를 자세히 읽고 단계별로 접근하는 것이 중요합니다!"
        else:
            return f"🐛 디버깅은 연습이 필요한 기술이에요! {topic} 관련 일반적인 오류 패턴을 먼저 학습해보세요. 정답: {correct_answer}. 코드를 한 줄씩 차근차근 읽으며 논리를 따라가보는 습관을 기르세요!"

    def _generate_true_false_feedback(self, score: float, correct_answer: str, user_answer: str, topic: str) -> str:
        """OX 문제 피드백"""
        if score >= 0.8:
            return f"✅ 정답이고 이유도 논리적입니다! {topic} 개념을 잘 이해하고 계시는 것 같습니다. 이런 논리적 사고력을 바탕으로 더 복잡한 개념도 쉽게 이해하실 수 있을 거예요!"
        elif score >= 0.6:
            return f"⭕ 정답은 맞지만 이유 설명을 좀 더 구체적으로 해보세요. {topic}에서 핵심 포인트를 놓치셨습니다. '왜냐하면', '따라서' 같은 논리적 접속사를 사용해서 더 명확하게 설명해보세요!"
        else:
            return f"❓ 답과 근거를 다시 생각해보세요. 정답: {correct_answer}. {topic} 개념의 기본 원리부터 차근차근 정리하고, 논리적으로 결론을 도출하는 연습을 해보시길 권장합니다!"

    def _generate_legacy_feedback(self, score: float, correct_answer: str, user_answer: str, topic: str) -> str:
        """기존 레거시 피드백 (하위 호환성)"""
        if score == 1.0:
            return f"🎉 완벽합니다! '{correct_answer}'를 정확히 입력하셨네요. {topic} 개념을 잘 이해하고 계시는 것 같습니다. 다음 단계로 넘어가셔도 좋겠어요!"
        elif score >= 0.5:
            return f"👍 거의 맞았습니다! 정답은 '{correct_answer}'입니다. 입력하신 '{user_answer}'와 의미상 비슷하지만 정확한 문법이나 표현이 조금 다릅니다. {topic} 관련 문법을 한 번 더 확인해보세요."
        else:
            hints = self._get_topic_hints(topic, "")
            return f"🤔 아쉽게도 틀렸습니다. 정답은 '{correct_answer}'입니다. {hints} {topic} 개념을 다시 한번 정리하고 비슷한 문제를 더 풀어보시면 도움이 될 거예요!"

    def _get_wrong_choice_hint(self, topic: str) -> str:
        """객관식 오답 선택지에 대한 힌트"""
        hints = {
            "딕셔너리": "딕셔너리의 키-값 구조를 다시 확인해보세요",
            "리스트": "리스트의 인덱싱과 슬라이싱을 복습해보세요",
            "문자열": "문자열 메서드의 동작 방식을 다시 정리해보세요",
            "반복문": "반복문의 실행 순서와 조건을 다시 생각해보세요",
            "조건문": "조건문의 논리 연산을 다시 확인해보세요",
            "함수": "함수의 매개변수와 반환값을 다시 정리해보세요",
        }
        return hints.get(topic, "관련 개념을 다시 확인해보세요")

    def _get_topic_hints(self, topic: str, context: str = "") -> str:
        """주제별 학습 힌트 제공"""
        hints = {
            "딕셔너리": "딕셔너리는 키-값 쌍으로 데이터를 저장합니다. .get(), .keys(), .values() 메서드를 활용해보세요.",
            "리스트": "리스트는 순서가 있는 데이터 구조입니다. 인덱싱[0], 슬라이싱[1:3], .append() 등을 연습해보세요.",
            "문자열": "문자열은 불변 객체입니다. .split(), .join(), .replace() 등의 메서드를 활용해보세요.",
            "반복문": "for문과 while문의 차이를 이해하고, range(), enumerate() 함수를 활용해보세요.",
            "조건문": "if, elif, else의 실행 순서를 이해하고, and, or, not 연산자를 활용해보세요.",
            "함수": "함수는 입력(매개변수)을 받아 처리 후 출력(반환값)을 제공합니다. def, return을 정확히 사용해보세요.",
            "변수": "변수는 데이터를 저장하는 공간입니다. 변수명 규칙과 타입 변환을 연습해보세요.",
            "집합": "집합은 중복을 허용하지 않는 데이터 구조입니다. 합집합, 교집합 연산을 활용해보세요."
        }
        return hints.get(topic, f"{topic} 관련 기본 개념을 다시 정리해보세요.")

scoring_service = ScoringService()
