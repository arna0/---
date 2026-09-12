import enum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Integer, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.teacher import Teacher
    from app.models.student import Student
    from app.models.schedule import ScheduleItem
    from app.models.assessment import AssessmentTask


class ClassProfile(str, enum.Enum):
    """Профильные направления в НИШ."""
    PMN = "ФМН"  # Физико-математическое направление
    CBN = "ХБН"  # Химико-биологическое направление
    GEN = "Общий" # 7-8 классы базовой школы
    HUM = "Общественно-гуманитарное"
    IT = "Информационно-технологическое"


class SchoolClass(Base, TimestampMixin):
    """Модель профильного класса НИШ (например, 10 'A' ФМН)."""
    __tablename__ = "school_classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False, comment="Параллель (7 - 12 классы)")
    section: Mapped[str] = mapped_column(String(5), nullable=False, comment="Литера класса (A, B, C, D, E...)")
    profile: Mapped[ClassProfile] = mapped_column(
        Enum(ClassProfile, native_enum=False), 
        default=ClassProfile.PMN,
        nullable=False, 
        comment="Профиль обучения (ФМН, ХБН и др.)"
    )
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, comment="Учебный год (например, 2025-2026)")
    language_of_instruction: Mapped[str] = mapped_column(String(50), default="Казахский", comment="Язык обучения (Казахский/Русский/Английский)")
    
    # Куратор класса (учитель)
    curator_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("teachers.id", ondelete="SET NULL"), 
        nullable=True, 
        comment="ID куратора (классного руководителя)"
    )

    # Связи
    curator: Mapped[Optional["Teacher"]] = relationship(
        "Teacher", 
        back_populates="curated_classes", 
        foreign_keys=[curator_id]
    )
    students: Mapped[List["Student"]] = relationship("Student", back_populates="school_class")
    schedule_items: Mapped[List["ScheduleItem"]] = relationship("ScheduleItem", back_populates="school_class")
    assessment_tasks: Mapped[List["AssessmentTask"]] = relationship("AssessmentTask", back_populates="school_class")

    @property
    def display_name(self) -> str:
        return f"{self.grade_level} {self.section} ({self.profile.value})"

    def __repr__(self) -> str:
        return f"<SchoolClass(id={self.id}, name='{self.grade_level}{self.section}', profile='{self.profile.value}')>"
