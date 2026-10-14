from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+asyncpg://edunova_user:edunova_pass@localhost:5433/edunova_db"
    )
    jwt_secret: str = "edunova-dev-secret-change-me-0123456789abcdef"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
