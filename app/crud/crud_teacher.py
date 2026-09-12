from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate


class CRUDTeacher(CRUDBase[Teacher, TeacherCreate, TeacherUpdate]):
    """CRUD операции для учителей."""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[Teacher]:
        statement = select(Teacher).where(Teacher.email == email)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi_by_department(
        self, db: AsyncSession, *, department: str, skip: int = 0, limit: int = 100
    ) -> List[Teacher]:
        statement = (
            select(Teacher)
            .where(Teacher.department.ilike(f"%{department}%"))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())


teacher_crud = CRUDTeacher(Teacher)
