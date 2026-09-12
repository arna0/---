from typing import Optional
from pydantic import EmailStr, Field
from app.schemas.common import BaseSchema, TimestampSchema


class TeacherBase(BaseSchema):
    first_name: str = Field(..., min_length=1, max_length=100, description="Имя учителя")
    last_name: str = Field(..., min_length=1, max_length=100, description="Фамилия учителя")
    middle_name: Optional[str] = Field(None, max_length=100, description="Отчество")
    email: EmailStr = Field(..., description="Корпоративный email")
    phone: Optional[str] = Field(None, max_length=20, description="Номер телефона")
    department: str = Field(..., min_length=2, max_length=150, description="Кафедра")
    qualification_category: Optional[str] = Field(None, description="Категория (педагог-эксперт/исследователь/мастер)")
    is_active: bool = Field(True, description="Активен ли сотрудник")


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    qualification_category: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherResponse(TeacherBase, TimestampSchema):
    id: int


class TeacherBriefResponse(BaseSchema):
    id: int
    first_name: str
    last_name: str
    department: str
