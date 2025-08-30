"""
심층 학습 분석 시스템 - Phase 4
- 학습 패턴 AI 분석
- 개인화 학습 경로 추천
- 실력 성장 예측
- 학습 효율성 최적화
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.models.orm import User, Submission, SubmissionItem, UserProgress, UserWeakness, LearningGoal
from app.services.ai_providers import get_ai_provider_manager, ModelTier, generate_ai_response, analyze_learning_pattern
from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)

class LearnerType(Enum):
    """학습자 유형"""
    FAST_LEARNER = "fast_learner"           # 빠른 학습자
    DEEP_THINKER = "deep_thinker"           # 심층 사고자  
    PRACTICAL_LEARNER = "practical_learner" # 실무형 학습자
    STEADY_LEARNER = "steady_learner"       # 꾸준한 학습자
    STRUGGLING_LEARNER = "struggling_learner" # 도움 필요 학습자

class LearningPhase(Enum):
    """학습 단계"""
    BEGINNER = "beginner"       # 초급
    INTERMEDIATE = "intermediate" # 중급
    ADVANCED = "advanced"       # 고급
    EXPERT = "expert"          # 전문가

@dataclass
class LearningMetrics:
    """학습 메트릭"""
    accuracy_trend: List[float]
    response_time_trend: List[float]
    difficulty_progression: List[int]
    topic_mastery: Dict[str, float]
    consistency_score: float
    improvement_rate: float
    engagement_level: float

@dataclass
class LearnerProfile:
    """학습자 프로필"""
    learner_type: LearnerType
    learning_phase: LearningPhase
    strengths: List[str]
    weaknesses: List[str]
    preferred_difficulty: int
    optimal_session_length: int
    learning_style_preferences: List[str]
    motivation_factors: List[str]

class DeepLearningAnalyzer:
    """심층 학습 분석기"""
    
    def __init__(self, db: Session):
        self.db = db
        self.redis_service = get_redis_service()
        self.ai_provider = get_ai_provider_manager()
        
        # 분석 모델 파라미터
        self.analysis_window_days = 30
        self.min_submissions_for_analysis = 5
        
        # 학습자 유형 분류 기준
        self.learner_type_criteria = {
            LearnerType.FAST_LEARNER: {
                'avg_accuracy': 0.8,
                'avg_response_time': 30,  # 초
                'consistency_threshold': 0.7
            },
            LearnerType.DEEP_THINKER: {
                'avg_accuracy': 0.85,
                'avg_response_time': 90,
                'consistency_threshold': 0.8
            },
            LearnerType.PRACTICAL_LEARNER: {
                'project_completion_rate': 0.8,
                'coding_accuracy': 0.75,
                'theory_vs_practice_ratio': 0.3
            },
            LearnerType.STEADY_LEARNER: {
                'consistency_threshold': 0.9,
                'daily_engagement': 0.7,
                'improvement_rate': 0.1
            }
        }
    
    async def analyze_user_deeply(self, user_id: int, use_ai: bool = True) -> Dict[str, Any]:
        """사용자 심층 분석"""
        try:
            # 캐시 확인
            cache_key = f"deep_analysis:{user_id}"
            cached_result = self.redis_service.get_cache(cache_key)
            
            if cached_result:
                logger.info(f"심층 분석 캐시 히트: user {user_id}")
                return cached_result
            
            # 학습 데이터 수집
            learning_data = await self._collect_learning_data(user_id)
            
            if len(learning_data['submissions']) < self.min_submissions_for_analysis:
                return {
                    'success': False,
                    'error': 'insufficient_data',
                    'message': f'분석을 위해 최소 {self.min_submissions_for_analysis}개의 제출이 필요합니다.',
                    'current_submissions': len(learning_data['submissions'])
                }
            
            # 학습 메트릭 계산
            metrics = self._calculate_learning_metrics(learning_data)
            
            # 학습자 프로필 생성
            learner_profile = self._generate_learner_profile(metrics, learning_data)
            
            # AI 기반 심층 분석 (선택적)
            ai_insights = {}
            if use_ai:
                ai_insights = await self._generate_ai_insights(user_id, learning_data, metrics)
            
            # 개인화 추천 생성
            recommendations = await self._generate_personalized_recommendations(
                user_id, learner_profile, metrics, ai_insights
            )
            
            # 학습 경로 제안
            learning_path = await self._suggest_learning_path(user_id, learner_profile, metrics)
            
            # 결과 구성
            analysis_result = {
                'success': True,
                'user_id': user_id,
                'analysis_date': datetime.utcnow().isoformat(),
                'data_period_days': self.analysis_window_days,
                'submissions_analyzed': len(learning_data['submissions']),
                'learner_profile': {
                    'type': learner_profile.learner_type.value,
                    'phase': learner_profile.learning_phase.value,
                    'strengths': learner_profile.strengths,
                    'weaknesses': learner_profile.weaknesses,
                    'preferred_difficulty': learner_profile.preferred_difficulty,
                    'optimal_session_length': learner_profile.optimal_session_length,
                    'learning_style': learner_profile.learning_style_preferences,
                    'motivation_factors': learner_profile.motivation_factors
                },
                'learning_metrics': {
                    'overall_accuracy': np.mean(metrics.accuracy_trend) if metrics.accuracy_trend else 0,
                    'avg_response_time': np.mean(metrics.response_time_trend) if metrics.response_time_trend else 0,
                    'consistency_score': metrics.consistency_score,
                    'improvement_rate': metrics.improvement_rate,
                    'engagement_level': metrics.engagement_level,
                    'topic_mastery': metrics.topic_mastery,
                    'difficulty_progression': metrics.difficulty_progression
                },
                'ai_insights': ai_insights,
                'recommendations': recommendations,
                'learning_path': learning_path,
                'next_actions': await self._generate_next_actions(learner_profile, metrics)
            }
            
            # 캐시 저장 (6시간)
            self.redis_service.set_cache(cache_key, analysis_result, 21600)
            
            logger.info(f"사용자 {user_id} 심층 분석 완료 - 유형: {learner_profile.learner_type.value}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"심층 분석 실패 user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_analysis': await self._generate_basic_analysis(user_id)
            }
    
    async def _collect_learning_data(self, user_id: int) -> Dict[str, Any]:
        """학습 데이터 수집"""
        try:
            # 기간 설정
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=self.analysis_window_days)
            
            # 제출 기록 조회
            submissions = self.db.query(SubmissionItem).join(Submission).filter(
                Submission.user_id == user_id,
                Submission.submitted_at >= start_date
            ).order_by(Submission.submitted_at.asc()).all()
            
            # 사용자 진도 조회
            user_progress = self.db.query(UserProgress).filter(
                UserProgress.user_id == user_id
            ).all()
            
            # 약점 데이터 조회
            weaknesses = self.db.query(UserWeakness).filter(
                UserWeakness.user_id == user_id
            ).all()
            
            # 학습 목표 조회
            learning_goals = self.db.query(LearningGoal).filter(
                LearningGoal.user_id == user_id,
                LearningGoal.status == 'active'
            ).all()
            
            return {
                'submissions': [{
                    'id': s.id,
                    'question_id': s.question_id,
                    'user_answer': s.user_answer,
                    'is_correct': s.is_correct,
                    'response_time': s.response_time,
                    'submitted_at': s.submitted_at.isoformat(),
                    'topic': getattr(s.question, 'topic', 'unknown') if hasattr(s, 'question') else 'unknown',
                    'difficulty': getattr(s.question, 'difficulty', 1) if hasattr(s, 'question') else 1
                } for s in submissions],
                'progress': [{
                    'module_id': p.module_id,
                    'completion_rate': p.completion_rate,
                    'last_accessed': p.last_accessed.isoformat() if p.last_accessed else None,
                    'time_spent_minutes': p.time_spent_minutes
                } for p in user_progress],
                'weaknesses': [{
                    'topic': w.topic,
                    'weakness_type': w.weakness_type,
                    'confidence_level': w.confidence_level,
                    'improvement_suggestions': w.improvement_suggestions
                } for w in weaknesses],
                'learning_goals': [{
                    'goal_type': g.goal_type,
                    'target_completion_date': g.target_completion_date.isoformat() if g.target_completion_date else None,
                    'progress_percentage': g.progress_percentage,
                    'description': g.description
                } for g in learning_goals]
            }
            
        except Exception as e:
            logger.error(f"학습 데이터 수집 실패 user {user_id}: {str(e)}")
            return {'submissions': [], 'progress': [], 'weaknesses': [], 'learning_goals': []}
    
    def _calculate_learning_metrics(self, learning_data: Dict[str, Any]) -> LearningMetrics:
        """학습 메트릭 계산"""
        try:
            submissions = learning_data['submissions']
            
            if not submissions:
                return LearningMetrics(
                    accuracy_trend=[],
                    response_time_trend=[],
                    difficulty_progression=[],
                    topic_mastery={},
                    consistency_score=0.0,
                    improvement_rate=0.0,
                    engagement_level=0.0
                )
            
            # 정확도 트렌드
            accuracy_trend = [s['is_correct'] for s in submissions]
            
            # 응답 시간 트렌드  
            response_time_trend = [s['response_time'] or 60 for s in submissions]
            
            # 난이도 진행도
            difficulty_progression = [s['difficulty'] for s in submissions]
            
            # 주제별 숙련도
            topic_mastery = {}
            topic_submissions = {}
            
            for s in submissions:
                topic = s['topic']
                if topic not in topic_submissions:
                    topic_submissions[topic] = []
                topic_submissions[topic].append(s['is_correct'])
            
            for topic, correct_list in topic_submissions.items():
                topic_mastery[topic] = np.mean(correct_list)
            
            # 일관성 점수 (정확도의 표준편차 기반)
            if len(accuracy_trend) > 1:
                accuracy_values = [1.0 if x else 0.0 for x in accuracy_trend]
                consistency_score = 1.0 - np.std(accuracy_values)
            else:
                consistency_score = 1.0
            
            # 개선율 (첫 절반 vs 마지막 절반 정확도 비교)
            if len(accuracy_trend) >= 4:
                mid_point = len(accuracy_trend) // 2
                first_half_accuracy = np.mean([1.0 if x else 0.0 for x in accuracy_trend[:mid_point]])
                second_half_accuracy = np.mean([1.0 if x else 0.0 for x in accuracy_trend[mid_point:]])
                improvement_rate = second_half_accuracy - first_half_accuracy
            else:
                improvement_rate = 0.0
            
            # 참여도 (일일 학습 빈도 기반)
            submission_dates = [datetime.fromisoformat(s['submitted_at']).date() for s in submissions]
            unique_dates = len(set(submission_dates))
            total_days = (max(submission_dates) - min(submission_dates)).days + 1 if submission_dates else 1
            engagement_level = min(1.0, unique_dates / total_days)
            
            return LearningMetrics(
                accuracy_trend=accuracy_trend,
                response_time_trend=response_time_trend,
                difficulty_progression=difficulty_progression,
                topic_mastery=topic_mastery,
                consistency_score=max(0.0, min(1.0, consistency_score)),
                improvement_rate=improvement_rate,
                engagement_level=engagement_level
            )
            
        except Exception as e:
            logger.error(f"학습 메트릭 계산 실패: {str(e)}")
            return LearningMetrics([], [], [], {}, 0.0, 0.0, 0.0)
    
    def _generate_learner_profile(self, metrics: LearningMetrics, learning_data: Dict[str, Any]) -> LearnerProfile:
        """학습자 프로필 생성"""
        try:
            # 평균 지표 계산
            avg_accuracy = np.mean([1.0 if x else 0.0 for x in metrics.accuracy_trend]) if metrics.accuracy_trend else 0
            avg_response_time = np.mean(metrics.response_time_trend) if metrics.response_time_trend else 60
            
            # 학습자 유형 분류
            learner_type = self._classify_learner_type(avg_accuracy, avg_response_time, metrics)
            
            # 학습 단계 결정
            learning_phase = self._determine_learning_phase(avg_accuracy, metrics.topic_mastery)
            
            # 강점과 약점 식별
            strengths, weaknesses = self._identify_strengths_weaknesses(metrics, learning_data)
            
            # 선호 난이도
            preferred_difficulty = self._calculate_preferred_difficulty(metrics.difficulty_progression, metrics.accuracy_trend)
            
            # 최적 세션 길이 (분)
            optimal_session_length = self._estimate_optimal_session_length(avg_response_time, metrics.engagement_level)
            
            # 학습 스타일 선호도
            learning_style_preferences = self._infer_learning_style(metrics, learning_data)
            
            # 동기 부여 요소
            motivation_factors = self._identify_motivation_factors(metrics, learning_data)
            
            return LearnerProfile(
                learner_type=learner_type,
                learning_phase=learning_phase,
                strengths=strengths,
                weaknesses=weaknesses,
                preferred_difficulty=preferred_difficulty,
                optimal_session_length=optimal_session_length,
                learning_style_preferences=learning_style_preferences,
                motivation_factors=motivation_factors
            )
            
        except Exception as e:
            logger.error(f"학습자 프로필 생성 실패: {str(e)}")
            return LearnerProfile(
                learner_type=LearnerType.STEADY_LEARNER,
                learning_phase=LearningPhase.BEGINNER,
                strengths=['기본기'],
                weaknesses=['경험 부족'],
                preferred_difficulty=2,
                optimal_session_length=30,
                learning_style_preferences=['점진적 학습'],
                motivation_factors=['성취감']
            )
    
    def _classify_learner_type(self, avg_accuracy: float, avg_response_time: float, metrics: LearningMetrics) -> LearnerType:
        """학습자 유형 분류"""
        
        # 빠른 학습자: 높은 정확도 + 빠른 응답
        if avg_accuracy >= 0.8 and avg_response_time <= 30 and metrics.consistency_score >= 0.7:
            return LearnerType.FAST_LEARNER
        
        # 심층 사고자: 높은 정확도 + 느린 응답 + 높은 일관성
        elif avg_accuracy >= 0.85 and avg_response_time >= 60 and metrics.consistency_score >= 0.8:
            return LearnerType.DEEP_THINKER
        
        # 꾸준한 학습자: 높은 일관성 + 꾸준한 참여
        elif metrics.consistency_score >= 0.8 and metrics.engagement_level >= 0.7:
            return LearnerType.STEADY_LEARNER
        
        # 도움 필요 학습자: 낮은 정확도 또는 일관성
        elif avg_accuracy < 0.6 or metrics.consistency_score < 0.5:
            return LearnerType.STRUGGLING_LEARNER
        
        # 기본값: 실무형 학습자
        else:
            return LearnerType.PRACTICAL_LEARNER
    
    def _determine_learning_phase(self, avg_accuracy: float, topic_mastery: Dict[str, float]) -> LearningPhase:
        """학습 단계 결정"""
        
        mastered_topics = sum(1 for score in topic_mastery.values() if score >= 0.8)
        total_topics = len(topic_mastery)
        
        if total_topics == 0:
            return LearningPhase.BEGINNER
        
        mastery_ratio = mastered_topics / total_topics
        
        if avg_accuracy >= 0.9 and mastery_ratio >= 0.8:
            return LearningPhase.EXPERT
        elif avg_accuracy >= 0.8 and mastery_ratio >= 0.6:
            return LearningPhase.ADVANCED
        elif avg_accuracy >= 0.7 and mastery_ratio >= 0.4:
            return LearningPhase.INTERMEDIATE
        else:
            return LearningPhase.BEGINNER
    
    def _identify_strengths_weaknesses(self, metrics: LearningMetrics, learning_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """강점과 약점 식별"""
        
        strengths = []
        weaknesses = []
        
        # 정확도 기반
        avg_accuracy = np.mean([1.0 if x else 0.0 for x in metrics.accuracy_trend]) if metrics.accuracy_trend else 0
        if avg_accuracy >= 0.8:
            strengths.append("높은 정확도")
        elif avg_accuracy < 0.6:
            weaknesses.append("정확도 개선 필요")
        
        # 일관성 기반
        if metrics.consistency_score >= 0.8:
            strengths.append("일관된 성과")
        elif metrics.consistency_score < 0.6:
            weaknesses.append("성과 일관성 부족")
        
        # 개선율 기반
        if metrics.improvement_rate > 0.2:
            strengths.append("빠른 학습 개선")
        elif metrics.improvement_rate < -0.1:
            weaknesses.append("학습 정체")
        
        # 참여도 기반
        if metrics.engagement_level >= 0.7:
            strengths.append("높은 학습 참여도")
        elif metrics.engagement_level < 0.4:
            weaknesses.append("학습 참여도 부족")
        
        # 주제별 숙련도 기반
        for topic, mastery in metrics.topic_mastery.items():
            if mastery >= 0.9:
                strengths.append(f"{topic} 영역 숙련")
            elif mastery < 0.5:
                weaknesses.append(f"{topic} 영역 보완 필요")
        
        # 기본값 설정
        if not strengths:
            strengths = ["학습 의지"]
        if not weaknesses:
            weaknesses = ["지속적인 연습 필요"]
        
        return strengths[:5], weaknesses[:5]  # 최대 5개씩
    
    def _calculate_preferred_difficulty(self, difficulty_progression: List[int], accuracy_trend: List[bool]) -> int:
        """선호 난이도 계산"""
        
        if not difficulty_progression or not accuracy_trend:
            return 2  # 기본값
        
        # 난이도별 정확도 계산
        difficulty_accuracy = {}
        for diff, correct in zip(difficulty_progression, accuracy_trend):
            if diff not in difficulty_accuracy:
                difficulty_accuracy[diff] = []
            difficulty_accuracy[diff].append(1.0 if correct else 0.0)
        
        # 각 난이도별 평균 정확도
        difficulty_scores = {}
        for diff, correct_list in difficulty_accuracy.items():
            accuracy = np.mean(correct_list)
            # 적절한 도전 수준 (70-85% 정확도) 선호
            if 0.7 <= accuracy <= 0.85:
                difficulty_scores[diff] = accuracy
            elif accuracy > 0.85:
                difficulty_scores[diff] = accuracy * 0.8  # 너무 쉬움
            else:
                difficulty_scores[diff] = accuracy * 0.9  # 너무 어려움
        
        if difficulty_scores:
            preferred_diff = max(difficulty_scores.keys(), key=lambda x: difficulty_scores[x])
            return min(5, max(1, preferred_diff))
        
        return 2
    
    def _estimate_optimal_session_length(self, avg_response_time: float, engagement_level: float) -> int:
        """최적 세션 길이 추정 (분)"""
        
        # 기본 세션 길이 (분)
        base_session = 30
        
        # 응답 시간에 따른 조정
        if avg_response_time <= 20:
            time_factor = 1.2  # 빠른 응답자는 더 긴 세션
        elif avg_response_time >= 60:
            time_factor = 0.8  # 느린 응답자는 짧은 세션
        else:
            time_factor = 1.0
        
        # 참여도에 따른 조정
        engagement_factor = 0.5 + engagement_level  # 0.5 ~ 1.5
        
        optimal_length = int(base_session * time_factor * engagement_factor)
        return min(90, max(15, optimal_length))  # 15-90분 범위
    
    def _infer_learning_style(self, metrics: LearningMetrics, learning_data: Dict[str, Any]) -> List[str]:
        """학습 스타일 추론"""
        
        styles = []
        
        # 응답 시간 기반
        avg_response_time = np.mean(metrics.response_time_trend) if metrics.response_time_trend else 60
        if avg_response_time <= 30:
            styles.append("직관적 학습")
        elif avg_response_time >= 90:
            styles.append("분석적 학습")
        else:
            styles.append("균형적 학습")
        
        # 일관성 기반
        if metrics.consistency_score >= 0.8:
            styles.append("체계적 학습")
        else:
            styles.append("창의적 학습")
        
        # 난이도 선호도 기반
        if metrics.difficulty_progression:
            avg_difficulty = np.mean(metrics.difficulty_progression)
            if avg_difficulty >= 4:
                styles.append("도전적 학습")
            elif avg_difficulty <= 2:
                styles.append("점진적 학습")
            else:
                styles.append("적응형 학습")
        
        return styles[:3]  # 최대 3개
    
    def _identify_motivation_factors(self, metrics: LearningMetrics, learning_data: Dict[str, Any]) -> List[str]:
        """동기 부여 요소 식별"""
        
        factors = []
        
        # 개선율 기반
        if metrics.improvement_rate > 0.1:
            factors.append("성장 실감")
        
        # 일관성 기반
        if metrics.consistency_score >= 0.7:
            factors.append("성취감")
        
        # 참여도 기반
        if metrics.engagement_level >= 0.6:
            factors.append("학습 즐거움")
        
        # 목표 기반 (학습 목표 존재 여부)
        if learning_data.get('learning_goals'):
            factors.append("목표 지향성")
        
        # 경쟁 요소
        if metrics.topic_mastery and max(metrics.topic_mastery.values()) >= 0.8:
            factors.append("숙련도 추구")
        
        # 기본 동기 요소
        if not factors:
            factors = ["지식 습득", "실력 향상"]
        
        return factors[:4]  # 최대 4개
    
    async def _generate_ai_insights(self, user_id: int, learning_data: Dict[str, Any], metrics: LearningMetrics) -> Dict[str, Any]:
        """AI 기반 심층 인사이트 생성"""
        
        try:
            # AI 분석 요청
            ai_analysis = await analyze_learning_pattern(
                learning_data['submissions'],
                user_id,
                use_premium=False  # 기본적으로 무료 모델 사용
            )
            
            # 추가 AI 인사이트 생성
            insight_prompt = f"""다음 학습자의 상세 데이터를 분석하여 개인화된 학습 인사이트를 제공해주세요.

