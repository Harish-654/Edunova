from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import Student, StudentMark, StudentPreference
from app.schemas.auth import StudentOut
from app.schemas.student import (
    MarksIn,
    MarksOut,
    PreferenceIn,
    PreferenceOut,
    StudentProfileUpdate,
)

router = APIRouter(prefix="/students", tags=["students"])


async def get_latest_mark(session: AsyncSession, student_id) -> StudentMark | None:
    return await session.scalar(
        select(StudentMark)
        .where(StudentMark.student_id == student_id)
        .order_by(StudentMark.mark_id.desc())
    )


async def get_latest_preference(
    session: AsyncSession, student_id
) -> StudentPreference | None:
    return await session.scalar(
        select(StudentPreference)
        .where(StudentPreference.student_id == student_id)
        .order_by(StudentPreference.created_at.desc())
    )


@router.get("/me/profile", response_model=StudentOut)
async def read_profile(user: Student = Depends(get_current_user)):
    return user


@router.put("/me/profile", response_model=StudentOut)
async def update_profile(
    payload: StudentProfileUpdate,
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/me/marks", response_model=MarksOut | None)
async def read_marks(
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_latest_mark(session, user.student_id)


@router.put("/me/marks", response_model=MarksOut)
async def upsert_marks(
    payload: MarksIn,
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    mark = await get_latest_mark(session, user.student_id)
    if mark is None:
        mark = StudentMark(student_id=user.student_id, **payload.model_dump())
        session.add(mark)
    else:
        for field, value in payload.model_dump().items():
            setattr(mark, field, value)
    await session.commit()
    await session.refresh(mark)
    return mark


@router.get("/me/preferences", response_model=PreferenceOut | None)
async def read_preferences(
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_latest_preference(session, user.student_id)


@router.put("/me/preferences", response_model=PreferenceOut)
async def upsert_preferences(
    payload: PreferenceIn,
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    preference = await get_latest_preference(session, user.student_id)
    if preference is None:
        preference = StudentPreference(student_id=user.student_id, **payload.model_dump())
        session.add(preference)
    else:
        for field, value in payload.model_dump().items():
            setattr(preference, field, value)
    await session.commit()
    await session.refresh(preference)
    return preference
