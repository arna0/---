from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_student import student_crud
from app.crud.crud_class import school_class_crud
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentDetailResponse,
)

router = APIRouter()


@router.get("/", response_model=List[StudentDetailResponse], summary="Список учащихся")
async def read_students(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    class_id: Optional[int] = Query(None, description="Фильтр по классу"),
    is_active: Optional[bool] = Query(None, description="Статус обучения"),
    search: Optional[str] = Query(None, description="Поиск по имени/фамилии"),
):
    """Возвращает список учеников с фильтрацией по классу, активности и поиску по ФИО."""
    return await student_crud.get_multi_filtered(
        db,
        class_id=class_id,
        is_active=is_active,
        search_name=search,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, summary="Зачислить ученика")
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создает запись нового ученика с валидацией ИИН и привязкой к классу."""
    existing_iin = await student_crud.get_by_iin(db, iin=student_in.iin)
    if existing_iin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ученик с таким ИИН уже зарегистрирован в системе",
        )
    if student_in.class_id:
        target_class = await school_class_crud.get(db, id=student_in.class_id)
        if not target_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Класс с ID {student_in.class_id} не найден",
            )
    return await student_crud.create(db, obj_in=student_in)


@router.get("/{student_id}", response_model=StudentDetailResponse, summary="Получить ученика по ID")
async def read_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает подробные данные об ученике и его классе."""
    student = await student_crud.get_with_class(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден",
        )
    return student


@router.patch("/{student_id}", response_model=StudentResponse, summary="Обновить данные ученика")
async def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновляет личные данные ученика или переводит в другой класс."""
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден",
        )
    if student_in.iin and student_in.iin != student.iin:
        existing_iin = await student_crud.get_by_iin(db, iin=student_in.iin)
        if existing_iin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ученик с таким ИИН уже зарегистрирован",
            )
    if student_in.class_id and student_in.class_id != student.class_id:
        target_class = await school_class_crud.get(db, id=student_in.class_id)
        if not target_class:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Класс с ID {student_in.class_id} не найден",
            )
    return await student_crud.update(db, db_obj=student, obj_in=student_in)


@router.delete("/{student_id}", response_model=StudentResponse, summary="Удалить ученика")
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаляет запись ученика."""
    student = await student_crud.get(db, id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ученик не найден",
        )
    return await student_crud.remove(db, id=student_id)
