from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.school_class import SchoolClass, ClassProfile
from app.schemas.school_class import SchoolClassCreate, SchoolClassUpdate


class CRUDSchoolClass(CRUDBase[SchoolClass, SchoolClassCreate, SchoolClassUpdate]):
    """CRUD операции для профильных классов НИШ."""

    async def get_with_curator(self, db: AsyncSession, *, id: int) -> Optional[SchoolClass]:
        statement = select(SchoolClass).options(selectinload(SchoolClass.curator)).where(SchoolClass.id == id)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        grade_level: Optional[int] = None,
        profile: Optional[ClassProfile] = None,
        academic_year: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SchoolClass]:
        statement = select(SchoolClass).options(selectinload(SchoolClass.curator))
        if grade_level is not None:
            statement = statement.where(SchoolClass.grade_level == grade_level)
        if profile is not None:
            statement = statement.where(SchoolClass.profile == profile)
        if academic_year is not None:
            statement = statement.where(SchoolClass.academic_year == academic_year)
        
        statement = statement.order_by(SchoolClass.grade_level, SchoolClass.section).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())


school_class_crud = CRUDSchoolClass(SchoolClass)
