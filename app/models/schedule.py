import enum
from datetime import time
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Integer, String, Enum, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.teacher import Teacher
    from app.models.school_class import SchoolClass
    from app.models.assessment import AssessmentTask


class DayOfWeek(int, enum.Enum):
    """Дни недели (1 = Понедельник, 6 = Суббота)."""
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


class Subject(Base, TimestampMixin):
    """Учебные предметы по программе НИШ (Интегрированная образовательная программа - ИОП)."""
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, comment="Название предмета (например, Математика, Физика, Global Perspectives)")
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, comment="Код предмета (например, MATH_ADV, PHYS_HL)")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Описание программы")

    # Связи
    schedule_items: Mapped[List["ScheduleItem"]] = relationship("ScheduleItem", back_populates="subject")
    assessment_tasks: Mapped[List["AssessmentTask"]] = relationship("AssessmentTask", back_populates="subject")

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, code='{self.code}', name='{self.name}')>"


class ScheduleItem(Base, TimestampMixin):
    """Элемент расписания уроков."""
    __tablename__ = "schedule_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    day_of_week: Mapped[DayOfWeek] = mapped_column(
        Enum(DayOfWeek, native_enum=False), 
        nullable=False, 
        comment="День недели (1-6)"
    )
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False, comment="Номер урока/пары (1-8)")
    start_time: Mapped[time] = mapped_column(Time, nullable=False, comment="Время начала урока")
    end_time: Mapped[time] = mapped_column(Time, nullable=False, comment="Время окончания урока")
    classroom: Mapped[str] = mapped_column(String(50), nullable=False, comment="Кабинет / Лаборатория (например, 204 Лаборатория Физики)")

    # Внешние ключи
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)

    # Связи
    school_class: Mapped["SchoolClass"] = relationship("SchoolClass", back_populates="schedule_items")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="schedule_items")
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="schedule_items")

    def __repr__(self) -> str:
        return f"<ScheduleItem(day={self.day_of_week}, lesson={self.lesson_number}, class_id={self.class_id}, room='{self.classroom}')>"
