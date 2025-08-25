"""
개인화된 AI 피드백 서비스 (Phase 2)
- 사용자 약점/강점 기반 맞춤 피드백
- 학습 패턴별 피드백 스타일 조정
- 커리어 목표 연계 개선 제안
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import logging
import json

from app.models.orm import (
    User, UserProgress, UserWeakness, UserTrackProgress, LearningGoal,
    LearningModule, Submission, SubmissionItem, Feedback
)
from app.services.llm_providers import get_llm_provider

logger = logging.getLogger(__name__)

class PersonalizedFeedbackService:
    """개인화된 AI 피드백 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_provider = get_llm_provider()
        
        # 학습자 유형별 피드백 스타일
        self.feedback_styles = {
            'fast_learner': {
                'tone': 'challenging',
                'detail_level': 'concise',
                'encouragement': 'achievement_focused',
                'suggestions': 'advanced_concepts'
            },
            'steady_learner': {
                'tone': 'supportive',
                'detail_level': 'moderate',
                'encouragement': 'progress_focused',
                'suggestions': 'step_by_step'
            },
            'thorough_learner': {
                'tone': 'detailed',
                'detail_level': 'comprehensive',
                'encouragement': 'understanding_focused',
                'suggestions': 'concept_reinforcement'
            },
            'developing_learner': {
                'tone': 'encouraging',
                'detail_level': 'detailed',
                'encouragement': 'effort_focused',
                'suggestions': 'foundational_review'
            }
        }
        
        # 약점 유형별 피드백 전략
        self.weakness_strategies = {
            'critical': {
                'priority': 'immediate_attention',
                'approach': 'focused_practice',
                'resources': 'targeted_exercises',
                'frequency': 'daily_practice'
            },
            'moderate': {
                'priority': 'scheduled_improvement',
                'approach': 'integrated_practice',
                'resources': 'complementary_materials',
                'frequency': 'regular_review'
            },
            'minor': {
                'priority': 'gradual_improvement',
                'approach': 'natural_integration',
                'resources': 'optional_exercises',
                'frequency': 'periodic_check'
            }
        }
    
    async def generate_personalized_feedback(
        self,
        user_id: int,
        submission_item_id: int,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        topic: str,
        question_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """개인화된 피드백 생성"""
        
        try:
            # 사용자 학습 프로필 조회
            user_profile = await self._get_user_learning_profile(user_id)
            
            # 약점 분석 및 업데이트
            weakness_analysis = await self._analyze_and_update_weaknesses(
                user_id, topic, is_correct, user_answer, correct_answer
            )
            
            # 개인화된 피드백 생성
            feedback_content = await self._generate_adaptive_feedback(
                user_profile=user_profile,
                weakness_analysis=weakness_analysis,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                topic=topic,
                question_context=question_context
            )
            
            # 피드백 저장
            feedback_record = await self._save_feedback_record(
                submission_item_id=submission_item_id,
                feedback_content=feedback_content,
                personalization_data={
                    'user_profile': user_profile['learning_pattern'],
                    'weakness_addressed': weakness_analysis.get('weakness_type'),
                    'feedback_style': user_profile['preferred_feedback_style']
                }
            )
            
            return {
                'success': True,
                'feedback': feedback_content,
                'personalization_applied': True,
                'learning_insights': weakness_analysis,
                'feedback_id': feedback_record.id if feedback_record else None
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized feedback for user {user_id}: {str(e)}")
            # 폴백: 기본 피드백 생성
            return await self._generate_fallback_feedback(
                user_answer, correct_answer, is_correct, topic
            )
    
    async def _get_user_learning_profile(self, user_id: int) -> Dict[str, Any]:
        """사용자 학습 프로필 조회"""
        
        # 사용자 기본 정보
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # 최근 진도 데이터
        recent_progress = self.db.query(UserProgress).filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.last_accessed_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).all()
        
        # 학습 패턴 분석
        learning_pattern = self._analyze_learning_pattern(recent_progress)
        
        # 현재 약점들
        current_weaknesses = self.db.query(UserWeakness).filter(
            and_(
                UserWeakness.user_id == user_id,
                UserWeakness.is_resolved == False
            )
        ).all()
        
        # 학습 목표
        learning_goals = self.db.query(LearningGoal).filter(
            and_(
                LearningGoal.user_id == user_id,
                LearningGoal.status == 'active'
            )
        ).all()
        
        # 트랙 진행 상황
        track_progress = self.db.query(UserTrackProgress).filter(
            UserTrackProgress.user_id == user_id
        ).all()
        
        return {
            'user_id': user_id,
            'learning_pattern': learning_pattern,
            'preferred_feedback_style': self.feedback_styles.get(learning_pattern, self.feedback_styles['steady_learner']),
            'current_weaknesses': current_weaknesses,
            'learning_goals': learning_goals,
            'track_progress': track_progress,
            'learning_velocity': self._calculate_learning_velocity(recent_progress),
            'preferred_difficulty': self._get_preferred_difficulty(track_progress),
            'industry_focus': self._get_industry_focus(track_progress)
        }
    
    async def _analyze_and_update_weaknesses(
        self,
        user_id: int,
        topic: str,
        is_correct: bool,
        user_answer: str,
        correct_answer: str
    ) -> Dict[str, Any]:
        """약점 분석 및 업데이트"""
        
        # 기존 약점 조회
        existing_weakness = self.db.query(UserWeakness).filter(
            and_(
                UserWeakness.user_id == user_id,
                UserWeakness.topic == topic,
                UserWeakness.is_resolved == False
            )
        ).first()
        
        if not is_correct:
            # 오답인 경우 약점 생성/업데이트
            if existing_weakness:
                # 기존 약점 업데이트
                existing_weakness.error_count += 1
                existing_weakness.last_updated_at = datetime.utcnow()
                
                # 정확도 재계산 (이동 평균)
                total_attempts = existing_weakness.error_count + max(1, existing_weakness.error_count * existing_weakness.accuracy_rate / (1 - existing_weakness.accuracy_rate))
                existing_weakness.accuracy_rate = max(0, (total_attempts - existing_weakness.error_count) / total_attempts)
                
                # 약점 심각도 업데이트
                if existing_weakness.error_count >= 5 and existing_weakness.accuracy_rate < 0.5:
                    existing_weakness.weakness_type = 'critical'
                elif existing_weakness.error_count >= 3 and existing_weakness.accuracy_rate < 0.7:
                    existing_weakness.weakness_type = 'moderate'
                else:
                    existing_weakness.weakness_type = 'minor'
                
                weakness_info = {
                    'weakness_id': existing_weakness.id,
                    'weakness_type': existing_weakness.weakness_type,
                    'error_count': existing_weakness.error_count,
                    'accuracy_rate': existing_weakness.accuracy_rate,
                    'is_new': False
                }
            else:
                # 새 약점 생성
                error_category = self._categorize_error(user_answer, correct_answer, topic)
                
                new_weakness = UserWeakness(
                    user_id=user_id,
                    category=error_category['category'],
                    subcategory=error_category['subcategory'],
                    topic=topic,
                    error_count=1,
                    accuracy_rate=0.0,
                    weakness_type='minor',
                    suggested_practice=await self._generate_practice_suggestion(topic, error_category)
                )
                
                self.db.add(new_weakness)
                self.db.flush()  # ID 생성을 위해
                
                weakness_info = {
                    'weakness_id': new_weakness.id,
                    'weakness_type': 'minor',
                    'error_count': 1,
                    'accuracy_rate': 0.0,
                    'is_new': True
                }
        else:
            # 정답인 경우 기존 약점 개선 반영
            if existing_weakness:
                # 정확도 개선
                total_attempts = existing_weakness.error_count + max(1, existing_weakness.error_count * existing_weakness.accuracy_rate / (1 - existing_weakness.accuracy_rate + 0.01))
                new_correct_answers = total_attempts - existing_weakness.error_count + 1
                existing_weakness.accuracy_rate = new_correct_answers / (total_attempts + 1)
                
                # 약점 해결 확인
                if existing_weakness.accuracy_rate > 0.8 and existing_weakness.error_count <= 2:
                    existing_weakness.is_resolved = True
                    existing_weakness.resolved_at = datetime.utcnow()
                    existing_weakness.improvement_trend = 'improving'
                
                weakness_info = {
                    'weakness_id': existing_weakness.id,
                    'improvement': True,
                    'new_accuracy': existing_weakness.accuracy_rate,
                    'is_resolved': existing_weakness.is_resolved
                }
            else:
                weakness_info = {'improvement': True, 'no_weakness_found': True}
        
        self.db.commit()
        return weakness_info
    
    async def _generate_adaptive_feedback(
        self,
        user_profile: Dict[str, Any],
        weakness_analysis: Dict[str, Any],
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        topic: str,
        question_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """적응형 피드백 생성"""
        
        feedback_style = user_profile['preferred_feedback_style']
        learning_pattern = user_profile['learning_pattern']
        
        # 프롬프트 구성
        system_prompt = self._build_personalized_system_prompt(
            feedback_style, learning_pattern, user_profile
        )
        
        # 컨텍스트 정보 구성
        context_info = {
            'topic': topic,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'weakness_analysis': weakness_analysis,
            'learning_goals': [goal.title for goal in user_profile['learning_goals']],
            'industry_focus': user_profile['industry_focus'],
            'question_context': question_context or {}
        }
        
        # 추가 지침 생성
        additional_guidance = self._generate_additional_guidance(
            user_profile, weakness_analysis, topic
        )
        
        user_prompt = f"""
답변 분석:
- 주제: {topic}
- 사용자 답변: {user_answer}
- 정답: {correct_answer}
- 결과: {'정답' if is_correct else '오답'}

약점 분석: {json.dumps(weakness_analysis, ensure_ascii=False, indent=2)}

추가 지침: {additional_guidance}

위 정보를 바탕으로 개인화된 피드백을 생성해주세요.
"""
        
        try:
            # LLM을 통한 피드백 생성
            feedback = await self.llm_provider.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            return feedback.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM feedback: {str(e)}")
            return self._generate_template_feedback(
                is_correct, topic, user_answer, correct_answer, feedback_style
            )
    
    def _build_personalized_system_prompt(
        self,
        feedback_style: Dict[str, str],
        learning_pattern: str,
        user_profile: Dict[str, Any]
    ) -> str:
        """개인화된 시스템 프롬프트 구성"""
        
        base_prompt = """당신은 개인화된 학습 피드백을 제공하는 AI 교육 전문가입니다."""
        
        # 학습자 유형별 톤 조정
        tone_guidance = {
            'challenging': "도전적이고 자극적인 톤으로, 더 높은 목표를 제시하세요.",
            'supportive': "지지적이고 격려하는 톤으로, 긍정적인 에너지를 전달하세요.",
            'detailed': "상세하고 분석적인 톤으로, 깊이 있는 설명을 제공하세요.",
            'encouraging': "격려하고 친근한 톤으로, 학습자의 노력을 인정하세요."
        }
        
        # 세부 수준 조정
        detail_guidance = {
            'concise': "핵심만 간결하게 전달하세요. 2-3문장 내외로 요약하세요.",
            'moderate': "적당한 수준의 설명을 제공하세요. 4-5문장 정도로 구성하세요.",
            'comprehensive': "상세하고 포괄적인 설명을 제공하세요. 개념의 배경과 응용까지 다루세요.",
            'detailed': "자세한 설명과 단계별 가이드를 제공하세요."
        }
        
        # 격려 방식 조정
        encouragement_guidance = {
            'achievement_focused': "성취와 목표 달성에 초점을 맞춘 격려를 하세요.",
            'progress_focused': "진전과 발전 과정에 초점을 맞춘 격려를 하세요.",
            'understanding_focused': "이해도와 학습 깊이에 초점을 맞춘 격려를 하세요.",
            'effort_focused': "노력과 시도 자체에 초점을 맞춘 격려를 하세요."
        }
        
        # 제안 방식 조정
        suggestion_guidance = {
            'advanced_concepts': "고급 개념이나 심화 학습을 제안하세요.",
            'step_by_step': "단계별 접근법과 체계적 학습을 제안하세요.",
            'concept_reinforcement': "기본 개념 강화와 반복 학습을 제안하세요.",
            'foundational_review': "기초 개념 복습과 토대 다지기를 제안하세요."
        }
        
        personalized_prompt = f"""
{base_prompt}

학습자 특성:
- 학습 패턴: {learning_pattern}
- 선호 난이도: {user_profile.get('preferred_difficulty', 2)}
- 업계 관심사: {user_profile.get('industry_focus', 'general')}
- 학습 속도: {user_profile.get('learning_velocity', 1.0):.1f}배

피드백 스타일 지침:
- 톤: {tone_guidance.get(feedback_style['tone'], '지지적이고 격려하는 톤')}
- 세부 수준: {detail_guidance.get(feedback_style['detail_level'], '적당한 수준의 설명')}
- 격려 방식: {encouragement_guidance.get(feedback_style['encouragement'], '진전에 초점을 맞춘 격려')}
- 제안 방식: {suggestion_guidance.get(feedback_style['suggestions'], '단계별 접근법 제안')}

피드백 구성 요소:
1. 답변에 대한 평가 (정답/오답 여부와 이유)
2. 개념 설명 (필요시)
3. 개인화된 격려와 조언
4. 구체적인 다음 단계 제안
5. 관련 실무 적용 팁 (업계 관심사 반영)

한국어로 응답하며, 친근하고 전문적인 교육자의 톤을 유지하세요.
"""
        
        return personalized_prompt
    
    def _generate_additional_guidance(
        self,
        user_profile: Dict[str, Any],
        weakness_analysis: Dict[str, Any],
        topic: str
    ) -> str:
        """추가 지침 생성"""
        
        guidance_parts = []
        
        # 약점 기반 지침
        if 'weakness_type' in weakness_analysis:
            weakness_type = weakness_analysis['weakness_type']
            strategy = self.weakness_strategies.get(weakness_type, {})
            
            if weakness_type == 'critical':
                guidance_parts.append("이는 중요한 약점 영역입니다. 집중적인 연습이 필요합니다.")
            elif weakness_type == 'moderate':
                guidance_parts.append("이 영역을 꾸준히 개선해나가면 전체적인 실력 향상에 도움됩니다.")
        
        # 학습 목표 연계
        if user_profile['learning_goals']:
            goal_titles = [goal.title for goal in user_profile['learning_goals']]
            guidance_parts.append(f"현재 학습 목표({', '.join(goal_titles[:2])})와 연계하여 설명해주세요.")
        
        # 업계 특화 조언
        if user_profile['industry_focus'] != 'general':
            industry = user_profile['industry_focus']
            guidance_parts.append(f"{industry} 업계에서의 실무 적용 관점을 포함해주세요.")
        
        # 학습 속도 반영
        velocity = user_profile.get('learning_velocity', 1.0)
        if velocity > 1.2:
            guidance_parts.append("빠른 학습 속도를 고려하여 심화 내용이나 응용 방법을 추가로 제안해주세요.")
        elif velocity < 0.8:
            guidance_parts.append("충분한 시간을 두고 단계별로 접근할 수 있는 방법을 제안해주세요.")
        
        return " ".join(guidance_parts) if guidance_parts else "일반적인 학습 조언을 제공해주세요."
    
    def _categorize_error(self, user_answer: str, correct_answer: str, topic: str) -> Dict[str, str]:
        """오류 분류"""
        
        # 간단한 오류 분류 로직 (실제로는 더 정교한 NLP 분석 필요)
        categories = {
            'syntax': ['문법', '구문', 'syntax'],
            'logic': ['논리', '순서', '흐름'],
            'concept': ['개념', '이해', '정의'],
            'debugging': ['오류', '버그', '디버깅']
        }
        
        for category, keywords in categories.items():
            if any(keyword in topic.lower() or keyword in user_answer.lower() for keyword in keywords):
                return {
                    'category': category,
                    'subcategory': topic.lower().replace(' ', '_')
                }
        
        return {
            'category': 'concept',
            'subcategory': topic.lower().replace(' ', '_')
        }
    
    async def _generate_practice_suggestion(self, topic: str, error_category: Dict[str, str]) -> str:
        """연습 제안 생성"""
        
        suggestions = {
            'syntax': f"{topic} 문법 규칙을 반복 연습하고 코드 작성 시 문법 체크를 습관화하세요.",
            'logic': f"{topic}의 실행 순서와 논리적 흐름을 단계별로 분석하는 연습을 하세요.",
            'concept': f"{topic}의 기본 개념을 다시 복습하고 실제 예제를 통해 이해를 깊이하세요.",
            'debugging': f"{topic} 관련 오류를 의도적으로 만들어보고 수정하는 연습을 하세요."
        }
        
        return suggestions.get(error_category['category'], f"{topic} 관련 기초 개념을 복습하세요.")
    
    def _generate_template_feedback(
        self,
        is_correct: bool,
        topic: str,
        user_answer: str,
        correct_answer: str,
        feedback_style: Dict[str, str]
    ) -> str:
        """템플릿 기반 피드백 생성 (폴백)"""
        
        if is_correct:
            return f"정답입니다! {topic}에 대한 이해가 잘 되어 있습니다. 다음 단계로 넘어가도 좋겠습니다."
        else:
            return f"아쉽게도 틀렸습니다. {topic}에서 정답은 '{correct_answer}'입니다. " \
                   f"'{user_answer}'와 차이점을 비교해보시고, 관련 개념을 다시 복습해보세요."
    
    async def _generate_fallback_feedback(
        self,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        topic: str
    ) -> Dict[str, Any]:
        """폴백 피드백 생성"""
        
        feedback = self._generate_template_feedback(
            is_correct, topic, user_answer, correct_answer, 
            self.feedback_styles['steady_learner']
        )
        
        return {
            'success': True,
            'feedback': feedback,
            'personalization_applied': False,
            'fallback_used': True
        }
    
    async def _save_feedback_record(
        self,
        submission_item_id: int,
        feedback_content: str,
        personalization_data: Dict[str, Any]
    ) -> Optional[Feedback]:
        """피드백 기록 저장"""
        
        try:
            feedback_record = Feedback(
                submission_item_id=submission_item_id,
                feedback_text=feedback_content,
                ai_generated=True,
                created_at=datetime.utcnow()
            )
            
            self.db.add(feedback_record)
            self.db.commit()
            
            return feedback_record
            
        except Exception as e:
            logger.error(f"Error saving feedback record: {str(e)}")
            self.db.rollback()
            return None
    
    def _analyze_learning_pattern(self, progress_data: List[UserProgress]) -> str:
        """학습 패턴 분석"""
        
        if not progress_data:
            return 'beginner'
        
        completed = [p for p in progress_data if p.status == 'completed']
        
        if len(completed) < 3:
            return 'developing_learner'
        
        # 최근 학습 성과 분석
        recent_completions = completed[-5:]
        avg_attempts = sum(p.total_attempts for p in recent_completions) / len(recent_completions)
        avg_success_rate = sum(
            p.successful_attempts / max(1, p.total_attempts) 
            for p in recent_completions
        ) / len(recent_completions)
        
        if avg_success_rate > 0.8 and avg_attempts < 3:
            return 'fast_learner'
        elif avg_success_rate > 0.6:
            return 'steady_learner'
        elif avg_attempts > 5:
            return 'thorough_learner'
        else:
            return 'developing_learner'
    
    def _calculate_learning_velocity(self, progress_data: List[UserProgress]) -> float:
        """학습 속도 계산"""
        
        if len(progress_data) < 2:
            return 1.0
        
        completed = [p for p in progress_data if p.status == 'completed']
        
        if len(completed) < 2:
            return 1.0
        
        # 평균 완료 시간 대비 실제 소요 시간
        total_estimated = len(completed) * 8 * 60  # 8시간 * 60분 기본 추정
        total_actual = sum(p.time_spent_minutes for p in completed)
        
        if total_actual == 0:
            return 1.0
        
        velocity = total_estimated / total_actual
        return max(0.5, min(2.0, velocity))  # 0.5-2.0 범위 제한
    
    def _get_preferred_difficulty(self, track_progress: List[UserTrackProgress]) -> int:
        """선호 난이도 계산"""
        
        if not track_progress:
            return 2
        
        active_tracks = [tp for tp in track_progress if tp.status in ['in_progress', 'not_started']]
        
        if active_tracks:
            return round(sum(tp.preferred_difficulty for tp in active_tracks) / len(active_tracks))
        
        return 2
    
    def _get_industry_focus(self, track_progress: List[UserTrackProgress]) -> str:
        """업계 관심사 파악"""
        
        if not track_progress:
            return 'general'
        
        industry_counts = {}
        for tp in track_progress:
            industry = tp.industry_preference
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        if industry_counts:
            return max(industry_counts, key=industry_counts.get)
        
        return 'general'

# 서비스 인스턴스 생성 헬퍼
def get_personalized_feedback_service(db: Session) -> PersonalizedFeedbackService:
    """개인화 피드백 서비스 인스턴스 반환"""
    return PersonalizedFeedbackService(db)
