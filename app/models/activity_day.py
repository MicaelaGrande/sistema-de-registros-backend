from sqlalchemy import Integer, ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import time
from app.database import Base


class Activity_day(Base):
    __tablename__ = "Activity_days"
    __table_args__ = (UniqueConstraint("activity_id", "day_id", "start_time"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    activity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("activities.id"), nullable=False
    )
    day_id: Mapped[int] = mapped_column(Integer, ForeignKey("day.id"), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)

    activity = relationship("Activity", back_populates="activity_days")
    day = relationship("Day", back_populates="activity_days")

    # Esta propiedad permite acceder al nombre del día fácilmente
    @property
    def day_name(self):
        return self.day.name.value 