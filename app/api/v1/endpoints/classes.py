from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_class import school_class_crud
from app.crud.crud_teacher import teacher_crud
from app.models.school_class import ClassProfile
from app.schemas.school_class import (
    SchoolClassCreate,
    SchoolClassUpdate,
    SchoolClassResponse,
    SchoolClassDetailResponse,
)

router = APIRouter()


@router.get("/", response_model=List[SchoolClassDetailResponse], summary="Список профильных классов")
async def read_classes(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    grade_level: Optional[int] = Query(None, ge=7, le=12, description="Параллель (7-12)"),
    profile: Optional[ClassProfile] = Query(None, description="Профиль (ФМН, ХБН и др.)"),
    academic_year: Optional[str] = Query(None, description="Учебный год"),
):
    """Возвращает список классов с фильтрацией по параллели, профилю и учебному году."""
    return await school_class_crud.get_multi_filtered(
        db,
        grade_level=grade_level,
        profile=profile,
        academic_year=academic_year,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=SchoolClassResponse, status_code=status.HTTP_201_CREATED, summary="Создать профильный класс")
async def create_class(
    class_in: SchoolClassCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создает новый профильный класс."""
    if class_in.curator_id:
        curator = await teacher_crud.get(db, id=class_in.curator_id)
        if not curator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Куратор с ID {class_in.curator_id} не найден",
            )
    return await school_class_crud.create(db, obj_in=class_in)


@router.get("/{class_id}", response_model=SchoolClassDetailResponse, summary="Получить класс по ID")
async def read_class(
    class_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает информацию о классе и его кураторе."""
    school_class = await school_class_crud.get_with_curator(db, id=class_id)
    if not school_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Класс не найден",
        )
    return school_class


@router.patch("/{class_id}", response_model=SchoolClassResponse, summary="Обновить данные класса")
async def update_class(
    class_id: int,
    class_in: SchoolClassUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Обновляет параметры профильного класса."""
    school_class = await school_class_crud.get(db, id=class_id)
    if not school_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Класс не найден",
        )
    if class_in.curator_id:
        curator = await teacher_crud.get(db, id=class_in.curator_id)
        if not curator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Куратор с ID {class_in.curator_id} не найден",
            )
    return await school_class_crud.update(db, db_obj=school_class, obj_in=class_in)


@router.delete("/{class_id}", response_model=SchoolClassResponse, summary="Удалить класс")
async def delete_class(
    class_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаляет класс по ID."""
    school_class = await school_class_crud.get(db, id=class_id)
    if not school_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Класс не найден",
        )
    return await school_class_crud.remove(db, id=class_id)
