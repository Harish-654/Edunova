import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: uuid.UUID
    full_name: str
    email: EmailStr
    role: str
    age: int | None = None
    category: str | None = None
    state_of_residence: str | None = None
    annual_family_income: float | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student: StudentOut
