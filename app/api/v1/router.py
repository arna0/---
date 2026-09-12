from fastapi import APIRouter
from app.api.v1.endpoints import (
    teachers,
    classes,
    students,
    schedule,
    assessments,
    announcements,
)

api_router = APIRouter()

api_router.include_router(teachers.router, prefix="/teachers", tags=["Учителя / Преподаватели"])
api_router.include_router(classes.router, prefix="/classes", tags=["Профильные классы"])
api_router.include_router(students.router, prefix="/students", tags=["Учащиеся"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["Расписание и Предметы"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Критериальное оценивание (ФО/СОР/СОЧ)"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["Объявления и Новости"])
