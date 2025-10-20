"""
MVP 복습 시스템 API

망각 곡선 기반 복습 스케줄링
- 틀린 문제 자동 추천
- 약점 분석
- 복습 우선순위 계산
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import math

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orm import User, UserProgress, Submission

router = APIRouter()


# ============= Models =============

class WeaknessAnalysis(BaseModel):
    """약점 분석 결과"""
    topic: str  # 주제
    concept: str  # 개념
    incorrect_count: int  # 틀린 횟수
    total_attempts: int  # 총 시도 횟수
    accuracy: float  # 정확도 (0-100)
    last_attempt: datetime  # 마지막 시도 시간
    priority_score: float  # 복습 우선순위 점수 (0-100)
    

class ReviewRecommendation(BaseModel):
    """복습 추천"""
    problem_id: int
    problem_title: str
    topic: str
    concept: str
    difficulty: str
    incorrect_count: int
    days_since_last: int  # 마지막 시도 후 경과일
    forgetting_risk: float  # 망각 위험도 (0-100)
    review_urgency: str  # 긴급도: critical, high, medium, low
    recommended_review_date: datetime
    

class ReviewStats(BaseModel):
    """복습 통계"""
    total_weak_concepts: int  # 약점 개념 수
    critical_reviews: int  # 긴급 복습 필요
    high_priority_reviews: int  # 높은 우선순위
    total_incorrect_problems: int  # 틀린 문제 수
    average_accuracy: float  # 평균 정확도
    improvement_rate: float  # 개선율 (지난주 대비)


class ReviewSessionRequest(BaseModel):
    """복습 세션 시작 요청"""
    max_problems: int = Field(default=10, ge=1, le=50, description="복습할 문제 수")
    focus_topics: Optional[List[str]] = Field(default=None, description="집중 주제")
    difficulty_preference: Optional[str] = Field(default=None, description="난이도 선호")


class ReviewSessionResponse(BaseModel):
    """복습 세션 응답"""
    session_id: str
    problems: List[ReviewRecommendation]
    total_count: int
    estimated_time_minutes: int
    focus_message: str


# ============= API Endpoints =============

@router.get("/stats", response_model=ReviewStats)
async def get_review_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    복습 통계 조회
    
    - 약점 개념 수
    - 긴급 복습 필요 문제 수
    - 평균 정확도
    - 개선율
    """
    
    # 틀린 제출 기록 조회
    incorrect_submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.is_correct == False
    ).all()
    
    # 약점 개념 분석
    weakness_map: Dict[str, WeaknessAnalysis] = {}
    
    for sub in incorrect_submissions:
        # 문제의 topic/concept 정보 (실제로는 Question 테이블 조인 필요)
        topic = sub.problem_id  # 임시: problem_id를 topic으로 사용
        concept = f"concept_{sub.problem_id}"  # 임시
        
        key = f"{topic}_{concept}"
        
        if key not in weakness_map:
            weakness_map[key] = {
                'topic': str(topic),
                'concept': concept,
                'incorrect': 0,
                'total': 0,
                'last_attempt': sub.submitted_at
            }
        
        weakness_map[key]['incorrect'] += 1
        weakness_map[key]['total'] += 1
        if sub.submitted_at > weakness_map[key]['last_attempt']:
            weakness_map[key]['last_attempt'] = sub.submitted_at
    
    # 우선순위 계산
    now = datetime.now()
    critical_count = 0
    high_priority_count = 0
    
    for key, data in weakness_map.items():
        days_since = (now - data['last_attempt']).days
        accuracy = ((data['total'] - data['incorrect']) / data['total'] * 100) if data['total'] > 0 else 0
        
        # 우선순위 점수 계산
        priority = calculate_priority_score(
            incorrect_count=data['incorrect'],
            days_since_last=days_since,
            accuracy=accuracy
        )
        
        if priority >= 80:
            critical_count += 1
        elif priority >= 60:
            high_priority_count += 1
    
    # 평균 정확도 계산
    total_submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).count()
    
    correct_submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.is_correct == True
    ).count()
    
    avg_accuracy = (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
    
    # 개선율 계산 (지난주 vs 이번주)
    week_ago = now - timedelta(days=7)
    
    last_week_correct = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.submitted_at < week_ago,
        Submission.is_correct == True
    ).count()
    
    last_week_total = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.submitted_at < week_ago
    ).count()
    
    this_week_correct = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.submitted_at >= week_ago,
        Submission.is_correct == True
    ).count()
    
    this_week_total = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.submitted_at >= week_ago
    ).count()
    
    last_week_acc = (last_week_correct / last_week_total * 100) if last_week_total > 0 else 0
    this_week_acc = (this_week_correct / this_week_total * 100) if this_week_total > 0 else 0
    improvement_rate = this_week_acc - last_week_acc
    
    return ReviewStats(
        total_weak_concepts=len(weakness_map),
        critical_reviews=critical_count,
        high_priority_reviews=high_priority_count,
        total_incorrect_problems=len(incorrect_submissions),
        average_accuracy=round(avg_accuracy, 1),
        improvement_rate=round(improvement_rate, 1)
    )


