from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router
from app.modules.ingestion.router import router as ingestion_router
from app.modules.matcher.router import router as match_router
from app.modules.questionnaire.router import router as questionnaire_router
from app.modules.students.router import router as students_router

API_PREFIX = "/api/v1"

app = FastAPI(title="EduNova API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(students_router, prefix=API_PREFIX)
app.include_router(catalog_router, prefix=API_PREFIX)
app.include_router(questionnaire_router, prefix=API_PREFIX)
app.include_router(match_router, prefix=API_PREFIX)
app.include_router(ingestion_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}
