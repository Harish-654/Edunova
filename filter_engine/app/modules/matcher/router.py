from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.entities import Student, StudentPreference
from app.modules.matcher.service import compute_matches
from app.schemas.matching import MatchResponse


router = APIRouter(prefix="/match", tags=["match"])


@router.post("/student/{student_id}/compute", response_model=MatchResponse)
async def compute_student_matches(
    student_id: UUID, db: AsyncSession = Depends(get_db)
) -> MatchResponse:
    try:
        return await compute_matches(db, student_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get(
    "/student/{student_id}/recommendations", response_model=MatchResponse
)
async def get_student_recommendations(
    student_id: UUID, db: AsyncSession = Depends(get_db)
) -> MatchResponse:
    if await db.get(Student, student_id) is None:
        raise HTTPException(status_code=404, detail="Student not found")

    preference = (
        await db.execute(
            select(StudentPreference)
            .where(StudentPreference.student_id == student_id)
            .order_by(StudentPreference.created_at.desc())
        )
    ).scalars().first()
    if preference is None or not preference.career_interest_statement:
        raise HTTPException(
            status_code=400,
            detail=(
                "Complete your career-interest preferences before requesting matches."
            ),
        )

    return await compute_matches(db, student_id)