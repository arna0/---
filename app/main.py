import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
# Импорт всех моделей для автоматической регистрации таблиц в метаданных Base
import app.models  # noqa: F401
from app.api.v1.router import api_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nis_portal")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: инициализация БД при старте и корректное закрытие пула соединений."""
    logger.info("Инициализация соединения с PostgreSQL и создание таблиц...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы базы данных успешно проверены/созданы.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
    
    yield

    logger.info("Закрытие соединений с базой данных...")
    await engine.dispose()
    logger.info("Приложение остановлено.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Асинхронный REST API бэкенд для образовательного портала Назарбаев Интеллектуальных Школ (НИШ). "
        "Включает управление учениками, учителями, профильными классами (ФМН/ХБН), "
        "расписанием уроков, критериальным оцениванием (ФО, БЖБ/СОР, ТЖБ/СОЧ) и школьными объявлениями."
    ),
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Настройка CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Healthcheck эндпоинт
@app.get("/health", tags=["Система"], summary="Проверка работоспособности сервиса")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": "development" if settings.DEBUG else "production",
    }


# Подключение основного роутера v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Главная"], include_in_schema=False)
async def root():
    return JSONResponse({
        "message": "Добро пожаловать в API образовательного портала НИШ!",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    })
