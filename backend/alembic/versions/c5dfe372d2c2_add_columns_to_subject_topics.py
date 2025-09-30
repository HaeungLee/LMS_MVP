"""add_columns_to_subject_topics

Revision ID: c5dfe372d2c2
Revises: 76441a356c59
Create Date: 2025-09-30 16:23:18.539039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5dfe372d2c2'
down_revision: Union[str, None] = '76441a356c59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to subject_topics table
    op.add_column('subject_topics', sa.Column('topic_name', sa.String(length=200), nullable=True))
    op.add_column('subject_topics', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('subject_topics', sa.Column('order_index', sa.Integer(), nullable=True))
    op.add_column('subject_topics', sa.Column('estimated_duration', sa.String(length=50), nullable=True))
    op.add_column('subject_topics', sa.Column('difficulty_level', sa.String(length=20), nullable=True))


def downgrade() -> None:
    # Remove added columns from subject_topics table
    op.drop_column('subject_topics', 'difficulty_level')
    op.drop_column('subject_topics', 'estimated_duration')
    op.drop_column('subject_topics', 'order_index')
    op.drop_column('subject_topics', 'description')
    op.drop_column('subject_topics', 'topic_name')
