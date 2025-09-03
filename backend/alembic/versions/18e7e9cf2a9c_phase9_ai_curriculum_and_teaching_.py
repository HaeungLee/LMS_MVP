"""phase9_ai_curriculum_and_teaching_sessions

Revision ID: 18e7e9cf2a9c
Revises: 32b7af170c59
Create Date: 2025-09-03 16:03:37.483662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18e7e9cf2a9c'
down_revision: Union[str, None] = '32b7af170c59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # AI 생성 커리큘럼 테이블
    op.create_table('ai_generated_curricula',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=True),  # Phase 8 연동
        sa.Column('subject_key', sa.String(100), nullable=True),  # 동적 과목 키
        sa.Column('learning_goals', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('difficulty_level', sa.Integer(), nullable=True),
        sa.Column('generated_syllabus', sa.JSON(), nullable=True),
        sa.Column('agent_conversation_log', sa.Text(), nullable=True),
        sa.Column('generation_metadata', sa.JSON(), nullable=True),  # AI 모델, 파라미터 등
        sa.Column('status', sa.String(20), nullable=False, server_default='generating'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_generated_curricula_user_id'), 'ai_generated_curricula', ['user_id'], unique=False)
    op.create_index(op.f('ix_ai_generated_curricula_subject_key'), 'ai_generated_curricula', ['subject_key'], unique=False)
    op.create_index(op.f('ix_ai_generated_curricula_status'), 'ai_generated_curricula', ['status'], unique=False)

    # AI 교육 세션 테이블
    op.create_table('ai_teaching_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('curriculum_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_title', sa.String(200), nullable=True),
        sa.Column('conversation_history', sa.JSON(), nullable=True),
        sa.Column('current_step', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_steps', sa.Integer(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=False, server_default='0'),
        sa.Column('session_status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('teaching_metadata', sa.JSON(), nullable=True),  # 세션 설정, AI 모델 등
        sa.Column('learning_progress', sa.JSON(), nullable=True),  # 단계별 이해도, 점수 등
        sa.Column('started_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_activity_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['curriculum_id'], ['ai_generated_curricula.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_teaching_sessions_user_id'), 'ai_teaching_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_ai_teaching_sessions_curriculum_id'), 'ai_teaching_sessions', ['curriculum_id'], unique=False)
    op.create_index(op.f('ix_ai_teaching_sessions_status'), 'ai_teaching_sessions', ['session_status'], unique=False)

    # AI 생성 콘텐츠 추적 테이블 (품질 관리용)
    op.create_table('ai_content_generation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),  # 'curriculum', 'teaching_response', 'problem'
        sa.Column('content_id', sa.Integer(), nullable=True),  # 관련 콘텐츠 ID
        sa.Column('ai_provider', sa.String(50), nullable=False),  # 'openai', 'openrouter'
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('prompt_template', sa.Text(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('generation_time_ms', sa.Integer(), nullable=True),
        sa.Column('cost_estimate', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),  # 나중에 품질 평가용
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_content_generation_logs_content_type'), 'ai_content_generation_logs', ['content_type'], unique=False)
    op.create_index(op.f('ix_ai_content_generation_logs_ai_provider'), 'ai_content_generation_logs', ['ai_provider'], unique=False)
    op.create_index(op.f('ix_ai_content_generation_logs_created_at'), 'ai_content_generation_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # 역순으로 테이블 삭제
    op.drop_index(op.f('ix_ai_content_generation_logs_created_at'), table_name='ai_content_generation_logs')
    op.drop_index(op.f('ix_ai_content_generation_logs_ai_provider'), table_name='ai_content_generation_logs')
    op.drop_index(op.f('ix_ai_content_generation_logs_content_type'), table_name='ai_content_generation_logs')
    op.drop_table('ai_content_generation_logs')
    
    op.drop_index(op.f('ix_ai_teaching_sessions_status'), table_name='ai_teaching_sessions')
    op.drop_index(op.f('ix_ai_teaching_sessions_curriculum_id'), table_name='ai_teaching_sessions')
    op.drop_index(op.f('ix_ai_teaching_sessions_user_id'), table_name='ai_teaching_sessions')
    op.drop_table('ai_teaching_sessions')
    
    op.drop_index(op.f('ix_ai_generated_curricula_status'), table_name='ai_generated_curricula')
    op.drop_index(op.f('ix_ai_generated_curricula_subject_key'), table_name='ai_generated_curricula')
    op.drop_index(op.f('ix_ai_generated_curricula_user_id'), table_name='ai_generated_curricula')
    op.drop_table('ai_generated_curricula')
