from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# GET
class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

#POST
class UserCreate(BaseModel):
    email: str
    password: str

# UPDATE
class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