@router.get("/weaknesses", response_model=List[WeaknessAnalysis])
async def get_weakness_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    약점 분석 조회
    
    - 틀린 문제들을 주제/개념별로 그룹화
    - 우선순위 순으로 정렬
    """
    
    # 틀린 제출 기록
    incorrect_submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.is_correct == False
    ).all()
    
    # 주제/개념별 그룹화
    weakness_map: Dict[str, dict] = {}
    
    for sub in incorrect_submissions:
        topic = str(sub.problem_id)  # 임시
        concept = f"concept_{sub.problem_id}"  # 임시
        
        key = f"{topic}_{concept}"
        
        if key not in weakness_map:
            weakness_map[key] = {
                'topic': topic,
                'concept': concept,
                'incorrect': 0,
                'total': 0,
                'last_attempt': sub.submitted_at
            }
        
        weakness_map[key]['incorrect'] += 1
        weakness_map[key]['total'] += 1
        if sub.submitted_at > weakness_map[key]['last_attempt']:
            weakness_map[key]['last_attempt'] = sub.submitted_at
    
    # WeaknessAnalysis 객체 생성 및 우선순위 계산
    now = datetime.now()
    weaknesses = []
    
    for key, data in weakness_map.items():
        days_since = (now - data['last_attempt']).days
        accuracy = ((data['total'] - data['incorrect']) / data['total'] * 100) if data['total'] > 0 else 0
        
        priority = calculate_priority_score(
            incorrect_count=data['incorrect'],
            days_since_last=days_since,
            accuracy=accuracy
        )
        
        weaknesses.append(WeaknessAnalysis(
            topic=data['topic'],
            concept=data['concept'],
            incorrect_count=data['incorrect'],
            total_attempts=data['total'],
            accuracy=round(accuracy, 1),
            last_attempt=data['last_attempt'],
            priority_score=round(priority, 1)
        ))
    
    # 우선순위 순 정렬
    weaknesses.sort(key=lambda x: x.priority_score, reverse=True)
    
    return weaknesses[:limit]


@router.post("/session/start", response_model=ReviewSessionResponse)
async def start_review_session(
    request: ReviewSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    복습 세션 시작
    
    - 망각 곡선 기반 문제 선택
    - 우선순위 높은 문제부터 추천
    - 세션 ID 생성
    """
    
    # 틀린 문제 조회
    incorrect_submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id,
        Submission.is_correct == False
    ).all()
    
    # 복습 추천 생성
    now = datetime.now()
    recommendations = []
    
    for sub in incorrect_submissions:
        days_since = (now - sub.submitted_at).days
        
        # 망각 위험도 계산 (에빙하우스 망각 곡선)
        forgetting_risk = calculate_forgetting_risk(days_since)
        
        # 복습 긴급도
        urgency = get_urgency_level(forgetting_risk)
        
        # 추천 복습 날짜
        recommended_date = calculate_next_review_date(
            last_attempt=sub.submitted_at,
            attempt_count=1,  # 임시
            was_correct=False
        )
        
        recommendations.append(ReviewRecommendation(
            problem_id=sub.problem_id,
            problem_title=f"Problem {sub.problem_id}",  # 임시
            topic="Python",  # 임시
            concept="Loops",  # 임시
            difficulty="medium",  # 임시
            incorrect_count=1,  # 임시
            days_since_last=days_since,
            forgetting_risk=round(forgetting_risk, 1),
            review_urgency=urgency,
            recommended_review_date=recommended_date
        ))
    
    # 망각 위험도 순으로 정렬
    recommendations.sort(key=lambda x: x.forgetting_risk, reverse=True)
    
    # 요청된 수만큼만
    selected = recommendations[:request.max_problems]
    
    # 세션 ID 생성
    session_id = f"review_{current_user.id}_{int(now.timestamp())}"
    
    # 예상 시간 (문제당 5분)
    estimated_time = len(selected) * 5
    
    # 집중 메시지
    if len(selected) == 0:
        focus_message = "🎉 복습할 문제가 없습니다! 완벽해요!"
    elif any(r.review_urgency == 'critical' for r in selected):
        focus_message = "⚠️ 긴급 복습이 필요한 문제가 있습니다!"
    else:
        focus_message = f"📚 {len(selected)}개 문제를 복습해봅시다!"
    
    return ReviewSessionResponse(
        session_id=session_id,
        problems=selected,
        total_count=len(selected),
        estimated_time_minutes=estimated_time,
        focus_message=focus_message
    )


