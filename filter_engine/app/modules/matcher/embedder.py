import hashlib
import math
import re

EMBEDDING_DIM = 1536


def embed_text(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIM
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        digest = int(hashlib.blake2b(token.encode(), digest_size=8).hexdigest(), 16)
        vector[digest % EMBEDDING_DIM] += 1.0 if (digest >> 63) & 1 else -1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return vector
    return [value / norm for value in vector]


def to_vector_literal(text: str) -> str:
    return "[" + ",".join(f"{value:.6f}" for value in embed_text(text)) + "]"
