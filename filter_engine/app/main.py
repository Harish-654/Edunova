from fastapi import FastAPI

from app.core.config import settings
from app.modules.matcher.router import router as matcher_router


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
app.include_router(matcher_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": settings.PROJECT_NAME, "version": settings.VERSION}


@app.get(f"{settings.API_PREFIX}/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.PROJECT_NAME}