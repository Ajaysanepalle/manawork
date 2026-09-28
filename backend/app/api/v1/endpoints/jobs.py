from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Text, cast, func, or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.job import Job, JobStatus
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.job import JobListData
from app.services.embeddings import EmbeddingUnavailableError, embed_text
from app.services.vector_store import QdrantVectorStore

router = APIRouter()


@router.get("", response_model=ApiResponse[JobListData])
def list_public_jobs(
    _: User = Depends(get_current_user),
    q: str | None = Query(default=None, max_length=120),
    location: str | None = Query(default=None, max_length=120),
    mode: str | None = Query(default=None, pattern="^(remote|hybrid|onsite)$"),
    sort: str = Query(default="newest", pattern="^(newest|salary)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    db: Session = Depends(get_db),
) -> ApiResponse[JobListData]:
    statement = select(Job).where(Job.status == JobStatus.PUBLISHED)
    if q:
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Job.title.ilike(term), Job.company.ilike(term), Job.description.ilike(term), cast(Job.tags, Text).ilike(term)))
    if location:
        statement = statement.where(Job.location.ilike(f"%{location.strip()}%"))
    if mode:
        statement = statement.where(Job.mode == mode)

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    if sort == "salary":
        statement = statement.order_by(Job.salary_value.desc().nullslast(), Job.created_at.desc())
    else:
        statement = statement.order_by(Job.created_at.desc())
    items = db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
    return ApiResponse(data=JobListData(items=[job.to_public_dict() for job in items], total=total, page=page, page_size=page_size))


@router.get("/semantic-search")
def semantic_job_search(
    _: User = Depends(get_current_user),
    q: str = Query(min_length=3, max_length=500),
    limit: int = Query(default=10, ge=1, le=50),
) -> dict[str, object]:
    try:
        vector = embed_text(q)
        hits = QdrantVectorStore().search_jobs(vector, limit=limit)
    except (EmbeddingUnavailableError, ValueError) as exc:
        raise HTTPException(status_code=503, detail={"success": False, "message": "Semantic search is temporarily unavailable", "error_code": "SEMANTIC_SEARCH_UNAVAILABLE"}) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"success": False, "message": "Semantic search is temporarily unavailable", "error_code": "VECTOR_STORE_UNAVAILABLE"}) from exc

    public_hits = [
        {"id": str(hit.id), "score": hit.score, "job": hit.payload}
        for hit in hits
        if hit.payload and hit.payload.get("status") == "PUBLISHED"
    ]
    return {
        "success": True,
        "data": {
            "items": public_hits,
            "total": len(public_hits),
        },
    }


@router.get("/{job_id}")
def get_public_job(job_id: UUID, _: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, object]:
    job = db.get(Job, job_id)
    if not job or job.status != JobStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail={"success": False, "message": "This role is no longer available", "error_code": "JOB_NOT_FOUND"})
    return {"success": True, "data": {"job": job.to_public_dict()}}
