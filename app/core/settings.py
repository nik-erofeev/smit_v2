import os
from enum import StrEnum, unique

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


@unique
class Environments(StrEnum):
    local = "local"
    qa = "qa"
    stage = "stage"
    prod = "prod"
    test = "test"


class DbConfig(BaseModel):
    dsn: str = "postgresql+asyncpg://user:password@host:port/db"
    max_size: int = 1
    debug: bool = False


class TGConfig(BaseModel):
    token: str = ""
    chat_id: str = ""


class KafkaConfig(BaseModel):
    host: str = ""
    port: int = 9092
    batch_size: int = 5
    topik: str = "default"

    @property
    def bootstrap_servers(self) -> str:
        return f"{self.host}:{self.port}"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )

    db: DbConfig = DbConfig()
    kafka: KafkaConfig = KafkaConfig()
    sentry_dsn: str | None = None
    tg: TGConfig = TGConfig()
    environment: Environments = Environments.local

    cors_origin_regex: str = (
        r"(http://|https://)?(.*\.)?(qa|stage|localhost|0.0.0.0)(\.ru)?(:\d+)?$"
    )


BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print("Путь к текущему файлу:", os.path.abspath(__file__))

# Загрузка переменных окружения из каждого файла
env_files = [".env", ".env.local.base", ".env.local"]

for env_file in env_files:
    env_file_path = os.path.join(BASE_PATH, env_file)
    load_dotenv(env_file_path)


APP_CONFIG = AppConfig()
