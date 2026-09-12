import enum
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Integer, String, Float, Enum, ForeignKey, Date, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.teacher import Teacher
    from app.models.school_class import SchoolClass
    from app.models.student import Student
    from app.models.schedule import Subject


class AssessmentType(str, enum.Enum):
    """Типы критериального оценивания в НИШ."""
    FORMATIVE = "ФО"                # Формативное оценивание (1-10 баллов или уровни с дескрипторами)
    SUMMATIVE_SECTION = "БЖБ/СОР"   # Суммативное оценивание за раздел / Бөлім бойынша жиынтық бағалау
    SUMMATIVE_TERM = "ТЖБ/СОЧ"      # Суммативное оценивание за четверть / Тоқсандық жиынтық бағалау
    EXTERNAL_EXAM = "Внешний экзамен" # Итоговый внешний экзамен (Кембридж / НИШ)


class AssessmentTask(Base, TimestampMixin):
    """Задание / работа критериального оценивания (СОР, СОЧ или ФО-активность)."""
    __tablename__ = "assessment_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="Тема или название работы")
    assessment_type: Mapped[AssessmentType] = mapped_column(
        Enum(AssessmentType, native_enum=False), 
        nullable=False, 
        comment="Тип оценивания (ФО, БЖБ/СОР, ТЖБ/СОЧ)"
    )
    term: Mapped[int] = mapped_column(Integer, nullable=False, comment="Учебная четверть (1, 2, 3, 4)")
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, comment="Учебный год (например, 2025-2026)")
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=10.0, comment="Максимальный первичный балл")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, comment="Весовой коэффициент в итоговой оценке")
    criteria_rubric: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Критерии оценивания и дескрипторы")
    task_date: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата проведения")

    # Внешние ключи
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_classes.id", ondelete="CASCADE"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)

    # Связи
    subject: Mapped["Subject"] = relationship("Subject", back_populates="assessment_tasks")
    school_class: Mapped["SchoolClass"] = relationship("SchoolClass", back_populates="assessment_tasks")
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="assessment_tasks")
    grades: Mapped[List["AssessmentGrade"]] = relationship("AssessmentGrade", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AssessmentTask(id={self.id}, type='{self.assessment_type.value}', title='{self.title}', max_score={self.max_score})>"


class AssessmentGrade(Base, TimestampMixin):
    """Результат / оценка конкретного ученика за работу."""
    __tablename__ = "assessment_grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("assessment_tasks.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    score: Mapped[float] = mapped_column(Float, nullable=False, comment="Набранный балл")
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Обратная связь учителя (дескрипторы, комментарий)")
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Связи
    task: Mapped["AssessmentTask"] = relationship("AssessmentTask", back_populates="grades")
    student: Mapped["Student"] = relationship("Student", back_populates="grades")

    @property
    def percentage(self) -> Optional[float]:
        from sqlalchemy import inspect
        insp = inspect(self)
        if insp is not None and "task" not in insp.unloaded:
            if self.task and self.task.max_score > 0:
                return round((self.score / self.task.max_score) * 100, 2)
        return None

    def __repr__(self) -> str:
        return f"<AssessmentGrade(id={self.id}, student_id={self.student_id}, score={self.score})>"
