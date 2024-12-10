import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.logger_config import logger
from app.core.settings import APP_CONFIG
from app.routers import router

app = FastAPI(
    title="ExampleApp",
    description="ExampleApp API 🚀",
    version="1.0.0",
    contact={"name": "Nik", "email": "example@example.com"},
    openapi_url="/api/v1/openapi.json",
    debug=True,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_CONFIG.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


# todo: доделать
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail} - Status Code: {exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/")
def home_page():
    logger.info("Home page accessed")
    return {"message": "Добро пожаловать!  Эта заготовка "}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
