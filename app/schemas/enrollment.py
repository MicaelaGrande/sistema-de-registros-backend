from pydantic import BaseModel


class ShowEnrollment(BaseModel):
    id: int
    student_id: int
    activity_id: int
    is_active: bool

    class Config:
        from_attributes = True


class CreateEnrollment(BaseModel):
    student_id: int
    activity_id: int


class UpdateEnrollment(BaseModel):
    is_active: bool
