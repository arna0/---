from datetime import date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.school_class import SchoolClass
    from app.models.assessment import AssessmentGrade


class Student(Base, TimestampMixin):
    """Модель ученика НИШ."""
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Имя")
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Фамилия")
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Отчество")
    iin: Mapped[str] = mapped_column(String(12), unique=True, index=True, nullable=False, comment="ИИН ученика (12 цифр)")
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата рождения")
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True, comment="Email ученика")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="Телефон ученика")
    parent_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="Телефон родителей/законных представителей")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="Статус обучения")

    # Привязка к профильному классу
    class_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("school_classes.id", ondelete="SET NULL"), 
        nullable=True, 
        comment="ID класса"
    )

    # Связи
    school_class: Mapped[Optional["SchoolClass"]] = relationship("SchoolClass", back_populates="students")
    grades: Mapped[List["AssessmentGrade"]] = relationship("AssessmentGrade", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name='{self.last_name} {self.first_name}', iin='{self.iin}')>"
