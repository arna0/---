from typing import Optional
from pydantic import Field
from app.schemas.common import BaseSchema, TimestampSchema
from app.models.announcement import TargetAudience, AnnouncementPriority
from app.schemas.teacher import TeacherBriefResponse


class AnnouncementBase(BaseSchema):
    title: str = Field(..., min_length=2, max_length=255, description="Заголовок объявления")
    content: str = Field(..., min_length=5, description="Текст объявления")
    target_audience: TargetAudience = Field(TargetAudience.ALL, description="Целевая аудитория")
    priority: AnnouncementPriority = Field(AnnouncementPriority.NORMAL, description="Приоритет")
    is_published: bool = Field(True, description="Статус публикации")
    target_class_id: Optional[int] = Field(None, description="ID целевого класса (если применимо)")
    author_id: int = Field(..., description="ID автора (учителя)")


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = Field(None, min_length=5)
    target_audience: Optional[TargetAudience] = None
    priority: Optional[AnnouncementPriority] = None
    is_published: Optional[bool] = None
    target_class_id: Optional[int] = None


class AnnouncementResponse(AnnouncementBase, TimestampSchema):
    id: int


class AnnouncementDetailResponse(AnnouncementResponse):
    author: Optional[TeacherBriefResponse] = None
