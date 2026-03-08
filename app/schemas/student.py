from pydantic import BaseModel, Field
from typing import Optional, List
from .activity import Activity

class ShowActivity(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ShowEnrollment(BaseModel):
    id: int
    is_active: bool
    activity: ShowActivity

    class Config:
        from_attributes = True


# GET
class ShowStudents(BaseModel):
    id: int
    name: str
    lastname: str
    dni: str
    age: int
    celphone: str
    celphone_optional: Optional[str] = None
    is_active: bool
    enrollments: List[ShowEnrollment] = Field(default_factory=list)

    class Config:
        from_attributes = True
 
# POST
class CreateStudent(BaseModel):
    name: str
    lastname: str
    dni: str
    age: int
    celphone: str
    celphone_optional: Optional[str] = None
    activities_id: List[int] 

# PUT
class UpdateStudent(BaseModel):
    name: Optional[str] = None
    lastname: Optional[str] = None
    dni: Optional[str] = None
    age: Optional[int] = None
    celphone: Optional[str] = None
    celphone_optional: Optional[str] = None
    is_active: Optional[bool] = None
