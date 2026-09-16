from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "EduNova Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+asyncpg://edunova_user:edunova_pass@localhost:5433/edunova_db"
    )

    JWT_SECRET: str = "edunova-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Embedding provider: "local" (deterministic hashing, offline) or "openai"
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_DIMENSIONS: int = 1536
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Match engine weights
    SEMANTIC_WEIGHT: float = 0.6
    PREFERENCE_WEIGHT: float = 0.4

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()