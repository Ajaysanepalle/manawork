import enum
from typing import Any
from uuid import UUID

from sqlalchemy import Enum, Index, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TimestampedModel


class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class Job(TimestampedModel):
    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_status_created_at", "status", "created_at"),
        Index("ix_jobs_location", "location"),
    )

    title: Mapped[str] = mapped_column(String(180), nullable=False)
    company: Mapped[str] = mapped_column(String(180), nullable=False)
    company_mark: Mapped[str] = mapped_column(String(8), default="?", nullable=False)
    company_tone: Mapped[str] = mapped_column(String(32), default="tone-leaf", nullable=False)
    location: Mapped[str] = mapped_column(String(180), nullable=False)
    mode: Mapped[str] = mapped_column(String(16), default="onsite", nullable=False)
    employment_type: Mapped[str] = mapped_column(String(32), default="Full-time", nullable=False)
    experience: Mapped[str] = mapped_column(String(80), nullable=False)
    salary: Mapped[str | None] = mapped_column(String(80))
    salary_value: Mapped[int | None] = mapped_column(Integer)
    apply_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsibilities: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    requirements: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus, name="job_status"), default=JobStatus.DRAFT, nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "title": self.title,
            "company": self.company,
            "companyMark": self.company_mark,
            "companyTone": self.company_tone,
            "location": self.location,
            "mode": self.mode,
            "employmentType": self.employment_type,
            "experience": self.experience,
            "salary": self.salary or "Salary not listed",
            "salaryValue": self.salary_value or 0,
            "applyUrl": self.apply_url,
            "postedAt": self.created_at.strftime("%Y-%m-%d"),
            "tags": self.tags,
            "description": self.description,
            "responsibilities": self.responsibilities,
            "requirements": self.requirements,
        }