from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from .activity_day import ActivityDay, ActivityDayCreate


# Schema simple de Student para evitar importación circular
class StudentInActivity(BaseModel):
    id: int
    name: str
    lastname: str
    dni: str
    age: int
    celphone: str
    celphone_optional: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class EnrollmentInActivity(BaseModel):
    id: int
    is_active: bool
    student: StudentInActivity

    class Config:
        from_attributes = True


# GET
class Activity(BaseModel):
    id: int
    name: str
    professor_name: str
    capacity: int
    activity_days: List[ActivityDay]  # aquí referenciamos los días de la actividad
    enrollments: List[EnrollmentInActivity] = Field(
        default_factory=list
    )  # estudiantes inscritos
    is_active: bool

    class Config:
        from_attributes = True


# POST
class CreateActivity(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    professor_name: str = Field(min_length=3, max_length=100)
    capacity: int = Field(gt=0)  # mayor que 0
    activity_days: List[ActivityDayCreate]

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("professor_name")
    @classmethod
    def normalize_professor_name(cls, v: str) -> str:
        return v.strip().lower()


# PUT
class UpdateActivity(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=150)
    professor_name: Optional[str] = Field(default=None, min_length=3, max_length=100)
    capacity: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip().title()

    @field_validator("professor_name")
    @classmethod
    def normalize_professor_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip().lower()
