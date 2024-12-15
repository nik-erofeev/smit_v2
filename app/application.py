from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from prometheus_client.exposition import make_asgi_app
from sqlalchemy import text
from starlette_prometheus import PrometheusMiddleware

from app.core.logger_config import logger
from app.core.settings import AppConfig
from app.dao.database import async_session_maker
from app.kafka.producer import KafkaProducer
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...Hello")

    logger.info("Initializing database connection...")
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(text("SELECT 1"))
    logger.info("Database connection initialized successfully.")

    logger.info("Starting Kafka producer...")
    producer = KafkaProducer()
    await producer.start()  # Инициализация KafkaProducer

    yield  # Здесь приложение будет работать

    logger.info("Shutting down server...")
    await producer.stop()  # Остановка KafkaProducer


def create_app(config: AppConfig) -> FastAPI:
    app = FastAPI(
        title=config.api.project_name,
        description=config.api.description,
        version=config.api.version,
        contact={"name": "Nik", "email": "example@example.com"},
        openapi_url=config.api.openapi_url,
        debug=config.api.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(PrometheusMiddleware, filter_unhandled_paths=True)
    app.mount("/metrics", make_asgi_app())

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
        return {"message": "Добро пожаловать! Эта заготовка"}

    @app.get("/favicon.ico")
    async def _favicon():
        return FileResponse("favicon.ico")

    return app