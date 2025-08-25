"""
고급 커리큘럼 추천 엔진 (Phase 2)
- 사용자 진도/약점 기반 개인화 추천
- 3가지 커리어 경로 특화 알고리즘
- 업계별 특화 모듈 우선순위
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import math
import logging

from app.models.orm import (
    User, CurriculumCategory, LearningTrack, LearningModule, LearningResource,
    UserProgress, UserWeakness, UserTrackProgress, LearningGoal, PersonalizedRecommendation
)

logger = logging.getLogger(__name__)

class AdvancedCurriculumRecommendationEngine:
    """고급 커리큘럼 추천 엔진"""
    
    def __init__(self, db: Session):
        self.db = db
        self.algorithm_version = "v2.0-phase2"
        
        # 커리어 경로별 가중치
        self.career_weights = {
            'saas_development': {
                'foundation': 0.4,
                'development': 0.5,
                'specialization': 0.1
            },
            'react_specialist': {
                'foundation': 0.2,
                'development': 0.6,
                'specialization': 0.2
            },
            'data_engineering_advanced': {
                'foundation': 0.3,
                'development': 0.4,
                'specialization': 0.3
            }
        }
        
        # 업계별 우선순위
        self.industry_priorities = {
            'fintech': ['security', 'api-design', 'data-processing', 'testing'],
            'ecommerce': ['scalability', 'ui-ux', 'payment-systems', 'analytics'],
            'enterprise': ['integration', 'security', 'documentation', 'architecture']
        }
    
    async def get_personalized_recommendations(
        self, 
        user_id: int, 
        recommendation_type: str = "next_module",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """사용자 맞춤 추천 생성"""
        
        try:
            # 사용자 정보 및 진도 조회
            user_data = await self._get_user_learning_profile(user_id)
            
            if not user_data:
                return await self._get_beginner_recommendations(user_id, limit)
            
            # 추천 타입별 분기
            if recommendation_type == "next_module":
                recommendations = await self._recommend_next_modules(user_data, limit)
            elif recommendation_type == "skill_reinforcement":
                recommendations = await self._recommend_skill_reinforcement(user_data, limit)
            elif recommendation_type == "career_path":
                recommendations = await self._recommend_career_advancement(user_data, limit)
            else:
                recommendations = await self._recommend_next_modules(user_data, limit)
            
            # 추천 기록 저장
            await self._save_recommendation_records(user_id, recommendations, recommendation_type)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {str(e)}")
            return []
    
    async def _get_user_learning_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """사용자 학습 프로필 조회"""
        
        # 기본 사용자 정보
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 트랙 진행 상황
        track_progress = self.db.query(UserTrackProgress).filter(
            UserTrackProgress.user_id == user_id
        ).all()
        
        # 모듈별 진행 상황  
        module_progress = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
        
        # 약점 분석
        weaknesses = self.db.query(UserWeakness).filter(
            and_(
                UserWeakness.user_id == user_id,
                UserWeakness.is_resolved == False
            )
        ).all()
        
        # 학습 목표
        goals = self.db.query(LearningGoal).filter(
            and_(
                LearningGoal.user_id == user_id,
                LearningGoal.status == 'active'
            )
        ).all()
        
        # 프로필 생성
        profile = {
            'user_id': user_id,
            'user': user,
            'track_progress': {tp.track_id: tp for tp in track_progress},
            'module_progress': {mp.module_id: mp for mp in module_progress if mp.module_id},
            'weaknesses': weaknesses,
            'goals': goals,
            'learning_velocity': self._calculate_learning_velocity(module_progress),
            'preferred_difficulty': self._get_preferred_difficulty(track_progress),
            'industry_preference': self._get_industry_preference(track_progress),
            'dominant_learning_pattern': self._analyze_learning_pattern(module_progress)
        }
        
        return profile
    
    async def _recommend_next_modules(self, user_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """다음 학습 모듈 추천"""
        
        recommendations = []
        
        # 현재 진행 중인 트랙들
        active_tracks = [
            tp for tp in user_data['track_progress'].values()
            if tp.status in ['in_progress', 'not_started']
        ]
        
        for track_progress in active_tracks:
            track = self.db.query(LearningTrack).filter(
                LearningTrack.id == track_progress.track_id
            ).first()
            
            if not track:
                continue
                
            # 트랙의 모든 모듈 조회
            modules = self.db.query(LearningModule).filter(
                LearningModule.track_id == track.id
            ).order_by(LearningModule.difficulty_level, LearningModule.created_at).all()
            
            # 다음 추천 모듈 찾기
            next_module = self._find_next_module_in_track(
                modules, 
                user_data['module_progress'],
                user_data['preferred_difficulty'],
                user_data['industry_preference']
            )
            
            if next_module:
                confidence = self._calculate_recommendation_confidence(
                    next_module, user_data, track_progress
                )
                
                reasoning = self._generate_recommendation_reasoning(
                    next_module, user_data, track_progress, "next_module"
                )
                
                recommendations.append({
                    'module_id': next_module.id,
                    'module': next_module,
                    'track': track,
                    'confidence_score': confidence,
                    'reasoning': reasoning,
                    'estimated_completion_time': self._estimate_completion_time(
                        next_module, user_data['learning_velocity']
                    ),
                    'prerequisites_met': self._check_prerequisites(
                        next_module, user_data['module_progress']
                    ),
                    'difficulty_match': self._calculate_difficulty_match(
                        next_module, user_data['preferred_difficulty']
                    )
                })
        
        # 약점 기반 추천 추가
        weakness_recommendations = await self._get_weakness_based_recommendations(
            user_data, limit // 2
        )
        recommendations.extend(weakness_recommendations)
        
        # 신규 트랙 추천 (진도가 빠른 경우)
        if user_data['learning_velocity'] > 1.2:
            new_track_recommendations = await self._recommend_new_tracks(
                user_data, limit // 3
            )
            recommendations.extend(new_track_recommendations)
        
        # 신뢰도순 정렬 및 제한
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        return recommendations[:limit]
    
    async def _recommend_skill_reinforcement(self, user_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """약점 보완을 위한 추천"""
        
        recommendations = []
        
        # 약점별 우선순위 계산
        critical_weaknesses = [
            w for w in user_data['weaknesses'] 
            if w.weakness_type == 'critical'
        ]
        
        moderate_weaknesses = [
            w for w in user_data['weaknesses']
            if w.weakness_type == 'moderate'
        ]
        
        # 심각한 약점 우선 처리
        for weakness in critical_weaknesses[:limit]:
            reinforcement_modules = self._find_reinforcement_modules(weakness)
            
            for module in reinforcement_modules:
                confidence = 0.9  # 약점 기반 추천은 높은 신뢰도
                
                reasoning = f"'{weakness.topic}' 영역의 약점 보완을 위한 집중 학습이 필요합니다. " \
                          f"현재 정확도: {weakness.accuracy_rate:.1%}, " \
                          f"평균 소요 시간: {weakness.avg_time_taken:.1f}초"
                
                recommendations.append({
                    'module_id': module.id,
                    'module': module,
                    'track': self.db.query(LearningTrack).filter(
                        LearningTrack.id == module.track_id
                    ).first(),
                    'confidence_score': confidence,
                    'reasoning': reasoning,
                    'weakness_addressed': weakness,
                    'priority_level': 'critical',
                    'estimated_improvement': self._estimate_skill_improvement(weakness, module)
                })
        
        # 중간 약점 추가 (공간이 있으면)
        remaining_slots = limit - len(recommendations)
        for weakness in moderate_weaknesses[:remaining_slots]:
            reinforcement_modules = self._find_reinforcement_modules(weakness)
            
            if reinforcement_modules:
                module = reinforcement_modules[0]  # 첫 번째만
                
                recommendations.append({
                    'module_id': module.id,
                    'module': module,
                    'track': self.db.query(LearningTrack).filter(
                        LearningTrack.id == module.track_id
                    ).first(),
                    'confidence_score': 0.75,
                    'reasoning': f"'{weakness.topic}' 기술 향상을 위한 보완 학습",
                    'weakness_addressed': weakness,
                    'priority_level': 'moderate',
                    'estimated_improvement': self._estimate_skill_improvement(weakness, module)
                })
        
        return recommendations
    
    async def _recommend_career_advancement(self, user_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """커리어 발전을 위한 추천"""
        
        recommendations = []
        
        # 사용자의 주요 커리어 목표 파악
        career_goals = [
            goal for goal in user_data['goals']
            if goal.goal_type == 'career_milestone'
        ]
        
        if not career_goals:
            # 기본 커리어 경로 추천
            return await self._get_default_career_recommendations(user_data, limit)
        
        for goal in career_goals:
            # 목표 달성을 위한 트랙 분석
            target_tracks = goal.target_tracks
            
            for track_id in target_tracks:
                track = self.db.query(LearningTrack).filter(
                    LearningTrack.id == track_id
                ).first()
                
                if not track:
                    continue
                
                # 해당 트랙의 고급 모듈들 조회
                advanced_modules = self.db.query(LearningModule).filter(
                    and_(
                        LearningModule.track_id == track_id,
                        LearningModule.difficulty_level >= 3,
                        LearningModule.module_type.in_(['specialization', 'project'])
                    )
                ).all()
                
                for module in advanced_modules:
                    if module.id not in user_data['module_progress']:
                        confidence = self._calculate_career_advancement_confidence(
                            module, goal, user_data
                        )
                        
                        reasoning = f"'{goal.title}' 목표 달성을 위한 전문 기술 습득. " \
                                  f"이 모듈은 {track.display_name}의 핵심 역량을 강화합니다."
                        
                        recommendations.append({
                            'module_id': module.id,
                            'module': module,
                            'track': track,
                            'confidence_score': confidence,
                            'reasoning': reasoning,
                            'career_goal': goal,
                            'advancement_type': 'specialization',
                            'business_impact': self._assess_business_impact(module, goal)
                        })
        
        # 신뢰도순 정렬
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        return recommendations[:limit]
    
    def _find_next_module_in_track(
        self, 
        modules: List[LearningModule], 
        module_progress: Dict[int, UserProgress],
        preferred_difficulty: int,
        industry_preference: str
    ) -> Optional[LearningModule]:
        """트랙 내에서 다음 모듈 찾기"""
        
        for module in modules:
            # 이미 완료된 모듈은 제외
            if module.id in module_progress:
                progress = module_progress[module.id]
                if progress.status == 'completed':
                    continue
                elif progress.status == 'in_progress':
                    return module  # 진행 중인 모듈 우선 반환
            
            # 전제조건 확인
            if not self._check_prerequisites(module, module_progress):
                continue
            
            # 난이도 적합성 확인  
            if abs(module.difficulty_level - preferred_difficulty) > 2:
                continue
            
            # 업계 선호도 반영
            if industry_preference != 'general':
                if module.industry_focus == industry_preference:
                    return module  # 업계 특화 모듈 우선
                elif module.industry_focus != 'general':
                    continue  # 다른 업계 특화 모듈은 제외
            
            # 조건을 만족하는 첫 번째 모듈 반환
            return module
        
        return None
    
    def _check_prerequisites(self, module: LearningModule, module_progress: Dict[int, UserProgress]) -> bool:
        """모듈 전제조건 확인"""
        
        if not module.prerequisites:
            return True
        
        # 모든 전제조건 모듈이 완료되었는지 확인
        for prereq_name in module.prerequisites:
            # 전제조건 모듈 찾기 (이름 기준)
            prereq_module = self.db.query(LearningModule).filter(
                LearningModule.name == prereq_name
            ).first()
            
            if prereq_module:
                if prereq_module.id not in module_progress:
                    return False
                
                progress = module_progress[prereq_module.id]
                if progress.status != 'completed':
                    return False
        
        return True
    
    def _calculate_recommendation_confidence(
        self, 
        module: LearningModule, 
        user_data: Dict[str, Any],
        track_progress: UserTrackProgress
    ) -> float:
        """추천 신뢰도 계산"""
        
        confidence = 0.5  # 기본 신뢰도
        
        # 난이도 적합성 (+0.2)
        difficulty_match = self._calculate_difficulty_match(
            module, user_data['preferred_difficulty']
        )
        confidence += difficulty_match * 0.2
        
        # 학습 속도 반영 (+0.15)
        velocity_factor = min(1.0, user_data['learning_velocity'] / 1.5)
        confidence += velocity_factor * 0.15
        
        # 업계 선호도 (+0.1)
        if module.industry_focus == user_data['industry_preference']:
            confidence += 0.1
        
        # 트랙 진행률 (+0.1)
        if track_progress.modules_completed > 0:
            completion_rate = track_progress.modules_completed / max(1, track_progress.total_modules)
            confidence += completion_rate * 0.1
        
        # 전제조건 충족 (+0.05)
        if self._check_prerequisites(module, user_data['module_progress']):
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def _calculate_difficulty_match(self, module: LearningModule, preferred_difficulty: int) -> float:
        """난이도 매칭 점수 계산"""
        
        diff = abs(module.difficulty_level - preferred_difficulty)
        
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.8
        elif diff == 2:
            return 0.5
        else:
            return 0.2
    
    def _generate_recommendation_reasoning(
        self, 
        module: LearningModule, 
        user_data: Dict[str, Any],
        track_progress: UserTrackProgress,
        rec_type: str
    ) -> str:
        """추천 이유 생성"""
        
        reasons = []
        
        if rec_type == "next_module":
            # 기본 추천 이유
            track = self.db.query(LearningTrack).filter(
                LearningTrack.id == track_progress.track_id
            ).first()
            
            reasons.append(f"{track.display_name} 과정의 다음 단계 학습")
            
            # 난이도 적합성
            if module.difficulty_level == user_data['preferred_difficulty']:
                reasons.append("현재 학습 수준에 적합한 난이도")
            elif module.difficulty_level == user_data['preferred_difficulty'] + 1:
                reasons.append("단계적 난이도 상승으로 실력 향상")
            
            # 업계 특화
            if module.industry_focus == user_data['industry_preference']:
                reasons.append(f"{user_data['industry_preference']} 업계 특화 기술")
            
            # 학습 패턴 반영
            if user_data['learning_velocity'] > 1.2:
                reasons.append("빠른 학습 속도에 맞춘 심화 학습")
            
            # 예상 완료 시간
            completion_time = self._estimate_completion_time(
                module, user_data['learning_velocity']
            )
            reasons.append(f"예상 완료 시간: {completion_time}시간")
        
        return " | ".join(reasons)
    
    def _estimate_completion_time(self, module: LearningModule, learning_velocity: float) -> int:
        """모듈 완료 예상 시간 계산"""
        
        base_hours = module.estimated_hours or 8
        adjusted_hours = base_hours / learning_velocity
        
        return max(1, round(adjusted_hours))
    
    def _calculate_learning_velocity(self, module_progress: List[UserProgress]) -> float:
        """학습 속도 계산"""
        
        if not module_progress:
            return 1.0
        
        completed_modules = [mp for mp in module_progress if mp.status == 'completed']
        
        if len(completed_modules) < 2:
            return 1.0
        
        # 최근 완료 모듈들의 평균 소요 시간 계산
        total_time = sum(mp.time_spent_minutes for mp in completed_modules[-5:])  # 최근 5개
        total_estimated = sum(
            (self.db.query(LearningModule).filter(LearningModule.id == mp.module_id).first().estimated_hours or 8) * 60
            for mp in completed_modules[-5:]
        )
        
        if total_estimated == 0:
            return 1.0
        
        # 실제 시간 / 예상 시간의 역수 = 학습 속도
        velocity = total_estimated / max(1, total_time)
        
        # 0.5 ~ 2.0 범위로 제한
        return max(0.5, min(2.0, velocity))
    
    def _get_preferred_difficulty(self, track_progress: List[UserTrackProgress]) -> int:
        """선호 난이도 계산"""
        
        if not track_progress:
            return 2  # 기본값
        
        # 진행 중인 트랙들의 선호 난이도 평균
        active_tracks = [tp for tp in track_progress if tp.status in ['in_progress', 'not_started']]
        
        if active_tracks:
            avg_difficulty = sum(tp.preferred_difficulty for tp in active_tracks) / len(active_tracks)
            return max(1, min(5, round(avg_difficulty)))
        
        return 2
    
    def _get_industry_preference(self, track_progress: List[UserTrackProgress]) -> str:
        """업계 선호도 파악"""
        
        if not track_progress:
            return 'general'
        
        # 가장 많이 선택된 업계
        industry_counts = {}
        for tp in track_progress:
            industry = tp.industry_preference
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        if industry_counts:
            return max(industry_counts, key=industry_counts.get)
        
        return 'general'
    
    def _analyze_learning_pattern(self, module_progress: List[UserProgress]) -> str:
        """학습 패턴 분석"""
        
        if not module_progress:
            return 'beginner'
        
        completed = [mp for mp in module_progress if mp.status == 'completed']
        
        if len(completed) < 3:
            return 'beginner'
        
        # 최근 학습 패턴 분석
        recent_completions = completed[-5:]
        avg_attempts = sum(mp.total_attempts for mp in recent_completions) / len(recent_completions)
        avg_success_rate = sum(
            mp.successful_attempts / max(1, mp.total_attempts) 
            for mp in recent_completions
        ) / len(recent_completions)
        
        if avg_success_rate > 0.8 and avg_attempts < 3:
            return 'fast_learner'
        elif avg_success_rate > 0.6:
            return 'steady_learner'
        elif avg_attempts > 5:
            return 'thorough_learner'
        else:
            return 'developing_learner'
    
    async def _get_beginner_recommendations(self, user_id: int, limit: int) -> List[Dict[str, Any]]:
        """초보자를 위한 기본 추천"""
        
        # Foundation 카테고리의 가장 기초적인 모듈들
        foundation_modules = self.db.query(LearningModule).join(LearningTrack).filter(
            and_(
                LearningTrack.category == 'foundation',
                LearningModule.difficulty_level == 1,
                LearningModule.prerequisites == []
            )
        ).order_by(LearningTrack.difficulty_level, LearningModule.created_at).limit(limit).all()
        
        recommendations = []
        for module in foundation_modules:
            track = self.db.query(LearningTrack).filter(LearningTrack.id == module.track_id).first()
            
            recommendations.append({
                'module_id': module.id,
                'module': module,
                'track': track,
                'confidence_score': 0.8,
                'reasoning': "프로그래밍 학습의 첫 단계로 추천되는 기초 과정",
                'estimated_completion_time': module.estimated_hours,
                'prerequisites_met': True,
                'is_beginner_friendly': True
            })
        
        return recommendations
    
    async def _get_weakness_based_recommendations(self, user_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """약점 기반 추천"""
        
        recommendations = []
        
        for weakness in user_data['weaknesses'][:limit]:
            modules = self._find_reinforcement_modules(weakness)
            
            if modules:
                module = modules[0]
                track = self.db.query(LearningTrack).filter(
                    LearningTrack.id == module.track_id
                ).first()
                
                recommendations.append({
                    'module_id': module.id,
                    'module': module,
                    'track': track,
                    'confidence_score': 0.85,
                    'reasoning': f"'{weakness.topic}' 약점 보완을 위한 집중 학습",
                    'weakness_type': weakness.weakness_type,
                    'improvement_expected': True
                })
        
        return recommendations
    
    def _find_reinforcement_modules(self, weakness: UserWeakness) -> List[LearningModule]:
        """약점 보완을 위한 모듈 찾기"""
        
        # 태그 기반 모듈 검색
        related_modules = self.db.query(LearningModule).filter(
            or_(
                LearningModule.tags.contains([weakness.subcategory]),
                LearningModule.tags.contains([weakness.topic]),
                LearningModule.name.ilike(f"%{weakness.topic}%")
            )
        ).limit(3).all()
        
        return related_modules
    
    def _estimate_skill_improvement(self, weakness: UserWeakness, module: LearningModule) -> Dict[str, Any]:
        """기술 향상 예상치 계산"""
        
        current_accuracy = weakness.accuracy_rate
        expected_improvement = 0.15 + (module.difficulty_level * 0.05)  # 15-40% 향상 예상
        
        return {
            'current_accuracy': current_accuracy,
            'expected_accuracy': min(1.0, current_accuracy + expected_improvement),
            'improvement_percentage': expected_improvement,
            'estimated_practice_time': module.estimated_hours * 1.5  # 복습 시간 포함
        }
    
    async def _recommend_new_tracks(self, user_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """새로운 트랙 추천"""
        
        # 아직 시작하지 않은 트랙들
        enrolled_track_ids = list(user_data['track_progress'].keys())
        
        available_tracks = self.db.query(LearningTrack).filter(
            ~LearningTrack.id.in_(enrolled_track_ids)
        ).order_by(LearningTrack.difficulty_level).limit(limit).all()
        
        recommendations = []
        for track in available_tracks:
            # 첫 번째 모듈 추천
            first_module = self.db.query(LearningModule).filter(
                and_(
                    LearningModule.track_id == track.id,
                    LearningModule.prerequisites == []
                )
            ).order_by(LearningModule.difficulty_level).first()
            
            if first_module:
                recommendations.append({
                    'module_id': first_module.id,
                    'module': first_module,
                    'track': track,
                    'confidence_score': 0.7,
                    'reasoning': f"새로운 영역 확장: {track.display_name} 시작",
                    'is_new_track': True,
                    'track_preview': True
                })
        
        return recommendations
    
    async def _get_default_career_recommendations(self, user_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """기본 커리어 추천"""
        
        # 현재 진행률 기반으로 다음 단계 커리어 모듈 추천
        specialization_modules = self.db.query(LearningModule).join(LearningTrack).filter(
            and_(
                LearningTrack.category == 'specialization',
                LearningModule.difficulty_level >= 3
            )
        ).limit(limit).all()
        
        recommendations = []
        for module in specialization_modules:
            track = self.db.query(LearningTrack).filter(LearningTrack.id == module.track_id).first()
            
            recommendations.append({
                'module_id': module.id,
                'module': module,
                'track': track,
                'confidence_score': 0.6,
                'reasoning': "전문성 강화를 위한 심화 과정",
                'career_advancement': True
            })
        
        return recommendations
    
    def _calculate_career_advancement_confidence(
        self, 
        module: LearningModule, 
        goal: LearningGoal, 
        user_data: Dict[str, Any]
    ) -> float:
        """커리어 발전 추천 신뢰도"""
        
        confidence = 0.6  # 기본값
        
        # 목표 우선순위 반영
        confidence += (goal.priority_level / 5) * 0.2
        
        # 모듈 난이도와 사용자 수준 매칭
        difficulty_match = self._calculate_difficulty_match(
            module, user_data['preferred_difficulty']
        )
        confidence += difficulty_match * 0.1
        
        # 목표 진행률 반영
        if goal.progress_percentage > 0.5:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _assess_business_impact(self, module: LearningModule, goal: LearningGoal) -> str:
        """비즈니스 임팩트 평가"""
        
        impact_levels = {
            'high': "실무 프로젝트에 즉시 적용 가능한 핵심 기술",
            'medium': "업무 효율성 향상에 도움되는 실용적 기술", 
            'low': "장기적 성장에 도움되는 기반 기술"
        }
        
        # 모듈 태그와 목표 유형 기반 판단
        if module.module_type == 'project':
            return impact_levels['high']
        elif module.difficulty_level >= 4:
            return impact_levels['medium']
        else:
            return impact_levels['low']
    
    async def _save_recommendation_records(
        self, 
        user_id: int, 
        recommendations: List[Dict[str, Any]], 
        rec_type: str
    ) -> None:
        """추천 기록 저장"""
        
        try:
            for rec in recommendations:
                recommendation_record = PersonalizedRecommendation(
                    user_id=user_id,
                    recommendation_type=rec_type,
                    recommended_item_type='module',
                    recommended_item_id=rec['module_id'],
                    reasoning=rec['reasoning'],
                    confidence_score=rec['confidence_score'],
                    algorithm_version=self.algorithm_version
                )
                
                self.db.add(recommendation_record)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error saving recommendation records: {str(e)}")
            self.db.rollback()

# 추천 엔진 인스턴스 생성 헬퍼 함수
def get_recommendation_engine(db: Session) -> AdvancedCurriculumRecommendationEngine:
    """추천 엔진 인스턴스 반환"""
    return AdvancedCurriculumRecommendationEngine(db)
