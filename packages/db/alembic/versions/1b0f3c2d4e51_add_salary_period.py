"""add salary period to user preferences

Revision ID: 1b0f3c2d4e51
Revises: 4c2d63d7a9b1
Create Date: 2026-03-04 04:35:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1b0f3c2d4e51"
down_revision = "4c2d63d7a9b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_preference_profiles", sa.Column("salary_period", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_preference_profiles", "salary_period")
