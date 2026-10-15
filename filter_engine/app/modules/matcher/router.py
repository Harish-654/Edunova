from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import Student
from app.modules.matcher.service import compute_recommendations
from app.schemas.match import RecommendationOut

router = APIRouter(prefix="/match", tags=["match"])


@router.get("/my", response_model=list[RecommendationOut])
async def my_matches(
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await compute_recommendations(session, user)


@router.post("/run", response_model=list[RecommendationOut])
async def run_matches(
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await compute_recommendations(session, user)
