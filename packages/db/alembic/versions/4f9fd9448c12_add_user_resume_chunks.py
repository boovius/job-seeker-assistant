"""add user resume chunks

Revision ID: 4f9fd9448c12
Revises: 7e2a9a9b1a21
Create Date: 2026-03-04 05:20:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4f9fd9448c12"
down_revision = "7e2a9a9b1a21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_resume_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_resume_chunks_user_id", "user_resume_chunks", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_resume_chunks_user_id", table_name="user_resume_chunks")
    op.drop_table("user_resume_chunks")
