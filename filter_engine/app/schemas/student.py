from pydantic import BaseModel, ConfigDict


class StudentProfileUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None
    category: str | None = None
    state_of_residence: str | None = None
    annual_family_income: float | None = None


class MarksIn(BaseModel):
    qualifying_degree: str
    overall_percentage: float
    graduation_year: int


class MarksOut(MarksIn):
    model_config = ConfigDict(from_attributes=True)


class PreferenceIn(BaseModel):
    preferred_fields: list[str] = []
    preferred_locations: list[str] = []
    career_interest_statement: str | None = None


class PreferenceOut(PreferenceIn):
    model_config = ConfigDict(from_attributes=True)
