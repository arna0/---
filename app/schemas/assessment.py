from datetime import date, datetime
from typing import Optional, List
from pydantic import Field
from app.schemas.common import BaseSchema, TimestampSchema
from app.models.assessment import AssessmentType
from app.schemas.schedule import SubjectResponse
from app.schemas.student import StudentBase


# --- AssessmentTask Schemas (СОР/СОЧ/ФО задания) ---
class AssessmentTaskBase(BaseSchema):
    title: str = Field(..., min_length=2, max_length=200, description="Тема работы")
    assessment_type: AssessmentType = Field(..., description="Тип: ФО, БЖБ/СОР, ТЖБ/СОЧ")
    term: int = Field(..., ge=1, le=4, description="Четверть (1-4)")
    academic_year: str = Field("2025-2026", description="Учебный год")
    max_score: float = Field(10.0, gt=0, description="Максимальный первичный балл")
    weight: float = Field(1.0, gt=0, description="Вес в итоговой оценке")
    criteria_rubric: Optional[str] = Field(None, description="Дескрипторы и критерии оценивания")
    task_date: date = Field(..., description="Дата проведения")
    subject_id: int = Field(..., description="ID предмета")
    class_id: int = Field(..., description="ID класса")
    teacher_id: int = Field(..., description="ID учителя")


class AssessmentTaskCreate(AssessmentTaskBase):
    pass


class AssessmentTaskUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    assessment_type: Optional[AssessmentType] = None
    term: Optional[int] = Field(None, ge=1, le=4)
    academic_year: Optional[str] = None
    max_score: Optional[float] = Field(None, gt=0)
    weight: Optional[float] = Field(None, gt=0)
    criteria_rubric: Optional[str] = None
    task_date: Optional[date] = None
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    teacher_id: Optional[int] = None


class AssessmentTaskResponse(AssessmentTaskBase, TimestampSchema):
    id: int


# --- AssessmentGrade Schemas (Выставленные оценки / баллы) ---
class AssessmentGradeBase(BaseSchema):
    task_id: int = Field(..., description="ID задания (СОР/СОЧ/ФО)")
    student_id: int = Field(..., description="ID ученика")
    score: float = Field(..., ge=0, description="Набранный балл")
    feedback: Optional[str] = Field(None, description="Обратная связь учителя / дескрипторы")


class AssessmentGradeCreate(AssessmentGradeBase):
    pass


class AssessmentGradeUpdate(BaseSchema):
    score: Optional[float] = Field(None, ge=0)
    feedback: Optional[str] = None


class AssessmentGradeResponse(AssessmentGradeBase, TimestampSchema):
    id: int
    graded_at: datetime
    percentage: Optional[float] = None


# --- Student Performance / Report Card Schemas ---
class StudentGradeReportItem(BaseSchema):
    grade_id: int
    task_id: int
    task_title: str
    assessment_type: AssessmentType
    term: int
    score: float
    max_score: float
    percentage: float
    feedback: Optional[str]
    subject_id: int
    graded_at: datetime


class StudentReportCardResponse(BaseSchema):
    student_id: int
    student_name: str
    term: Optional[int] = None
    grades: List[StudentGradeReportItem]
    average_percentage: float
