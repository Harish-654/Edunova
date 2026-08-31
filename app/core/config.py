from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "EduNova Backend"
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:edunova_pass@localhost:5432/edunova_db"
    )

    class Config:
        env_file = ".env"


settings = Settings()
