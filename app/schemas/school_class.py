from typing import Optional
from pydantic import Field
from app.schemas.common import BaseSchema, TimestampSchema
from app.models.school_class import ClassProfile
from app.schemas.teacher import TeacherBriefResponse


class SchoolClassBase(BaseSchema):
    grade_level: int = Field(..., ge=7, le=12, description="Параллель (7-12 классы)")
    section: str = Field(..., min_length=1, max_length=5, description="Литера класса (A, B, C...)")
    profile: ClassProfile = Field(ClassProfile.PMN, description="Профиль обучения")
    academic_year: str = Field("2025-2026", min_length=4, max_length=20, description="Учебный год")
    language_of_instruction: str = Field("Казахский", max_length=50, description="Язык обучения")
    curator_id: Optional[int] = Field(None, description="ID куратора")


class SchoolClassCreate(SchoolClassBase):
    pass


class SchoolClassUpdate(BaseSchema):
    grade_level: Optional[int] = Field(None, ge=7, le=12)
    section: Optional[str] = Field(None, min_length=1, max_length=5)
    profile: Optional[ClassProfile] = None
    academic_year: Optional[str] = None
    language_of_instruction: Optional[str] = None
    curator_id: Optional[int] = None


class SchoolClassResponse(SchoolClassBase, TimestampSchema):
    id: int


class SchoolClassDetailResponse(SchoolClassResponse):
    curator: Optional[TeacherBriefResponse] = None
