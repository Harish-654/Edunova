from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import QuestionnaireResponse, Student, StudentMark, StudentPreference
from app.modules.questionnaire.questions import INTEREST_FIELDS, INTEREST_LABELS
from app.schemas.questionnaire import QuestionnaireResult


def as_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def derive_fields(interests: list[str]) -> list[str]:
    fields: list[str] = []
    for interest in interests:
        for field in INTEREST_FIELDS.get(interest, []):
            if field not in fields:
                fields.append(field)
    return fields


def build_statement(interests: list[str], free_text: str, degree: str | None) -> str:
    parts = [INTEREST_LABELS[item] for item in interests if item in INTEREST_LABELS]
    if free_text.strip():
        parts.append(free_text.strip())
    if degree:
        parts.append(f"I have completed {degree}.")
    return ". ".join(parts)


async def submit_questionnaire(
    session: AsyncSession, student: Student, answers: dict
) -> QuestionnaireResult:
    profile_updates = {
        "full_name": answers.get("full_name"),
        "age": as_int(answers.get("age")),
        "category": answers.get("category"),
        "state_of_residence": answers.get("state_of_residence"),
        "annual_family_income": as_float(answers.get("annual_family_income")),
    }
    for field, value in profile_updates.items():
        if value is not None:
            setattr(student, field, value)

    degree = answers.get("qualifying_degree")
    percentage = as_float(answers.get("overall_percentage"))
    graduation_year = as_int(answers.get("graduation_year"))
    if degree and percentage is not None and graduation_year is not None:
        mark = await session.scalar(
            select(StudentMark).where(StudentMark.student_id == student.student_id)
        )
        if mark is None:
            session.add(
                StudentMark(
                    student_id=student.student_id,
                    qualifying_degree=degree,
                    overall_percentage=percentage,
                    graduation_year=graduation_year,
                )
            )
        else:
            mark.qualifying_degree = degree
            mark.overall_percentage = percentage
            mark.graduation_year = graduation_year

    interests = as_list(answers.get("interests"))
    fields = derive_fields(interests)
    free_text = str(answers.get("career_interest_statement") or "")
    statement = build_statement(interests, free_text, degree)

    preference = await session.scalar(
        select(StudentPreference).where(
            StudentPreference.student_id == student.student_id
        )
    )
    preferred_locations = as_list(answers.get("preferred_locations"))
    if preference is None:
        session.add(
            StudentPreference(
                student_id=student.student_id,
                preferred_fields=fields,
                preferred_locations=preferred_locations,
                career_interest_statement=statement,
            )
        )
    else:
        preference.preferred_fields = fields
        preference.preferred_locations = preferred_locations
        preference.career_interest_statement = statement

    session.add(
        QuestionnaireResponse(
            student_id=student.student_id,
            answers=answers,
            derived_statement=statement,
            derived_fields=fields,
        )
    )
    await session.commit()
    return QuestionnaireResult(
        derived_statement=statement,
        derived_fields=fields,
        career_interest_statement=statement,
        profile_updated=True,
    )
