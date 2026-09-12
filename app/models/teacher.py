from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.school_class import SchoolClass
    from app.models.schedule import ScheduleItem
    from app.models.assessment import AssessmentTask
    from app.models.announcement import Announcement


class Teacher(Base, TimestampMixin):
    """Модель учителя НИШ (педагог, куратор, заведующий кафедрой)."""
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Имя")
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Фамилия")
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Отчество")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False, comment="Корпоративный email")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="Номер телефона")
    
    # Специфика НИШ: кафедра и категория
    department: Mapped[str] = mapped_column(String(150), nullable=False, comment="Кафедра (например, Кафедра математики, Кафедра естественных наук)")
    qualification_category: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        comment="Квалификационная категория НИШ (педагог-эксперт, педагог-исследователь, педагог-мастер)"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="Статус активности сотрудника")

    # Связи (Relationships)
    curated_classes: Mapped[List["SchoolClass"]] = relationship(
        "SchoolClass", 
        back_populates="curator", 
        foreign_keys="SchoolClass.curator_id"
    )
    schedule_items: Mapped[List["ScheduleItem"]] = relationship("ScheduleItem", back_populates="teacher")
    assessment_tasks: Mapped[List["AssessmentTask"]] = relationship("AssessmentTask", back_populates="teacher")
    announcements: Mapped[List["Announcement"]] = relationship("Announcement", back_populates="author")

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, name='{self.last_name} {self.first_name}', department='{self.department}')>"
