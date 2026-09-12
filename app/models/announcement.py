import enum
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Integer, String, Text, Enum, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.teacher import Teacher


class TargetAudience(str, enum.Enum):
    """Целевая аудитория объявления."""
    ALL = "ALL"                    # Все пользователи
    STUDENTS = "STUDENTS"          # Только учащиеся
    TEACHERS = "TEACHERS"          # Только преподаватели
    PARENTS = "PARENTS"            # Только родители
    CLASS_SPECIFIC = "CLASS"       # Определенный класс


class AnnouncementPriority(str, enum.Enum):
    """Уровень приоритета объявления."""
    LOW = "Низкий"
    NORMAL = "Обычный"
    IMPORTANT = "Важно"
    URGENT = "Срочно"


class Announcement(Base, TimestampMixin):
    """Модель школьного объявления / новости на портале НИШ."""
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Заголовок объявления")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Текст объявления")
    target_audience: Mapped[TargetAudience] = mapped_column(
        Enum(TargetAudience, native_enum=False), 
        default=TargetAudience.ALL, 
        nullable=False, 
        comment="Целевая аудитория"
    )
    priority: Mapped[AnnouncementPriority] = mapped_column(
        Enum(AnnouncementPriority, native_enum=False), 
        default=AnnouncementPriority.NORMAL, 
        nullable=False, 
        comment="Приоритет новости"
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, comment="Опубликовано")
    target_class_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("school_classes.id", ondelete="SET NULL"), 
        nullable=True, 
        comment="ID целевого класса (если применимо)"
    )

    # Автор (учитель / администрация)
    author_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("teachers.id", ondelete="CASCADE"), 
        nullable=False, 
        comment="Автор объявления"
    )

    # Связи
    author: Mapped["Teacher"] = relationship("Teacher", back_populates="announcements")

    def __repr__(self) -> str:
        return f"<Announcement(id={self.id}, title='{self.title[:30]}', priority='{self.priority.value}')>"
