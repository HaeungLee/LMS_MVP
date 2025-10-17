"""
MVP Week 1: 목표 기반 커리큘럼 서비스
기존 LangChainTwoAgentCurriculumGenerator를 활용하여
사용자 목표에 최적화된 학습 로드맵 생성
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.langchain_curriculum_generator import LangChainTwoAgentCurriculumGenerator
from app.models.ai_curriculum import AIGeneratedCurriculum
from app.models.orm import User

logger = logging.getLogger(__name__)


class GoalBasedCurriculumService:
    """
    목표 기반 커리큘럼 생성 서비스 (MVP 래퍼)
    
    기존 시스템 활용:
    - LangChainTwoAgentCurriculumGenerator (2-Agent 협력)
    - AIGeneratedCurriculum 모델 (DB 저장)
    
    MVP 특화:
    - 명확한 취업/이직 목표 중심
    - 주차별 테마 + 일일 과제 구조
    - 구체적 결과물(Deliverable) 명시
    """
    
    def __init__(self):
        self.generator = LangChainTwoAgentCurriculumGenerator()
        
        # MVP 목표 템플릿 (확장 가능하도록 설계)
        self.goal_templates = {
            "backend_developer": {
                "display_name": "백엔드 개발자 (FastAPI)",
                "description": "Python FastAPI로 REST API를 설계하고 배포할 수 있는 백엔드 개발자",
                "default_weeks": 12,
                "core_technologies": ["FastAPI", "PostgreSQL", "Docker", "REST API", "Authentication"],
                "learning_path": [
                    "FastAPI 기초 & 라우팅",
                    "데이터베이스 설계 & SQLAlchemy",
                    "인증 & 보안",
                    "비동기 처리",
                    "테스트 자동화",
                    "배포 & 운영"
                ]
            },
            "data_analyst": {
                "display_name": "데이터 분석가 (Pandas)",
                "description": "Python으로 데이터를 분석하고 시각화할 수 있는 데이터 분석가",
                "default_weeks": 10,
                "core_technologies": ["Pandas", "NumPy", "Matplotlib", "SQL", "Jupyter"],
                "learning_path": [
                    "Pandas 기초",
                    "데이터 전처리",
                    "탐색적 데이터 분석",
                    "SQL 쿼리",
                    "시각화",
                    "실전 프로젝트"
                ]
            },
            "automation_engineer": {
                "display_name": "자동화 엔지니어",
                "description": "Python으로 업무를 자동화하고 효율을 높이는 엔지니어",
                "default_weeks": 8,
                "core_technologies": ["Selenium", "Beautiful Soup", "Schedule", "API", "Excel"],
                "learning_path": [
                    "웹 스크래핑 기초",
                    "API 활용",
                    "Excel 자동화",
                    "스케줄링",
                    "실전 자동화"
                ]
            }
        }
    
    async def generate_goal_based_curriculum(
        self,
        user_id: int,
        goal_key: str,  # "backend_developer", "data_analyst", etc.
        current_level: str = "Python 기초 완료",
        target_weeks: Optional[int] = None,
        daily_study_minutes: int = 60,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        목표 기반 커리큘럼 생성 (MVP 핵심 기능)
        
        Args:
            user_id: 사용자 ID
            goal_key: 목표 키 (goal_templates에 정의된 것)
            current_level: 현재 수준 (예: "Python 기초 완료")
            target_weeks: 목표 주차 (None이면 기본값 사용)
            daily_study_minutes: 일일 학습 시간 (분)
            db: 데이터베이스 세션
            
        Returns:
            {
                "curriculum_id": 123,
                "goal": "백엔드 개발자 (FastAPI)",
                "total_weeks": 12,
                "daily_minutes": 60,
                "weekly_themes": [
                    {
                        "week": 1,
                        "theme": "FastAPI 기초 & 라우팅",
                        "description": "...",
                        "daily_tasks": [
                            {
                                "day": 1,
                                "task": "FastAPI 설치 및 첫 API 만들기",
                                "deliverable": "Hello World API 배포",
                                "learning_objectives": ["FastAPI 설치", "기본 라우팅"],
                                "study_time_minutes": 60
                            },
                            // ... 6일치
                        ]
                    },
                    // ... 11주치
                ]
            }
        """
        try:
            logger.info(f"목표 기반 커리큘럼 생성 시작: user_id={user_id}, goal={goal_key}")
            
            # 1. 목표 템플릿 가져오기
            if goal_key not in self.goal_templates:
                raise ValueError(f"지원하지 않는 목표: {goal_key}")
            
            goal_template = self.goal_templates[goal_key]
            weeks = target_weeks or goal_template["default_weeks"]
            
            # 2. 학습 목표 구성
            learning_goals = self._build_learning_goals(
                goal_template, current_level, daily_study_minutes
            )
            
            # 3. 기존 LangChain 생성기 호출 (2-Agent 협력)
            base_curriculum = await self.generator.generate_curriculum(
                topic=goal_template["display_name"],
                difficulty_level="intermediate",  # MVP는 중급 수준 가정
                duration_weeks=weeks,
                learning_goals=learning_goals,
                subject_context={
                    "goal_key": goal_key,
                    "technologies": goal_template["core_technologies"],
                    "learning_path": goal_template["learning_path"]
                }
            )
            
            # 4. MVP 형식으로 변환 (주차별 → 일일 과제)
            mvp_curriculum = self._transform_to_daily_tasks(
                base_curriculum,
                goal_template,
                weeks,
                daily_study_minutes
            )
            
            # 5. 데이터베이스 저장
            if db:
                curriculum_record = await self._save_to_database(
                    db, user_id, goal_key, mvp_curriculum, base_curriculum
                )
                mvp_curriculum["curriculum_id"] = curriculum_record.id
            
            logger.info(f"목표 기반 커리큘럼 생성 완료: curriculum_id={mvp_curriculum.get('curriculum_id')}")
            return mvp_curriculum
            
        except Exception as e:
            logger.error(f"목표 기반 커리큘럼 생성 실패: {str(e)}")
            raise
    
    def _build_learning_goals(
        self,
        goal_template: Dict[str, Any],
        current_level: str,
        daily_minutes: int
    ) -> List[str]:
        """학습 목표 구성"""
        goals = [
            f"목표: {goal_template['description']}",
            f"현재 수준: {current_level}",
            f"일일 학습 시간: {daily_minutes}분",
        ]
        
        # 핵심 기술 학습 목표 추가
        goals.append("핵심 기술:")
        for tech in goal_template["core_technologies"]:
            goals.append(f"  - {tech} 실무 활용 가능 수준")
        
        # 최종 결과물 명시
        goals.append("최종 결과물: 포트폴리오에 넣을 수 있는 실전 프로젝트 1개")
        
        return goals
    
    def _transform_to_daily_tasks(
        self,
        base_curriculum: Dict[str, Any],
        goal_template: Dict[str, Any],
        weeks: int,
        daily_minutes: int
    ) -> Dict[str, Any]:
        """
        기존 커리큘럼을 MVP 일일 과제 형식으로 변환
        
        기존 구조: weekly_content = [{"week": 1, "topics": [...]}]
        MVP 구조: weekly_themes = [{"week": 1, "theme": "...", "daily_tasks": [...]}]
        """
        mvp_curriculum = {
            "goal": goal_template["display_name"],
            "description": goal_template["description"],
            "total_weeks": weeks,
            "daily_minutes": daily_minutes,
            "core_technologies": goal_template["core_technologies"],
            "weekly_themes": []
        }
        
        # 기존 커리큘럼에서 주차별 콘텐츠 추출
        weekly_content = base_curriculum.get("weekly_content", [])
        learning_path = goal_template["learning_path"]
        
        for week_idx in range(weeks):
            week_num = week_idx + 1
            
            # 주차 테마 (learning_path에서 순환)
            theme = learning_path[week_idx % len(learning_path)]
            
            # 해당 주차의 토픽들 가져오기
            week_data = next(
                (w for w in weekly_content if w.get("week") == week_num),
                {"topics": []}
            )
            
            # 일일 과제 생성 (주 5일, 주말 제외)
            daily_tasks = self._generate_daily_tasks(
                week_num, theme, week_data, daily_minutes
            )
            
            mvp_curriculum["weekly_themes"].append({
                "week": week_num,
                "theme": theme,
                "description": week_data.get("description", f"{theme}을 학습합니다"),
                "daily_tasks": daily_tasks
            })
        
        return mvp_curriculum
    
    def _generate_daily_tasks(
        self,
        week_num: int,
        theme: str,
        week_data: Dict[str, Any],
        daily_minutes: int
    ) -> List[Dict[str, Any]]:
        """
        일일 과제 생성 (주 5일)
        
        구조:
        - Day 1-2: 개념 학습 (교과서)
        - Day 3-4: 실습 (코딩)
        - Day 5: 퀴즈 & 복습
        """
        topics = week_data.get("topics", [])
        daily_tasks = []
        
        # 5일치 과제 템플릿
        task_templates = [
            {
                "day": 1,
                "type": "concept",
                "task_prefix": "개념 학습:",
                "deliverable_prefix": "이해하기:"
            },
            {
                "day": 2,
                "type": "concept",
                "task_prefix": "심화 학습:",
                "deliverable_prefix": "예제 따라하기:"
            },
            {
                "day": 3,
                "type": "practice",
                "task_prefix": "실습:",
                "deliverable_prefix": "구현하기:"
            },
            {
                "day": 4,
                "type": "practice",
                "task_prefix": "프로젝트:",
                "deliverable_prefix": "완성하기:"
            },
            {
                "day": 5,
                "type": "quiz",
                "task_prefix": "복습:",
                "deliverable_prefix": "문제 풀기:"
            }
        ]
        
        for template in task_templates:
            day = template["day"]
            
            # 토픽에서 해당 날짜에 맞는 내용 추출
            topic_idx = (day - 1) % max(len(topics), 1)
            topic = topics[topic_idx] if topics else {"name": theme, "description": ""}
            
            task = {
                "day": day,
                "date_offset": (week_num - 1) * 7 + day,  # 전체 일정에서의 날짜
                "type": template["type"],
                "task": f"{template['task_prefix']} {topic.get('name', theme)}",
                "deliverable": self._generate_deliverable(
                    template["deliverable_prefix"], 
                    topic, 
                    template["type"]
                ),
                "learning_objectives": self._extract_learning_objectives(topic),
                "study_time_minutes": daily_minutes,
                "resources": topic.get("resources", [])
            }
            
            daily_tasks.append(task)
        
        return daily_tasks
    
    def _generate_deliverable(
        self, 
        prefix: str, 
        topic: Dict[str, Any], 
        task_type: str
    ) -> str:
        """구체적 결과물 생성"""
        topic_name = topic.get("name", "개념")
        
        if task_type == "concept":
            return f"{prefix} {topic_name} 핵심 개념 정리"
        elif task_type == "practice":
            return f"{prefix} {topic_name} 실습 코드 작성 및 테스트"
        else:  # quiz
            return f"{prefix} {topic_name} 퀴즈 3문제 이상 정답"
    
    def _extract_learning_objectives(self, topic: Dict[str, Any]) -> List[str]:
        """학습 목표 추출"""
        objectives = topic.get("learning_objectives", [])
        if not objectives:
            # 기본 목표 생성
            topic_name = topic.get("name", "")
            objectives = [
                f"{topic_name} 이해하기",
                f"{topic_name} 실습하기",
                f"{topic_name} 활용하기"
            ]
        return objectives[:3]  # 최대 3개
    
    async def _save_to_database(
        self,
        db: Session,
        user_id: int,
        goal_key: str,
        mvp_curriculum: Dict[str, Any],
        base_curriculum: Dict[str, Any]
    ) -> AIGeneratedCurriculum:
        """데이터베이스에 저장"""
        try:
            curriculum = AIGeneratedCurriculum(
                user_id=user_id,
                subject_key=goal_key,
                learning_goals=[mvp_curriculum["goal"], mvp_curriculum["description"]],
                difficulty_level=5,  # MVP는 중급(5/10)
                generated_syllabus=mvp_curriculum,  # MVP 형식
                agent_conversation_log=base_curriculum.get("conversation_log", ""),
                generation_metadata={
                    "framework": "langchain",
                    "goal_key": goal_key,
                    "total_weeks": mvp_curriculum["total_weeks"],
                    "daily_minutes": mvp_curriculum["daily_minutes"],
                    "generated_at": datetime.utcnow().isoformat()
                },
                status="completed"
            )
            
            db.add(curriculum)
            db.commit()
            db.refresh(curriculum)
            
            logger.info(f"커리큘럼 DB 저장 완료: id={curriculum.id}")
            return curriculum
            
        except Exception as e:
            db.rollback()
            logger.error(f"커리큘럼 DB 저장 실패: {str(e)}")
            raise
    
    def get_available_goals(self) -> List[Dict[str, Any]]:
        """사용 가능한 목표 목록 반환 (온보딩용)"""
        return [
            {
                "goal_key": key,
                "display_name": template["display_name"],
                "description": template["description"],
                "default_weeks": template["default_weeks"],
                "core_technologies": template["core_technologies"]
            }
            for key, template in self.goal_templates.items()
        ]
    
    def get_curriculum_by_id(
        self,
        curriculum_id: int,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """저장된 커리큘럼 조회"""
        try:
            curriculum = db.query(AIGeneratedCurriculum).filter(
                AIGeneratedCurriculum.id == curriculum_id
            ).first()
            
            if not curriculum:
                return None
            
            return curriculum.generated_syllabus
            
        except Exception as e:
            logger.error(f"커리큘럼 조회 실패: {str(e)}")
            return None
    
    def get_user_curricula(
        self,
        user_id: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """사용자의 모든 커리큘럼 조회"""
        try:
            curricula = db.query(AIGeneratedCurriculum).filter(
                AIGeneratedCurriculum.user_id == user_id,
                AIGeneratedCurriculum.status == "completed"
            ).order_by(AIGeneratedCurriculum.created_at.desc()).all()
            
            return [
                {
                    "curriculum_id": c.id,
                    "goal": c.generated_syllabus.get("goal"),
                    "total_weeks": c.generated_syllabus.get("total_weeks"),
                    "created_at": c.created_at.isoformat()
                }
                for c in curricula
            ]
            
        except Exception as e:
            logger.error(f"커리큘럼 목록 조회 실패: {str(e)}")
            return []


# 싱글톤 인스턴스 (FastAPI Depends에서 사용)
_goal_based_curriculum_service = None

def get_goal_based_curriculum_service() -> GoalBasedCurriculumService:
    """의존성 주입용 서비스 인스턴스"""
    global _goal_based_curriculum_service
    if _goal_based_curriculum_service is None:
        _goal_based_curriculum_service = GoalBasedCurriculumService()
    return _goal_based_curriculum_service
