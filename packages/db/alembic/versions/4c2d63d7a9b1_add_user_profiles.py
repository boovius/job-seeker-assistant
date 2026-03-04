\"\"\"add user preference and value profiles

Revision ID: 4c2d63d7a9b1
Revises: 276f2e157e0d
Create Date: 2026-03-04 04:25:00.000000
\"\"\"

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = \"4c2d63d7a9b1\"
down_revision = \"276f2e157e0d\"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        \"user_preference_profiles\",
        sa.Column(\"id\", postgresql.UUID(as_uuid=True), server_default=sa.text(\"gen_random_uuid()\"), nullable=False),
        sa.Column(\"user_id\", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(\"location\", sa.Text(), nullable=True),
        sa.Column(\"work_mode\", sa.Text(), nullable=True),
        sa.Column(\"salary_min\", sa.Integer(), nullable=True),
        sa.Column(\"salary_max\", sa.Integer(), nullable=True),
        sa.Column(\"salary_currency\", sa.Text(), nullable=True),
        sa.Column(\"sector\", sa.Text(), nullable=True),
        sa.Column(\"target_role\", sa.Text(), nullable=True),
        sa.Column(\"company_size\", sa.Text(), nullable=True),
        sa.Column(\"updated_at\", sa.DateTime(timezone=True), server_default=sa.text(\"now()\"), nullable=True),
        sa.PrimaryKeyConstraint(\"id\"),
        sa.UniqueConstraint(\"user_id\", name=\"uq_user_preference_profiles_user_id\"),
    )

    op.create_table(
        \"user_value_profiles\",
        sa.Column(\"id\", postgresql.UUID(as_uuid=True), server_default=sa.text(\"gen_random_uuid()\"), nullable=False),
        sa.Column(\"user_id\", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(\"values\", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(\"dream_job_description\", sa.Text(), nullable=True),
        sa.Column(\"updated_at\", sa.DateTime(timezone=True), server_default=sa.text(\"now()\"), nullable=True),
        sa.PrimaryKeyConstraint(\"id\"),
        sa.UniqueConstraint(\"user_id\", name=\"uq_user_value_profiles_user_id\"),
    )


def downgrade() -> None:
    op.drop_table(\"user_value_profiles\")
    op.drop_table(\"user_preference_profiles\")