학습 메트릭:
- 평균 정확도: {np.mean([1.0 if x else 0.0 for x in metrics.accuracy_trend]) if metrics.accuracy_trend else 0:.2f}
- 일관성 점수: {metrics.consistency_score:.2f}
- 개선율: {metrics.improvement_rate:.2f}
- 참여도: {metrics.engagement_level:.2f}
- 주제별 숙련도: {json.dumps(metrics.topic_mastery, ensure_ascii=False)}

다음 관점에서 인사이트를 제공해주세요:
1. 학습자의 독특한 패턴이나 특성
2. 숨겨진 잠재력이나 강점
3. 예상되는 학습 장애물
4. 동기 유지 전략
5. 장기적 성장 예측

결과를 JSON 형태로 구조화해주세요."""

            ai_insights_response = await generate_ai_response(
                prompt=insight_prompt,
                task_type="analysis",
                model_preference=ModelTier.FREE,
                user_id=user_id,
                temperature=0.3
            )
            
            # JSON 파싱 시도
            try:
                ai_insights = json.loads(ai_insights_response.get('response', '{}'))
            except:
                ai_insights = {
                    'raw_insights': ai_insights_response.get('response', ''),
                    'parsing_error': True
                }
            
            # AI 분석 결과 통합
            combined_insights = {
                'pattern_analysis': ai_analysis,
                'detailed_insights': ai_insights,
                'ai_model_used': ai_insights_response.get('model', 'unknown'),
                'analysis_cost': ai_insights_response.get('cost_estimate', 0),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return combined_insights
            
        except Exception as e:
            logger.error(f"AI 인사이트 생성 실패: {str(e)}")
            return {
                'error': str(e),
                'fallback_insights': {
                    'pattern': '기본 분석만 가능',
                    'recommendation': '더 많은 데이터가 필요합니다'
                }
            }
    
    async def _generate_personalized_recommendations(
        self, 
        user_id: int, 
        profile: LearnerProfile, 
        metrics: LearningMetrics,
        ai_insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """개인화 추천 생성"""
        
        recommendations = []
        
        # 학습자 유형별 추천
        if profile.learner_type == LearnerType.FAST_LEARNER:
            recommendations.append({
                'type': 'difficulty_increase',
                'title': '도전적인 문제 시도',
                'description': '현재 수준보다 높은 난이도의 문제에 도전해보세요',
                'priority': 'high',
                'action': f'difficulty_{profile.preferred_difficulty + 1}_problems'
            })
        
        elif profile.learner_type == LearnerType.STRUGGLING_LEARNER:
            recommendations.append({
                'type': 'foundation_strengthening',
                'title': '기초 개념 복습',
                'description': '기본 개념을 다시 정리하고 연습문제를 풀어보세요',
                'priority': 'high',
                'action': 'review_basics'
            })
        
        # 약점 개선 추천
        for weakness in profile.weaknesses[:2]:  # 상위 2개 약점
            recommendations.append({
                'type': 'weakness_improvement',
                'title': f'{weakness} 집중 학습',
                'description': f'{weakness} 영역의 추가 학습 자료를 제공합니다',
                'priority': 'medium',
                'action': f'focus_on_{weakness.replace(" ", "_")}'
            })
        
        # 학습 스타일별 추천
        if '직관적 학습' in profile.learning_style_preferences:
            recommendations.append({
                'type': 'learning_style',
                'title': '빠른 문제 해결 연습',
                'description': '시간 제한이 있는 문제들로 직관력을 키워보세요',
                'priority': 'medium',
                'action': 'timed_practice'
            })
        
        # 참여도 기반 추천
        if metrics.engagement_level < 0.5:
            recommendations.append({
                'type': 'engagement_boost',
                'title': '학습 동기 향상 활동',
                'description': '게임화된 학습이나 그룹 활동에 참여해보세요',
                'priority': 'high',
                'action': 'gamified_learning'
            })
        
        return recommendations[:5]  # 최대 5개 추천
    
    async def _suggest_learning_path(
        self, 
        user_id: int, 
        profile: LearnerProfile, 
        metrics: LearningMetrics
    ) -> Dict[str, Any]:
        """학습 경로 제안"""
        
        # 현재 숙련도 기반 다음 단계 결정
        next_topics = []
        review_topics = []
        
        for topic, mastery in metrics.topic_mastery.items():
            if mastery >= 0.8:
                # 숙련된 주제 -> 심화 학습
                next_topics.append({
                    'topic': f'{topic}_advanced',
                    'type': 'advancement',
                    'difficulty': profile.preferred_difficulty + 1,
                    'estimated_time_weeks': 2
                })
            elif mastery < 0.6:
                # 부족한 주제 -> 복습 필요
                review_topics.append({
                    'topic': topic,
                    'type': 'review',
                    'difficulty': max(1, profile.preferred_difficulty - 1),
                    'estimated_time_weeks': 1
                })
        
        # 학습 단계별 경로
        phase_progression = {
            LearningPhase.BEGINNER: 'intermediate_foundations',
            LearningPhase.INTERMEDIATE: 'advanced_concepts',
            LearningPhase.ADVANCED: 'expert_applications',
            LearningPhase.EXPERT: 'specialization_tracks'
        }
        
        next_phase_focus = phase_progression.get(profile.learning_phase, 'continued_practice')
        
        return {
            'current_phase': profile.learning_phase.value,
            'next_phase_focus': next_phase_focus,
            'review_needed': review_topics,
            'advancement_ready': next_topics,
            'recommended_weekly_hours': profile.optimal_session_length * 3 // 60,  # 주 3회 기준
            'milestone_timeline': {
                '1_week': 'Review and consolidation',
                '1_month': 'Next difficulty level mastery',
                '3_months': 'Phase advancement',
                '6_months': 'Specialization exploration'
            }
        }
    
    async def _generate_next_actions(self, profile: LearnerProfile, metrics: LearningMetrics) -> List[Dict[str, str]]:
        """다음 액션 제안"""
        
        actions = []
        
        # 즉시 실행 가능한 액션들
        actions.append({
            'title': '오늘의 학습 세션',
            'description': f'{profile.optimal_session_length}분간 난이도 {profile.preferred_difficulty} 문제 풀기',
            'timeframe': 'today',
            'category': 'practice'
        })
        
        if metrics.consistency_score < 0.7:
            actions.append({
                'title': '일정한 학습 패턴 만들기',
                'description': '매일 같은 시간에 짧은 학습 세션 진행',
                'timeframe': 'this_week',
                'category': 'habit'
            })
        
        if profile.weaknesses:
            actions.append({
                'title': f'{profile.weaknesses[0]} 보완 학습',
                'description': '약점 영역의 기초 개념부터 차근차근 학습',
                'timeframe': 'this_week',
                'category': 'improvement'
            })
        
        actions.append({
            'title': '학습 목표 설정',
            'description': '다음 달까지의 구체적인 학습 목표를 세우고 계획 수립',
            'timeframe': 'this_week',
            'category': 'planning'
        })
        
        return actions
    
    async def _generate_basic_analysis(self, user_id: int) -> Dict[str, Any]:
        """기본 분석 (폴백)"""
        
        return {
            'success': True,
            'user_id': user_id,
            'analysis_type': 'basic_fallback',
            'learner_profile': {
                'type': LearnerType.STEADY_LEARNER.value,
                'phase': LearningPhase.BEGINNER.value,
                'message': '더 많은 학습 데이터가 축적되면 상세한 분석이 가능합니다'
            },
            'recommendations': [
                {
                    'type': 'general',
                    'title': '꾸준한 학습 지속',
                    'description': '규칙적인 학습 습관을 만들어보세요',
                    'priority': 'high'
                }
            ]
        }

# 전역 인스턴스 생성 함수
def get_deep_learning_analyzer(db: Session) -> DeepLearningAnalyzer:
    """심층 학습 분석기 인스턴스 반환"""
    return DeepLearningAnalyzer(db)
