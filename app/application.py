from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.logger_config import logger
from app.core.settings import AppConfig
from app.kafka.dependencies import kafka_producer
from app.redis.dependencies import redis_cli
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server...")

    logger.info("Starting Kafka producer...")
    await kafka_producer.start()  # если нужен постоянный коннект

    logger.info("Starting Redis client...")
    await redis_cli.setup()  # если нужен постоянный коннект

    yield  # Здесь приложение будет работать

    logger.info("Shutting down server...")
    await kafka_producer.stop()
    await redis_cli.close()


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

    # from prometheus_client.exposition import make_asgi_app
    # from starlette_prometheus import PrometheusMiddleware
    # app.add_middleware(PrometheusMiddleware, filter_unhandled_paths=True)
    # app.mount("/metrics", make_asgi_app())

    app.include_router(router)

    # после app.include_router, то будут видный в сваггере. Иначе объявлять до
    # эндпоинт для отображения метрик для их дальнейшего сбора Прометеусом
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=[".*admin.*", "/metrics"],
    )
    instrumentator.instrument(app).expose(app)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail} - Status Code: {exc.status_code}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.get("/", tags=["Home"])
    def home_page():
        logger.debug("Home page accessed")
        return {"message": "Добро пожаловать! Эта заготовка"}

    @app.get("/favicon.ico")
    async def _favicon():
        return FileResponse("favicon.ico")

    return app
