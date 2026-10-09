import hashlib
import math
import re
from typing import Any

from app.core.config import settings


_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD_RE.findall((text or "").lower())


class LocalEmbedder:
    """Deterministic feature-hashed bag-of-words embeddings."""

    def __init__(self, dim: int = 1536):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        tokens = _tokenize(text)
        vector = [0.0] * self.dim
        for token in tokens:
            for gram in (token, token[:5], token[-5:]):
                digest = hashlib.blake2b(
                    gram.encode("utf-8"), digest_size=8
                ).hexdigest()
                index = int(digest[:14], 16) % self.dim
                sign = 1.0 if int(digest[14:16], 16) % 2 == 0 else -1.0
                vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class OpenAiEmbedder:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def embed(self, text: str) -> list[float]:
        import openai

        client = openai.Client(api_key=self.api_key)
        response = client.embeddings.create(model=self.model, input=text)
        return list(response.data[0].embedding)


class EmbeddingService:
    def __init__(self) -> None:
        self.backend: Any = self._build_backend()

    def _build_backend(self) -> Any:
        if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            return OpenAiEmbedder(
                settings.OPENAI_API_KEY,
                settings.OPENAI_EMBEDDING_MODEL,
            )
        return LocalEmbedder(settings.EMBEDDING_DIMENSIONS)

    def embed(self, text: str) -> list[float]:
        return self.backend.embed(text)

    def to_vector_literal(self, text: str) -> str:
        vector = self.embed(text)
        return "[" + ",".join(f"{value:.6f}" for value in vector) + "]"


embedding_service = EmbeddingService()