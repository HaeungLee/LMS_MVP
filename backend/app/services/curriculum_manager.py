from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.orm import User, Submission, SubmissionItem, StudentAssignment
# from app.services.ai_question_generator import ai_question_generator


class CurriculumManager:
    """수업 진도 관리 시스템"""
    
    def __init__(self):
        # 주제별 학습 순서 정의
        self.learning_path = {
            "python_basics": [
                {"topic": "변수와 자료형", "estimated_days": 2, "prerequisites": []},
                {"topic": "조건문", "estimated_days": 3, "prerequisites": ["변수와 자료형"]},
                {"topic": "반복문", "estimated_days": 3, "prerequisites": ["조건문"]},
                {"topic": "함수", "estimated_days": 4, "prerequisites": ["반복문"]},
                {"topic": "리스트와 딕셔너리", "estimated_days": 4, "prerequisites": ["함수"]},
                {"topic": "클래스와 객체", "estimated_days": 5, "prerequisites": ["리스트와 딕셔너리"]},
                {"topic": "파일 입출력", "estimated_days": 3, "prerequisites": ["클래스와 객체"]},
                {"topic": "예외 처리", "estimated_days": 2, "prerequisites": ["파일 입출력"]},
                {"topic": "모듈과 패키지", "estimated_days": 3, "prerequisites": ["예외 처리"]},
                {"topic": "라이브러리 활용", "estimated_days": 4, "prerequisites": ["모듈과 패키지"]}
            ],
            "web_development": [
                {"topic": "HTML 기초", "estimated_days": 3, "prerequisites": []},
                {"topic": "CSS 스타일링", "estimated_days": 4, "prerequisites": ["HTML 기초"]},
                {"topic": "JavaScript 기초", "estimated_days": 5, "prerequisites": ["CSS 스타일링"]},
                {"topic": "DOM 조작", "estimated_days": 4, "prerequisites": ["JavaScript 기초"]},
                {"topic": "이벤트 처리", "estimated_days": 3, "prerequisites": ["DOM 조작"]},
                {"topic": "비동기 프로그래밍", "estimated_days": 5, "prerequisites": ["이벤트 처리"]},
                {"topic": "REST API", "estimated_days": 4, "prerequisites": ["비동기 프로그래밍"]},
                {"topic": "프레임워크 활용", "estimated_days": 6, "prerequisites": ["REST API"]}
            ]
        }
        
        # 각 주제별 학습 목표
        self.topic_learning_objectives = {
            "변수와 자료형": [
                "변수 선언과 할당 방법 이해",
                "기본 자료형(int, float, str, bool) 구분",
                "자료형 변환 방법 습득",
                "변수 명명 규칙 준수"
            ],
            "조건문": [
                "if, elif, else 구문 작성",
                "비교 연산자와 논리 연산자 활용",
                "중첩 조건문 구현",
                "조건문을 활용한 분기 처리"
            ],
            "반복문": [
                "for문과 while문 구분하여 사용",
                "range() 함수 활용",
                "break와 continue 활용",
                "중첩 반복문 구현"
            ],
            "함수": [
                "함수 정의와 호출",
                "매개변수와 반환값 활용",
                "지역변수와 전역변수 구분",
                "람다 함수 활용"
            ]
        }
    
    async def get_daily_learning_plan(self, user_id: int, subject: str) -> Dict[str, Any]:
        """사용자별 일일 학습 계획 생성"""
        db = next(get_db())
        try:
            # 사용자의 현재 진도 분석
            current_progress = await self._analyze_current_progress(db, user_id, subject)
            
            # 다음 학습할 주제 결정
            next_topic = await self._determine_next_topic(current_progress, subject)
            
            # 일일 문제 생성 계획
            problem_count = 5
            estimated_time_minutes = problem_count * 3  # 문제당 3분 예상
            target_accuracy = 0.75  # 75% 목표 정답률
            
            daily_plan = {
                "date": datetime.now().isoformat(),
                "user_id": user_id,
                "subject": subject,
                "current_topic": next_topic,
                "topic": next_topic,  # 프론트엔드 호환
                "difficulty": "medium",  # 기본 난이도
                "problem_count": problem_count,  # 프론트엔드 호환
                "estimated_time": estimated_time_minutes * 60,  # 초 단위로 변환
                "target_accuracy": target_accuracy,  # 0-1 범위
                "estimated_completion_days": self._get_estimated_days(subject, next_topic),
                "recommended_questions": problem_count,  # 기존 호환성
                "difficulty_distribution": {
                    "easy": 2,
                    "medium": 2,
                    "hard": 1
                },
                "focus_areas": [
                    "문법 정확성",
                    "변수명 규칙",
                    "코드 최적화"
                ],
                "learning_objectives": self.topic_learning_objectives.get(next_topic, []),
                "prerequisites_completed": current_progress.get("completed_topics", [])
            }
            
            return daily_plan
            
        except Exception as e:
            return {
                "error": f"일일 계획 생성 실패: {str(e)}",
                "fallback_plan": self._get_fallback_plan(subject)
            }
        finally:
            db.close()
    
    async def _analyze_current_progress(self, db: Session, user_id: int, subject: str) -> Dict[str, Any]:
        """사용자 현재 진도 분석"""
        # 최근 30일 제출 기록 조회
        recent_submissions = db.query(Submission).filter(
            Submission.user_id == user_id,
            Submission.subject == subject,
            Submission.submitted_at >= datetime.now() - timedelta(days=30)
        ).order_by(desc(Submission.submitted_at)).limit(20).all()
        
        topic_scores = {}
        completed_topics = []
        
        for submission in recent_submissions:
            items = db.query(SubmissionItem).filter(
                SubmissionItem.submission_id == submission.id
            ).all()
            
            for item in items:
                topic = getattr(item, 'topic', 'unknown')
                if topic not in topic_scores:
                    topic_scores[topic] = []
                topic_scores[topic].append(item.score)
        
        # 주제별 평균 점수 계산 및 완료 주제 판단
        for topic, scores in topic_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 0.8 and len(scores) >= 3:  # 80% 이상, 3문제 이상
                completed_topics.append(topic)
        
        return {
            "completed_topics": completed_topics,
            "topic_scores": {topic: sum(scores)/len(scores) for topic, scores in topic_scores.items()},
            "total_submissions": len(recent_submissions),
            "recent_activity": len([s for s in recent_submissions if s.submitted_at >= datetime.now() - timedelta(days=7)])
        }
    
    async def _determine_next_topic(self, progress: Dict[str, Any], subject: str) -> str:
        """다음 학습 주제 결정"""
        completed_topics = progress.get("completed_topics", [])
        learning_path = self.learning_path.get(subject, [])
        
        for topic_info in learning_path:
            topic = topic_info["topic"]
            prerequisites = topic_info["prerequisites"]
            
            # 아직 완료하지 않은 주제 중에서
            if topic not in completed_topics:
                # 선수 조건이 모두 완료된 주제 찾기
                if all(prereq in completed_topics for prereq in prerequisites):
                    return topic
        
        # 모든 주제가 완료되었거나 적절한 주제를 찾지 못한 경우
        if learning_path:
            return learning_path[0]["topic"]  # 첫 번째 주제 반환
        
        return "기초"  # 기본값
    
    def _get_estimated_days(self, subject: str, topic: str) -> int:
        """주제별 예상 완료 일수"""
        learning_path = self.learning_path.get(subject, [])
        for topic_info in learning_path:
            if topic_info["topic"] == topic:
                return topic_info["estimated_days"]
        return 3  # 기본값
    
    def _get_fallback_plan(self, subject: str) -> Dict[str, Any]:
        """오류 시 기본 계획"""
        return {
            "date": datetime.now().isoformat(),
            "subject": subject,
            "current_topic": "기초",
            "recommended_questions": 3,
            "difficulty_distribution": {"easy": 2, "medium": 1, "hard": 0},
            "note": "기본 학습 계획이 적용되었습니다."
        }
    
    async def track_learning_progress(self, user_id: int, subject: str, topic: str, score: float) -> Dict[str, Any]:
        """학습 진도 추적"""
        db = next(get_db())
        try:
            # 현재 주제의 이전 성과 조회
            week_ago = datetime.now() - timedelta(days=7)
            recent_submissions = db.query(Submission).filter(
                Submission.user_id == user_id,
                Submission.subject == subject,
                Submission.submitted_at >= week_ago
            ).all()
            
            # 성과 분석
            topic_performances = {}
            for submission in recent_submissions:
                # 여기서는 submission에서 topic 정보를 가져와야 하지만
                # 현재 스키마에는 topic 필드가 없으므로 임시로 처리
                current_topic = topic  # 현재 제출된 주제
                if current_topic not in topic_performances:
                    topic_performances[current_topic] = []
                topic_performances[current_topic].append(score)
            
            # 주제별 평균 점수
            avg_scores = {}
            for t, scores in topic_performances.items():
                avg_scores[t] = sum(scores) / len(scores) if scores else 0
            
            # 진도 상태 판정
            current_avg = avg_scores.get(topic, score)
            progress_status = "excellent" if current_avg >= 0.9 else \
                            "good" if current_avg >= 0.7 else \
                            "needs_improvement" if current_avg >= 0.5 else "struggling"
            
            # 다음 단계 추천
            next_action = self._recommend_next_action(progress_status, current_avg, topic)
            
            return {
                "user_id": user_id,
                "subject": subject,
                "current_topic": topic,
                "current_score": score,
                "topic_average": current_avg,
                "progress_status": progress_status,
                "next_action": next_action,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"진도 추적 실패: {str(e)}"}
        finally:
            db.close()
    
    def _recommend_next_action(self, status: str, avg_score: float, topic: str) -> Dict[str, Any]:
        """다음 행동 추천"""
        if status == "excellent":
            return {
                "action": "advance",
                "message": "훌륭합니다! 다음 주제로 진행하세요.",
                "recommended_difficulty": "medium_to_hard"
            }
        elif status == "good":
            return {
                "action": "reinforce",
                "message": "좋은 성과입니다. 몇 가지 심화 문제를 더 풀어보세요.",
                "recommended_difficulty": "medium"
            }
        elif status == "needs_improvement":
            return {
                "action": "practice",
                "message": "더 많은 연습이 필요합니다. 기초를 다시 확인해보세요.",
                "recommended_difficulty": "easy_to_medium"
            }
        else:  # struggling
            return {
                "action": "review",
                "message": "기초 개념을 다시 학습하고 쉬운 문제부터 시작하세요.",
                "recommended_difficulty": "easy"
            }
    
    async def generate_adaptive_curriculum(self, user_id: int, subject: str, target_days: int = 30) -> Dict[str, Any]:
        """적응형 커리큘럼 생성"""
        db = next(get_db())
        try:
            # 사용자 현재 상태 분석
            current_progress = await self._analyze_current_progress(db, user_id, subject)
            
            # 학습 경로에서 남은 주제들
            learning_path = self.learning_path.get(subject, [])
            completed_topics = current_progress.get("completed_topics", [])
            remaining_topics = [
                topic for topic in learning_path 
                if topic["topic"] not in completed_topics
            ]
            
            # 목표 기간에 맞춰 스케줄 조정
            total_estimated_days = sum(topic["estimated_days"] for topic in remaining_topics)
            
            if total_estimated_days > target_days:
                # 압축 스케줄 - 각 주제당 시간 단축
                compression_ratio = target_days / total_estimated_days
                for topic in remaining_topics:
                    topic["adjusted_days"] = max(1, int(topic["estimated_days"] * compression_ratio))
            else:
                # 여유 스케줄 - 심화 학습 추가
                for topic in remaining_topics:
                    topic["adjusted_days"] = topic["estimated_days"]
                    topic["extra_practice"] = True
            
            # 일별 세부 계획 생성
            daily_schedule = self._create_daily_schedule(remaining_topics, target_days)
            
            return {
                "user_id": user_id,
                "subject": subject,
                "target_days": target_days,
                "total_topics": len(remaining_topics),
                "completed_topics_count": len(completed_topics),
                "daily_schedule": daily_schedule,
                "estimated_completion": (datetime.now() + timedelta(days=target_days)).isoformat(),
                "curriculum_created": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"커리큘럼 생성 실패: {str(e)}"}
        finally:
            db.close()
    
    def _create_daily_schedule(self, topics: List[Dict], target_days: int) -> List[Dict[str, Any]]:
        """일별 스케줄 생성"""
        schedule = []
        current_day = 1
        
        for topic in topics:
            days_for_topic = topic.get("adjusted_days", topic["estimated_days"])
            
            for day in range(days_for_topic):
                day_plan = {
                    "day": current_day,
                    "topic": topic["topic"],
                    "day_of_topic": day + 1,
                    "total_days_for_topic": days_for_topic,
                    "recommended_questions": 5 if day < days_for_topic - 1 else 8,  # 마지막 날은 더 많이
                    "difficulty_focus": "easy" if day == 0 else "medium" if day < days_for_topic - 1 else "mixed",
                    "learning_objectives": self.topic_learning_objectives.get(topic["topic"], [])[:2],  # 일일 목표는 2개로 제한
                    "is_assessment_day": day == days_for_topic - 1  # 주제 마지막 날은 평가
                }
                schedule.append(day_plan)
                current_day += 1
                
                if current_day > target_days:
                    break
            
            if current_day > target_days:
                break
        
        return schedule
    
    async def get_class_overview(self, teacher_id: int, subject: str) -> Dict[str, Any]:
        """반 전체 학습 현황 개요"""
        db = next(get_db())
        try:
            # 해당 선생님의 학생들 조회 (실제로는 teacher-student 관계 테이블 필요)
            # 임시로 모든 학생으로 처리
            students = db.query(User).filter(
                User.role == "student"
            ).all()
            
            class_progress = []
            overall_stats = {
                "total_students": len(students),
                "active_students": 0,
                "struggling_students": 0,
                "advanced_students": 0,
                "average_progress": 0
            }
            
            total_progress_sum = 0
            
            for student in students:
                student_progress = await self._analyze_current_progress(db, student.id, subject)
                
                # 활동성 확인 (최근 7일 내 제출)
                is_active = student_progress.get("recent_activity", 0) > 0
                if is_active:
                    overall_stats["active_students"] += 1
                
                # 진도율 계산
                completed_count = len(student_progress.get("completed_topics", []))
                total_topics = len(self.learning_path.get(subject, []))
                progress_percentage = (completed_count / total_topics * 100) if total_topics > 0 else 0
                
                # 학생 분류
                avg_score = sum(student_progress.get("topic_scores", {}).values()) / len(student_progress.get("topic_scores", {})) if student_progress.get("topic_scores") else 0
                
                if avg_score < 0.6:
                    overall_stats["struggling_students"] += 1
                    status = "struggling"
                elif avg_score > 0.85:
                    overall_stats["advanced_students"] += 1
                    status = "advanced"
                else:
                    status = "on_track"
                
                class_progress.append({
                    "student_id": student.id,
                    "student_name": getattr(student, 'name', f'Student {student.id}'),
                    "progress_percentage": progress_percentage,
                    "completed_topics": student_progress.get("completed_topics", []),
                    "average_score": avg_score,
                    "status": status,
                    "last_activity": student_progress.get("recent_activity", 0),
                    "is_active": is_active
                })
                
                total_progress_sum += progress_percentage
            
            overall_stats["average_progress"] = total_progress_sum / len(students) if students else 0
            
            # 주제별 클래스 성과
            topic_performance = self._analyze_class_topic_performance(class_progress)
            
            return {
                "teacher_id": teacher_id,
                "subject": subject,
                "overview_date": datetime.now().isoformat(),
                "overall_stats": overall_stats,
                "student_progress": class_progress,
                "topic_performance": topic_performance,
                "recommendations": self._generate_class_recommendations(overall_stats, topic_performance)
            }
            
        except Exception as e:
            return {"error": f"반 현황 조회 실패: {str(e)}"}
        finally:
            db.close()
    
    def _analyze_class_topic_performance(self, class_progress: List[Dict]) -> Dict[str, Any]:
        """반 전체 주제별 성과 분석"""
        topic_stats = {}
        
        for student in class_progress:
            for topic in student.get("completed_topics", []):
                if topic not in topic_stats:
                    topic_stats[topic] = {
                        "completed_count": 0,
                        "total_students": len(class_progress),
                        "completion_rate": 0
                    }
                topic_stats[topic]["completed_count"] += 1
        
        # 완료율 계산
        for topic, stats in topic_stats.items():
            stats["completion_rate"] = stats["completed_count"] / stats["total_students"] * 100
        
        return topic_stats
    
    def _generate_class_recommendations(self, stats: Dict, topic_performance: Dict) -> List[str]:
        """반 전체 학습 추천사항 생성"""
        recommendations = []
        
        if stats["struggling_students"] > stats["total_students"] * 0.3:
            recommendations.append("어려움을 겪는 학생이 많습니다. 기초 개념 복습 시간을 늘려보세요.")
        
        if stats["active_students"] < stats["total_students"] * 0.7:
            recommendations.append("학습 참여도가 낮습니다. 동기부여 방안을 고려해보세요.")
        
        # 특정 주제에서 낮은 완료율
        low_completion_topics = [
            topic for topic, perf in topic_performance.items() 
            if perf["completion_rate"] < 50
        ]
        if low_completion_topics:
            recommendations.append(f"다음 주제들의 완료율이 낮습니다: {', '.join(low_completion_topics)}")
        
        if stats["advanced_students"] > stats["total_students"] * 0.4:
            recommendations.append("우수한 학생들이 많습니다. 심화 과제를 추가로 제공해보세요.")
        
        return recommendations


# 싱글톤 인스턴스 생성
curriculum_manager = CurriculumManager()

# 모듈 레벨에서 export할 객체들 명시
__all__ = ['CurriculumManager', 'curriculum_manager']
