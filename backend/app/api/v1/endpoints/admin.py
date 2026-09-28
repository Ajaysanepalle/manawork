import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.models.user import User
from app.schemas.job import JobCreate

router = APIRouter()
_TONES = ["tone-saffron", "tone-leaf", "tone-blue", "tone-lilac", "tone-coral", "tone-mint"]


def _salary_value(salary: str | None) -> int | None:
    if not salary:
        return None
    numbers = re.findall(r"\d+", salary.replace(",", ""))
    return int(numbers[-1]) if numbers else None


def _company_mark(company: str) -> str:
    letters = [part[0] for part in company.split() if part]
    return "".join(letters[:2]).upper() or "?"


def _populate_job(job: Job, payload: JobCreate, admin: User) -> None:
    company = payload.company.strip()
    job.title = payload.title.strip()
    job.company = company
    job.company_mark = _company_mark(company)
    job.company_tone = _TONES[len(company) % len(_TONES)]
    job.location = payload.location.strip()
    job.mode = payload.mode
    job.employment_type = payload.employment_type.strip() or "Full-time"
    job.experience = payload.experience.strip()
    job.salary = payload.salary.strip() if payload.salary else None
    job.salary_value = _salary_value(payload.salary)
    job.apply_url = str(payload.apply_url)
    job.tags = [tag.strip() for tag in payload.tags if tag.strip()][:12]
    job.description = payload.description.strip()
    job.responsibilities = [item.strip() for item in payload.responsibilities if item.strip()][:20]
    job.requirements = [item.strip() for item in payload.requirements if item.strip()][:20]
    job.updated_by = admin.id


def _get_owned_job(job_id: UUID, db: Session, admin: User) -> Job:
    job = db.scalar(select(Job).where(Job.id == job_id, Job.created_by == admin.id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs")
def list_admin_jobs(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> dict[str, object]:
    items = db.scalars(select(Job).where(Job.created_by == admin.id).order_by(Job.created_at.desc())).all()
    return {"success": True, "data": {"items": [job.to_public_dict() | {"status": job.status.value} for job in items], "total": len(items)}}


@router.post("/jobs")
def create_job(payload: JobCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> dict[str, object]:
    job = Job(status=JobStatus.PUBLISHED, created_by=admin.id)
    _populate_job(job, payload, admin)
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"success": True, "message": "Job published", "data": {"job": job.to_public_dict()}}


@router.put("/jobs/{job_id}")
def update_job(
    job_id: UUID,
    payload: JobCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict[str, object]:
    job = _get_owned_job(job_id, db, admin)
    _populate_job(job, payload, admin)
    db.commit()
    db.refresh(job)
    return {"success": True, "message": "Job updated", "data": {"job": job.to_public_dict()}}


@router.delete("/jobs/{job_id}")
def delete_job(job_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> dict[str, object]:
    job = _get_owned_job(job_id, db, admin)
    db.delete(job)
    db.commit()
    return {"success": True, "message": "Job deleted", "data": {}}


@router.get("/users")
def list_tracked_users(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> dict[str, object]:
    users = db.scalars(select(User).where(User.role != "ADMIN").order_by(User.created_at.desc())).all()
    return {
        "success": True,
        "data": {
            "items": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "picture_url": user.picture_url,
                    "role": user.role,
                    "signup_method": user.signup_method,
                    "google_linked": bool(user.google_sub),
                    "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                    "last_login_method": user.last_login_method,
                    "last_login_ip": user.last_login_ip,
                    "created_at": user.created_at.isoformat(),
                    "is_active": user.is_active,
                }
                for user in users
            ],
            "total": len(users),
        },
    }
