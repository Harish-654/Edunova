from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Student
from app.schemas.auth import LoginRequest, RegisterRequest, StudentOut, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)):
    email = payload.email.lower()
    existing = await session.scalar(select(Student).where(Student.email == email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    student = Student(
        full_name=payload.full_name,
        email=email,
        password_hash=hash_password(payload.password),
        role="student",
    )
    session.add(student)
    await session.commit()
    await session.refresh(student)
    token = create_access_token(str(student.student_id), student.role)
    return TokenResponse(access_token=token, student=StudentOut.model_validate(student))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    student = await session.scalar(
        select(Student).where(Student.email == payload.email.lower())
    )
    if student is None or not verify_password(payload.password, student.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(str(student.student_id), student.role)
    return TokenResponse(access_token=token, student=StudentOut.model_validate(student))


@router.get("/me", response_model=StudentOut)
async def me(user: Student = Depends(get_current_user)):
    return user
