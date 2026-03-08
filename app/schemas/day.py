from pydantic import BaseModel
from app.enums import Day_Name


class Day(BaseModel):
    id: int
    name: Day_Name

    class Config:
        from_attributes = True
