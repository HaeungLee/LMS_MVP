"""
Phase 10: 적응형 난이도 조절 엔진
- 실시간 성과 기반 난이도 조정
- 학습자 개별 특성 분석
- 최적 학습 구간 유지
- 동적 피드백 시스템
"""

import asyncio
import json
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.redis_service import get_redis_service
from app.models.orm import User, Question, Submission
from app.core.database import get_db

logger = logging.getLogger(__name__)

class LearningState(Enum):
    """학습 상태"""
    STRUGGLING = "struggling"       # 어려워함 (정답률 < 60%)
    LEARNING = "learning"           # 학습중 (정답률 60-80%)
    MASTERING = "mastering"         # 숙달중 (정답률 80-95%)
    MASTERED = "mastered"           # 숙달완료 (정답률 > 95%)

class DifficultyAdjustment(Enum):
    """난이도 조정 방향"""
    DECREASE_MAJOR = "decrease_major"   # 큰 폭 하향
    DECREASE_MINOR = "decrease_minor"   # 소폭 하향
    MAINTAIN = "maintain"               # 유지
    INCREASE_MINOR = "increase_minor"   # 소폭 상향
    INCREASE_MAJOR = "increase_major"   # 큰 폭 상향

@dataclass
class LearnerProfile:
    """학습자 프로필"""
    user_id: int
    learning_style: str  # visual, auditory, kinesthetic, reading
    preferred_pace: str  # slow, normal, fast
    confidence_level: float  # 0.0 - 1.0
    persistence_score: float  # 0.0 - 1.0
    current_focus_areas: List[str]
    strengths: List[str]
    weaknesses: List[str]
    last_updated: datetime

@dataclass
class PerformanceMetrics:
    """성과 지표"""
    accuracy: float  # 정답률
    response_time: float  # 평균 응답 시간
    consistency: float  # 일관성 점수
    improvement_rate: float  # 향상 속도
    engagement_score: float  # 참여도
    difficulty_comfort_zone: Tuple[float, float]  # 적정 난이도 구간

@dataclass
class AdaptationRecommendation:
    """적응 추천"""
    current_difficulty: float
    recommended_difficulty: float
    adjustment_type: DifficultyAdjustment
    confidence: float
    reasoning: str
    suggested_actions: List[str]
    estimated_mastery_time: Optional[int] = None

