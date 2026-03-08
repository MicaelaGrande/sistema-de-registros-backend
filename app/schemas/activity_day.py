from pydantic import BaseModel, field_validator
from datetime import time
from .day import Day
from app.enums import Day_Name
from typing import Optional

#GET
class ActivityDay(BaseModel):
    id: int
    day: Day
    start_time: time

    class Config:
        from_attributes = True

class ActivityDayWithActivity(BaseModel):
    id: int
    day: Day
    start_time: time
    activity_id: int

    class Config:
        from_attributes = True

#POST
class ActivityDayCreate(BaseModel):
    day_name: Day_Name
    start_time: time
    
    @field_validator('day_name', mode='before')
    @classmethod
    def normalize_day_name(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

#PUT
class ActivityDayUpdate(BaseModel):
    day_name: Optional[Day_Name] = None
    start_time: Optional[time] = None
    
    @field_validator('day_name', mode='before')
    @classmethod
    def normalize_day_name(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v
