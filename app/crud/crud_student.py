from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    """CRUD операции для учеников."""

    async def get_by_iin(self, db: AsyncSession, *, iin: str) -> Optional[Student]:
        statement = select(Student).where(Student.iin == iin)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_with_class(self, db: AsyncSession, *, id: int) -> Optional[Student]:
        statement = select(Student).options(selectinload(Student.school_class)).where(Student.id == id)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        class_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Student]:
        statement = select(Student).options(selectinload(Student.school_class))
        if class_id is not None:
            statement = statement.where(Student.class_id == class_id)
        if is_active is not None:
            statement = statement.where(Student.is_active == is_active)
        if search_name:
            statement = statement.where(
                (Student.first_name.ilike(f"%{search_name}%")) | 
                (Student.last_name.ilike(f"%{search_name}%"))
            )

        statement = statement.order_by(Student.last_name, Student.first_name).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())


student_crud = CRUDStudent(Student)
