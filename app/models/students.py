from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    dni: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    age: Mapped[int] = mapped_column(nullable=False)
    celphone: Mapped[str] = mapped_column(String(20), nullable=False)
    celphone_optional: Mapped[str] = mapped_column(String(20), default="-")
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relación con enrollments
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")