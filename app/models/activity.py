from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    professor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[Boolean] =  mapped_column(Boolean, default=True)

    activity_days = relationship(
        "Activity_day", back_populates="activity", cascade="all, delete-orphan"
    )
    enrollments = relationship("Enrollment", back_populates="activity", cascade="all, delete-orphan")
