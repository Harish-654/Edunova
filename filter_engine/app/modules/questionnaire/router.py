from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models import QuestionnaireResponse, Student
from app.modules.questionnaire.questions import QUESTIONS
from app.modules.questionnaire.service import submit_questionnaire
from app.schemas.questionnaire import (
    QuestionOut,
    QuestionnaireResult,
    QuestionnaireStored,
    QuestionnaireSubmit,
)

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


@router.get("/questions", response_model=list[QuestionOut])
async def get_questions():
    return QUESTIONS


@router.post("/submit", response_model=QuestionnaireResult)
async def submit(
    payload: QuestionnaireSubmit,
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await submit_questionnaire(session, user, payload.answers)


@router.get("/me", response_model=QuestionnaireStored | None)
async def my_response(
    user: Student = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await session.scalar(
        select(QuestionnaireResponse)
        .where(QuestionnaireResponse.student_id == user.student_id)
        .order_by(QuestionnaireResponse.created_at.desc())
    )
