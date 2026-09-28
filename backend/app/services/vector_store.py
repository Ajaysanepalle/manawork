from collections.abc import Sequence
from typing import Any
from uuid import UUID

from qdrant_client import QdrantClient, models

from app.core.config import get_settings


class QdrantVectorStore:
    def __init__(self, client: QdrantClient | None = None) -> None:
        settings = get_settings()
        self.client = client or QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None, timeout=3)
        self.vector_size = settings.qdrant_vector_size

    def healthcheck(self) -> bool:
        return self.client.get_collections() is not None

    def ensure_collection(self, collection: str) -> None:
        if not self.client.collection_exists(collection):
            self.client.create_collection(
                collection_name=collection,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
            )

    def upsert(self, collection: str, point_id: str, vector: Sequence[float], payload: dict[str, Any]) -> None:
        if len(vector) != self.vector_size:
            raise ValueError(f"Expected vector with {self.vector_size} dimensions")
        try:
            parsed_point_id = UUID(point_id)
        except ValueError as error:
            raise ValueError("point_id must be a UUID") from error
        self.ensure_collection(collection)
        self.client.upsert(
            collection_name=collection,
            points=[models.PointStruct(id=str(parsed_point_id), vector=list(vector), payload=payload)],
            wait=True,
        )

    def search(self, collection: str, vector: Sequence[float], limit: int = 10, query_filter: models.Filter | None = None) -> list[models.ScoredPoint]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        if len(vector) != self.vector_size:
            raise ValueError(f"Expected vector with {self.vector_size} dimensions")
        result = self.client.query_points(
            collection_name=collection,
            query=list(vector),
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
        return result.points

    def delete(self, collection: str, point_ids: Sequence[str]) -> None:
        if point_ids:
            self.client.delete(collection_name=collection, points_selector=models.PointIdsList(points=list(point_ids)), wait=True)

    def search_jobs(self, vector: Sequence[float], limit: int = 10) -> list[models.ScoredPoint]:
        settings = get_settings()
        return self.search(settings.qdrant_jobs_collection, vector, limit=limit)

    def index_job(self, point_id: str, vector: Sequence[float], payload: dict[str, Any]) -> None:
        settings = get_settings()
        self.upsert(settings.qdrant_jobs_collection, point_id, vector, payload)