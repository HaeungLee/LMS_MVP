"""
Phase 10: 고급 학습 분석 시스템
- 심층 학습 패턴 분석
- 예측적 성과 모델링
- 개인화된 학습 경로 추천
- 실시간 개선 제안
"""

import asyncio
import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.redis_service import get_redis_service
from app.services.ai_providers import AIProviderManager, AIRequest
from app.models.orm import User, Subject, Question, Submission
from app.core.database import get_db

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """분석 유형"""
    PERFORMANCE_TREND = "performance_trend"
    LEARNING_PATTERN = "learning_pattern"
    WEAKNESS_ANALYSIS = "weakness_analysis"
    STRENGTH_MAPPING = "strength_mapping"
    PREDICTIVE_MODELING = "predictive_modeling"
    COMPARATIVE_ANALYSIS = "comparative_analysis"

class InsightLevel(Enum):
    """인사이트 수준"""
    BASIC = "basic"           # 기본 통계
    INTERMEDIATE = "intermediate"  # 패턴 분석
    ADVANCED = "advanced"     # 예측 모델링
    EXPERT = "expert"         # 심층 AI 분석

@dataclass
class LearningTrend:
    """학습 추세"""
    period: str
    accuracy_trend: float  # 정답률 변화율
    speed_trend: float     # 속도 변화율
    consistency_trend: float  # 일관성 변화율
    engagement_trend: float   # 참여도 변화율
    difficulty_progression: float  # 난이도 진전도

@dataclass
class WeaknessAnalysis:
    """약점 분석"""
    topic: str
    severity: float  # 0.0-1.0
    frequency: int   # 틀린 횟수
    pattern_type: str  # careless, conceptual, procedural
    improvement_potential: float  # 개선 가능성
    recommended_actions: List[str]

@dataclass
class StrengthMapping:
    """강점 매핑"""
    topic: str
    proficiency_level: float  # 숙련도
    consistency: float
    teaching_potential: float  # 다른 사람을 가르칠 수 있는 정도
    advanced_readiness: float  # 고급 학습 준비도

@dataclass
class PredictiveInsight:
    """예측 인사이트"""
    prediction_type: str
    target_metric: str
    current_value: float
    predicted_value: float
    confidence: float
    time_horizon: str  # 예측 기간
    factors: List[str]  # 영향 요인들

@dataclass
class LearningAnalyticsReport:
    """학습 분석 보고서"""
    user_id: int
    subject_key: str
    analysis_period: str
    generated_at: datetime
    
    # 핵심 지표
    overall_score: float
    learning_velocity: float
    mastery_prediction: Dict[str, float]
    
    # 상세 분석
    trends: List[LearningTrend]
    weaknesses: List[WeaknessAnalysis]
    strengths: List[StrengthMapping]
    predictions: List[PredictiveInsight]
    
    # 추천사항
    immediate_actions: List[str]
    strategic_recommendations: List[str]
    resource_suggestions: List[str]

