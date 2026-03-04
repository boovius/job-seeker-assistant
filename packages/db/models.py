from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func

from db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    canonical_url = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=True)
    company_name = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    remote_flag = Column(Boolean, nullable=True)
    description = Column(Text, nullable=True)
    source_type = Column(Text, nullable=False)  # enum later
    date_posted = Column(DateTime(timezone=True), nullable=True)
    status = Column(Text, nullable=False, default="new")


class ManualSubmission(Base):
    __tablename__ = "manual_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    url = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Text, nullable=False, default="queued")


class IdealJobSubmission(Base):
    __tablename__ = "ideal_job_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    url = Column(Text, nullable=False)
    why_text = Column(Text, nullable=False)
    page_text = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="queued")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    fetched_at = Column(DateTime(timezone=True), nullable=True)


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(Text, nullable=False)
    website = Column(Text, nullable=True)
    climate_tags = Column(ARRAY(Text), nullable=True)
    sector = Column(Text, nullable=True)
    funding_stage_guess = Column(Text, nullable=True)
    company_summary = Column(Text, nullable=True)


class Enrichment(Base):
    __tablename__ = "enrichments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    structured_requirements = Column(JSONB, nullable=True)
    extracted_tech_stack = Column(ARRAY(Text), nullable=True)
    risks = Column(Text, nullable=True)
    role_summary = Column(Text, nullable=True)


class FitScore(Base):
    __tablename__ = "fit_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    overall_score = Column(Integer, nullable=True)
    dimension_scores = Column(JSONB, nullable=True)
    rationale = Column(Text, nullable=True)
    pitch_bullets = Column(ARRAY(Text), nullable=True)


class ResumeVariant(Base):
    __tablename__ = "resume_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    variant_markdown = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    preference_type = Column(Text, nullable=False)
    value = Column(JSONB, nullable=False)


class UserPreferenceProfile(Base):
    __tablename__ = "user_preference_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_preference_profiles_user_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    location = Column(Text, nullable=True)
    work_mode = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(Text, nullable=True)
    salary_period = Column(Text, nullable=True)
    sector = Column(Text, nullable=True)
    target_role = Column(Text, nullable=True)
    company_size = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserValueProfile(Base):
    __tablename__ = "user_value_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_value_profiles_user_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    values = Column(JSONB, nullable=True)
    dream_job_description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserResume(Base):
    __tablename__ = "user_resumes"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_resumes_user_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    resume_text = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserResumeChunk(Base):
    __tablename__ = "user_resume_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WorkflowQueue(Base):
    __tablename__ = "workflow_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    task_type = Column(Text, nullable=False)
    payload = Column(JSONB, nullable=True)
    status = Column(Text, nullable=False, default="queued")
    attempts = Column(Integer, nullable=False, default=0)
    lease_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    slug = Column(Text, unique=True, nullable=False)
    adapter = Column(Text, nullable=False)
    kind = Column(Text, nullable=False)
    base_url = Column(Text, nullable=True)
    default_config = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserSource(Base):
    __tablename__ = "user_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    weight = Column(Integer, nullable=False, default=1)
    filters = Column(JSONB, nullable=True)
    schedule = Column(JSONB, nullable=True)


class SourceCursor(Base):
    __tablename__ = "source_cursors"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    cursor = Column(JSONB, nullable=True)
    etag = Column(Text, nullable=True)
    last_modified = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserSourceConfig(Base):
    __tablename__ = "user_source_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    yaml_text = Column(Text, nullable=False)
    config_json = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
