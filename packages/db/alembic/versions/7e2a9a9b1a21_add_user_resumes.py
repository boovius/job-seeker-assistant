"""add user resumes

Revision ID: 7e2a9a9b1a21
Revises: 6b0d8f0f62d2
Create Date: 2026-03-04 05:05:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7e2a9a9b1a21"
down_revision = "6b0d8f0f62d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_text", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_resumes_user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_resumes")
