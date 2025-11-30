"""add_performance_indexes

데이터베이스 쿼리 성능 최적화를 위한 복합 인덱스 추가

Revision ID: f1a2b3c4d5e6
Revises: b2ffb027ab6d
Create Date: 2025-11-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'b2ffb027ab6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    성능 최적화를 위한 인덱스 추가
    
    1. 자주 사용되는 쿼리 패턴에 대한 복합 인덱스
    2. 정렬/필터링 조합 최적화
    3. JOIN 성능 개선
    """
    
    # ============================================
    # submissions 테이블 - 대시보드 쿼리 최적화
    # ============================================
    # 사용자별 최근 제출 조회 (user_id + submitted_at DESC)
    op.create_index(
        'idx_submissions_user_submitted',
        'submissions',
        ['user_id', sa.text('submitted_at DESC')],
        unique=False
    )
    
    # 과목별 통계 쿼리 최적화 (subject + submitted_at)
    op.create_index(
        'idx_submissions_subject_date',
        'submissions',
        ['subject', 'submitted_at'],
        unique=False
    )
    
    # ============================================
    # submission_items 테이블 - 채점 쿼리 최적화
    # ============================================
    # 토픽별 정답률 분석 (topic + score)
    op.create_index(
        'idx_submission_items_topic_score',
        'submission_items',
        ['topic', 'score'],
        unique=False
    )
    
    # question_id로 빠른 조회 (FK이지만 인덱스 없음)
    op.create_index(
        'idx_submission_items_question_id',
        'submission_items',
        ['question_id'],
        unique=False
    )
    
    # ============================================
    # questions 테이블 - 문제 조회 최적화
    # ============================================
    # 과목+난이도 필터링 (가장 빈번한 쿼리 패턴)
    op.create_index(
        'idx_questions_subject_difficulty',
        'questions',
        ['subject', 'difficulty'],
        unique=False
    )
    
    # 활성 문제만 조회하는 경우
    op.create_index(
        'idx_questions_active_subject',
        'questions',
        ['is_active', 'subject'],
        unique=False
    )
    
    # 토픽+활성 상태
    op.create_index(
        'idx_questions_topic_active',
        'questions',
        ['topic', 'is_active'],
        unique=False
    )
    
    # ============================================
    # user_progress 테이블 - 학습 진도 조회 최적화
    # ============================================
    # 사용자별 최근 접근 순
    op.create_index(
        'idx_user_progress_user_last_accessed',
        'user_progress',
        ['user_id', sa.text('last_accessed_at DESC')],
        unique=False
    )
    
    # 트랙별 완료율 분석
    op.create_index(
        'idx_user_progress_track_status',
        'user_progress',
        ['track_id', 'status'],
        unique=False
    )
    
    # ============================================
    # ai_teaching_sessions 테이블 - 세션 조회 최적화
    # ============================================
    # 사용자별 최근 세션
    op.create_index(
        'idx_ai_sessions_user_activity',
        'ai_teaching_sessions',
        ['user_id', sa.text('last_activity_at DESC')],
        unique=False
    )
    
    # ============================================
    # feedbacks 테이블 - 피드백 조회 최적화
    # ============================================
    # AI 생성 피드백 필터
    op.create_index(
        'idx_feedbacks_ai_generated',
        'feedbacks',
        ['ai_generated', 'created_at'],
        unique=False
    )
    
    # ============================================
    # refresh_tokens 테이블 - 토큰 검증 최적화
    # ============================================
    # 만료되지 않은 유효 토큰 조회
    op.create_index(
        'idx_refresh_tokens_valid',
        'refresh_tokens',
        ['user_id', 'revoked', 'expires_at'],
        unique=False
    )
    
    # ============================================
    # student_assignments 테이블 - 과제 조회 최적화
    # ============================================
    # 사용자+과목 조합
    op.create_index(
        'idx_student_assignments_user_subject',
        'student_assignments',
        ['user_id', 'subject'],
        unique=False
    )


def downgrade() -> None:
    """인덱스 제거"""
    
    # student_assignments
    op.drop_index('idx_student_assignments_user_subject', table_name='student_assignments')
    
    # refresh_tokens
    op.drop_index('idx_refresh_tokens_valid', table_name='refresh_tokens')
    
    # feedbacks
    op.drop_index('idx_feedbacks_ai_generated', table_name='feedbacks')
    
    # ai_teaching_sessions
    op.drop_index('idx_ai_sessions_user_activity', table_name='ai_teaching_sessions')
    
    # user_progress
    op.drop_index('idx_user_progress_track_status', table_name='user_progress')
    op.drop_index('idx_user_progress_user_last_accessed', table_name='user_progress')
    
    # questions
    op.drop_index('idx_questions_topic_active', table_name='questions')
    op.drop_index('idx_questions_active_subject', table_name='questions')
    op.drop_index('idx_questions_subject_difficulty', table_name='questions')
    
    # submission_items
    op.drop_index('idx_submission_items_question_id', table_name='submission_items')
    op.drop_index('idx_submission_items_topic_score', table_name='submission_items')
    
    # submissions
    op.drop_index('idx_submissions_subject_date', table_name='submissions')
    op.drop_index('idx_submissions_user_submitted', table_name='submissions')
