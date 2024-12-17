import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
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

    # эндпоинт для отображения метрик для их дальнейшего сбора Прометеусом
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=[".*admin.*", "/metrics"],
    )
    instrumentator.instrument(app).expose(app, include_in_schema=True)  # можно выкл

    app.include_router(router)

    @app.exception_handler(Exception)
    async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"An unexpected error occurred: {exc=!r}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )

    # локально и в докере разные workdir при запуске приложения
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
    FAVICON_PATH = os.path.join(BASE_DIR, "../favicon.ico")

    templates = Jinja2Templates(directory=TEMPLATES_DIR)

    @app.get("/", tags=["Home"], include_in_schema=False)
    def home_page(request: Request) -> Response:
        logger.debug("Home page accessed")
        return templates.TemplateResponse(
            name="index.html",
            context={"request": request},
        )

    @app.get("/favicon.ico", include_in_schema=False)
    async def _favicon() -> FileResponse:
        return FileResponse(FAVICON_PATH)

    return app
