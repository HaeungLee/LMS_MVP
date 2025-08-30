"""add_quiz_sessions_quiz_answers_recent_activities_username

Revision ID: b1a2c3d4e5f6
Revises: 8f6a841d7170
Create Date: 2025-08-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1a2c3d4e5f6'
down_revision: Union[str, None] = '8f6a841d7170'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nullable username column to users
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))

    # Create quiz_sessions table
    op.create_table(
        'quiz_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_type', sa.String(length=50), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=True),
        sa.Column('answered_questions', sa.Integer(), nullable=True),
        sa.Column('skipped_questions', sa.Integer(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('time_taken', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('shuffle_enabled', sa.Boolean(), nullable=True),
        sa.Column('easy_count', sa.Integer(), nullable=True),
        sa.Column('medium_count', sa.Integer(), nullable=True),
        sa.Column('hard_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_sessions_id'), 'quiz_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_quiz_sessions_user_id'), 'quiz_sessions', ['user_id'], unique=False)

    # Create quiz_answers table
    op.create_table(
        'quiz_answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('user_answer', sa.Text(), nullable=True),
        sa.Column('correct_answer', sa.String(length=200), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('is_skipped', sa.Boolean(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['quiz_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_answers_id'), 'quiz_answers', ['id'], unique=False)
    op.create_index(op.f('ix_quiz_answers_session_id'), 'quiz_answers', ['session_id'], unique=False)

    # Create recent_activities table
    op.create_table(
        'recent_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=True),
        sa.Column('activity_description', sa.String(length=200), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('topic', sa.String(length=100), nullable=True),
        sa.Column('difficulty', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recent_activities_id'), 'recent_activities', ['id'], unique=False)
    op.create_index(op.f('ix_recent_activities_user_id'), 'recent_activities', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop recent_activities, quiz_answers, quiz_sessions tables
    op.drop_index(op.f('ix_recent_activities_user_id'), table_name='recent_activities')
    op.drop_index(op.f('ix_recent_activities_id'), table_name='recent_activities')
    op.drop_table('recent_activities')

    op.drop_index(op.f('ix_quiz_answers_session_id'), table_name='quiz_answers')
    op.drop_index(op.f('ix_quiz_answers_id'), table_name='quiz_answers')
    op.drop_table('quiz_answers')

    op.drop_index(op.f('ix_quiz_sessions_user_id'), table_name='quiz_sessions')
    op.drop_index(op.f('ix_quiz_sessions_id'), table_name='quiz_sessions')
    op.drop_table('quiz_sessions')

    # Remove username column from users
    op.drop_column('users', 'username')
