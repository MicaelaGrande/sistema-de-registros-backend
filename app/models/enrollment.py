from sqlalchemy import Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Enrollment(Base):
    __tablename__= "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "activity_id", name="unique_student_activity"),
    )

    id: Mapped[int] =  mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id: Mapped[int] = mapped_column(Integer, ForeignKey("activities.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relaciones
    student = relationship("Student", back_populates="enrollments")
    activity = relationship("Activity", back_populates="enrollments")