class AdaptiveDifficultyEngine:
    """적응형 난이도 조절 엔진"""
    
    def __init__(self):
        self.redis_service = get_redis_service()
        
        # 적응 알고리즘 설정
        self.config = {
            "target_accuracy": 0.75,  # 목표 정답률
            "comfort_zone": (0.70, 0.85),  # 적정 정답률 구간
            "min_samples": 5,  # 최소 문제 수
            "adaptation_sensitivity": 0.1,  # 조정 민감도
            "confidence_threshold": 0.7,  # 신뢰도 임계값
            "time_weight": 0.3,  # 시간 가중치
            "accuracy_weight": 0.7,  # 정확도 가중치
        }
    
    async def analyze_learner_performance(
        self,
        user_id: int,
        subject_key: str,
        recent_submissions: List[Dict[str, Any]],
        db: Session
    ) -> PerformanceMetrics:
        """학습자 성과 분석"""
        
        try:
            if not recent_submissions or len(recent_submissions) < self.config["min_samples"]:
                # 충분한 데이터가 없는 경우 기본값 반환
                return PerformanceMetrics(
                    accuracy=0.75,
                    response_time=60.0,
                    consistency=0.8,
                    improvement_rate=0.0,
                    engagement_score=0.7,
                    difficulty_comfort_zone=(0.6, 0.8)
                )
            
            # 기본 지표 계산
            accuracy = self._calculate_accuracy(recent_submissions)
            response_time = self._calculate_avg_response_time(recent_submissions)
            consistency = self._calculate_consistency(recent_submissions)
            improvement_rate = self._calculate_improvement_rate(recent_submissions)
            engagement_score = await self._calculate_engagement_score(user_id, recent_submissions)
            
            # 적정 난이도 구간 계산
            comfort_zone = self._calculate_comfort_zone(recent_submissions, accuracy)
            
            return PerformanceMetrics(
                accuracy=accuracy,
                response_time=response_time,
                consistency=consistency,
                improvement_rate=improvement_rate,
                engagement_score=engagement_score,
                difficulty_comfort_zone=comfort_zone
            )
            
        except Exception as e:
            logger.error(f"성과 분석 실패: {str(e)}")
            raise
    
    async def recommend_difficulty_adjustment(
        self,
        user_id: int,
        subject_key: str,
        current_difficulty: float,
        performance_metrics: PerformanceMetrics,
        learner_profile: LearnerProfile
    ) -> AdaptationRecommendation:
        """난이도 조정 추천"""
        
        try:
            # 현재 학습 상태 판단
            learning_state = self._determine_learning_state(performance_metrics)
            
            # 적응 알고리즘 적용
            adjustment = self._calculate_difficulty_adjustment(
                current_difficulty,
                performance_metrics,
                learner_profile,
                learning_state
            )
            
            # 추천 난이도 계산
            recommended_difficulty = self._apply_adjustment(
                current_difficulty,
                adjustment,
                performance_metrics
            )
            
            # 신뢰도 계산
            confidence = self._calculate_confidence(performance_metrics, learner_profile)
            
            # 추천 이유 생성
            reasoning = self._generate_reasoning(
                learning_state,
                adjustment,
                performance_metrics,
                learner_profile
            )
            
            # 추천 액션 생성
            suggested_actions = self._generate_suggested_actions(
                learning_state,
                adjustment,
                performance_metrics
            )
            
            # 예상 숙달 시간 계산
            mastery_time = self._estimate_mastery_time(
                current_difficulty,
                recommended_difficulty,
                performance_metrics,
                learner_profile
            )
            
            return AdaptationRecommendation(
                current_difficulty=current_difficulty,
                recommended_difficulty=recommended_difficulty,
                adjustment_type=adjustment,
                confidence=confidence,
                reasoning=reasoning,
                suggested_actions=suggested_actions,
                estimated_mastery_time=mastery_time
            )
            
        except Exception as e:
            logger.error(f"난이도 조정 추천 실패: {str(e)}")
            # 안전한 기본 추천
            return AdaptationRecommendation(
                current_difficulty=current_difficulty,
                recommended_difficulty=current_difficulty,
                adjustment_type=DifficultyAdjustment.MAINTAIN,
                confidence=0.5,
                reasoning="데이터 부족으로 현재 난이도 유지를 추천합니다.",
                suggested_actions=["더 많은 문제를 풀어 데이터를 축적해보세요."]
            )
    
    # ========== 계산 메서드들 ==========
    
    def _calculate_accuracy(self, submissions: List[Dict[str, Any]]) -> float:
        """정답률 계산"""
        if not submissions:
            return 0.0
        
        correct_count = sum(1 for s in submissions if s.get('is_correct', False))
        return correct_count / len(submissions)
    
    def _calculate_avg_response_time(self, submissions: List[Dict[str, Any]]) -> float:
        """평균 응답 시간 계산"""
        times = [s.get('response_time', 60) for s in submissions if s.get('response_time')]
        return sum(times) / len(times) if times else 60.0
    
    def _calculate_consistency(self, submissions: List[Dict[str, Any]]) -> float:
        """일관성 점수 계산"""
        if len(submissions) < 3:
            return 0.8
        
        results = [1 if s.get('is_correct', False) else 0 for s in submissions]
        consistency_score = 0.0
        for i in range(1, len(results)):
            if results[i] == results[i-1]:
                consistency_score += 1
        
        return consistency_score / (len(results) - 1) if len(results) > 1 else 0.8
    
    def _calculate_improvement_rate(self, submissions: List[Dict[str, Any]]) -> float:
        """향상 속도 계산"""
        if len(submissions) < 5:
            return 0.0
        
        sorted_submissions = sorted(submissions, key=lambda x: x.get('submitted_at', ''))
        mid_point = len(sorted_submissions) // 2
        first_half = sorted_submissions[:mid_point]
        second_half = sorted_submissions[mid_point:]
        
        first_accuracy = self._calculate_accuracy(first_half)
        second_accuracy = self._calculate_accuracy(second_half)
        
        return second_accuracy - first_accuracy
    
    async def _calculate_engagement_score(
        self,
        user_id: int,
        submissions: List[Dict[str, Any]]
    ) -> float:
        """참여도 점수 계산"""
        return 0.7  # 간소화된 버전
    
    def _calculate_comfort_zone(
        self,
        submissions: List[Dict[str, Any]],
        current_accuracy: float
    ) -> Tuple[float, float]:
        """적정 난이도 구간 계산"""
        if current_accuracy > 0.9:
            return (0.7, 0.9)
        elif current_accuracy > 0.8:
            return (0.65, 0.85)
        elif current_accuracy > 0.7:
            return (0.6, 0.8)
        elif current_accuracy > 0.6:
            return (0.55, 0.75)
        else:
            return (0.5, 0.7)
    
    def _determine_learning_state(self, metrics: PerformanceMetrics) -> LearningState:
        """학습 상태 판단"""
        accuracy = metrics.accuracy
        
        if accuracy < 0.6:
            return LearningState.STRUGGLING
        elif accuracy < 0.8:
            return LearningState.LEARNING
        elif accuracy < 0.95:
            return LearningState.MASTERING
        else:
            return LearningState.MASTERED
    
    def _calculate_difficulty_adjustment(
        self,
        current_difficulty: float,
        metrics: PerformanceMetrics,
        profile: LearnerProfile,
        state: LearningState
    ) -> DifficultyAdjustment:
        """난이도 조정 계산"""
        target_accuracy = self.config["target_accuracy"]
        accuracy_diff = metrics.accuracy - target_accuracy
        
        if state == LearningState.STRUGGLING:
            if accuracy_diff < -0.2:
                return DifficultyAdjustment.DECREASE_MAJOR
            else:
                return DifficultyAdjustment.DECREASE_MINOR
        elif state == LearningState.LEARNING:
            if abs(accuracy_diff) < 0.05:
                return DifficultyAdjustment.MAINTAIN
            elif accuracy_diff < 0:
                return DifficultyAdjustment.DECREASE_MINOR
            else:
                return DifficultyAdjustment.INCREASE_MINOR
        elif state == LearningState.MASTERING:
            return DifficultyAdjustment.INCREASE_MINOR
        else:  # MASTERED
            return DifficultyAdjustment.INCREASE_MAJOR
    
    def _apply_adjustment(
        self,
        current_difficulty: float,
        adjustment: DifficultyAdjustment,
        metrics: PerformanceMetrics
    ) -> float:
        """조정 적용"""
        adjustment_map = {
            DifficultyAdjustment.DECREASE_MAJOR: -0.3,
            DifficultyAdjustment.DECREASE_MINOR: -0.1,
            DifficultyAdjustment.MAINTAIN: 0.0,
            DifficultyAdjustment.INCREASE_MINOR: 0.1,
            DifficultyAdjustment.INCREASE_MAJOR: 0.3
        }
        
        change = adjustment_map[adjustment]
        new_difficulty = current_difficulty + change
        
        return max(0.1, min(1.0, new_difficulty))
    
    def _calculate_confidence(
        self,
        metrics: PerformanceMetrics,
        profile: LearnerProfile
    ) -> float:
        """신뢰도 계산"""
        factors = [metrics.consistency, metrics.engagement_score, profile.confidence_level]
        return sum(factors) / len(factors)
    
    def _generate_reasoning(
        self,
        state: LearningState,
        adjustment: DifficultyAdjustment,
        metrics: PerformanceMetrics,
        profile: LearnerProfile
    ) -> str:
        """추천 이유 생성"""
        accuracy_pct = f"{metrics.accuracy * 100:.1f}%"
        
        state_messages = {
            LearningState.STRUGGLING: f"현재 정답률이 {accuracy_pct}로 어려움을 겪고 있어",
            LearningState.LEARNING: f"현재 정답률이 {accuracy_pct}로 학습이 진행 중이야",
            LearningState.MASTERING: f"현재 정답률이 {accuracy_pct}로 숙달 과정에 있어",
            LearningState.MASTERED: f"현재 정답률이 {accuracy_pct}로 이미 숙달 완료 상태야"
        }
        
        adjustment_messages = {
            DifficultyAdjustment.DECREASE_MAJOR: "난이도를 크게 낮춰서 자신감을 회복하는 것이 좋겠어",
            DifficultyAdjustment.DECREASE_MINOR: "난이도를 조금 낮춰서 안정적인 학습을 도모하자",
            DifficultyAdjustment.MAINTAIN: "현재 난이도가 적절하니 유지하면서 꾸준히 학습하자",
            DifficultyAdjustment.INCREASE_MINOR: "난이도를 조금 높여서 도전해볼 시간이야",
            DifficultyAdjustment.INCREASE_MAJOR: "난이도를 크게 높여서 새로운 도전을 해보자"
        }
        
        return f"{state_messages[state]}. {adjustment_messages[adjustment]}."
    
    def _generate_suggested_actions(
        self,
        state: LearningState,
        adjustment: DifficultyAdjustment,
        metrics: PerformanceMetrics
    ) -> List[str]:
        """추천 액션 생성"""
        actions = []
        
        if state == LearningState.STRUGGLING:
            actions.extend([
                "기초 개념 복습하기",
                "힌트를 적극 활용하기",
                "천천히 문제 읽고 이해하기"
            ])
        elif state == LearningState.LEARNING:
            actions.extend([
                "꾸준한 반복 학습하기",
                "다양한 유형의 문제 도전하기",
                "틀린 문제 다시 풀어보기"
            ])
        elif state == LearningState.MASTERING:
            actions.extend([
                "응용 문제 도전하기",
                "시간 제한 두고 풀기",
                "다른 사람에게 설명해보기"
            ])
        else:  # MASTERED
            actions.extend([
                "고급 문제에 도전하기",
                "새로운 토픽 학습 시작하기",
                "프로젝트 실습해보기"
            ])
        
        return actions[:3]
    
    def _estimate_mastery_time(
        self,
        current_difficulty: float,
        recommended_difficulty: float,
        metrics: PerformanceMetrics,
        profile: LearnerProfile
    ) -> int:
        """숙달 시간 예측 (분 단위)"""
        base_time = 60
        difficulty_diff = abs(recommended_difficulty - current_difficulty)
        time_adjustment = difficulty_diff * 30
        
        if metrics.accuracy > 0.8:
            time_adjustment *= 0.7
        elif metrics.accuracy < 0.6:
            time_adjustment *= 1.5
        
        if profile.preferred_pace == "fast":
            time_adjustment *= 0.8
        elif profile.preferred_pace == "slow":
            time_adjustment *= 1.3
        
        return int(base_time + time_adjustment)


def get_adaptive_difficulty_engine() -> AdaptiveDifficultyEngine:
    """적응형 난이도 엔진 인스턴스 반환"""
    return AdaptiveDifficultyEngine()