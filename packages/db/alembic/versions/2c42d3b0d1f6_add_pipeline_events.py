"""add pipeline events

Revision ID: 2c42d3b0d1f6
Revises: 4f9fd9448c12
Create Date: 2026-03-06 01:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2c42d3b0d1f6"
down_revision = "4f9fd9448c12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pipeline_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipeline_events_user_id", "pipeline_events", ["user_id"])
    op.create_index("ix_pipeline_events_task_id", "pipeline_events", ["task_id"])
    op.create_index("ix_pipeline_events_event_type", "pipeline_events", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_events_event_type", table_name="pipeline_events")
    op.drop_index("ix_pipeline_events_task_id", table_name="pipeline_events")
    op.drop_index("ix_pipeline_events_user_id", table_name="pipeline_events")
    op.drop_table("pipeline_events")
