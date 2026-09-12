from datetime import datetime
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Базовая Pydantic-схема с поддержкой from_attributes (ORM mode)."""
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseSchema, Generic[T]):
    """Обобщенный ответ с пагинацией."""
    total: int
    items: List[T]
    page: int
    size: int
