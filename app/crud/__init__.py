from app.crud.base import CRUDBase
from app.crud.crud_teacher import teacher_crud, CRUDTeacher
from app.crud.crud_class import school_class_crud, CRUDSchoolClass
from app.crud.crud_student import student_crud, CRUDStudent
from app.crud.crud_schedule import subject_crud, schedule_crud, CRUDSubject, CRUDScheduleItem
from app.crud.crud_assessment import assessment_task_crud, assessment_grade_crud, CRUDAssessmentTask, CRUDAssessmentGrade
from app.crud.crud_announcement import announcement_crud, CRUDAnnouncement

__all__ = [
    "CRUDBase",
    "teacher_crud",
    "CRUDTeacher",
    "school_class_crud",
    "CRUDSchoolClass",
    "student_crud",
    "CRUDStudent",
    "subject_crud",
    "schedule_crud",
    "CRUDSubject",
    "CRUDScheduleItem",
    "assessment_task_crud",
    "assessment_grade_crud",
    "CRUDAssessmentTask",
    "CRUDAssessmentGrade",
    "announcement_crud",
    "CRUDAnnouncement",
]
