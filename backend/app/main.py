from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router
from app.modules.ingestion.router import router as ingestion_router
from app.modules.ingestion.scheduler import start_scheduler, stop_scheduler
from app.modules.matcher.router import router as matcher_router
from app.modules.scholarship.router import router as scholarship_router
from app.modules.student.router import router as student_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "AI-driven career guidance & examination matching platform: "
        "hybrid hard-eligibility gate + pgvector semantic matching."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API = settings.API_PREFIX

app.include_router(auth_router, prefix=API)
app.include_router(student_router, prefix=API)
app.include_router(catalog_router, prefix=API)
app.include_router(ingestion_router, prefix=API)
app.include_router(matcher_router, prefix=API)
app.include_router(scholarship_router, prefix=API)


@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get(f"{API}/health")
async def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}