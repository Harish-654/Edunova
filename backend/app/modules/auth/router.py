from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.entities import Student
from app.schemas.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    StudentOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def _student_to_out(student: Student) -> StudentOut:
    return StudentOut.model_validate(student)


def _auth_response(student: Student) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(str(student.student_id)),
        user=StudentOut.model_validate(student),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    exists = (
        await db.execute(select(Student).where(Student.email == payload.email.lower()))
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")

    student = Student(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        age=payload.age,
        category=payload.category,
        state_of_residence=payload.state_of_residence,
        annual_family_income=payload.annual_family_income,
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return _auth_response(student)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    student = (
        await db.execute(select(Student).where(Student.email == payload.email.lower()))
    ).scalar_one_or_none()
    if not student or not verify_password(payload.password, student.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return _auth_response(student)


@router.get("/me", response_model=StudentOut)
async def me(authorization: str, db: AsyncSession = Depends(get_db)):
    token = authorization.replace("Bearer ", "")
    student_id = decode_access_token(token)
    if not student_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentOut.model_validate(student)