import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True, scope="function")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NIS Portal API"

@pytest.mark.asyncio
async def test_full_nis_portal_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create Teacher
        teacher_payload = {
            "first_name": "Алихан",
            "last_name": "Бейсенов",
            "middle_name": "Канатович",
            "email": "a.beisenov@nis.edu.kz",
            "phone": "+77011112233",
            "department": "Кафедра физико-математических дисциплин",
            "qualification_category": "педагог-исследователь",
            "is_active": True
        }
        res_t = await ac.post("/api/v1/teachers/", json=teacher_payload)
        assert res_t.status_code == 201, res_t.text
        teacher = res_t.json()
        teacher_id = teacher["id"]
        assert teacher["last_name"] == "Бейсенов"

        # 2. Create School Class (ФМН)
        class_payload = {
            "grade_level": 10,
            "section": "A",
            "profile": "ФМН",
            "academic_year": "2025-2026",
            "language_of_instruction": "Казахский",
            "curator_id": teacher_id
        }
        res_c = await ac.post("/api/v1/classes/", json=class_payload)
        assert res_c.status_code == 201, res_c.text
        school_class = res_c.json()
        class_id = school_class["id"]

        # 3. Create Student
        student_payload = {
            "first_name": "Арман",
            "last_name": "Сериков",
            "middle_name": "Ерланулы",
            "iin": "080512550123",
            "date_of_birth": "2008-05-12",
            "email": "a.serikov@nis.edu.kz",
            "phone": "+77771234567",
            "parent_phone": "+77019876543",
            "class_id": class_id,
            "is_active": True
        }
        res_s = await ac.post("/api/v1/students/", json=student_payload)
        assert res_s.status_code == 201, res_s.text
        student = res_s.json()
        student_id = student["id"]
        assert student["iin"] == "080512550123"

        # Duplicate IIN validation check
        res_s_dup = await ac.post("/api/v1/students/", json=student_payload)
        assert res_s_dup.status_code == 400

        # 4. Create Subject
        subject_payload = {
            "name": "Физика HL (углубленная)",
            "code": "PHYS_HL",
            "description": "Интегрированная программа по физике углубленного уровня"
        }
        res_subj = await ac.post("/api/v1/schedule/subjects", json=subject_payload)
        assert res_subj.status_code == 201, res_subj.text
        subject = res_subj.json()
        subject_id = subject["id"]

        # 5. Create Schedule Item
        schedule_payload = {
            "day_of_week": 1,
            "lesson_number": 1,
            "start_time": "08:30:00",
            "end_time": "09:15:00",
            "classroom": "Кабинет 302 (Физическая лаборатория)",
            "class_id": class_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id
        }
        res_sch = await ac.post("/api/v1/schedule/items", json=schedule_payload)
        assert res_sch.status_code == 201, res_sch.text

        # 6. Create Criterion Assessment Task (БЖБ / СОР)
        task_payload = {
            "title": "БЖБ №1 по механике",
            "assessment_type": "БЖБ/СОР",
            "term": 1,
            "academic_year": "2025-2026",
            "max_score": 15.0,
            "weight": 1.0,
            "criteria_rubric": "Законы Ньютона и сохранение импульса",
            "task_date": "2025-10-15",
            "subject_id": subject_id,
            "class_id": class_id,
            "teacher_id": teacher_id
        }
        res_task = await ac.post("/api/v1/assessments/tasks", json=task_payload)
        assert res_task.status_code == 201, res_task.text
        task = res_task.json()
        task_id = task["id"]

        # 7. Post Grade for Student
        grade_payload = {
            "task_id": task_id,
            "student_id": student_id,
            "score": 14.0,
            "feedback": "Отличный вывод формулы импульса, обрати внимание на единицы измерения."
        }
        res_grade = await ac.post("/api/v1/assessments/grades", json=grade_payload)
        assert res_grade.status_code == 201, res_grade.text
        grade = res_grade.json()
        assert grade["score"] == 14.0

        # Check Student Report Card
        res_rc = await ac.get(f"/api/v1/assessments/report-card/{student_id}?term=1")
        assert res_rc.status_code == 200, res_rc.text
        report_card = res_rc.json()
        assert report_card["student_id"] == student_id
        assert len(report_card["grades"]) == 1
        assert report_card["average_percentage"] == round((14.0 / 15.0) * 100, 2)

        # 8. Create Announcement
        ann_payload = {
            "title": "Олимпиада по физике им. Аль-Фараби",
            "content": "Внимание учащихся 10-12 классов! Регистрация на школьный этап олимпиады открыта до пятницы.",
            "target_audience": "STUDENTS",
            "priority": "Важно",
            "is_published": True,
            "target_class_id": class_id,
            "author_id": teacher_id
        }
        res_ann = await ac.post("/api/v1/announcements/", json=ann_payload)
        assert res_ann.status_code == 201, res_ann.text
        ann = res_ann.json()
        assert ann["title"] == ann_payload["title"]

        # Get announcements feed
        res_ann_feed = await ac.get("/api/v1/announcements/")
        assert res_ann_feed.status_code == 200
        assert len(res_ann_feed.json()) == 1