class EnhancedLearningAnalytics:
    """고급 학습 분석 시스템"""
    
    def __init__(self):
        self.redis_service = get_redis_service()
        self.ai_provider = AIProviderManager()
        
        # 분석 설정
        self.config = {
            "min_data_points": 10,
            "trend_analysis_period": 30,  # 일
            "prediction_horizon": 14,  # 일
            "weakness_threshold": 0.6,  # 정답률 임계값
            "strength_threshold": 0.85,
            "confidence_threshold": 0.7
        }
    
    async def generate_comprehensive_report(
        self,
        user_id: int,
        subject_key: str,
        analysis_type: AnalysisType = AnalysisType.PERFORMANCE_TREND,
        insight_level: InsightLevel = InsightLevel.INTERMEDIATE,
        db: Session = None
    ) -> LearningAnalyticsReport:
        """종합 학습 분석 보고서 생성"""
        
        try:
            logger.info(f"학습 분석 시작: {user_id} - {subject_key} ({insight_level.value})")
            
            # 1. 학습 데이터 수집
            learning_data = await self._collect_learning_data(user_id, subject_key, db)
            
            if len(learning_data['submissions']) < self.config["min_data_points"]:
                return await self._generate_minimal_report(user_id, subject_key, learning_data)
            
            # 2. 추세 분석
            trends = await self._analyze_learning_trends(learning_data)
            
            # 3. 약점 분석
            weaknesses = await self._analyze_weaknesses(learning_data, db)
            
            # 4. 강점 매핑
            strengths = await self._map_strengths(learning_data, db)
            
            # 5. 예측 모델링 (고급 수준 이상)
            predictions = []
            if insight_level in [InsightLevel.ADVANCED, InsightLevel.EXPERT]:
                predictions = await self._generate_predictions(learning_data, trends)
            
            # 6. AI 기반 심층 분석 (전문가 수준)
            ai_insights = []
            if insight_level == InsightLevel.EXPERT:
                ai_insights = await self._generate_ai_insights(
                    user_id, subject_key, learning_data, trends, weaknesses, strengths
                )
            
            # 7. 추천사항 생성
            recommendations = await self._generate_recommendations(
                learning_data, trends, weaknesses, strengths, predictions
            )
            
            # 8. 종합 점수 계산
            overall_score = self._calculate_overall_score(trends, weaknesses, strengths)
            learning_velocity = self._calculate_learning_velocity(trends)
            mastery_prediction = await self._predict_mastery_timeline(
                user_id, subject_key, learning_data, trends
            )
            
            # 보고서 구성
            report = LearningAnalyticsReport(
                user_id=user_id,
                subject_key=subject_key,
                analysis_period=f"최근 {self.config['trend_analysis_period']}일",
                generated_at=datetime.utcnow(),
                overall_score=overall_score,
                learning_velocity=learning_velocity,
                mastery_prediction=mastery_prediction,
                trends=trends,
                weaknesses=weaknesses,
                strengths=strengths,
                predictions=predictions,
                immediate_actions=recommendations.get('immediate', []),
                strategic_recommendations=recommendations.get('strategic', []),
                resource_suggestions=recommendations.get('resources', [])
            )
            
            # 캐싱
            await self._cache_analysis_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"학습 분석 실패: {str(e)}")
            raise
    
    async def get_real_time_insights(
        self,
        user_id: int,
        current_session_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """실시간 학습 인사이트"""
        
        try:
            # 현재 세션 분석
            session_performance = self._analyze_current_session(current_session_data)
            
            # 즉시 피드백 생성
            immediate_feedback = await self._generate_immediate_feedback(
                user_id, session_performance, db
            )
            
            # 적응형 제안
            adaptive_suggestions = await self._generate_adaptive_suggestions(
                user_id, session_performance, db
            )
            
            return {
                "session_analysis": session_performance,
                "immediate_feedback": immediate_feedback,
                "adaptive_suggestions": adaptive_suggestions,
                "confidence_boost": self._calculate_confidence_boost(session_performance),
                "next_recommended_action": await self._get_next_action(user_id, session_performance, db)
            }
            
        except Exception as e:
            logger.error(f"실시간 인사이트 생성 실패: {str(e)}")
            return {"error": "실시간 분석 실패"}
    
    async def compare_with_peers(
        self,
        user_id: int,
        subject_key: str,
        comparison_group: str = "similar_level",
        db: Session = None
    ) -> Dict[str, Any]:
        """동급생 비교 분석"""
        
        try:
            # 사용자 데이터
            user_data = await self._collect_learning_data(user_id, subject_key, db)
            
            # 비교군 데이터
            peer_data = await self._collect_peer_data(subject_key, comparison_group, db)
            
            if not peer_data:
                return {"error": "비교 데이터 부족"}
            
            # 비교 분석
            comparison = {
                "accuracy_percentile": self._calculate_percentile(
                    user_data['avg_accuracy'], [p['accuracy'] for p in peer_data]
                ),
                "speed_percentile": self._calculate_percentile(
                    user_data['avg_response_time'], [p['response_time'] for p in peer_data], reverse=True
                ),
                "consistency_percentile": self._calculate_percentile(
                    user_data['consistency'], [p['consistency'] for p in peer_data]
                ),
                "improvement_rate_percentile": self._calculate_percentile(
                    user_data['improvement_rate'], [p['improvement_rate'] for p in peer_data]
                )
            }
            
            # 상대적 강약점 분석
            relative_analysis = self._analyze_relative_performance(user_data, peer_data)
            
            # 개선 가능성 평가
            improvement_potential = self._assess_improvement_potential(comparison, relative_analysis)
            
            return {
                "comparison_group": comparison_group,
                "peer_count": len(peer_data),
                "percentile_rankings": comparison,
                "relative_strengths": relative_analysis['strengths'],
                "relative_weaknesses": relative_analysis['weaknesses'],
                "improvement_potential": improvement_potential,
                "peer_learning_strategies": await self._extract_peer_strategies(peer_data)
            }
            
        except Exception as e:
            logger.error(f"동급생 비교 분석 실패: {str(e)}")
            return {"error": "비교 분석 실패"}
    
    # ========== 내부 분석 메서드들 ==========
    
    async def _collect_learning_data(
        self,
        user_id: int,
        subject_key: str,
        db: Session
    ) -> Dict[str, Any]:
        """학습 데이터 수집"""
        
        # 최근 제출 데이터
        recent_submissions = db.execute(text("""
            SELECT s.*, q.difficulty, q.topic, q.question_type
            FROM submissions s
            JOIN questions q ON s.question_id = q.id
            WHERE s.user_id = :user_id 
            AND q.subject = :subject_key
            AND s.submitted_at >= NOW() - INTERVAL '30 days'
            ORDER BY s.submitted_at DESC
            LIMIT 100
        """), {"user_id": user_id, "subject_key": subject_key}).fetchall()
        
        # 기본 통계 계산
        submissions_data = []
        for sub in recent_submissions:
            submissions_data.append({
                "id": sub.id,
                "question_id": sub.question_id,
                "is_correct": sub.is_correct,
                "response_time": getattr(sub, 'response_time', 60),
                "submitted_at": sub.submitted_at.isoformat(),
                "difficulty": getattr(sub, 'difficulty', 'medium'),
                "topic": getattr(sub, 'topic', 'general'),
                "question_type": getattr(sub, 'question_type', 'multiple_choice')
            })
        
        # 집계 통계
        if submissions_data:
            avg_accuracy = sum(1 for s in submissions_data if s['is_correct']) / len(submissions_data)
            avg_response_time = sum(s['response_time'] for s in submissions_data) / len(submissions_data)
            consistency = self._calculate_consistency_score(submissions_data)
            improvement_rate = self._calculate_improvement_rate(submissions_data)
        else:
            avg_accuracy = 0.0
            avg_response_time = 60.0
            consistency = 0.5
            improvement_rate = 0.0
        
        return {
            "submissions": submissions_data,
            "avg_accuracy": avg_accuracy,
            "avg_response_time": avg_response_time,
            "consistency": consistency,
            "improvement_rate": improvement_rate,
            "total_questions": len(submissions_data),
            "study_period_days": 30
        }
    
    async def _analyze_learning_trends(self, learning_data: Dict[str, Any]) -> List[LearningTrend]:
        """학습 추세 분석"""
        
        submissions = learning_data['submissions']
        if len(submissions) < 7:  # 최소 1주일 데이터
            return []
        
        # 주간별 데이터 분리
        weekly_data = self._group_by_weeks(submissions)
        
        trends = []
        for week_idx, (week_name, week_data) in enumerate(weekly_data.items()):
            if week_idx == 0:  # 첫 주는 비교 대상이 없음
                continue
            
            prev_week = list(weekly_data.values())[week_idx - 1]
            
            # 추세 계산
            accuracy_trend = self._calculate_trend(
                [s['is_correct'] for s in prev_week],
                [s['is_correct'] for s in week_data]
            )
            
            speed_trend = self._calculate_trend(
                [s['response_time'] for s in prev_week],
                [s['response_time'] for s in week_data],
                reverse=True  # 시간은 낮을수록 좋음
            )
            
            trends.append(LearningTrend(
                period=week_name,
                accuracy_trend=accuracy_trend,
                speed_trend=speed_trend,
                consistency_trend=0.0,  # 간소화
                engagement_trend=0.0,
                difficulty_progression=0.0
            ))
        
        return trends
    
    async def _analyze_weaknesses(
        self,
        learning_data: Dict[str, Any],
        db: Session
    ) -> List[WeaknessAnalysis]:
        """약점 분석"""
        
        submissions = learning_data['submissions']
        
        # 토픽별 성과 분석
        topic_performance = {}
        for sub in submissions:
            topic = sub['topic']
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0, 'errors': []}
            
            topic_performance[topic]['total'] += 1
            if sub['is_correct']:
                topic_performance[topic]['correct'] += 1
            else:
                topic_performance[topic]['errors'].append(sub)
        
        # 약점 식별
        weaknesses = []
        for topic, perf in topic_performance.items():
            if perf['total'] < 3:  # 충분한 데이터 없음
                continue
            
            accuracy = perf['correct'] / perf['total']
            if accuracy < self.config['weakness_threshold']:
                severity = 1.0 - accuracy
                
                weaknesses.append(WeaknessAnalysis(
                    topic=topic,
                    severity=severity,
                    frequency=len(perf['errors']),
                    pattern_type=self._classify_error_pattern(perf['errors']),
                    improvement_potential=self._assess_improvement_potential_topic(perf),
                    recommended_actions=self._generate_weakness_actions(topic, severity)
                ))
        
        # 심각도 순 정렬
        weaknesses.sort(key=lambda x: x.severity, reverse=True)
        
        return weaknesses[:5]  # 상위 5개 약점
    
    async def _map_strengths(
        self,
        learning_data: Dict[str, Any],
        db: Session
    ) -> List[StrengthMapping]:
        """강점 매핑"""
        
        submissions = learning_data['submissions']
        
        # 토픽별 성과 분석
        topic_performance = {}
        for sub in submissions:
            topic = sub['topic']
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0, 'times': []}
            
            topic_performance[topic]['total'] += 1
            topic_performance[topic]['times'].append(sub['response_time'])
            if sub['is_correct']:
                topic_performance[topic]['correct'] += 1
        
        # 강점 식별
        strengths = []
        for topic, perf in topic_performance.items():
            if perf['total'] < 3:
                continue
            
            accuracy = perf['correct'] / perf['total']
            if accuracy >= self.config['strength_threshold']:
                avg_time = sum(perf['times']) / len(perf['times'])
                consistency = self._calculate_topic_consistency(perf)
                
                strengths.append(StrengthMapping(
                    topic=topic,
                    proficiency_level=accuracy,
                    consistency=consistency,
                    teaching_potential=min(accuracy * consistency, 1.0),
                    advanced_readiness=self._assess_advanced_readiness(accuracy, avg_time, consistency)
                ))
        
        # 숙련도 순 정렬
        strengths.sort(key=lambda x: x.proficiency_level, reverse=True)
        
        return strengths[:5]  # 상위 5개 강점
    
    def _calculate_consistency_score(self, submissions: List[Dict[str, Any]]) -> float:
        """일관성 점수 계산"""
        if len(submissions) < 5:
            return 0.5
        
        # 연속된 결과의 일관성 측정
        results = [1 if s['is_correct'] else 0 for s in submissions]
        consistency_count = 0
        
        for i in range(1, len(results)):
            if results[i] == results[i-1]:
                consistency_count += 1
        
        return consistency_count / (len(results) - 1)
    
    def _calculate_improvement_rate(self, submissions: List[Dict[str, Any]]) -> float:
        """향상 속도 계산"""
        if len(submissions) < 10:
            return 0.0
        
        # 시간순 정렬
        sorted_subs = sorted(submissions, key=lambda x: x['submitted_at'])
        
        # 전반부와 후반부 비교
        mid_point = len(sorted_subs) // 2
        first_half = sorted_subs[:mid_point]
        second_half = sorted_subs[mid_point:]
        
        first_accuracy = sum(1 for s in first_half if s['is_correct']) / len(first_half)
        second_accuracy = sum(1 for s in second_half if s['is_correct']) / len(second_half)
        
        return second_accuracy - first_accuracy
    
    def _calculate_overall_score(
        self,
        trends: List[LearningTrend],
        weaknesses: List[WeaknessAnalysis],
        strengths: List[StrengthMapping]
    ) -> float:
        """종합 점수 계산"""
        
        # 기본 점수 (강점 기반)
        strength_score = sum(s.proficiency_level for s in strengths) / max(len(strengths), 1) if strengths else 0.5
        
        # 약점 패널티
        weakness_penalty = sum(w.severity for w in weaknesses) / max(len(weaknesses), 1) if weaknesses else 0.0
        
        # 추세 보너스
        trend_bonus = 0.0
        if trends:
            recent_trends = trends[-3:]  # 최근 3주
            avg_accuracy_trend = sum(t.accuracy_trend for t in recent_trends) / len(recent_trends)
            trend_bonus = max(0, avg_accuracy_trend) * 0.2
        
        # 종합 계산
        overall = strength_score - (weakness_penalty * 0.3) + trend_bonus
        
        return max(0.0, min(1.0, overall))
    
    def _calculate_learning_velocity(self, trends: List[LearningTrend]) -> float:
        """학습 속도 계산"""
        if not trends:
            return 0.5
        
        # 최근 추세들의 평균
        recent_trends = trends[-4:]  # 최근 4주
        
        velocity_factors = []
        for trend in recent_trends:
            # 정확도 향상과 속도 향상을 결합
            combined_improvement = (trend.accuracy_trend + trend.speed_trend) / 2
            velocity_factors.append(combined_improvement)
        
        avg_velocity = sum(velocity_factors) / len(velocity_factors)
        
        # 0.0-1.0 범위로 정규화
        return max(0.0, min(1.0, (avg_velocity + 1.0) / 2.0))
    
    async def _cache_analysis_report(self, report: LearningAnalyticsReport):
        """분석 보고서 캐싱"""
        cache_key = f"learning_analytics:{report.user_id}:{report.subject_key}"
        
        # 직렬화 가능한 형태로 변환
        cache_data = {
            "user_id": report.user_id,
            "subject_key": report.subject_key,
            "overall_score": report.overall_score,
            "learning_velocity": report.learning_velocity,
            "generated_at": report.generated_at.isoformat(),
            "trend_count": len(report.trends),
            "weakness_count": len(report.weaknesses),
            "strength_count": len(report.strengths)
        }
        
        self.redis_service.set_cache(cache_key, cache_data, 3600)  # 1시간 캐시


def get_enhanced_learning_analytics() -> EnhancedLearningAnalytics:
    """고급 학습 분석 시스템 인스턴스 반환"""
    return EnhancedLearningAnalytics()