# ============= Helper Functions =============

def calculate_priority_score(
    incorrect_count: int,
    days_since_last: int,
    accuracy: float
) -> float:
    """
    복습 우선순위 점수 계산 (0-100)
    
    요소:
    - 틀린 횟수 (많을수록 높음)
    - 경과 시간 (오래될수록 높음)
    - 정확도 (낮을수록 높음)
    """
    
    # 틀린 횟수 점수 (0-40)
    incorrect_score = min(incorrect_count * 10, 40)
    
    # 경과 시간 점수 (0-40)
    # 1일: 5점, 3일: 15점, 7일: 30점, 14일+: 40점
    time_score = min(days_since_last * 3, 40)
    
    # 정확도 점수 (0-20)
    # 낮을수록 높은 점수
    accuracy_score = (100 - accuracy) / 5
    
    total = incorrect_score + time_score + accuracy_score
    
    return min(total, 100)


def calculate_forgetting_risk(days_since_last: int) -> float:
    """
    망각 위험도 계산 (에빙하우스 망각 곡선)
    
    망각 곡선: R = e^(-t/S)
    - R: 기억 유지율
    - t: 경과 시간 (일)
    - S: 기억 강도 (기본 3일)
    
    망각 위험도 = 100 - (R * 100)
    """
    
    S = 3  # 기억 강도 (일)
    retention = math.exp(-days_since_last / S)
    forgetting_risk = (1 - retention) * 100
    
    return min(forgetting_risk, 100)


def get_urgency_level(forgetting_risk: float) -> str:
    """
    망각 위험도에 따른 긴급도 레벨
    
    - critical: 80% 이상
    - high: 60-80%
    - medium: 40-60%
    - low: 40% 미만
    """
    
    if forgetting_risk >= 80:
        return "critical"
    elif forgetting_risk >= 60:
        return "high"
    elif forgetting_risk >= 40:
        return "medium"
    else:
        return "low"


def calculate_next_review_date(
    last_attempt: datetime,
    attempt_count: int,
    was_correct: bool
) -> datetime:
    """
    다음 복습 날짜 계산 (간격 반복 학습)
    
    간격:
    - 1회차: 1일 후
    - 2회차: 3일 후
    - 3회차: 7일 후
    - 4회차: 14일 후
    - 5회차+: 30일 후
    
    틀린 경우: 간격 초기화
    """
    
    if not was_correct:
        # 틀렸으면 1일 후 다시 복습
        return last_attempt + timedelta(days=1)
    
    # 간격 반복 학습 (Spaced Repetition)
    intervals = [1, 3, 7, 14, 30]
    
    interval_index = min(attempt_count - 1, len(intervals) - 1)
    days_to_add = intervals[interval_index]
    
    return last_attempt + timedelta(days=days_to_add)
