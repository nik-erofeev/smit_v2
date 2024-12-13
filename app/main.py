from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.logger_config import logger
from app.core.settings import APP_CONFIG
from app.dao.database import async_session_maker
from app.routers import router

if APP_CONFIG.sentry_dsn and APP_CONFIG.environment != "local":
    sentry_sdk.init(dsn=str(APP_CONFIG.sentry_dsn), enable_tracing=True)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    logger.info("Starting server...Hello")
    # Здесь можно выполнить инициализацию, например, подключение к базе данных
    # Инициализация соединения с базой данных
    logger.info("Initializing database connection...")
    async with async_session_maker() as session:
        # Здесь можно выполнить очистку БД или создание таблиц

        # Проверка соединения с базой данных
        async with session.begin():
            await session.execute(text("SELECT 1"))

    logger.info("Database connection initialized successfully.")

    yield

    # Код, который выполняется при завершении работы приложения
    logger.info("Shutting down server...")

    # Здесь можно добавить код для завершения фоновых задач или других ресурсов, если это необходимо
    logger.info("Server stop by user, shutting down! Bye-Bye!!!")


app = FastAPI(
    title=APP_CONFIG.api.project_name,
    description=APP_CONFIG.api.description,
    version=APP_CONFIG.api.version,
    contact={"name": "Nik", "email": "example@example.com"},
    openapi_url=APP_CONFIG.api.openapi_url,
    debug=APP_CONFIG.api.debug,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_CONFIG.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail} - Status Code: {exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/", tags=["Home"])
def home_page():
    logger.info("Home page accessed")
    return {"message": "Добро пожаловать!  Эта заготовка "}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
