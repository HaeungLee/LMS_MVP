"""
MVP Week 1: 일일 학습 서비스
오늘의 학습 콘텐츠 제공 (교과서 + 실습 + 퀴즈)

기존 서비스 통합:
- SyllabusBasedTeachingAgent (교과서/개념 설명)
- CodeExecutionService (실습/코드 실행)
- AIQuestionGeneratorEnhanced (퀴즈 생성)
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.services.syllabus_based_teaching_agent import (
    SyllabusBasedTeachingAgent,
    TeachingResponse
)
from app.services.code_execution_service import (
    CodeExecutionService,
    ExecutionResult,
    TestCase
)
from app.services.ai_question_generator_enhanced import (
    AIQuestionGeneratorEnhanced,
    QuestionGenerationRequest,
    QuestionType,
    DifficultyLevel
)
from app.models.ai_curriculum import AIGeneratedCurriculum, AITeachingSession
from app.models.orm import User
from app.models.code_problem import CodeProblem, CodeSubmission
from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class DailyLearningService:
    """
    일일 학습 서비스 (MVP 래퍼)
    
    기존 시스템 활용:
    - SyllabusBasedTeachingAgent → 교과서 (개념 설명)
    - CodeExecutionService → 실습 (코드 실행)
    - AIQuestionGeneratorEnhanced → 퀴즈 (문제 생성)
    
    MVP 특화:
    - 커리큘럼의 특정 날짜 학습 콘텐츠 제공
    - 3단계 구조: 교과서 → 실습 → 퀴즈
    - 진도 추적 및 완료율 계산
    """
    
    def __init__(self):
        self.teaching_agent = SyllabusBasedTeachingAgent()
        self.code_executor = CodeExecutionService()
        self.question_generator = AIQuestionGeneratorEnhanced()
        self.redis_service = get_redis_service()

    def _extract_response_text(self, response: Any) -> str:
        """
        Normalize various provider response shapes into a plain string.

        Handles:
        - dict-like responses with keys like 'response', 'text', 'content'
        - JSON-encoded strings (attempts to json.loads)
        - plain strings
        - objects with a .text attribute
        """
        try:
            # dict-like
            if isinstance(response, dict):
                for k in ("response", "text", "content", "answer"):
                    if k in response and isinstance(response[k], str):
                        return response[k]
                # fallback: jsonify the dict
                try:
                    return json.dumps(response, ensure_ascii=False)
                except Exception:
                    return str(response)

            # plain string: maybe JSON
            if isinstance(response, str):
                try:
                    parsed = json.loads(response)
                    # if parsed is dict/has expected keys, try again
                    if isinstance(parsed, dict):
                        return self._extract_response_text(parsed)
                    # otherwise, return the stringified parsed
                    return str(parsed)
                except Exception:
                    return response

            # object with `.text` attribute (requests-like)
            if hasattr(response, "text") and isinstance(getattr(response, "text"), str):
                return getattr(response, "text")

            # fallback
            return str(response)
        except Exception:
            try:
                return str(response)
            except Exception:
                return ""

    def _normalize_syllabus(self, syllabus_raw: Any) -> Dict[str, Any]:
        """Ensure syllabus is a dict. If it's a JSON string try to parse it, otherwise return a minimal structure."""
        if syllabus_raw is None:
            return {}
        if isinstance(syllabus_raw, dict):
            return syllabus_raw
        if isinstance(syllabus_raw, str):
            try:
                parsed = json.loads(syllabus_raw)
                if isinstance(parsed, dict):
                    return parsed
                # if it's not a dict, keep as text under 'raw'
                return {"raw": str(parsed)}
            except Exception:
                return {"raw": syllabus_raw}
        # unknown type
        try:
            return dict(syllabus_raw)
        except Exception:
            return {"raw": str(syllabus_raw)}
    
    async def get_today_learning(
        self,
        user_id: int,
        curriculum_id: int,
        target_date: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        오늘의 학습 콘텐츠 가져오기
        
        Args:
            user_id: 사용자 ID
            curriculum_id: 커리큘럼 ID
            target_date: 학습 날짜 (None이면 오늘)
            db: 데이터베이스 세션
            
        Returns:
            {
                "date": "2025-10-17",
                "week": 1,
                "day": 3,
                "theme": "FastAPI 기초 & 라우팅",
                "task": "실습: FastAPI 라우팅",
                "deliverable": "구현하기: 기본 CRUD API",
                "status": "not_started",  # not_started, in_progress, completed
                "sections": {
                    "textbook": {...},    # 교과서 (개념)
                    "practice": {...},    # 실습 (코딩)
                    "quiz": {...}         # 퀴즈
                },
                "progress": {
                    "textbook_read": false,
                    "practice_submitted": false,
                    "quiz_completed": false,
                    "completion_percentage": 0
                }
            }
        """
        try:
            import time
            start_time = time.time()
            logger.info(f"⏱️ [START] 오늘의 학습 조회: user_id={user_id}, curriculum_id={curriculum_id}")
            
            # 1. 커리큘럼 조회
            step_start = time.time()
            curriculum = await self._get_curriculum(curriculum_id, user_id, db)
            logger.info(f"⏱️ [1/6] 커리큘럼 조회: {time.time() - step_start:.2f}초")
            if not curriculum:
                raise ValueError("커리큘럼을 찾을 수 없습니다")
            
            # 2. 학습 시작일 기준 현재 학습 날짜 계산
            step_start = time.time()
            current_day_info = self._calculate_current_day(
                curriculum, target_date
            )
            logger.info(f"⏱️ [2/6] 날짜 계산: {time.time() - step_start:.2f}초")
            
            # 3. Redis 캐시 확인 (curriculum_id + week + day 기준)
            cache_key = f"daily_learning:{curriculum_id}:w{current_day_info['week']}d{current_day_info['day']}"
            cached_sections = self.redis_service.get_cache(cache_key)
            
            if cached_sections:
                logger.info(f"✅ Redis 캐시 히트: {cache_key} (생성 비용 절약: ~7-8초)")
                # 캐시된 섹션 사용 (progress는 실시간 조회)
                step_start = time.time()
                daily_task = self._get_daily_task_from_curriculum(
                    curriculum, current_day_info["week"], current_day_info["day"]
                )
                logger.info(f"⏱️ [3/6] 태스크 추출: {time.time() - step_start:.2f}초")
                
                step_start = time.time()
                progress = await self._get_daily_progress(
                    user_id, curriculum_id, current_day_info, db
                )
                logger.info(f"⏱️ [4/6] 진도 계산: {time.time() - step_start:.2f}초")
                
                total_time = time.time() - start_time
                logger.info(f"⏱️ [DONE] 캐시 사용 총 소요시간: {total_time:.2f}초")
                
                return {
                    "date": (target_date or datetime.utcnow()).strftime("%Y-%m-%d"),
                    "week": current_day_info["week"],
                    "day": current_day_info["day"],
                    "theme": daily_task.get("theme", ""),
                    "task": daily_task.get("task", ""),
                    "deliverable": daily_task.get("deliverable", ""),
                    "learning_objectives": daily_task.get("learning_objectives", []),
                    "study_time_minutes": daily_task.get("study_time_minutes", 60),
                    "status": progress["overall_status"],
                    "sections": cached_sections,
                    "progress": progress
                }
            
            # 캐시 미스 - 새로 생성
            logger.info(f"❌ Redis 캐시 미스: {cache_key} (LLM 호출하여 생성 중...)")
            
            # 4. 해당 날짜의 학습 콘텐츠 가져오기
            step_start = time.time()
            daily_task = self._get_daily_task_from_curriculum(
                curriculum, current_day_info["week"], current_day_info["day"]
            )
            logger.info(f"⏱️ [3/6] 태스크 추출: {time.time() - step_start:.2f}초")
            
            # 5. 3가지 섹션 병렬 생성 (성능 최적화)
            step_start = time.time()
            import asyncio
            textbook_section, practice_section, quiz_section = await asyncio.gather(
                self._generate_textbook_section(daily_task, curriculum, user_id, db),
                self._generate_practice_section(daily_task, curriculum, user_id, db),
                self._generate_quiz_section(daily_task, curriculum, user_id, db)
            )
            logger.info(f"⏱️ [4-6/6] 3개 섹션 병렬 생성: {time.time() - step_start:.2f}초 (이전 방식 대비 ~60% 단축)")
            
            # 6. 섹션 데이터 Redis에 저장 (24시간 TTL)
            sections_data = {
                "textbook": textbook_section,
                "practice": practice_section,
                "quiz": quiz_section
            }
            self.redis_service.set_cache(cache_key, sections_data, 86400)  # 24시간
            logger.info(f"💾 Redis 캐시 저장: {cache_key} (TTL: 24시간)")
            
            # 7. 진도 상태 조회
            step_start = time.time()
            progress = await self._get_daily_progress(
                user_id, curriculum_id, current_day_info, db
            )
            logger.info(f"⏱️ [7/7] 진도 조회: {time.time() - step_start:.2f}초")
            
            # 8. 결과 조합
            today_learning = {
                "date": (target_date or datetime.utcnow()).strftime("%Y-%m-%d"),
                "week": current_day_info["week"],
                "day": current_day_info["day"],
                "theme": daily_task.get("theme", ""),
                "task": daily_task.get("task", ""),
                "deliverable": daily_task.get("deliverable", ""),
                "learning_objectives": daily_task.get("learning_objectives", []),
                "study_time_minutes": daily_task.get("study_time_minutes", 60),
                "status": progress["overall_status"],
                "sections": sections_data,
                "progress": progress
            }
            
            total_time = time.time() - start_time
            logger.info(f"✅ [DONE] 오늘의 학습 생성 완료: Week {current_day_info['week']} Day {current_day_info['day']} (총 {total_time:.2f}초)")
            
            # 10초 이상 걸리면 경고
            if total_time > 10:
                logger.warning(f"⚠️ 느린 응답 감지: {total_time:.2f}초 (교재:{textbook_section.get('available')}, 실습:{practice_section.get('available')}, 퀴즈:{quiz_section.get('available')})")
            
            return today_learning
            
        except Exception as e:
            logger.error(f"❌ 오늘의 학습 조회 실패: {str(e)}")
            raise
    
    async def _get_curriculum(
        self,
        curriculum_id: int,
        user_id: int,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """커리큘럼 조회"""
        curriculum = db.query(AIGeneratedCurriculum).filter(
            AIGeneratedCurriculum.id == curriculum_id,
            AIGeneratedCurriculum.user_id == user_id
        ).first()
        
        if not curriculum:
            return None
        
        # Normalize syllabus which may be stored as dict or raw string
        syllabus = self._normalize_syllabus(curriculum.generated_syllabus)
        return {
            "id": curriculum.id,
            "goal": syllabus.get("goal") if isinstance(syllabus, dict) else None,
            "syllabus": syllabus,
            "created_at": curriculum.created_at
        }
    
    def _calculate_current_day(
        self,
        curriculum: Dict[str, Any],
        target_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        학습 시작일 기준 현재 학습 날짜 계산
        
        Returns:
            {"week": 1, "day": 3, "total_days": 3}
        """
        start_date = curriculum["created_at"]
        current_date = target_date or datetime.utcnow()
        
        # 경과 일수 계산 (1부터 시작)
        days_elapsed = (current_date.date() - start_date.date()).days + 1
        
        # 주차 계산 (주 5일 기준, 주말 제외)
        # 간단하게: 7일마다 1주차 증가
        week = ((days_elapsed - 1) // 7) + 1
        day = ((days_elapsed - 1) % 7) + 1
        
        # 주 5일만 학습 (Day 6-7은 주말, 다음 주로)
        if day > 5:
            week += 1
            day = 1
        
        return {
            "week": week,
            "day": day,
            "total_days": days_elapsed
        }
    
    def _get_daily_task_from_curriculum(
        self,
        curriculum: Dict[str, Any],
        week: int,
        day: int
    ) -> Dict[str, Any]:
        """커리큘럼에서 특정 주차/날짜의 과제 가져오기"""
        syllabus = curriculum["syllabus"]
        weekly_themes = syllabus.get("weekly_themes", [])
        
        # 해당 주차 찾기
        week_data = next(
            (w for w in weekly_themes if w["week"] == week),
            None
        )
        
        if not week_data:
            # 커리큘럼 범위 초과 (완료 상태)
            return {
                "theme": "완료",
                "task": "축하합니다! 모든 커리큘럼을 완료했습니다.",
                "deliverable": "최종 프로젝트 완성",
                "type": "completed",
                "learning_objectives": []
            }
        
        # 해당 날짜의 과제 찾기
        daily_tasks = week_data.get("daily_tasks", [])
        task = next(
            (t for t in daily_tasks if t["day"] == day),
            None
        )
        
        if not task:
            # 해당 날짜 없음 (주말 등)
            return {
                "theme": week_data["theme"],
                "task": "휴식",
                "deliverable": "복습 및 정리",
                "type": "rest",
                "learning_objectives": []
            }
        
        # 주차 테마 추가
        task["theme"] = week_data["theme"]
        return task
    
    async def _generate_textbook_section(
        self,
        daily_task: Dict[str, Any],
        curriculum: Dict[str, Any],
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        교재 섹션 생성 (개념 설명)
        
        실제 LLM으로 풍부한 교재 생성
        """
        try:
            logger.info(f"교재 생성 시작: {daily_task['task']}")
            
            # LLM으로 교재 생성
            from app.services.langchain_hybrid_provider import get_langchain_hybrid_provider
            
            provider = get_langchain_hybrid_provider()
            goal = curriculum["goal"]
            theme = daily_task.get("theme", "")
            task = daily_task.get("task", "")
            objectives = daily_task.get("learning_objectives", [])
            
            # 교재 생성 프롬프트
            textbook_prompt = f"""당신은 {goal} 분야의 전문 교육자입니다.

오늘의 학습 주제: {theme}
학습 과제: {task}
학습 목표:
{chr(10).join([f"- {obj}" for obj in objectives])}

다음 형식으로 상세한 교재를 한국어로 작성하세요:

# {theme}

## 📚 학습 목표
{chr(10).join([f"- {obj}" for obj in objectives])}

## 🎯 핵심 개념
(개념을 초보자도 이해할 수 있게 상세히 설명 - 800-1000자)

## 💻 실습 예제
```language
(실제 동작하는 코드 예제 - 주석 포함)
```

## 🔍 심화 학습
(추가로 알아두면 좋은 내용 - 300-500자)

## ✅ 체크포인트
- [ ] (이해 확인 항목 3-5개)

## 💡 학습 팁
- (효과적인 학습 방법 2-3개)

**중요 규칙:**
1. 반드시 한국어로만 작성
2. {goal} 분야와 100% 관련된 내용만
3. 초보자 눈높이에 맞춘 설명
4. 실제 동작하는 코드 예제 필수
5. 총 2000-3000자 분량
6. Markdown 형식 준수
"""
            
            # LLM 호출
            response = await provider.generate_response(
                prompt=textbook_prompt,
                temperature=0.7,
                max_tokens=3000
            )

            textbook_content = self._extract_response_text(response)
            
            if not textbook_content or len(textbook_content) < 500:
                raise ValueError("생성된 교재가 너무 짧습니다")
            
            logger.info(f"교재 생성 완료: {len(textbook_content)}자")
            
            return {
                "type": "textbook",
                "title": "📖 개념 학습",
                "content": textbook_content,
                "examples": self._extract_code_examples(textbook_content),
                "learning_tips": self._extract_learning_tips(textbook_content),
                "estimated_read_time": max(5, len(textbook_content) // 200)  # 200자/분
            }
            
        except Exception as e:
            logger.error(f"교재 섹션 생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 폴백: 기본 교재
            return {
                "type": "textbook",
                "title": "📖 개념 학습",
                "content": self._generate_fallback_textbook(daily_task, curriculum),
                "examples": [],
                "learning_tips": ["교재를 천천히 읽으며 이해하세요", "예제 코드를 직접 실행해보세요"],
                "estimated_read_time": 10
            }
    
    async def _generate_practice_section(
        self,
        daily_task: Dict[str, Any],
        curriculum: Dict[str, Any],
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        실습 섹션 생성 (코딩 과제)
        
        LLM으로 실습 문제 자동 생성
        """
        try:
            logger.info(f"실습 문제 생성 시작: {daily_task['task']}")
            
            from app.services.langchain_hybrid_provider import get_langchain_hybrid_provider
            
            provider = get_langchain_hybrid_provider()
            goal = curriculum["goal"]
            theme = daily_task.get("theme", "")
            task = daily_task.get("task", "")
            deliverable = daily_task.get("deliverable", "")
            
            # 실습 문제 생성 프롬프트 (JSON 구조화)
            practice_prompt = f"""당신은 {goal} 분야의 실습 문제 출제 전문가입니다.

학습 주제: {theme}
오늘의 과제: {task}
목표 결과물: {deliverable}

아래 JSON 형식으로 실습 문제를 생성하세요:

{{
  "title": "{task}",
  "description": "초보자가 이해할 수 있는 구체적인 문제 설명 (200-300자)",
  "requirements": [
    "구체적인 구현 요구사항 1",
    "구체적인 구현 요구사항 2",
    "구체적인 구현 요구사항 3"
  ],
  "starter_code": "# 기본 구조\\n# TODO: 여기를 구현하세요\\n\\ndef solution():\\n    pass",
  "test_cases": [
    {{
      "input": "예제 입력 데이터",
      "expected_output": "예제 출력 데이터",
      "description": "기본 케이스"
    }}
  ],
  "hints": [
    "문제 해결 힌트 1",
    "문제 해결 힌트 2"
  ],
  "difficulty": "easy",
  "estimated_time_minutes": 30,
  "examples": [
    {{
      "input": "입력 예시",
      "output": "출력 예시",
      "explanation": "설명"
    }}
  ]
}}

**중요 규칙:**
1. 반드시 유효한 JSON 형식으로만 출력
2. {goal} 분야와 직접 관련된 문제만
3. 초보자가 30분 내에 풀 수 있는 난이도
4. 실제 동작하는 코드만
5. 모두 한국어로 작성
6. starter_code는 Python 코드로 작성
7. test_cases는 최소 1개 이상 제공
"""
            
            response = await provider.generate_response(
                prompt=practice_prompt,
                temperature=0.7,
                max_tokens=2000
            )

            practice_content = self._extract_response_text(response)
            
            # JSON 파싱 시도
            practice_data = self._parse_practice_json(practice_content)
            
            if practice_data:
                # JSON 형식으로 파싱 성공
                logger.info(f"실습 문제 생성 완료 (구조화된 데이터)")
                return {
                    "type": "practice",
                    "title": "💻 실습",
                    "available": True,
                    "problem_id": None,
                    "description": practice_data.get("description", practice_content),
                    "requirements": practice_data.get("requirements", []),
                    "starter_code": practice_data.get("starter_code", f"# {task}\n# TODO: 여기에 코드를 작성하세요\n\ndef solution():\n    pass"),
                    "test_cases": practice_data.get("test_cases", []),
                    "difficulty": practice_data.get("difficulty", daily_task.get("difficulty", "easy")),
                    "estimated_time": practice_data.get("estimated_time_minutes", 30),
                    "hints": practice_data.get("hints", []),
                    "examples": practice_data.get("examples", [])
                }
            else:
                # 텍스트 형식 파싱 (폴백)
                starter_code = self._extract_starter_code(practice_content)
                if not starter_code:
                    starter_code = f"# {task}\n# TODO: 여기에 코드를 작성하세요\n\ndef solution():\n    pass"
                
                logger.info(f"실습 문제 생성 완료 (텍스트 파싱)")
                return {
                    "type": "practice",
                    "title": "💻 실습",
                    "available": True,
                    "problem_id": None,
                    "description": practice_content,
                    "starter_code": starter_code,
                    "test_cases": [],
                    "difficulty": daily_task.get("difficulty", "easy"),
                    "estimated_time": 30,
                    "hints": self._extract_hints(practice_content)
                }
            
        except Exception as e:
            logger.error(f"실습 섹션 생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 폴백
            return {
                "type": "practice",
                "title": "💻 실습",
                "available": True,
                "problem_id": None,
                "description": daily_task.get("deliverable", task),
                "starter_code": "# 여기에 코드를 작성하세요\n\n",
                "test_cases": [],
                "difficulty": "medium",
                "estimated_time": 30,
                "hints": ["교재에서 배운 내용을 활용하세요", "천천히 단계별로 구현하세요"]
            }
    
    async def _generate_quiz_section(
        self,
        daily_task: Dict[str, Any],
        curriculum: Dict[str, Any],
        user_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        퀴즈 섹션 생성
        
        LLM으로 퀴즈 자동 생성
        """
        try:
            logger.info(f"퀴즈 생성 시작: {daily_task['task']}")
            
            from app.services.langchain_hybrid_provider import get_langchain_hybrid_provider
            
            provider = get_langchain_hybrid_provider()
            goal = curriculum["goal"]
            theme = daily_task.get("theme", "")
            objectives = daily_task.get("learning_objectives", [])
            
            # 퀴즈 생성 프롬프트 (JSON 구조화)
            quiz_prompt = f"""당신은 {goal} 분야의 평가 전문가입니다.

학습 주제: {theme}
학습 목표:
{chr(10).join([f"- {obj}" for obj in objectives])}

오늘 배운 내용을 바탕으로 객관식 퀴즈 3문제를 아래 JSON 형식으로 생성하세요:

{{
  "questions": [
    {{
      "id": 1,
      "text": "질문 내용을 명확하게 작성",
      "options": [
        "선택지 1",
        "선택지 2",
        "선택지 3",
        "선택지 4"
      ],
      "correct": 1,
      "explanation": "정답인 이유와 오답이 왜 틀렸는지 100-150자로 설명",
      "difficulty": "easy",
      "topic": "{theme}"
    }}
  ]
}}

**중요 규칙:**
1. 반드시 유효한 JSON 형식으로만 출력
2. {goal} 분야의 핵심 개념을 묻는 문제
3. 오늘 학습 목표와 직접 관련된 내용만
4. 초보자가 이해할 수 있는 수준
5. 오답 선택지도 그럴듯하게 작성
6. options는 정확히 4개 제공
7. correct는 0-3 사이의 인덱스 (0=첫번째 선택지)
8. 해설은 100-150자로 명확하게
9. 모두 한국어로 작성
10. 정확히 3문제 생성
"""
            
            response = await provider.generate_response(
                prompt=quiz_prompt,
                temperature=0.7,
                max_tokens=2000
            )

            quiz_content = self._extract_response_text(response)
            
            # JSON 파싱 시도
            quiz_data = self._parse_quiz_json(quiz_content)
            
            if quiz_data and "questions" in quiz_data:
                questions = quiz_data["questions"]
                logger.info(f"퀴즈 생성 완료 (구조화된 데이터): {len(questions)}문제")
            else:
                # 텍스트 형식 파싱 (폴백)
                questions = self._parse_quiz_content(quiz_content)
                logger.info(f"퀴즈 생성 완료 (텍스트 파싱): {len(questions)}문제")
            
            if not questions or len(questions) == 0:
                raise ValueError("퀴즈 생성 실패")
            
            return {
                "type": "quiz",
                "title": "✍️ 퀴즈",
                "available": True,
                "question_count": len(questions),
                "questions": questions,
                "passing_score": 60,
                "estimated_time": len(questions) * 2
            }
            
        except Exception as e:
            logger.error(f"퀴즈 섹션 생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 폴백: 기본 퀴즈
            return {
                "type": "quiz",
                "title": "✍️ 퀴즈",
                "available": True,
                "question_count": 1,
                "questions": [
                    {
                        "id": 1,
                        "text": f"{daily_task.get('theme', '')}에서 가장 중요한 개념은 무엇인가요?",
                        "options": [
                            "기본 개념 이해",
                            "실습을 통한 학습",
                            "꾸준한 복습",
                            "모두 중요함"
                        ],
                        "correct": 3,
                        "explanation": "모든 요소가 함께 어우러질 때 효과적인 학습이 가능합니다."
                    }
                ],
                "passing_score": 60,
                "estimated_time": 2
            }
    
    async def _get_daily_progress(
        self,
        user_id: int,
        curriculum_id: int,
        day_info: Dict[str, int],
        db: Session
    ) -> Dict[str, Any]:
        """
        일일 진도 상태 조회
        
        AITeachingSession을 활용하여 오늘의 학습 상태 확인
        """
        try:
            from datetime import datetime, timedelta
            from app.models.orm import QuizSession, QuizAnswer
            from app.models.code_problem import CodeSubmission
            
            # 오늘 날짜 범위
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            # 1. 퀴즈 완료 여부 확인
            quiz_completed = db.query(QuizSession).filter(
                QuizSession.user_id == user_id,
                QuizSession.completed_at >= today_start,
                QuizSession.completed_at < today_end,
                QuizSession.answered_questions > 0
            ).first() is not None
            
            # 2. 실습 제출 여부 확인
            practice_submitted = db.query(CodeSubmission).filter(
                CodeSubmission.user_id == user_id,
                CodeSubmission.submitted_at >= today_start,
                CodeSubmission.submitted_at < today_end
            ).first() is not None
            
            # 3. 교재 읽음 여부 (AITeachingSession의 last_activity_at 확인)
            teaching_session = db.query(AITeachingSession).filter(
                AITeachingSession.user_id == user_id,
                AITeachingSession.curriculum_id == curriculum_id,
                AITeachingSession.last_activity_at >= today_start
            ).first()
            
            textbook_read = teaching_session is not None
            
            # 4. 완료율 계산
            completed_count = sum([textbook_read, practice_submitted, quiz_completed])
            completion_percentage = int((completed_count / 3) * 100)
            
            # 5. 전체 상태 결정
            if completion_percentage == 0:
                overall_status = "not_started"
            elif completion_percentage == 100:
                overall_status = "completed"
            else:
                overall_status = "in_progress"
            
            return {
                "textbook_read": textbook_read,
                "practice_submitted": practice_submitted,
                "quiz_completed": quiz_completed,
                "completion_percentage": completion_percentage,
                "overall_status": overall_status
            }
            
        except Exception as e:
            logger.error(f"진도 조회 실패: {str(e)}")
            # 에러 시 기본값 반환
            return {
                "textbook_read": False,
                "practice_submitted": False,
                "quiz_completed": False,
                "completion_percentage": 0,
                "overall_status": "not_started"
            }
    
    def _parse_practice_json(self, content: str) -> Optional[Dict[str, Any]]:
        """실습 문제 JSON 파싱"""
        try:
            # JSON 추출 시도
            content = content.strip()
            
            # JSON이 코드 블록 안에 있을 수 있음
            if '```json' in content or '```' in content:
                import re
                json_match = re.search(r'```(?:json)?\s*\n(.*?)```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1).strip()
            
            # JSON 파싱
            if content.startswith('{'):
                parsed = json.loads(content)
                
                # 필수 필드 검증
                if isinstance(parsed, dict) and "description" in parsed:
                    return parsed
            
            return None
            
        except json.JSONDecodeError as e:
            logger.debug(f"실습 JSON 파싱 실패: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"실습 JSON 파싱 오류: {str(e)}")
            return None
    
    def _parse_quiz_json(self, content: str) -> Optional[Dict[str, Any]]:
        """퀴즈 JSON 파싱"""
        try:
            # JSON 추출 시도
            content = content.strip()
            
            # JSON이 코드 블록 안에 있을 수 있음
            if '```json' in content or '```' in content:
                import re
                json_match = re.search(r'```(?:json)?\s*\n(.*?)```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1).strip()
            
            # JSON 파싱
            if content.startswith('{'):
                parsed = json.loads(content)
                
                # 필수 필드 검증
                if isinstance(parsed, dict) and "questions" in parsed:
                    questions = parsed["questions"]
                    
                    # 각 문제 검증 및 정규화
                    normalized_questions = []
                    for q in questions:
                        if not isinstance(q, dict):
                            continue
                        
                        # 필수 필드 확인
                        if "text" not in q or "options" not in q or "correct" not in q:
                            continue
                        
                        # options가 4개인지 확인
                        if not isinstance(q["options"], list) or len(q["options"]) < 2:
                            continue
                        
                        normalized_questions.append({
                            "id": q.get("id", len(normalized_questions) + 1),
                            "text": q["text"],
                            "options": q["options"],
                            "correct": q["correct"],
                            "explanation": q.get("explanation", ""),
                            "difficulty": q.get("difficulty", "easy"),
                            "topic": q.get("topic", "")
                        })
                    
                    if normalized_questions:
                        return {"questions": normalized_questions}
            
            return None
            
        except json.JSONDecodeError as e:
            logger.debug(f"퀴즈 JSON 파싱 실패: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"퀴즈 JSON 파싱 오류: {str(e)}")
            return None
    
    def _extract_code_examples(self, content: str) -> List[Dict[str, str]]:
        """텍스트에서 코드 예제 추출"""
        # 간단한 마크다운 코드 블록 파싱
        import re
        
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        return [
            {
                "language": lang or "python",
                "code": code.strip()
            }
            for lang, code in code_blocks
        ]
    
    def _extract_learning_tips(self, content: str) -> List[str]:
        """교재에서 학습 팁 추출"""
        import re
        
        # "💡 학습 팁" 섹션 찾기
        tips_section = re.search(r'##\s*💡\s*학습 팁\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        
        if not tips_section:
            return ["천천히 읽으며 이해하세요", "예제 코드를 직접 실행해보세요"]
        
        tips_text = tips_section.group(1)
        # - 로 시작하는 항목 추출
        tips = re.findall(r'^-\s*(.+)$', tips_text, re.MULTILINE)
        
        return tips if tips else ["천천히 읽으며 이해하세요"]
    
    def _extract_starter_code(self, content: str) -> str:
        """실습 문제에서 시작 코드 추출"""
        import re
        
        # "## 시작 코드" 섹션 찾기
        starter_section = re.search(r'##\s*시작 코드\s*\n```\w*\n(.*?)```', content, re.DOTALL)
        
        if starter_section:
            return starter_section.group(1).strip()
        
        # 첫 번째 코드 블록 사용
        first_code = re.search(r'```\w*\n(.*?)```', content, re.DOTALL)
        if first_code:
            return first_code.group(1).strip()
        
        return ""
    
    def _extract_hints(self, content: str) -> List[str]:
        """실습 문제에서 힌트 추출"""
        import re
        
        # "## 힌트" 섹션 찾기
        hints_section = re.search(r'##\s*힌트\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        
        if not hints_section:
            return ["교재에서 배운 내용을 활용하세요", "천천히 단계별로 구현하세요"]
        
        hints_text = hints_section.group(1)
        # - 로 시작하는 항목 추출
        hints = re.findall(r'^-\s*(.+)$', hints_text, re.MULTILINE)
        
        return hints if hints else ["교재에서 배운 내용을 활용하세요"]
    
    def _parse_quiz_content(self, content: str) -> List[Dict[str, Any]]:
        """LLM이 생성한 퀴즈 텍스트를 파싱"""
        import re
        
        questions = []
        
        # "**문제 N:**" 패턴으로 문제 분리
        problem_pattern = r'\*\*문제\s+(\d+):\*\*\s*(.*?)(?=\*\*문제\s+\d+:|\Z)'
        matches = re.findall(problem_pattern, content, re.DOTALL)
        
        for idx, (num, problem_text) in enumerate(matches, 1):
            try:
                # 질문 텍스트 추출 (첫 줄)
                lines = problem_text.strip().split('\n')
                question_text = lines[0].strip()
                
                # 선택지 추출 (A), B), C), D))
                options = []
                for line in lines[1:]:
                    option_match = re.match(r'^[A-D]\)\s*(.+)$', line.strip())
                    if option_match:
                        options.append(option_match.group(1))
                
                if len(options) < 2:
                    continue
                
                # 정답 추출
                answer_match = re.search(r'\*\*정답:\*\*\s*([A-D])', problem_text)
                correct_index = 0
                if answer_match:
                    correct_letter = answer_match.group(1)
                    correct_index = ord(correct_letter) - ord('A')
                
                # 해설 추출
                explanation_match = re.search(r'\*\*해설:\*\*\s*(.+?)(?=\n\n|\Z)', problem_text, re.DOTALL)
                explanation = explanation_match.group(1).strip() if explanation_match else ""
                
                questions.append({
                    "id": idx,
                    "text": question_text,
                    "options": options,
                    "correct": correct_index,
                    "explanation": explanation
                })
                
            except Exception as e:
                logger.error(f"퀴즈 문제 파싱 실패 #{idx}: {str(e)}")
                continue
        
        return questions
    
    def _generate_fallback_textbook(self, daily_task: Dict[str, Any], curriculum: Dict[str, Any]) -> str:
        """폴백 교재 생성"""
        theme = daily_task.get("theme", "")
        task = daily_task.get("task", "")
        objectives = daily_task.get("learning_objectives", [])
        
        content = f"""# {theme}

## 📚 학습 목표
{chr(10).join([f"- {obj}" for obj in objectives])}

## 🎯 핵심 개념

오늘은 **{theme}**에 대해 학습합니다.

{task}

## 💻 실습 예제

아래 예제를 통해 개념을 이해해보세요:

```python
# 예제 코드
def example():
    print("Hello, World!")
```

## 💡 학습 팁

- 교재를 천천히 읽으며 이해하세요
- 예제 코드를 직접 실행해보세요
- 이해가 안 되는 부분은 AI 멘토에게 질문하세요

## ✅ 체크포인트

- [ ] 핵심 개념을 이해했나요?
- [ ] 예제 코드를 실행해봤나요?
- [ ] 실습 문제를 풀 준비가 되었나요?
"""
        return content
    
    async def submit_practice(
        self,
        user_id: int,
        curriculum_id: int,
        problem_id: Optional[int],
        code: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        실습 코드 제출 및 실행
        
        Returns:
            {
                "success": True/False,
                "output": "...",
                "test_results": [...],
                "feedback": "..."
            }
        """
        try:
            # 코드 실행
            if problem_id:
                # 문제의 테스트 케이스로 실행
                problem = db.query(CodeProblem).filter(
                    CodeProblem.id == problem_id
                ).first()
                
                if problem:
                    test_cases = [
                        TestCase(
                            input_data=tc.input_data,
                            expected_output=tc.expected_output,
                            description=tc.description
                        )
                        for tc in problem.test_cases
                    ]
                    
                    result = await self.code_executor.execute_python_code(
                        code, test_cases
                    )
                else:
                    result = await self.code_executor.execute_python_code(code)
            else:
                # 자유 실행
                result = await self.code_executor.execute_python_code(code)
            
            # 제출 기록 저장
            submission = CodeSubmission(
                user_id=user_id,
                problem_id=problem_id or 0,  # None인 경우 0으로 설정
                code=code,
                language="python",
                status="accepted" if result.success else "wrong_answer",
                execution_time_ms=result.execution_time_ms if hasattr(result, 'execution_time_ms') else None,
                passed_tests=len([t for t in (result.test_results or []) if t.get('passed', False)]),
                total_tests=len(result.test_results or []),
                test_results=result.test_results,
                judged_at=datetime.utcnow()
            )
            db.add(submission)
            db.commit()
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "test_results": result.test_results,
                "execution_time_ms": result.execution_time_ms,
                "feedback": "✅ 정답입니다!" if result.success else "❌ 다시 시도해보세요."
            }
            
        except Exception as e:
            logger.error(f"실습 제출 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "feedback": "코드 실행 중 오류가 발생했습니다."
            }
    
    async def submit_quiz_answer(
        self,
        user_id: int,
        curriculum_id: int,
        question_id: int,
        answer: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        퀴즈 답변 제출 및 DB 저장
        
        Returns:
            {
                "correct": True/False,
                "explanation": "...",
                "score": 10,
                "session_id": 123
            }
        """
        try:
            from app.models.orm import QuizSession, QuizAnswer
            from datetime import datetime, timedelta
            
            # 1. 오늘의 학습 세션 찾기 또는 생성
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            quiz_session = db.query(QuizSession).filter(
                QuizSession.user_id == user_id,
                QuizSession.completed_at >= today_start,
                QuizSession.completed_at < today_end
            ).order_by(QuizSession.completed_at.desc()).first()
            
            # 세션이 없으면 새로 생성
            if not quiz_session:
                quiz_session = QuizSession(
                    user_id=user_id,
                    session_type=f"curriculum_{curriculum_id}",
                    total_questions=0,
                    answered_questions=0,
                    skipped_questions=0,
                    total_score=0.0,
                    time_taken=0,
                    completed_at=datetime.utcnow()
                )
                db.add(quiz_session)
                db.flush()  # ID 생성
            
            # 2. Question 조회 및 LLM 기반 정답 확인
            from app.models.orm import Question
            
            question = db.query(Question).filter(Question.id == question_id).first()
            
            if not question:
                return {
                    "success": False,
                    "error": "문제를 찾을 수 없습니다.",
                    "correct": False,
                    "score": 0.0
                }
            
            # LLM을 사용한 유연한 정답 검증
            is_correct, explanation = await self._verify_answer_with_llm(
                question=question,
                user_answer=answer
            )
            
            score = 10.0 if is_correct else 0.0
            
            # 3. QuizAnswer 레코드 저장
            quiz_answer = QuizAnswer(
                session_id=quiz_session.id,
                question_id=question_id,
                user_answer=answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                is_skipped=False,
                score=score,
                answered_at=datetime.utcnow()
            )
            db.add(quiz_answer)
            
            # 4. 세션 통계 업데이트
            quiz_session.total_questions += 1
            quiz_session.answered_questions += 1
            quiz_session.total_score += score
            
            db.commit()
            
            logger.info(f"퀴즈 답변 저장 완료: user={user_id}, question={question_id}, correct={is_correct}")
            
            return {
                "correct": is_correct,
                "explanation": explanation,
                "score": score,
                "session_id": quiz_session.id,
                "total_score": quiz_session.total_score,
                "answered_count": quiz_session.answered_questions
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"퀴즈 답변 저장 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 저장 실패 시에도 사용자에게 피드백은 제공
            return {
                "correct": True,
                "explanation": "답변이 제출되었습니다.",
                "score": 0,
                "error": "저장 중 오류가 발생했습니다."
            }

    async def track_textbook_reading(
        self,
        user_id: int,
        curriculum_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        교재 읽기 추적
        
        사용자가 교재 탭을 열었을 때 호출되어 진도에 반영됩니다.
        AITeachingSession의 last_activity_at을 업데이트하여 
        _get_daily_progress에서 textbook_read 플래그가 True가 되도록 합니다.
        
        Returns:
            {
                "success": True,
                "message": "교재 읽기가 기록되었습니다.",
                "last_activity_at": "2025-10-22T10:30:00"
            }
        """
        try:
            from app.models.ai_curriculum import AITeachingSession
            from datetime import datetime
            
            # 1. 현재 커리큘럼의 AITeachingSession 찾기
            teaching_session = db.query(AITeachingSession).filter(
                AITeachingSession.user_id == user_id,
                AITeachingSession.curriculum_id == curriculum_id
            ).first()
            
            # 2. 세션이 없으면 새로 생성
            if not teaching_session:
                teaching_session = AITeachingSession(
                    user_id=user_id,
                    curriculum_id=curriculum_id,
                    current_week=1,
                    current_day=1,
                    completion_percentage=0,
                    started_at=datetime.utcnow(),
                    last_activity_at=datetime.utcnow()
                )
                db.add(teaching_session)
                logger.info(f"새로운 AITeachingSession 생성: user={user_id}, curriculum={curriculum_id}")
            else:
                # 3. 기존 세션의 last_activity_at 업데이트
                teaching_session.last_activity_at = datetime.utcnow()
                logger.info(f"AITeachingSession last_activity_at 업데이트: user={user_id}, curriculum={curriculum_id}")
            
            db.commit()
            
            return {
                "success": True,
                "message": "교재 읽기가 기록되었습니다.",
                "last_activity_at": teaching_session.last_activity_at.isoformat(),
                "teaching_session_id": teaching_session.id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"교재 읽기 추적 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "message": "교재 읽기 추적에 실패했습니다."
            }
    
    async def _verify_answer_with_llm(
        self,
        question: Any,
        user_answer: str
    ) -> tuple[bool, str]:
        """
        LLM을 사용하여 사용자 답변을 유연하게 검증
        
        Args:
            question: Question 모델 객체
            user_answer: 사용자가 제출한 답변
            
        Returns:
            (is_correct, explanation) 튜플
        """
        try:
            from app.services.langchain_hybrid_provider import LangChainHybridProvider
            
            # 문제 유형별 검증 프롬프트
            question_type = question.question_type.lower()
            
            # 객관식 (Multiple Choice)
            if "multiple" in question_type or "choice" in question_type:
                # 객관식은 정확한 매칭
                user_answer_clean = str(user_answer).strip().upper()
                correct_answer_clean = str(question.correct_answer).strip().upper()
                
                is_correct = user_answer_clean == correct_answer_clean
                
                if is_correct:
                    explanation = f"정답입니다! {question.explanation or '잘 이해하셨네요.'}"
                else:
                    explanation = f"정답은 '{question.correct_answer}'입니다. {question.explanation or '다시 한번 복습해보세요.'}"
                
                return is_correct, explanation
            
            # 주관식 (Short Answer, Essay 등) - LLM 평가
            else:
                provider = LangChainHybridProvider()
                llm = provider.get_llm()
                
                verification_prompt = f"""당신은 공정하고 정확한 채점 전문가입니다.

학생의 답변이 정답과 의미상 일치하는지 평가해주세요.

**문제:**
{question.code_snippet}

**정답:**
{question.correct_answer}

**학생 답변:**
{user_answer}

**평가 기준:**
1. 핵심 개념이 정확히 포함되어 있는가?
2. 의미상 정답과 동일한가? (표현이 다르더라도 의미가 같으면 정답)
3. 오타나 사소한 표현 차이는 무시
4. 완전히 틀린 개념이나 반대 의미는 오답

**응답 형식 (반드시 이 형식을 따라주세요):**
정답여부: [정답/오답]
설명: [학생에게 피드백할 한글 설명 2-3문장]

예시:
정답여부: 정답
설명: 완벽합니다! 핵심 개념을 정확히 이해하고 계시네요.

또는:
정답여부: 오답
설명: 아쉽게도 핵심 개념이 빠졌습니다. [정답]은 [설명]을 의미합니다."""

                response = await llm.ainvoke(verification_prompt)
                response_text = self._extract_response_text(response)
                
                # 응답 파싱
                is_correct = "정답여부: 정답" in response_text or "정답여부:정답" in response_text
                
                # 설명 추출
                if "설명:" in response_text:
                    explanation = response_text.split("설명:")[-1].strip()
                else:
                    explanation = response_text
                
                # 설명이 너무 길면 자르기
                if len(explanation) > 300:
                    explanation = explanation[:300] + "..."
                
                return is_correct, explanation
                
        except Exception as e:
            logger.error(f"LLM 답변 검증 실패: {str(e)}")
            # 폴백: 단순 문자열 비교
            user_clean = str(user_answer).strip().lower()
            correct_clean = str(question.correct_answer).strip().lower()
            
            is_correct = user_clean == correct_clean
            explanation = "정답입니다!" if is_correct else f"정답은 '{question.correct_answer}'입니다."
            
            return is_correct, explanation


# 싱글톤 인스턴스
_daily_learning_service = None

def get_daily_learning_service() -> DailyLearningService:
    """의존성 주입용 서비스 인스턴스"""
    global _daily_learning_service
    if _daily_learning_service is None:
        _daily_learning_service = DailyLearningService()
    return _daily_learning_service
