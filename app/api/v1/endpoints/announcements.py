from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.crud_announcement import announcement_crud
from app.crud.crud_teacher import teacher_crud
from app.crud.crud_class import school_class_crud
from app.models.announcement import TargetAudience, AnnouncementPriority
from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse,
    AnnouncementDetailResponse,
)

router = APIRouter()


@router.get("/", response_model=List[AnnouncementDetailResponse], summary="Список объявлений и новостей")
async def read_announcements(
    db: AsyncSession = Depends(get_db),
    audience: Optional[TargetAudience] = Query(None, description="Фильтр по аудитории (STUDENTS, TEACHERS, PARENTS)"),
    priority: Optional[AnnouncementPriority] = Query(None, description="Фильтр по приоритету"),
    target_class_id: Optional[int] = Query(None, description="Фильтр по классу"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Возвращает список актуальных объявлений портала с фильтрацией."""
    return await announcement_crud.get_multi_filtered(
        db,
        audience=audience,
        priority=priority,
        target_class_id=target_class_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED, summary="Опубликовать объявление")
async def create_announcement(
    announcement_in: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
):
    """Публикует новое объявление от имени преподавателя/администратора."""
    author = await teacher_crud.get(db, id=announcement_in.author_id)
    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автор (учитель) не найден")

    if announcement_in.target_class_id:
        target_class = await school_class_crud.get(db, id=announcement_in.target_class_id)
        if not target_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Целевой класс не найден")

    return await announcement_crud.create(db, obj_in=announcement_in)


@router.get("/{announcement_id}", response_model=AnnouncementDetailResponse, summary="Получить объявление по ID")
async def read_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает объявление с информацией об авторе."""
    announcement = await announcement_crud.get_with_author(db, id=announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено")
    return announcement


@router.patch("/{announcement_id}", response_model=AnnouncementResponse, summary="Редактировать объявление")
async def update_announcement(
    announcement_id: int,
    announcement_in: AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Редактирует существующее объявление."""
    announcement = await announcement_crud.get(db, id=announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено")

    if announcement_in.target_class_id:
        target_class = await school_class_crud.get(db, id=announcement_in.target_class_id)
        if not target_class:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Целевой класс не найден")

    return await announcement_crud.update(db, db_obj=announcement, obj_in=announcement_in)


@router.delete("/{announcement_id}", response_model=AnnouncementResponse, summary="Удалить объявление")
async def delete_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удаляет объявление."""
    announcement = await announcement_crud.get(db, id=announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Объявление не найдено")
    return await announcement_crud.remove(db, id=announcement_id)
