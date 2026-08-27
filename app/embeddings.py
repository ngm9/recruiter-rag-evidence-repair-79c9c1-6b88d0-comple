from __future__ import annotations

from collections.abc import Iterable

from fastembed import TextEmbedding

from app.config import get_settings


class EmbeddingService:
    def __init__(self, model_name: str | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self._model = TextEmbedding(model_name=self.model_name)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        prepared = [text.replace("\n", " ").strip() for text in texts]
        if not prepared:
            return []
        return [list(vector) for vector in self._model.embed(prepared)]

    def embed_query(self, query: str) -> list[float]:
        vectors = self.embed_texts([query])
        if not vectors:
            raise ValueError("query text is empty")
        return vectors[0]
