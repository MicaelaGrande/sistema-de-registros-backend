from sqlalchemy import Integer, ForeignKey, Time, Enum
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.database import Base
from app.enums import Day_Name


class Day(Base):
    __tablename__ = "day"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Day_Name] = mapped_column(Enum(Day_Name), nullable=False)

    activity_days = relationship(
        "Activity_day", back_populates="day", cascade="all, delete-orphan"
    )
    
