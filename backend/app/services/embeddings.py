import httpx

from app.core.config import get_settings


class EmbeddingUnavailableError(RuntimeError):
    pass


def embed_text(text: str) -> list[float]:
    settings = get_settings()
    try:
        response = httpx.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/embed",
            json={"model": settings.embedding_model, "input": text},
            timeout=30,
        )
        response.raise_for_status()
        embeddings = response.json().get("embeddings")
        if not embeddings or not isinstance(embeddings[0], list):
            raise EmbeddingUnavailableError("Embedding model returned no vector")
        vector = [float(value) for value in embeddings[0]]
        if len(vector) != settings.qdrant_vector_size:
            raise EmbeddingUnavailableError(
                f"Configured Qdrant vector size is {settings.qdrant_vector_size}, model returned {len(vector)}"
            )
        return vector
    except (httpx.HTTPError, ValueError, TypeError, KeyError) as error:
        raise EmbeddingUnavailableError("Local embedding model is unavailable") from error


def embed_job_text(*, title: str, company: str, location: str, description: str, skills: list[str]) -> list[float]:
    content = "\n".join((f"Title: {title}", f"Company: {company}", f"Location: {location}", f"Skills: {', '.join(skills)}", f"Description: {description}"))
    return embed_text(content)