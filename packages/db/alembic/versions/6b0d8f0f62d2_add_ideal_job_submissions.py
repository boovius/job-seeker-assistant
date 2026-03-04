"""add ideal job submissions

Revision ID: 6b0d8f0f62d2
Revises: 1b0f3c2d4e51
Create Date: 2026-03-04 04:55:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6b0d8f0f62d2"
down_revision = "1b0f3c2d4e51"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ideal_job_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("why_text", sa.Text(), nullable=False),
        sa.Column("page_text", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="queued"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ideal_job_submissions")
