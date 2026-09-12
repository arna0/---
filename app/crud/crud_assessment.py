from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.assessment import AssessmentTask, AssessmentGrade, AssessmentType
from app.models.student import Student
from app.schemas.assessment import (
    AssessmentTaskCreate,
    AssessmentTaskUpdate,
    AssessmentGradeCreate,
    AssessmentGradeUpdate,
    StudentReportCardResponse,
    StudentGradeReportItem,
)


class CRUDAssessmentTask(CRUDBase[AssessmentTask, AssessmentTaskCreate, AssessmentTaskUpdate]):
    """CRUD операции для заданий критериального оценивания (ФО, БЖБ/СОР, ТЖБ/СОЧ)."""

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        class_id: Optional[int] = None,
        subject_id: Optional[int] = None,
        term: Optional[int] = None,
        assessment_type: Optional[AssessmentType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AssessmentTask]:
        statement = select(AssessmentTask)
        if class_id is not None:
            statement = statement.where(AssessmentTask.class_id == class_id)
        if subject_id is not None:
            statement = statement.where(AssessmentTask.subject_id == subject_id)
        if term is not None:
            statement = statement.where(AssessmentTask.term == term)
        if assessment_type is not None:
            statement = statement.where(AssessmentTask.assessment_type == assessment_type)

        statement = statement.order_by(AssessmentTask.task_date.desc()).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())


class CRUDAssessmentGrade(CRUDBase[AssessmentGrade, AssessmentGradeCreate, AssessmentGradeUpdate]):
    """CRUD операции для выставления и получения оценок учеников."""

    async def get_by_task_and_student(
        self, db: AsyncSession, *, task_id: int, student_id: int
    ) -> Optional[AssessmentGrade]:
        statement = select(AssessmentGrade).where(
            AssessmentGrade.task_id == task_id,
            AssessmentGrade.student_id == student_id,
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_student_report_card(
        self, db: AsyncSession, *, student_id: int, term: Optional[int] = None
    ) -> Optional[StudentReportCardResponse]:
        """Формирование сводной ведомости критериального оценивания для ученика."""
        student_statement = select(Student).where(Student.id == student_id)
        student_result = await db.execute(student_statement)
        student = student_result.scalars().first()
        if not student:
            return None

        statement = (
            select(AssessmentGrade)
            .join(AssessmentGrade.task)
            .options(selectinload(AssessmentGrade.task))
            .where(AssessmentGrade.student_id == student_id)
        )
        if term is not None:
            statement = statement.where(AssessmentTask.term == term)

        result = await db.execute(statement)
        grades = list(result.scalars().all())

        items = []
        total_percentage = 0.0
        count = 0

        for g in grades:
            pct = g.percentage
            total_percentage += pct
            count += 1
            items.append(
                StudentGradeReportItem(
                    grade_id=g.id,
                    task_id=g.task_id,
                    task_title=g.task.title,
                    assessment_type=g.task.assessment_type,
                    term=g.task.term,
                    score=g.score,
                    max_score=g.task.max_score,
                    percentage=pct,
                    feedback=g.feedback,
                    subject_id=g.task.subject_id,
                    graded_at=g.graded_at,
                )
            )

        avg_pct = round(total_percentage / count, 2) if count > 0 else 0.0

        return StudentReportCardResponse(
            student_id=student.id,
            student_name=f"{student.last_name} {student.first_name}",
            term=term,
            grades=items,
            average_percentage=avg_pct,
        )


assessment_task_crud = CRUDAssessmentTask(AssessmentTask)
assessment_grade_crud = CRUDAssessmentGrade(AssessmentGrade)
