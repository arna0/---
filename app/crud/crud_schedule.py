from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.schedule import Subject, ScheduleItem, DayOfWeek
from app.schemas.schedule import (
    SubjectCreate,
    SubjectUpdate,
    ScheduleItemCreate,
    ScheduleItemUpdate,
)


class CRUDSubject(CRUDBase[Subject, SubjectCreate, SubjectUpdate]):
    """CRUD операции для предметов."""

    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Subject]:
        statement = select(Subject).where(Subject.code == code)
        result = await db.execute(statement)
        return result.scalars().first()


class CRUDScheduleItem(CRUDBase[ScheduleItem, ScheduleItemCreate, ScheduleItemUpdate]):
    """CRUD операции для элементов расписания."""

    async def get_with_details(self, db: AsyncSession, *, id: int) -> Optional[ScheduleItem]:
        statement = (
            select(ScheduleItem)
            .options(
                selectinload(ScheduleItem.school_class),
                selectinload(ScheduleItem.subject),
                selectinload(ScheduleItem.teacher),
            )
            .where(ScheduleItem.id == id)
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        class_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        day_of_week: Optional[DayOfWeek] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ScheduleItem]:
        statement = select(ScheduleItem).options(
            selectinload(ScheduleItem.school_class),
            selectinload(ScheduleItem.subject),
            selectinload(ScheduleItem.teacher),
        )
        if class_id is not None:
            statement = statement.where(ScheduleItem.class_id == class_id)
        if teacher_id is not None:
            statement = statement.where(ScheduleItem.teacher_id == teacher_id)
        if day_of_week is not None:
            statement = statement.where(ScheduleItem.day_of_week == day_of_week)

        statement = statement.order_by(ScheduleItem.day_of_week, ScheduleItem.lesson_number).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())


subject_crud = CRUDSubject(Subject)
schedule_crud = CRUDScheduleItem(ScheduleItem)
