from datetime import date
from typing import Optional
from pydantic import EmailStr, Field, field_validator
from app.schemas.common import BaseSchema, TimestampSchema
from app.schemas.school_class import SchoolClassResponse


class StudentBase(BaseSchema):
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя ученика")
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия ученика")
    middle_name: Optional[str] = Field(None, max_length=100, description="Отчество")
    iin: str = Field(..., min_length=12, max_length=12, description="ИИН (12 цифр)")
    date_of_birth: date = Field(..., description="Дата рождения")
    email: Optional[EmailStr] = Field(None, description="Email ученика")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон ученика")
    parent_phone: Optional[str] = Field(None, max_length=20, description="Телефон родителей")
    class_id: Optional[int] = Field(None, description="ID класса")
    is_active: bool = Field(True, description="Статус обучения")

    @field_validator("iin")
    def validate_iin(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 12:
            raise ValueError("ИИН должен состоять ровно из 12 цифр")
        return v


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    iin: Optional[str] = Field(None, min_length=12, max_length=12)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None
    class_id: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("iin")
    def validate_iin(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v.isdigit() or len(v) != 12):
            raise ValueError("ИИН должен состоять ровно из 12 цифр")
        return v


class StudentResponse(StudentBase, TimestampSchema):
    id: int


class StudentDetailResponse(StudentResponse):
    school_class: Optional[SchoolClassResponse] = None
