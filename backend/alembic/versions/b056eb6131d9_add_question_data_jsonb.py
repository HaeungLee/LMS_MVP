"""add_question_data_jsonb

Revision ID: b056eb6131d9
Revises: b1a2c3d4e5f6
Create Date: 2025-09-01 10:26:38.007078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b056eb6131d9'
down_revision: Union[str, None] = 'b1a2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add question_data JSONB, metadata JSONB, ai_generated boolean columns to questions table"""

    # Add new columns to questions table
    op.add_column('questions', sa.Column('question_data', sa.JSON(), nullable=True))
    op.add_column('questions', sa.Column('question_metadata', sa.JSON(), nullable=True))
    op.add_column('questions', sa.Column('ai_generated', sa.Boolean(), server_default=sa.text('false'), nullable=False))

    # Note: GIN indexes will be created separately after migration
    # For now, just create a basic index on ai_generated
    op.execute("CREATE INDEX IF NOT EXISTS idx_question_ai_generated ON questions (ai_generated);")


def downgrade() -> None:
    """Remove added columns from questions table"""

    # Drop indexes first
    op.execute("DROP INDEX IF EXISTS idx_question_ai_generated;")
    # Note: GIN index should be dropped manually if it exists

    # Drop columns
    op.drop_column('questions', 'ai_generated')
    op.drop_column('questions', 'question_metadata')
    op.drop_column('questions', 'question_data')
