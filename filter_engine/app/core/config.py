from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "EduNova Filter Engine"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+asyncpg://edunova_user:edunova_pass@localhost:5433/edunova_db"
    )

    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_DIMENSIONS: int = 1536
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    SEMANTIC_WEIGHT: float = 0.6
    PREFERENCE_WEIGHT: float = 0.4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()