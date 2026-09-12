from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_schedule import subject_crud, schedule_crud
from app.crud.crud_class import school_class_crud
from app.crud.crud_teacher import teacher_crud
from app.models.schedule import DayOfWeek
from app.schemas.schedule import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    ScheduleItemCreate,
    ScheduleItemUpdate,
    ScheduleItemResponse,
    ScheduleItemDetailResponse,
)

router = APIRouter()


# -------------------------------------------------------------
# Subjects (Предметы)
# -------------------------------------------------------------
@router.get("/subjects", response_model=List[SubjectResponse], summary="Список предметов")
async def read_subjects(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Возвращает список предметов."""
    return await subject_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, summary="Добавить предмет")
async def create_subject(
    subject_in: SubjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создает новый учебный предмет."""
    existing = await subject_crud.get_by_code(db, code=subject_in.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Предмет с кодом '{subject_in.code}' уже существует",
        )
    return await subject_crud.create(db, obj_in=subject_in)


@router.get("/subjects/{subject_id}", response_model=SubjectResponse, summary="Получить предмет по ID")
async def read_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает данные о предмете."""
    subject = await subject_crud.get(db, id=subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден",
        )
    return subject


@router.patch("/subjects/{subject_id}", response_model=SubjectResponse, summary="Обновить предмет")
async def update_subject(
    subject_id: int,
    subject_in: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновляет информацию о предмете."""
    subject = await subject_crud.get(db, id=subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден",
        )
    if subject_in.code and subject_in.code != subject.code:
        existing = await subject_crud.get_by_code(db, code=subject_in.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Предмет с кодом '{subject_in.code}' уже существует",
            )
    return await subject_crud.update(db, db_obj=subject, obj_in=subject_in)


@router.delete("/subjects/{subject_id}", response_model=SubjectResponse, summary="Удалить предмет")
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаляет предмет."""
    subject = await subject_crud.get(db, id=subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден",
        )
    return await subject_crud.remove(db, id=subject_id)


# -------------------------------------------------------------
# Schedule Items (Расписание)
# -------------------------------------------------------------
@router.get("/items", response_model=List[ScheduleItemDetailResponse], summary="Получить расписание уроков")
async def read_schedule_items(
    db: AsyncSession = Depends(get_db),
    class_id: Optional[int] = Query(None, description="Фильтр по классу"),
    teacher_id: Optional[int] = Query(None, description="Фильтр по учителю"),
    day_of_week: Optional[DayOfWeek] = Query(None, description="Фильтр по дню недели (1-6)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Возвращает расписание уроков с фильтрацией по классу, преподавателю и дням недели."""
    return await schedule_crud.get_multi_filtered(
        db,
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=day_of_week,
        skip=skip,
        limit=limit,
    )


@router.post("/items", response_model=ScheduleItemResponse, status_code=status.HTTP_201_CREATED, summary="Добавить урок в расписание")
async def create_schedule_item(
    item_in: ScheduleItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Добавляет урок в расписание с проверкой связности класса, предмета и учителя."""
    # Проверка класса
    school_class = await school_class_crud.get(db, id=item_in.class_id)
    if not school_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Класс с ID {item_in.class_id} не найден")

    # Проверка предмета
    subject = await subject_crud.get(db, id=item_in.subject_id)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Предмет с ID {item_in.subject_id} не найден")

    # Проверка учителя
    teacher = await teacher_crud.get(db, id=item_in.teacher_id)
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Учитель с ID {item_in.teacher_id} не найден")

    return await schedule_crud.create(db, obj_in=item_in)


@router.get("/items/{item_id}", response_model=ScheduleItemDetailResponse, summary="Получить урок по ID")
async def read_schedule_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает детальную информацию о конкретном уроке в расписании."""
    item = await schedule_crud.get_with_details(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Урок не найден в расписании")
    return item


@router.patch("/items/{item_id}", response_model=ScheduleItemResponse, summary="Обновить урок в расписании")
async def update_schedule_item(
    item_id: int,
    item_in: ScheduleItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновляет информацию об уроке в расписании."""
    item = await schedule_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Урок не найден в расписании")

    if item_in.class_id:
        c = await school_class_crud.get(db, id=item_in.class_id)
        if not c:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Класс не найден")

    if item_in.subject_id:
        s = await subject_crud.get(db, id=item_in.subject_id)
        if not s:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Предмет не найден")

    if item_in.teacher_id:
        t = await teacher_crud.get(db, id=item_in.teacher_id)
        if not t:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Учитель не найден")

    return await schedule_crud.update(db, db_obj=item, obj_in=item_in)


@router.delete("/items/{item_id}", response_model=ScheduleItemResponse, summary="Удалить урок из расписания")
async def delete_schedule_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаляет урок из расписания."""
    item = await schedule_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Урок не найден в расписании")
    return await schedule_crud.remove(db, id=item_id)
