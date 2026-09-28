from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class JobListData(BaseModel):
    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    company: str = Field(min_length=2, max_length=180)
    location: str = Field(min_length=2, max_length=180)
    mode: str = Field(default="onsite", pattern="^(remote|hybrid|onsite)$")
    employment_type: str = Field(default="Full-time", max_length=32)
    experience: str = Field(min_length=1, max_length=80)
    salary: str | None = Field(default=None, max_length=80)
    apply_url: HttpUrl
    tags: list[str] = Field(default_factory=list)
    description: str = Field(min_length=10, max_length=8000)
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
