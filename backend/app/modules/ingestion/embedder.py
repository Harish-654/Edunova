"""Embeddings pipeline.

Generates 1536-dimensional semantic vectors for natural-language text.

Provider matrix:
  - "local": deterministic, offline, hashing-based embeddings. Always works,
    identical inputs -> identical vectors (so cosine similarity is meaningful).
  - "openai": talks to OpenAI `text-embedding-3-small` when an API key exists.
"""

import hashlib
import math
import os
import re
from typing import Any

from app.core.config import settings

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD_RE.findall((text or "").lower())


class LocalEmbedder:
    """Feature-hashed bag-of-words embedding with a deterministic seed."""

    dim: int

    def __init__(self, dim: int = 1536):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        tokens = _tokenize(text)
        vector = [0.0] * self.dim
        for i, tok in enumerate(tokens):
            for gram in (tok, tok[:5], tok[-5:]):
                h = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).hexdigest()
                idx = int(h[:14], 16) % self.dim
                sign = 1.0 if int(h[14:16], 16) % 2 == 0 else -1.0
                vector[idx] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class OpenAiEmbedder:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def embed(self, text: str) -> list[float]:
        # Imported lazily so the package does not hard-depend on `openai`.
        import openai

        client = openai.Client(api_key=self.api_key)
        resp = client.embeddings.create(model=self.model, input=text)
        return list(resp.data[0].embedding)


class EmbeddingService:
    def __init__(self) -> None:
        self.backend: Any = self._build_backend()

    def _build_backend(self) -> Any:
        if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            return OpenAiEmbedder(settings.OPENAI_API_KEY, settings.OPENAI_EMBEDDING_MODEL)
        return LocalEmbedder(settings.EMBEDDING_DIMENSIONS)

    def embed(self, text: str) -> list[float]:
        return self.backend.embed(text)

    def to_vector_literal(self, text: str) -> str:
        vector = self.embed(text)
        return "[" + ",".join(f"{v:.6f}" for v in vector) + "]"


embedding_service = EmbeddingService()