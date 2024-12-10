import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger_config import logger
from app.core.settings import APP_CONFIG
from app.routers import router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_CONFIG.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
def home_page():
    logger.info("Home page accessed")
    return {"message": "Добро пожаловать!  Эта заготовка "}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
