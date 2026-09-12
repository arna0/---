from datetime import time
from typing import Optional
from pydantic import Field
from app.schemas.common import BaseSchema, TimestampSchema
from app.models.schedule import DayOfWeek
from app.schemas.school_class import SchoolClassResponse
from app.schemas.teacher import TeacherBriefResponse


# --- Subject Schemas ---
class SubjectBase(BaseSchema):
    name: str = Field(..., min_length=2, max_length=150, description="Название предмета")
    code: str = Field(..., min_length=2, max_length=20, description="Код предмета (например, MATH_ADV)")
    description: Optional[str] = Field(None, max_length=500)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = None


class SubjectResponse(SubjectBase, TimestampSchema):
    id: int


# --- ScheduleItem Schemas ---
class ScheduleItemBase(BaseSchema):
    day_of_week: DayOfWeek = Field(..., description="День недели (1 - Пн, 6 - Сб)")
    lesson_number: int = Field(..., ge=1, le=8, description="Номер урока (1-8)")
    start_time: time = Field(..., description="Время начала")
    end_time: time = Field(..., description="Время окончания")
    classroom: str = Field(..., min_length=1, max_length=50, description="Кабинет/Лаборатория")
    class_id: int = Field(..., description="ID класса")
    subject_id: int = Field(..., description="ID предмета")
    teacher_id: int = Field(..., description="ID учителя")


class ScheduleItemCreate(ScheduleItemBase):
    pass


class ScheduleItemUpdate(BaseSchema):
    day_of_week: Optional[DayOfWeek] = None
    lesson_number: Optional[int] = Field(None, ge=1, le=8)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    classroom: Optional[str] = None
    class_id: Optional[int] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None


class ScheduleItemResponse(ScheduleItemBase, TimestampSchema):
    id: int


class ScheduleItemDetailResponse(ScheduleItemResponse):
    school_class: Optional[SchoolClassResponse] = None
    subject: Optional[SubjectResponse] = None
    teacher: Optional[TeacherBriefResponse] = None
