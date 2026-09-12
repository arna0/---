from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.announcement import Announcement, TargetAudience, AnnouncementPriority
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate


class CRUDAnnouncement(CRUDBase[Announcement, AnnouncementCreate, AnnouncementUpdate]):
    """CRUD операции для школьных объявлений и новостей."""

    async def get_with_author(self, db: AsyncSession, *, id: int) -> Optional[Announcement]:
        statement = select(Announcement).options(selectinload(Announcement.author)).where(Announcement.id == id)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        audience: Optional[TargetAudience] = None,
        priority: Optional[AnnouncementPriority] = None,
        target_class_id: Optional[int] = None,
        only_published: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Announcement]:
        statement = select(Announcement).options(selectinload(Announcement.author))
        if only_published:
            statement = statement.where(Announcement.is_published == True)
        if audience is not None:
            statement = statement.where(
                (Announcement.target_audience == audience) | (Announcement.target_audience == TargetAudience.ALL)
            )
        if priority is not None:
            statement = statement.where(Announcement.priority == priority)
        if target_class_id is not None:
            statement = statement.where(
                (Announcement.target_class_id == target_class_id) | (Announcement.target_class_id.is_(None))
            )

        statement = statement.order_by(Announcement.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())


announcement_crud = CRUDAnnouncement(Announcement)
