from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_assessment import assessment_task_crud, assessment_grade_crud
from app.crud.crud_student import student_crud
from app.crud.crud_class import school_class_crud
from app.crud.crud_schedule import subject_crud
from app.crud.crud_teacher import teacher_crud
from app.models.assessment import AssessmentType
from app.schemas.assessment import (
    AssessmentTaskCreate,
    AssessmentTaskUpdate,
    AssessmentTaskResponse,
    AssessmentGradeCreate,
    AssessmentGradeUpdate,
    AssessmentGradeResponse,
    StudentReportCardResponse,
)

router = APIRouter()


# -------------------------------------------------------------
# Assessment Tasks (Задания ФО / БЖБ(СОР) / ТЖБ(СОЧ))
# -------------------------------------------------------------
@router.get("/tasks", response_model=List[AssessmentTaskResponse], summary="Список работ оценивания")
async def read_assessment_tasks(
    db: AsyncSession = Depends(get_db),
    class_id: Optional[int] = Query(None, description="Фильтр по классу"),
    subject_id: Optional[int] = Query(None, description="Фильтр по предмету"),
    term: Optional[int] = Query(None, ge=1, le=4, description="Четверть (1-4)"),
    assessment_type: Optional[AssessmentType] = Query(None, description="Тип (ФО, БЖБ/СОР, ТЖБ/СОЧ)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Возвращает список работ критериального оценивания с фильтрацией."""
    return await assessment_task_crud.get_multi_filtered(
        db,
        class_id=class_id,
        subject_id=subject_id,
        term=term,
        assessment_type=assessment_type,
        skip=skip,
        limit=limit,
    )


@router.post("/tasks", response_model=AssessmentTaskResponse, status_code=status.HTTP_201_CREATED, summary="Создать работу оценивания")
async def create_assessment_task(
    task_in: AssessmentTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создает работу критериального оценивания (СОР/СОЧ/ФО)."""
    if not await school_class_crud.get(db, id=task_in.class_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Класс не найден")
    if not await subject_crud.get(db, id=task_in.subject_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден")
    if not await teacher_crud.get(db, id=task_in.teacher_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден")

    return await assessment_task_crud.create(db, obj_in=task_in)


@router.get("/tasks/{task_id}", response_model=AssessmentTaskResponse, summary="Получить работу по ID")
async def read_assessment_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает данные о задании."""
    task = await assessment_task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Работа оценивания не найдена")
    return task


@router.patch("/tasks/{task_id}", response_model=AssessmentTaskResponse, summary="Обновить работу оценивания")
async def update_assessment_task(
    task_id: int,
    task_in: AssessmentTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновляет параметры работы критериального оценивания."""
    task = await assessment_task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Работа не найдена")
    return await assessment_task_crud.update(db, db_obj=task, obj_in=task_in)


@router.delete("/tasks/{task_id}", response_model=AssessmentTaskResponse, summary="Удалить работу оценивания")
async def delete_assessment_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаляет работу оценивания и все выставленные за нее оценки."""
    task = await assessment_task_crud.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Работа не найдена")
    return await assessment_task_crud.remove(db, id=task_id)


# -------------------------------------------------------------
# Assessment Grades (Выставление оценок и баллов)
# -------------------------------------------------------------
@router.post("/grades", response_model=AssessmentGradeResponse, status_code=status.HTTP_201_CREATED, summary="Выставить балл ученику")
async def record_student_grade(
    grade_in: AssessmentGradeCreate,
    db: AsyncSession = Depends(get_db),
):
    """Выставляет оценку ученику за конкретный СОР/СОЧ или ФО-задание."""
    task = await assessment_task_crud.get(db, id=grade_in.task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задание оценивания не найдено")

    student = await student_crud.get(db, id=grade_in.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ученик не найден")

    if grade_in.score > task.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Балл ({grade_in.score}) не может превышать максимальный балл за работу ({task.max_score})",
        )

    # Проверка, нет ли уже выставленной оценки за это задание
    existing_grade = await assessment_grade_crud.get_by_task_and_student(
        db, task_id=grade_in.task_id, student_id=grade_in.student_id
    )
    if existing_grade:
        # Если оценка уже есть, обновляем ее
        return await assessment_grade_crud.update(db, db_obj=existing_grade, obj_in=grade_in)

    return await assessment_grade_crud.create(db, obj_in=grade_in)


@router.patch("/grades/{grade_id}", response_model=AssessmentGradeResponse, summary="Изменить балл")
async def update_grade(
    grade_id: int,
    grade_in: AssessmentGradeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновляет балл или комментарий обратной связи."""
    grade = await assessment_grade_crud.get(db, id=grade_id)
    if not grade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запись оценки не найдена")

    task = await assessment_task_crud.get(db, id=grade.task_id)
    if grade_in.score is not None and task and grade_in.score > task.max_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Балл ({grade_in.score}) не может превышать максимальный балл ({task.max_score})",
        )

    return await assessment_grade_crud.update(db, db_obj=grade, obj_in=grade_in)


@router.get("/report-card/{student_id}", response_model=StudentReportCardResponse, summary="Электронный табель / ведомость ученика")
async def get_student_report_card(
    student_id: int,
    term: Optional[int] = Query(None, ge=1, le=4, description="Четверть (1-4)"),
    db: AsyncSession = Depends(get_db),
):
    """Формирует сводную ведомость оценок, процентов и дескрипторов ученика за выбранную четверть."""
    report = await assessment_grade_crud.get_student_report_card(db, student_id=student_id, term=term)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ученик не найден")
    return report
