from __future__ import annotations

import asyncio
import json
import random
from typing import Dict, List, Optional, Any
import re
from datetime import datetime

from app.services.llm_providers import get_llm_provider
from app.services.llm_cache import feedback_cache
from app.models.question_types import (
    QuestionType, DifficultyLevel, QuestionUnion,
    MultipleChoiceQuestion, ShortAnswerQuestion, CodeCompletionQuestion,
    DebugCodeQuestion, TrueFalseQuestion
)


class AIQuestionGenerator:
    """AI 기반 문제 생성 서비스"""
    
    def __init__(self):
        self.difficulty_levels = ["easy", "medium", "hard"]
        self.question_types = [
            "multiple_choice", "short_answer", "code_completion", 
            "debug_code", "true_false", "fill_in_the_blank"  # 기존 유형 유지
        ]
        
        # 5가지 문제 유형별 AI 프롬프트 템플릿
        self.question_generation_prompts = {
            "multiple_choice": """
당신은 파이썬 프로그래밍 교육 전문가입니다.
다음 조건으로 객관식 문제를 생성해주세요:

**주제**: {topic}
**난이도**: {difficulty}
**학습 목표**: {learning_objectives}

**요구사항**:
- 명확하고 구체적인 질문
- 4개의 선택지 (A, B, C, D로 시작)
- 정답 1개, 그럴듯한 오답 3개
- 각 오답 선택지에 대한 설명
- 정답에 대한 상세 해설

**JSON 형식으로 응답해주세요**:
{{
    "question": "문제 내용",
    "options": ["A) 선택지1", "B) 선택지2", "C) 선택지3", "D) 선택지4"],
    "correct_answer": "A",
    "explanation": "정답 해설 (왜 이것이 정답인지 상세히 설명)",
    "distractor_analysis": {{
        "B": "B를 선택하는 이유와 왜 틀렸는지 설명",
        "C": "C를 선택하는 이유와 왜 틀렸는지 설명", 
        "D": "D를 선택하는 이유와 왜 틀렸는지 설명"
    }}
}}
""",

            "short_answer": """
당신은 파이썬 프로그래밍 교육 전문가입니다.
다음 조건으로 주관식 문제를 생성해주세요:

**주제**: {topic}
**난이도**: {difficulty}
**학습 목표**: {learning_objectives}

**요구사항**:
- 2-3문장으로 답할 수 있는 개념 설명 문제
- 핵심 키워드 3-5개가 포함되어야 하는 답안
- 모범 답안 100-200자
- 채점 기준 명확화

**JSON 형식으로 응답해주세요**:
{{
    "question": "문제 내용 (예: ~에 대해 설명하세요)",
    "expected_keywords": ["키워드1", "키워드2", "키워드3", "키워드4"],
    "sample_answer": "모범 답안 예시 (100-200자)",
    "scoring_criteria": {{
        "keyword_match": 0.4,
        "semantic_similarity": 0.6
    }},
    "min_length": 80,
    "max_length": 250
}}
""",

            "code_completion": """
당신은 파이썬 프로그래밍 교육 전문가입니다.
다음 조건으로 코드 완성 문제를 생성해주세요:

**주제**: {topic}
**난이도**: {difficulty}
**학습 목표**: {learning_objectives}

**요구사항**:
- 실무에서 자주 사용되는 패턴
- 2-4개의 빈칸 (____로 표시)
- 각 빈칸에 대한 힌트
- 테스트 케이스 3개 이상

**JSON 형식으로 응답해주세요**:
{{
    "question": "다음 함수를 완성하세요: [함수의 목적 설명]",
    "code_template": "def function_name(params):\\n    # 설명\\n    ____ = ____\\n    for item in ____:\\n        if ____:\\n            ____\\n    return ____",
    "blanks": ["정답1", "정답2", "정답3", "정답4"],
    "blank_hints": ["힌트1", "힌트2", "힌트3", "힌트4"],
    "test_cases": [
        {{"input": "입력예시1", "output": "예상출력1"}},
        {{"input": "입력예시2", "output": "예상출력2"}},
        {{"input": "입력예시3", "output": "예상출력3"}}
    ]
}}
""",

            "debug_code": """
당신은 파이썬 프로그래밍 교육 전문가입니다.
다음 조건으로 디버깅 문제를 생성해주세요:

**주제**: {topic}
**난이도**: {difficulty}
**학습 목표**: {learning_objectives}

**요구사항**:
- 실제 초보자가 자주 하는 실수 1-2개
- 각 버그의 원인과 수정 방법 설명
- 수정된 완전한 코드
- 실행 가능한 코드 예제

**JSON 형식으로 응답해주세요**:
{{
    "question": "다음 코드의 오류를 찾아 수정하세요",
    "buggy_code": "# 목적: [코드가 하려는 일]\\ndef function_name():\\n    # 버그가 포함된 코드\\n    pass",
    "errors": [
        {{"line": 3, "error": "오류 설명", "fix": "수정 방법"}},
        {{"line": 5, "error": "오류 설명2", "fix": "수정 방법2"}}
    ],
    "corrected_code": "# 수정된 완전한 코드",
    "bug_types": ["syntax", "logic", "runtime"]
}}
""",

            "true_false": """
당신은 파이썬 프로그래밍 교육 전문가입니다.
다음 조건으로 참/거짓 문제를 생성해주세요:

**주제**: {topic}
**난이도**: {difficulty}
**학습 목표**: {learning_objectives}

**요구사항**:
- 명확한 참/거짓 판단이 가능한 문장
- 일반적인 오해나 혼동을 다루는 내용
- 상세한 해설과 이유

**JSON 형식으로 응답해주세요**:
{{
    "statement": "판단할 문장 (예: 파이썬에서 ...는 ...이다)",
    "correct_answer": true,
    "explanation": "정답 해설 (왜 참/거짓인지 상세히 설명)",
    "common_misconception": "학습자가 자주 틀리는 이유나 혼동하는 개념"
}}
"""
        }
        
        # 주제별 학습 목표 매핑
        self.topic_learning_objectives = {
            "딕셔너리": {
                "easy": ["기본 메서드 (.get(), .keys(), .values())", "키-값 접근"],
                "medium": ["딕셔너리 컴프리헨션", "중첩 딕셔너리 처리"],
                "hard": ["defaultdict, Counter 활용", "딕셔너리 병합 기법"]
            },
            "리스트": {
                "easy": ["기본 메서드 (.append(), .pop(), .insert())", "인덱싱과 슬라이싱"],
                "medium": ["리스트 컴프리헨션", "정렬과 필터링"],
                "hard": ["다차원 리스트", "리스트 메모리 최적화"]
            },
            "문자열": {
                "easy": ["기본 메서드 (.strip(), .split(), .join())", "문자열 포매팅"],
                "medium": ["정규표현식 기초", "문자열 검색과 치환"],
                "hard": ["고급 정규표현식", "유니코드 처리"]
            },
            "반복문": {
                "easy": ["for문 기초", "range() 함수"],
                "medium": ["중첩 반복문", "enumerate(), zip() 활용"],
                "hard": ["제너레이터와 이터레이터", "반복문 최적화"]
            },
            "조건문": {
                "easy": ["if-elif-else 구조", "논리 연산자"],
                "medium": ["조건문과 함수 결합", "삼항 연산자"],
                "hard": ["복잡한 조건 로직", "조건문 최적화"]
            },
            "함수": {
                "easy": ["함수 정의와 호출", "매개변수와 반환값"],
                "medium": ["기본값, 가변인자", "람다 함수"],
                "hard": ["데코레이터", "클로저와 스코프"]
            }
        }

    async def generate_questions_for_daily_curriculum(
        self, 
        topic: str, 
        difficulty: str = "easy", 
        count: int = 5,
        student_weaknesses: List[str] = None
    ) -> List[Dict[str, Any]]:
        """일일 수업 진도에 맞춘 문제 생성"""
        
        provider = get_llm_provider()
        if not provider:
            return self._generate_template_questions(topic, difficulty, count)
        
        generated_questions = []
        learning_objectives = self.topic_learning_objectives.get(topic, {}).get(difficulty, [])
        
        for i in range(count):
            try:
                question = await self._generate_single_question(
                    provider, topic, difficulty, learning_objectives, student_weaknesses
                )
                if question:
                    question["id"] = self._generate_temp_id()
                    question["created_at"] = datetime.now().isoformat()
                    question["ai_generated"] = True
                    generated_questions.append(question)
                    
                # API 호출 간격 조절
                if i < count - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                print(f"문제 생성 실패 (#{i+1}): {e}")
                # 실패 시 템플릿 문제 추가
                template_question = self._create_template_question(topic, difficulty, i)
                if template_question:
                    generated_questions.append(template_question)
        
        return generated_questions

    async def _generate_single_question(
        self, 
        provider, 
        topic: str, 
        difficulty: str, 
        learning_objectives: List[str],
        student_weaknesses: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """단일 문제 생성"""
        
        system_prompt = self._create_question_generation_system_prompt()
        user_prompt = self._create_question_generation_user_prompt(
            topic, difficulty, learning_objectives, student_weaknesses
        )
        
        try:
            content = await provider.generate(system_prompt, user_prompt, max_tokens=300)
            if content:
                return self._parse_generated_question(content, topic, difficulty)
        except Exception as e:
            print(f"AI 문제 생성 실패: {e}")
            
        return None

    def _create_question_generation_system_prompt(self) -> str:
        """문제 생성용 시스템 프롬프트"""
        return """당신은 프로그래밍 교육 전문가입니다. 
주어진 주제와 난이도에 맞는 고품질 코딩 문제를 생성하세요.

다음 JSON 형식으로 응답하세요:
{
    "question_type": "fill_in_the_blank",
    "code_snippet": "실제 실행 가능한 파이썬 코드 (빈칸은 ____로 표시)",
    "answer": "빈칸에 들어갈 정답",
    "rubric": "채점 기준 (1-2문장)",
    "explanation": "문제 해설 (학습 포인트 포함)"
}

주의사항:
1. 코드는 실제 실행 가능해야 함
2. 빈칸은 정확히 ____로 표시
3. 답안은 간단명료하게 (단어 또는 짧은 구문)
4. 실무에서 자주 사용하는 패턴 위주로 출제"""

    def _create_question_generation_user_prompt(
        self, 
        topic: str, 
        difficulty: str, 
        learning_objectives: List[str],
        student_weaknesses: List[str] = None
    ) -> str:
        """문제 생성용 사용자 프롬프트"""
        
        weakness_focus = ""
        if student_weaknesses:
            weakness_focus = f"\n\n특히 다음 취약점을 보완할 수 있는 문제로: {', '.join(student_weaknesses)}"
        
        objectives_text = ", ".join(learning_objectives) if learning_objectives else f"{topic} 기초 개념"
        
        return f"""다음 조건에 맞는 파이썬 프로그래밍 문제를 생성해주세요:

【문제 조건】
- 주제: {topic}
- 난이도: {difficulty}
- 학습 목표: {objectives_text}
- 문제 유형: 빈칸 채우기{weakness_focus}

실제 개발에서 자주 사용되는 실용적인 예제로 만들어주세요.
초보자도 이해할 수 있도록 코드는 간단하고 명확하게 작성해주세요."""

    def _parse_generated_question(self, content: str, topic: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """생성된 문제 파싱 및 검증"""
        try:
            # JSON 추출 시도
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                question_data = json.loads(json_str)
                
                # 필수 필드 검증
                required_fields = ["question_type", "code_snippet", "answer", "rubric"]
                if all(field in question_data for field in required_fields):
                    # 추가 메타데이터 설정
                    question_data.update({
                        "subject": "python_basics",
                        "topic": topic,
                        "difficulty": difficulty,
                        "created_by": "AI",
                        "is_active": True
                    })
                    return question_data
                    
        except (json.JSONDecodeError, KeyError) as e:
            print(f"문제 파싱 실패: {e}")
            
        return None

    def _generate_template_questions(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """AI 사용 불가능 시 템플릿 문제 생성"""
        template_questions = []
        
        for i in range(count):
            question = self._create_template_question(topic, difficulty, i)
            if question:
                template_questions.append(question)
                
        return template_questions

    def _create_template_question(self, topic: str, difficulty: str, index: int) -> Optional[Dict[str, Any]]:
        """템플릿 기반 문제 생성"""
        templates = {
            "딕셔너리": {
                "easy": [
                    {
                        "code_snippet": "my_dict = {'name': 'Alice', 'age': 25}\nresult = my_dict.____('name')",
                        "answer": "get",
                        "rubric": "딕셔너리의 get() 메서드를 정확히 사용했는지 평가"
                    },
                    {
                        "code_snippet": "data = {'a': 1, 'b': 2}\nkeys_list = list(data.____())",
                        "answer": "keys",
                        "rubric": "딕셔너리의 keys() 메서드를 정확히 사용했는지 평가"
                    }
                ]
            },
            "리스트": {
                "easy": [
                    {
                        "code_snippet": "numbers = [1, 2, 3]\nnumbers.____(4)  # 리스트 끝에 요소 추가",
                        "answer": "append",
                        "rubric": "리스트의 append() 메서드를 정확히 사용했는지 평가"
                    },
                    {
                        "code_snippet": "items = [1, 2, 3, 4, 5]\nlast_item = items.____()  # 마지막 요소 제거하면서 반환",
                        "answer": "pop",
                        "rubric": "리스트의 pop() 메서드를 정확히 사용했는지 평가"
                    }
                ]
            }
        }
        
        topic_templates = templates.get(topic, {}).get(difficulty, [])
        if topic_templates and index < len(topic_templates):
            template = topic_templates[index]
            return {
                "id": self._generate_temp_id(),
                "subject": "python_basics",
                "topic": topic,
                "question_type": "fill_in_the_blank",
                "difficulty": difficulty,
                "created_by": "AI_Template",
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "ai_generated": True,
                **template
            }
        
        return None

    def _generate_temp_id(self) -> int:
        """임시 ID 생성 (실제로는 데이터베이스에서 자동 생성)"""
        return random.randint(100000, 999999)

    async def analyze_student_weaknesses(self, user_id: int, subject: str = "python_basics") -> List[str]:
        """학생의 취약점 분석 (추후 데이터베이스 연동)"""
        # 임시 구현 - 실제로는 제출 기록을 분석
        common_weaknesses = ["메서드 사용법", "문법 정확성", "변수명 규칙"]
        return random.sample(common_weaknesses, 2)

    async def generate_adaptive_questions(
        self, 
        user_id: int, 
        current_topic: str, 
        performance_history: List[Dict] = None
    ) -> List[Dict[str, Any]]:
        """학습자 맞춤형 적응 문제 생성"""
        
        # 성과 분석
        if performance_history:
            avg_score = sum(h.get('score', 0) for h in performance_history) / len(performance_history)
            weak_topics = [h['topic'] for h in performance_history if h.get('score', 0) < 0.6]
        else:
            avg_score = 0.5
            weak_topics = []
        
        # 난이도 조정
        if avg_score >= 0.8:
            difficulty = "medium"
        elif avg_score >= 0.6:
            difficulty = "easy"
        else:
            difficulty = "easy"
            
        # 취약점 기반 문제 생성
        student_weaknesses = await self.analyze_student_weaknesses(user_id)
        
        return await self.generate_questions_for_daily_curriculum(
            topic=current_topic,
            difficulty=difficulty,
            count=3,
            student_weaknesses=student_weaknesses
        )

    async def generate_question_by_type(
        self, 
        question_type: str,
        topic: str,
        difficulty: str,
        context: Dict = None
    ) -> Dict[str, Any]:
        """문제 유형별 생성 메인 함수"""
        
        # 1. 입력 검증
        if question_type not in self.question_types:
            raise ValueError(f"지원하지 않는 문제 유형: {question_type}")
        
        # 2. 학습 목표 가져오기
        learning_objectives = self._get_learning_objectives(topic, difficulty)
        
        # 3. AI 프롬프트 생성
        try:
            if question_type in self.question_generation_prompts:
                prompt = self.question_generation_prompts[question_type].format(
                    topic=topic,
                    difficulty=difficulty,
                    learning_objectives=", ".join(learning_objectives)
                )
                
                # 4. AI 호출
                ai_response = await self._call_ai_api_new(prompt)
                question = self._parse_ai_response_new(ai_response, question_type)
                
            else:
                # 기존 fill_in_the_blank 방식 사용
                question = await self.generate_questions_for_daily_curriculum(
                    subject="python_basics",
                    topic=topic,
                    difficulty=difficulty,
                    count=1
                )
                if question:
                    return question[0]
                
        except Exception as e:
            print(f"❌ AI 문제 생성 실패 ({question_type}): {e}")
            # 5. 폴백 시스템
            question = await self._generate_fallback_question(question_type, topic, difficulty)
        
        # 6. 기본 메타데이터 추가
        question.update({
            "type": question_type,
            "topic": topic,
            "difficulty": difficulty,
            "estimated_time": self._estimate_time(question_type, difficulty),
            "learning_objectives": learning_objectives,
            "created_at": datetime.now().isoformat(),
            "ai_generated": True
        })
        
        return question

    async def generate_mixed_question_set(
        self,
        topic: str,
        difficulty: str, 
        question_mix: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """여러 문제 유형을 한 번에 생성 (순차 처리로 Rate Limit 방지)"""
        
        questions = []
        
        for question_type, count in question_mix.items():
            for i in range(count):
                try:
                    # Rate Limiting 방지를 위한 대기 (첫 번째 문제 제외)
                    if questions:  # 첫 번째 문제가 아니라면
                        print(f"⏳ Rate Limit 방지 대기 중... (2초)")
                        await asyncio.sleep(2)
                    
                    print(f"🔄 {question_type} 문제 생성 중... ({i+1}/{count})")
                    question = await self.generate_question_by_type(
                        question_type, topic, difficulty
                    )
                    questions.append(question)
                    print(f"✅ {question_type} 문제 생성 완료")
                    
                except Exception as e:
                    print(f"❌ {question_type} 문제 생성 실패: {e}")
                    # 실패한 문제는 템플릿으로 대체
                    fallback_question = self._generate_fallback_question(question_type, topic, difficulty)
                    if fallback_question:
                        questions.append(fallback_question)
                        print(f"🔄 {question_type} 템플릿 문제로 대체 완료")
                    continue
        
        # 문제 순서 셔플
        random.shuffle(questions)
        
        print(f"🎯 총 {len(questions)}개 문제 생성 완료")
        return questions

    async def _call_ai_api_new(self, prompt: str) -> str:
        """새로운 AI API 호출 함수"""
        try:
            print(f"🚀 AI API 호출 시작...")
            
            llm = get_llm_provider()
            if not llm:
                print("❌ LLM 제공자를 사용할 수 없습니다")
                raise Exception("LLM 제공자를 사용할 수 없습니다. OpenRouter API 키를 확인해주세요.")
            
            print(f"🔧 LLM 제공자 확인됨, AI 호출 중...")
            
            # OpenRouter API는 system_prompt와 user_prompt를 구분
            response = await llm.generate(
                system_prompt="당신은 파이썬 프로그래밍 교육 전문가입니다. JSON 형식으로만 응답해주세요.",
                user_prompt=prompt,
                max_tokens=1500
            )
            
            if not response:
                print("❌ AI 응답이 비어있습니다")
                raise Exception("AI 응답이 비어있습니다")
            
            print(f"✅ AI API 호출 성공, 응답 길이: {len(response)}")
            return response
        except Exception as e:
            print(f"❌ AI API 호출 실패: {e}")
            raise

    def _parse_ai_response_new(self, response: str, question_type: str) -> Dict[str, Any]:
        """AI 응답을 파싱하여 문제 데이터로 변환"""
        try:
            # JSON 응답 파싱
            question_data = json.loads(response)
            
            # 필수 필드 검증
            required_fields = {
                "multiple_choice": ["question", "options", "correct_answer", "explanation"],
                "short_answer": ["question", "expected_keywords", "sample_answer"],
                "code_completion": ["question", "code_template", "blanks"],
                "debug_code": ["question", "buggy_code", "errors", "corrected_code"],
                "true_false": ["statement", "correct_answer", "explanation"]
            }
            
            if question_type in required_fields:
                for field in required_fields[question_type]:
                    if field not in question_data:
                        raise ValueError(f"필수 필드 누락: {field}")

            # Normalize field names: some prompts use 'options' while frontend expects 'choices'
            if 'options' in question_data and 'choices' not in question_data:
                opts = question_data.get('options') or []
                # Ensure list and clean prefixed labels like 'A) ...' or 'A. ...'
                if isinstance(opts, list):
                    cleaned = []
                    for o in opts:
                        if isinstance(o, str):
                            cleaned.append(re.sub(r'^[A-Za-z][\)\.\-:\s]*', '', o).strip())
                        else:
                            cleaned.append(str(o))
                else:
                    cleaned = [str(opts)]
                question_data['choices'] = cleaned

            # Backwards: if 'choices' present but frontend expects 'options', keep both to be safe
            if 'choices' in question_data and 'options' not in question_data:
                question_data['options'] = question_data['choices']
            
            return question_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {e}")
            print(f"응답: {response}")
            raise ValueError(f"AI 응답 JSON 파싱 실패: {e}")

    async def _generate_fallback_question(
        self, 
        question_type: str, 
        topic: str, 
        difficulty: str
    ) -> Dict[str, Any]:
        """AI 실패 시 템플릿 기반 폴백 문제 생성"""
        
        fallback_questions = {
            "multiple_choice": {
                "question": f"{topic}에 대한 기본 개념을 확인하는 문제입니다.",
                "options": [
                    "A) 첫 번째 선택지",
                    "B) 두 번째 선택지", 
                    "C) 세 번째 선택지",
                    "D) 네 번째 선택지"
                ],
                "correct_answer": "A",
                "explanation": f"{topic}의 기본 개념입니다.",
                "distractor_analysis": {
                    "B": "일반적인 오해입니다.",
                    "C": "부분적으로 맞지만 완전하지 않습니다.",
                    "D": "잘못된 접근입니다."
                }
            },
            "short_answer": {
                "question": f"{topic}에 대해 간단히 설명해주세요.",
                "expected_keywords": [topic, "파이썬", "프로그래밍"],
                "sample_answer": f"{topic}는 파이썬 프로그래밍의 중요한 개념입니다.",
                "scoring_criteria": {"keyword_match": 0.4, "semantic_similarity": 0.6},
                "min_length": 50,
                "max_length": 200
            },
            "code_completion": {
                "question": f"{topic}을 활용한 간단한 코드를 완성하세요.",
                "code_template": "# 코드 완성 문제\nresult = ____\nprint(result)",
                "blanks": ["None"],
                "blank_hints": ["적절한 값을 입력하세요"],
                "test_cases": [{"input": "test", "output": "result"}]
            },
            "debug_code": {
                "question": f"{topic} 관련 코드의 오류를 수정하세요.",
                "buggy_code": "# 오류가 있는 코드\nprint('Hello World'",
                "errors": [{"line": 2, "error": "괄호 누락", "fix": "닫는 괄호 추가"}],
                "corrected_code": "# 수정된 코드\nprint('Hello World')",
                "bug_types": ["syntax"]
            },
            "true_false": {
                "statement": f"{topic}는 파이썬에서 중요한 개념이다.",
                "correct_answer": True,
                "explanation": f"{topic}는 실제로 파이썬 프로그래밍에서 중요합니다.",
                "common_misconception": "기본 개념이라서 중요하지 않다고 생각할 수 있습니다."
            }
        }
        
        return fallback_questions.get(question_type, {})

    def _estimate_time(self, question_type: str, difficulty: str) -> int:
        """문제 유형과 난이도에 따른 예상 소요 시간 (초)"""
        base_times = {
            "multiple_choice": 120,
            "short_answer": 180,
            "code_completion": 300,
            "debug_code": 240,
            "true_false": 60
        }
        
        difficulty_multipliers = {
            "easy": 0.8,
            "medium": 1.0,
            "hard": 1.3
        }
        
        base = base_times.get(question_type, 180)
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        
        return int(base * multiplier)

    def _get_learning_objectives(self, topic: str, difficulty: str) -> List[str]:
        """주제와 난이도에 따른 학습 목표 반환"""
        if hasattr(self, 'topic_learning_objectives') and topic in self.topic_learning_objectives:
            return self.topic_learning_objectives[topic].get(difficulty, [f"{topic} 기초 개념"])
        return [f"{topic} 기초 개념", "문제 해결 능력"]


# 전역 인스턴스
ai_question_generator = AIQuestionGenerator()

# 모듈 레벨에서 export할 객체들 명시
__all__ = ['AIQuestionGenerator', 'ai_question_generator']
