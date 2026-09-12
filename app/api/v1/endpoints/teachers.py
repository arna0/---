from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_teacher import teacher_crud
from app.schemas.teacher import (
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse,
)

router = APIRouter()


@router.get("/", response_model=List[TeacherResponse], summary="Получить список учителей")
async def read_teachers(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department: Optional[str] = Query(None, description="Фильтр по кафедре"),
):
    """Возвращает список учителей с возможностью пагинации и фильтрации по кафедре."""
    if department:
        return await teacher_crud.get_multi_by_department(
            db, department=department, skip=skip, limit=limit
        )
    return await teacher_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED, summary="Добавить нового учителя")
async def create_teacher(
    teacher_in: TeacherCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создает запись нового учителя."""
    existing = await teacher_crud.get_by_email(db, email=teacher_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Учитель с таким корпоративным email уже существует",
        )
    return await teacher_crud.create(db, obj_in=teacher_in)


@router.get("/{teacher_id}", response_model=TeacherResponse, summary="Получить учителя по ID")
async def read_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает детальную информацию об учителе по ID."""
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учитель не найден",
        )
    return teacher


@router.patch("/{teacher_id}", response_model=TeacherResponse, summary="Обновить данные учителя")
async def update_teacher(
    teacher_id: int,
    teacher_in: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновляет данные существующего учителя."""
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учитель не найден",
        )
    if teacher_in.email and teacher_in.email != teacher.email:
        existing = await teacher_crud.get_by_email(db, email=teacher_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Учитель с таким email уже зарегистрирован",
            )
    return await teacher_crud.update(db, db_obj=teacher, obj_in=teacher_in)


@router.delete("/{teacher_id}", response_model=TeacherResponse, summary="Удалить учителя")
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаляет запись учителя по ID."""
    teacher = await teacher_crud.get(db, id=teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учитель не найден",
        )
    return await teacher_crud.remove(db, id=teacher_id)
