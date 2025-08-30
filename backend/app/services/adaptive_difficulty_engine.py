"""
실시간 적응형 난이도 조절 엔진 - Phase 4
- 사용자 실력에 따른 동적 난이도 조절
- 실시간 성과 분석
- 최적 도전 수준 유지
- 학습 효율성 극대화
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from app.models.orm import Question, Submission, SubmissionItem, User, UserProgress
from app.services.redis_service import get_redis_service
from app.services.ai_providers import generate_ai_response, ModelTier

logger = logging.getLogger(__name__)

class DifficultyTrend(Enum):
    """난이도 조절 방향"""
    INCREASE = "increase"    # 난이도 상승
    MAINTAIN = "maintain"    # 현재 유지  
    DECREASE = "decrease"    # 난이도 하락
    ADAPTIVE = "adaptive"    # 점진적 조절

class PerformanceZone(Enum):
    """성과 구간"""
    COMFORT_ZONE = "comfort"      # 너무 쉬움 (90%+ 정답률)
    OPTIMAL_ZONE = "optimal"      # 최적 구간 (70-85% 정답률)
    CHALLENGE_ZONE = "challenge"  # 도전 구간 (50-70% 정답률)
    STRUGGLE_ZONE = "struggle"    # 어려움 구간 (50% 미만)

@dataclass
class DifficultyMetrics:
    """난이도 메트릭"""
    current_accuracy: float
    response_time_trend: List[float]
    confidence_level: float
    recent_improvements: float
    frustration_indicators: float
    engagement_score: float

@dataclass
class DifficultyRecommendation:
    """난이도 추천"""
    recommended_difficulty: int
    confidence: float
    reasoning: str
    expected_accuracy: float
    adjustment_timeline: str

class AdaptiveDifficultyEngine:
    """적응형 난이도 조절 엔진"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_service = get_redis_service()
        
        # 성과 구간별 목표 정확도
        self.target_accuracy_ranges = {
            PerformanceZone.COMFORT_ZONE: (0.9, 1.0),
            PerformanceZone.OPTIMAL_ZONE: (0.7, 0.85),
            PerformanceZone.CHALLENGE_ZONE: (0.5, 0.7),
            PerformanceZone.STRUGGLE_ZONE: (0.0, 0.5)
        }
        
        # 난이도 조절 파라미터
        self.adjustment_parameters = {
            'min_questions_for_adjustment': 3,
            'confidence_threshold': 0.7,
            'max_difficulty_jump': 2,
            'min_difficulty': 1,
            'max_difficulty': 5,
            'adjustment_window_minutes': 30
        }
        
        # 학습자 상태별 가중치
        self.learner_weights = {
            'beginner': {'accuracy': 0.6, 'confidence': 0.4},
            'intermediate': {'accuracy': 0.5, 'confidence': 0.3, 'improvement': 0.2},
            'advanced': {'accuracy': 0.4, 'confidence': 0.3, 'challenge_seeking': 0.3}
        }
    
    async def calculate_optimal_difficulty(
        self, 
        user_id: int, 
        topic: Optional[str] = None,
        current_difficulty: Optional[int] = None
    ) -> DifficultyRecommendation:
        """최적 난이도 계산"""
        
        try:
            # 사용자 최근 성과 데이터 수집
            performance_data = await self._collect_performance_data(user_id, topic)
            
            if not performance_data['recent_submissions']:
                # 데이터 부족시 기본 난이도
                return self._get_default_difficulty_recommendation(user_id, current_difficulty)
            
            # 난이도 메트릭 계산
            metrics = self._calculate_difficulty_metrics(performance_data)
            
            # 현재 성과 구간 판단
            performance_zone = self._determine_performance_zone(metrics)
            
            # 난이도 조절 방향 결정
            adjustment_direction = self._determine_adjustment_direction(
                metrics, performance_zone, current_difficulty
            )
            
            # 새로운 난이도 계산
            new_difficulty = self._calculate_new_difficulty(
                current_difficulty or 2, 
                adjustment_direction, 
                metrics,
                performance_data
            )
            
            # 추천 결과 생성
            recommendation = DifficultyRecommendation(
                recommended_difficulty=new_difficulty,
                confidence=self._calculate_recommendation_confidence(metrics, performance_data),
                reasoning=self._generate_reasoning(adjustment_direction, performance_zone, metrics),
                expected_accuracy=self._predict_accuracy(new_difficulty, metrics),
                adjustment_timeline=self._estimate_adjustment_timeline(adjustment_direction)
            )
            
            # 결과 캐싱
            await self._cache_difficulty_recommendation(user_id, topic, recommendation)
            
            logger.info(f"난이도 추천 완료 - User: {user_id}, 현재: {current_difficulty} -> 추천: {new_difficulty}")
            return recommendation
            
        except Exception as e:
            logger.error(f"난이도 계산 실패 user {user_id}: {str(e)}")
            return self._get_fallback_recommendation(current_difficulty)
    
    async def _collect_performance_data(self, user_id: int, topic: Optional[str] = None) -> Dict[str, Any]:
        """성과 데이터 수집"""
        
        try:
            # 최근 30분간의 제출 기록
            recent_time = datetime.utcnow() - timedelta(minutes=30)
            
            query = self.db.query(SubmissionItem).join(Submission).filter(
                Submission.user_id == user_id,
                Submission.submitted_at >= recent_time
            )
            
            # 토픽 필터링
            if topic:
                query = query.join(Question).filter(Question.topic == topic)
            
            recent_submissions = query.order_by(Submission.submitted_at.desc()).limit(10).all()
            
            # 더 넓은 기간의 데이터 (분석용)
            extended_time = datetime.utcnow() - timedelta(days=7)
            extended_query = self.db.query(SubmissionItem).join(Submission).filter(
                Submission.user_id == user_id,
                Submission.submitted_at >= extended_time
            )
            
            if topic:
                extended_query = extended_query.join(Question).filter(Question.topic == topic)
            
            extended_submissions = extended_query.order_by(Submission.submitted_at.desc()).limit(50).all()
            
            return {
                'recent_submissions': [{
                    'id': s.id,
                    'question_id': s.question_id,
                    'is_correct': s.is_correct,
                    'response_time': s.response_time,
                    'submitted_at': s.submitted_at.isoformat(),
                    'difficulty': getattr(s.question, 'difficulty', 2) if hasattr(s, 'question') else 2,
                    'confidence_score': getattr(s, 'confidence_score', 0.5)
                } for s in recent_submissions],
                'extended_submissions': [{
                    'is_correct': s.is_correct,
                    'response_time': s.response_time,
                    'difficulty': getattr(s.question, 'difficulty', 2) if hasattr(s, 'question') else 2,
                    'submitted_at': s.submitted_at.isoformat()
                } for s in extended_submissions],
                'user_level': await self._get_user_level(user_id)
            }
            
        except Exception as e:
            logger.error(f"성과 데이터 수집 실패: {str(e)}")
            return {'recent_submissions': [], 'extended_submissions': [], 'user_level': 'beginner'}
    
    def _calculate_difficulty_metrics(self, performance_data: Dict[str, Any]) -> DifficultyMetrics:
        """난이도 메트릭 계산"""
        
        recent = performance_data['recent_submissions']
        extended = performance_data['extended_submissions']
        
        if not recent:
            return DifficultyMetrics(0.5, [], 0.5, 0.0, 0.0, 0.5)
        
        # 현재 정확도
        current_accuracy = np.mean([s['is_correct'] for s in recent])
        
        # 응답 시간 트렌드
        response_times = [s['response_time'] or 60 for s in recent]
        
        # 신뢰도 수준
        confidence_scores = [s.get('confidence_score', 0.5) for s in recent]
        confidence_level = np.mean(confidence_scores)
        
        # 최근 개선도 (최근 vs 이전 정확도 비교)
        recent_improvements = 0.0
        if len(extended) >= 6:
            old_accuracy = np.mean([s['is_correct'] for s in extended[len(recent):len(recent)+5]])
            recent_improvements = current_accuracy - old_accuracy
        
        # 좌절 지표 (연속 틀린 문제, 급격한 응답시간 증가)
        frustration_indicators = self._calculate_frustration_indicators(recent)
        
        # 참여도 점수
        engagement_score = self._calculate_engagement_score(recent, extended)
        
        return DifficultyMetrics(
            current_accuracy=current_accuracy,
            response_time_trend=response_times,
            confidence_level=confidence_level,
            recent_improvements=recent_improvements,
            frustration_indicators=frustration_indicators,
            engagement_score=engagement_score
        )
    
    def _determine_performance_zone(self, metrics: DifficultyMetrics) -> PerformanceZone:
        """성과 구간 판단"""
        
        accuracy = metrics.current_accuracy
        
        if accuracy >= 0.9:
            return PerformanceZone.COMFORT_ZONE
        elif accuracy >= 0.7:
            return PerformanceZone.OPTIMAL_ZONE
        elif accuracy >= 0.5:
            return PerformanceZone.CHALLENGE_ZONE
        else:
            return PerformanceZone.STRUGGLE_ZONE
    
    def _determine_adjustment_direction(
        self, 
        metrics: DifficultyMetrics, 
        zone: PerformanceZone,
        current_difficulty: Optional[int]
    ) -> DifficultyTrend:
        """조절 방향 결정"""
        
        # 구간별 기본 조절 방향
        zone_adjustments = {
            PerformanceZone.COMFORT_ZONE: DifficultyTrend.INCREASE,
            PerformanceZone.OPTIMAL_ZONE: DifficultyTrend.MAINTAIN,
            PerformanceZone.CHALLENGE_ZONE: DifficultyTrend.ADAPTIVE,
            PerformanceZone.STRUGGLE_ZONE: DifficultyTrend.DECREASE
        }
        
        base_direction = zone_adjustments[zone]
        
        # 추가 요소 고려
        
        # 좌절 지표가 높으면 난이도 하락
        if metrics.frustration_indicators > 0.7:
            return DifficultyTrend.DECREASE
        
        # 신뢰도가 낮으면 유지 또는 하락
        if metrics.confidence_level < 0.4 and zone != PerformanceZone.COMFORT_ZONE:
            return DifficultyTrend.DECREASE if zone == PerformanceZone.STRUGGLE_ZONE else DifficultyTrend.MAINTAIN
        
        # 최근 개선이 있으면 도전적 조절
        if metrics.recent_improvements > 0.2:
            return DifficultyTrend.INCREASE if base_direction != DifficultyTrend.DECREASE else DifficultyTrend.ADAPTIVE
        
        # 참여도가 낮으면 난이도 조절로 흥미 유발
        if metrics.engagement_score < 0.4:
            return DifficultyTrend.ADAPTIVE
        
        return base_direction
    
    def _calculate_new_difficulty(
        self, 
        current_difficulty: int, 
        direction: DifficultyTrend, 
        metrics: DifficultyMetrics,
        performance_data: Dict[str, Any]
    ) -> int:
        """새로운 난이도 계산"""
        
        adjustment_size = self._calculate_adjustment_size(metrics, performance_data)
        
        if direction == DifficultyTrend.INCREASE:
            new_difficulty = current_difficulty + adjustment_size
        elif direction == DifficultyTrend.DECREASE:
            new_difficulty = current_difficulty - adjustment_size
        elif direction == DifficultyTrend.ADAPTIVE:
            # 점진적 조절 (성과에 따라 미세 조정)
            if metrics.current_accuracy > 0.6:
                new_difficulty = current_difficulty + adjustment_size // 2
            else:
                new_difficulty = current_difficulty - adjustment_size // 2
        else:  # MAINTAIN
            new_difficulty = current_difficulty
        
        # 범위 제한
        new_difficulty = max(
            self.adjustment_parameters['min_difficulty'],
            min(self.adjustment_parameters['max_difficulty'], new_difficulty)
        )
        
        # 최대 점프 제한
        max_jump = self.adjustment_parameters['max_difficulty_jump']
        if abs(new_difficulty - current_difficulty) > max_jump:
            if new_difficulty > current_difficulty:
                new_difficulty = current_difficulty + max_jump
            else:
                new_difficulty = current_difficulty - max_jump
        
        return new_difficulty
    
    def _calculate_adjustment_size(self, metrics: DifficultyMetrics, performance_data: Dict[str, Any]) -> int:
        """조절 크기 계산"""
        
        base_size = 1
        
        # 정확도에 따른 조절
        if metrics.current_accuracy >= 0.95 or metrics.current_accuracy <= 0.3:
            base_size = 2  # 극단적인 경우 큰 조절
        
        # 신뢰도에 따른 조절
        if metrics.confidence_level < 0.3:
            base_size = max(1, base_size - 1)  # 신뢰도 낮으면 작은 조절
        
        # 좌절 지표에 따른 조절
        if metrics.frustration_indicators > 0.8:
            base_size = min(2, base_size + 1)  # 좌절 높으면 큰 하향 조절
        
        return base_size
    
    def _calculate_frustration_indicators(self, recent_submissions: List[Dict]) -> float:
        """좌절 지표 계산"""
        
        if len(recent_submissions) < 3:
            return 0.0
        
        frustration_score = 0.0
        
        # 연속 오답 패널티
        consecutive_wrong = 0
        max_consecutive = 0
        
        for submission in recent_submissions:
            if not submission['is_correct']:
                consecutive_wrong += 1
                max_consecutive = max(max_consecutive, consecutive_wrong)
            else:
                consecutive_wrong = 0
        
        if max_consecutive >= 3:
            frustration_score += 0.4
        elif max_consecutive >= 2:
            frustration_score += 0.2
        
        # 응답 시간 급증 패널티
        response_times = [s.get('response_time', 60) for s in recent_submissions]
        if len(response_times) >= 3:
            recent_avg = np.mean(response_times[:3])
            earlier_avg = np.mean(response_times[3:6]) if len(response_times) >= 6 else recent_avg
            
            if recent_avg > earlier_avg * 1.5:  # 50% 이상 증가
                frustration_score += 0.3
        
        # 신뢰도 하락
        confidence_scores = [s.get('confidence_score', 0.5) for s in recent_submissions]
        if len(confidence_scores) >= 3:
            if np.mean(confidence_scores[:3]) < 0.3:
                frustration_score += 0.3
        
        return min(1.0, frustration_score)
    
    def _calculate_engagement_score(self, recent: List[Dict], extended: List[Dict]) -> float:
        """참여도 점수 계산"""
        
        if not recent:
            return 0.5
        
        engagement_score = 0.5  # 기본 점수
        
        # 제출 빈도
        if len(recent) >= 5:
            engagement_score += 0.2
        elif len(recent) >= 3:
            engagement_score += 0.1
        
        # 응답 시간 일관성 (너무 빠르거나 느리지 않음)
        response_times = [s.get('response_time', 60) for s in recent]
        if response_times:
            avg_time = np.mean(response_times)
            if 10 <= avg_time <= 120:  # 10초~2분 사이가 정상
                engagement_score += 0.1
        
        # 신뢰도 점수 (높은 신뢰도는 참여도 반영)
        confidence_scores = [s.get('confidence_score', 0.5) for s in recent]
        if confidence_scores and np.mean(confidence_scores) > 0.6:
            engagement_score += 0.2
        
        return min(1.0, engagement_score)
    
    async def _get_user_level(self, user_id: int) -> str:
        """사용자 레벨 조회"""
        
        try:
            # 전체 제출 통계 기반 레벨 판단
            total_submissions = self.db.query(SubmissionItem).join(Submission).filter(
                Submission.user_id == user_id
            ).count()
            
            if total_submissions < 10:
                return 'beginner'
            elif total_submissions < 50:
                return 'intermediate'
            else:
                return 'advanced'
                
        except Exception:
            return 'beginner'
    
    def _calculate_recommendation_confidence(self, metrics: DifficultyMetrics, performance_data: Dict[str, Any]) -> float:
        """추천 신뢰도 계산"""
        
        confidence = 0.5  # 기본 신뢰도
        
        # 데이터 충분성
        recent_count = len(performance_data['recent_submissions'])
        if recent_count >= 5:
            confidence += 0.3
        elif recent_count >= 3:
            confidence += 0.2
        
        # 성과 일관성
        if len(metrics.response_time_trend) > 1:
            time_std = np.std(metrics.response_time_trend)
            if time_std < 30:  # 응답시간이 일관됨
                confidence += 0.1
        
        # 신뢰도 수준
        if metrics.confidence_level > 0.7:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, direction: DifficultyTrend, zone: PerformanceZone, metrics: DifficultyMetrics) -> str:
        """추천 이유 생성"""
        
        reasons = []
        
        if zone == PerformanceZone.COMFORT_ZONE:
            reasons.append(f"현재 정확도 {metrics.current_accuracy:.1%}로 너무 쉬운 수준입니다")
        elif zone == PerformanceZone.OPTIMAL_ZONE:
            reasons.append(f"현재 정확도 {metrics.current_accuracy:.1%}로 적절한 도전 수준입니다")
        elif zone == PerformanceZone.STRUGGLE_ZONE:
            reasons.append(f"현재 정확도 {metrics.current_accuracy:.1%}로 어려움을 겪고 있습니다")
        
        if metrics.frustration_indicators > 0.5:
            reasons.append("좌절 지표가 감지되어 난이도 조절이 필요합니다")
        
        if metrics.recent_improvements > 0.1:
            reasons.append("최근 성과 개선이 있어 더 도전적인 문제를 시도할 수 있습니다")
        
        if metrics.engagement_score < 0.4:
            reasons.append("참여도가 낮아 흥미를 유발하는 난이도 조절이 필요합니다")
        
        return ". ".join(reasons) if reasons else "종합적인 성과 분석을 통한 추천입니다"
    
    def _predict_accuracy(self, new_difficulty: int, metrics: DifficultyMetrics) -> float:
        """예상 정확도 예측"""
        
        # 간단한 선형 모델 (실제로는 더 정교한 모델 사용 가능)
        base_accuracy = metrics.current_accuracy
        
        # 난이도 1 증가시 정확도 약 10% 감소 가정
        difficulty_impact = (new_difficulty - 2) * -0.1  # 난이도 2를 기준으로
        
        predicted = base_accuracy + difficulty_impact
        
        # 신뢰도와 개선도 반영
        confidence_factor = (metrics.confidence_level - 0.5) * 0.1
        improvement_factor = metrics.recent_improvements * 0.5
        
        predicted += confidence_factor + improvement_factor
        
        return max(0.1, min(0.95, predicted))
    
    def _estimate_adjustment_timeline(self, direction: DifficultyTrend) -> str:
        """조절 타임라인 추정"""
        
        if direction == DifficultyTrend.INCREASE:
            return "다음 3-5문제 후 재평가"
        elif direction == DifficultyTrend.DECREASE:
            return "즉시 적용, 3문제 후 재평가"
        elif direction == DifficultyTrend.ADAPTIVE:
            return "점진적 조절, 5문제 후 재평가"
        else:
            return "현재 난이도 유지, 5문제 후 재평가"
    
    async def _cache_difficulty_recommendation(self, user_id: int, topic: Optional[str], recommendation: DifficultyRecommendation):
        """난이도 추천 캐싱"""
        
        try:
            cache_key = f"difficulty_rec:{user_id}:{topic or 'general'}"
            cache_data = {
                'recommendation': {
                    'difficulty': recommendation.recommended_difficulty,
                    'confidence': recommendation.confidence,
                    'reasoning': recommendation.reasoning,
                    'expected_accuracy': recommendation.expected_accuracy,
                    'timeline': recommendation.adjustment_timeline
                },
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.redis_service.set_cache(cache_key, cache_data, 1800)  # 30분
            
        except Exception as e:
            logger.error(f"난이도 추천 캐싱 실패: {str(e)}")
    
    def _get_default_difficulty_recommendation(self, user_id: int, current_difficulty: Optional[int]) -> DifficultyRecommendation:
        """기본 난이도 추천"""
        
        default_difficulty = current_difficulty or 2
        
        return DifficultyRecommendation(
            recommended_difficulty=default_difficulty,
            confidence=0.5,
            reasoning="충분한 데이터가 없어 현재 난이도를 유지합니다",
            expected_accuracy=0.7,
            adjustment_timeline="더 많은 데이터 축적 후 재평가"
        )
    
    def _get_fallback_recommendation(self, current_difficulty: Optional[int]) -> DifficultyRecommendation:
        """폴백 추천"""
        
        return DifficultyRecommendation(
            recommended_difficulty=current_difficulty or 2,
            confidence=0.3,
            reasoning="시스템 오류로 인한 기본 추천",
            expected_accuracy=0.6,
            adjustment_timeline="시스템 복구 후 재평가"
        )
    
    async def get_next_question_difficulty(self, user_id: int, topic: str) -> int:
        """다음 문제 난이도 추천 (간단 버전)"""
        
        try:
            # 캐시된 추천 확인
            cache_key = f"difficulty_rec:{user_id}:{topic}"
            cached = self.redis_service.get_cache(cache_key)
            
            if cached and cached.get('recommendation'):
                return cached['recommendation']['difficulty']
            
            # 새로 계산
            current_difficulty = await self._get_current_difficulty(user_id, topic)
            recommendation = await self.calculate_optimal_difficulty(user_id, topic, current_difficulty)
            
            return recommendation.recommended_difficulty
            
        except Exception as e:
            logger.error(f"다음 문제 난이도 추천 실패: {str(e)}")
            return 2  # 기본 난이도
    
    async def _get_current_difficulty(self, user_id: int, topic: str) -> int:
        """현재 난이도 조회"""
        
        try:
            # 최근 제출된 문제의 난이도
            recent_submission = self.db.query(SubmissionItem).join(Submission).join(Question).filter(
                Submission.user_id == user_id,
                Question.topic == topic
            ).order_by(Submission.submitted_at.desc()).first()
            
            if recent_submission and hasattr(recent_submission, 'question'):
                return getattr(recent_submission.question, 'difficulty', 2)
            
            return 2  # 기본 난이도
            
        except Exception:
            return 2

# 전역 인스턴스 생성 함수
def get_adaptive_difficulty_engine(db: Session) -> AdaptiveDifficultyEngine:
    """적응형 난이도 엔진 인스턴스 반환"""
    return AdaptiveDifficultyEngine(db)
