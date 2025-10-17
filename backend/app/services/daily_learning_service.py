"""
MVP Week 1: 일일 학습 서비스
오늘의 학습 콘텐츠 제공 (교과서 + 실습 + 퀴즈)

기존 서비스 통합:
- SyllabusBasedTeachingAgent (교과서/개념 설명)
- CodeExecutionService (실습/코드 실행)
- AIQuestionGeneratorEnhanced (퀴즈 생성)
"""

import logging
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
            logger.info(f"오늘의 학습 조회: user_id={user_id}, curriculum_id={curriculum_id}")
            
            # 1. 커리큘럼 조회
            curriculum = await self._get_curriculum(curriculum_id, user_id, db)
            if not curriculum:
                raise ValueError("커리큘럼을 찾을 수 없습니다")
            
            # 2. 학습 시작일 기준 현재 학습 날짜 계산
            current_day_info = self._calculate_current_day(
                curriculum, target_date
            )
            
            # 3. 해당 날짜의 학습 콘텐츠 가져오기
            daily_task = self._get_daily_task_from_curriculum(
                curriculum, current_day_info["week"], current_day_info["day"]
            )
            
            # 4. 3가지 섹션 생성
            textbook_section = await self._generate_textbook_section(
                daily_task, curriculum, user_id, db
            )
            
            practice_section = await self._generate_practice_section(
                daily_task, curriculum, user_id, db
            )
            
            quiz_section = await self._generate_quiz_section(
                daily_task, curriculum, user_id, db
            )
            
            # 5. 진도 상태 조회
            progress = await self._get_daily_progress(
                user_id, curriculum_id, current_day_info, db
            )
            
            # 6. 결과 조합
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
                "sections": {
                    "textbook": textbook_section,
                    "practice": practice_section,
                    "quiz": quiz_section
                },
                "progress": progress
            }
            
            logger.info(f"오늘의 학습 생성 완료: Week {current_day_info['week']} Day {current_day_info['day']}")
            return today_learning
            
        except Exception as e:
            logger.error(f"오늘의 학습 조회 실패: {str(e)}")
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
        
        return {
            "id": curriculum.id,
            "goal": curriculum.generated_syllabus.get("goal"),
            "syllabus": curriculum.generated_syllabus,
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
        교과서 섹션 생성 (개념 설명)
        
        SyllabusBasedTeachingAgent 활용
        """
        try:
            # 교육 세션 시작 또는 재개
            session, initial_message = await self.teaching_agent.start_teaching_session(
                curriculum_id=curriculum["id"],
                user_id=user_id,
                db=db
            )
            
            # 오늘의 학습 주제로 메시지 전송
            topic_message = f"{daily_task['task']}에 대해 설명해주세요. 초보자도 이해할 수 있게 예제와 함께 설명해주세요."
            
            response = await self.teaching_agent.send_message(
                session_id=session.id,
                user_message=topic_message,
                db=db
            )
            
            return {
                "type": "textbook",
                "title": "📖 개념 학습",
                "content": response.message,
                "examples": self._extract_code_examples(response.message),
                "learning_tips": response.learning_tips or [],
                "estimated_read_time": 10  # 분
            }
            
        except Exception as e:
            logger.error(f"교과서 섹션 생성 실패: {str(e)}")
            # 폴백: 간단한 설명
            return {
                "type": "textbook",
                "title": "📖 개념 학습",
                "content": f"{daily_task['task']}\n\n학습 목표:\n" + \
                          "\n".join([f"- {obj}" for obj in daily_task.get("learning_objectives", [])]),
                "examples": [],
                "learning_tips": [],
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
        
        CodeProblem 조회 또는 생성
        """
        try:
            # 해당 주제의 코딩 문제 조회
            task_type = daily_task.get("type", "concept")
            
            if task_type not in ["practice", "project"]:
                # 실습이 아닌 경우
                return {
                    "type": "practice",
                    "title": "💻 실습",
                    "available": False,
                    "message": "오늘은 개념 학습에 집중하세요. 실습은 다음 날 진행됩니다."
                }
            
            # 기존 문제 조회 (태그 기반)
            problem = db.query(CodeProblem).filter(
                CodeProblem.title.contains(daily_task["theme"])
            ).first()
            
            if not problem:
                # 폴백: 기본 실습 과제
                return {
                    "type": "practice",
                    "title": "💻 실습",
                    "available": True,
                    "problem_id": None,
                    "description": daily_task["deliverable"],
                    "starter_code": "# 여기에 코드를 작성하세요\n\ndef solution():\n    pass",
                    "test_cases": [],
                    "difficulty": daily_task.get("difficulty", "medium"),
                    "estimated_time": 30  # 분
                }
            
            return {
                "type": "practice",
                "title": "💻 실습",
                "available": True,
                "problem_id": problem.id,
                "description": problem.description,
                "starter_code": problem.starter_code,
                "test_cases": [
                    {
                        "input": tc.input_data,
                        "expected": tc.expected_output,
                        "description": tc.description
                    }
                    for tc in problem.test_cases
                ],
                "difficulty": problem.difficulty,
                "estimated_time": 30
            }
            
        except Exception as e:
            logger.error(f"실습 섹션 생성 실패: {str(e)}")
            return {
                "type": "practice",
                "title": "💻 실습",
                "available": False,
                "message": "실습 과제를 불러올 수 없습니다."
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
        
        AIQuestionGeneratorEnhanced 활용
        """
        try:
            task_type = daily_task.get("type", "concept")
            
            if task_type != "quiz":
                # 퀴즈 날이 아닌 경우
                return {
                    "type": "quiz",
                    "title": "✍️ 퀴즈",
                    "available": False,
                    "message": "Day 5에 주간 퀴즈를 진행합니다."
                }
            
            # 문제 생성 요청
            request = QuestionGenerationRequest(
                user_id=user_id,
                subject_key=curriculum["syllabus"].get("core_technologies", ["Python"])[0],
                topic=daily_task["theme"],
                question_type=QuestionType.MULTIPLE_CHOICE,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                count=3  # MVP는 3문제
            )
            
            questions = await self.question_generator.generate_questions(request, db)
            
            return {
                "type": "quiz",
                "title": "✍️ 퀴즈",
                "available": True,
                "question_count": len(questions),
                "questions": [
                    {
                        "id": i,
                        "text": q.question_text,
                        "options": q.options,
                        "type": q.question_type.value,
                        "estimated_time": q.estimated_time or 2  # 분
                    }
                    for i, q in enumerate(questions, 1)
                ],
                "passing_score": 60,  # 60% 이상
                "estimated_time": sum(q.estimated_time or 2 for q in questions)
            }
            
        except Exception as e:
            logger.error(f"퀴즈 섹션 생성 실패: {str(e)}")
            return {
                "type": "quiz",
                "title": "✍️ 퀴즈",
                "available": False,
                "message": "퀴즈를 불러올 수 없습니다."
            }
    
    async def _get_daily_progress(
        self,
        user_id: int,
        curriculum_id: int,
        day_info: Dict[str, int],
        db: Session
    ) -> Dict[str, Any]:
        """일일 진도 상태 조회"""
        # TODO: 실제 진도 추적 테이블에서 조회
        # 지금은 Mock 데이터
        
        return {
            "textbook_read": False,
            "practice_submitted": False,
            "quiz_completed": False,
            "completion_percentage": 0,
            "overall_status": "not_started"  # not_started, in_progress, completed
        }
    
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
                problem_id=problem_id,
                code=code,
                status="passed" if result.success else "failed",
                output=result.output,
                error_message=result.error,
                execution_time_ms=result.execution_time_ms
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
        퀴즈 답변 제출
        
        Returns:
            {
                "correct": True/False,
                "explanation": "...",
                "score": 10
            }
        """
        # TODO: 실제 답변 검증 및 저장
        # 지금은 Mock
        
        return {
            "correct": True,
            "explanation": "정답입니다! 잘 이해하셨네요.",
            "score": 10
        }


# 싱글톤 인스턴스
_daily_learning_service = None

def get_daily_learning_service() -> DailyLearningService:
    """의존성 주입용 서비스 인스턴스"""
    global _daily_learning_service
    if _daily_learning_service is None:
        _daily_learning_service = DailyLearningService()
    return _daily_learning_service
