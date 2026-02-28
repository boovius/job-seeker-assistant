"""add user_source_configs

Revision ID: 9b6c1c1a3f4b
Revises: a48a2004e9a3
Create Date: 2026-02-28 10:30:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9b6c1c1a3f4b"
down_revision = "a48a2004e9a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_source_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("yaml_text", sa.Text(), nullable=False),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_source_configs")
