from uuid import uuid4

import pytest
from qdrant_client import QdrantClient

from app.services.vector_store import QdrantVectorStore


def test_qdrant_vector_round_trip() -> None:
    store = QdrantVectorStore(QdrantClient(":memory:"))
    store.vector_size = 3
    point_id = str(uuid4())

    store.upsert("test_jobs", point_id, [1.0, 0.0, 0.0], {"title": "Backend engineer"})
    results = store.search("test_jobs", [1.0, 0.0, 0.0], limit=5)

    assert len(results) == 1
    assert str(results[0].id) == point_id
    assert results[0].payload == {"title": "Backend engineer"}


def test_qdrant_rejects_wrong_vector_dimensions() -> None:
    store = QdrantVectorStore(QdrantClient(":memory:"))
    store.vector_size = 3

    with pytest.raises(ValueError, match="3 dimensions"):
        store.upsert("test_jobs", str(uuid4()), [1.0, 0.0], {})