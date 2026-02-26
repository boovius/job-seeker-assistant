from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
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


class WorkflowQueue(Base):
    __tablename__ = "workflow_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    task_type = Column(Text, nullable=False)
    payload = Column(JSONB, nullable=True)
    status = Column(Text, nullable=False, default="queued")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
