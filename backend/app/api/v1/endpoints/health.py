from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.vector_store import QdrantVectorStore

router = APIRouter()


@router.get("/health")
def health() -> dict[str, object]:
    return {"success": True, "data": {"status": "ok"}}


@router.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"success": False, "message": "Database is unavailable", "error_code": "DATABASE_UNAVAILABLE"}) from exc
    return {"success": True, "data": {"status": "ready", "database": "ok"}}


@router.get("/health/vector")
def vector_health() -> dict[str, object]:
    try:
        QdrantVectorStore().healthcheck()
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"success": False, "message": "Vector search is temporarily unavailable", "error_code": "VECTOR_STORE_UNAVAILABLE"}) from exc
    return {"success": True, "data": {"status": "ok", "provider": "qdrant"}}