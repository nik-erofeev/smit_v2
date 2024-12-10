import os
from enum import StrEnum, unique

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
    commit: bool = False
    echo: bool = False


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
    db: DbConfig = DbConfig()
    kafka: KafkaConfig = KafkaConfig()
    sentry_dsn: str | None = None
    tg: TGConfig = TGConfig()
    environment: Environments = Environments.local
    SECRET_KEY: str | None = None
    ALGORITHM: str | None = None

    cors_origin_regex: str = (
        r"(http://|https://)?(.*\.)?(qa|stage|localhost|0.0.0.0)(\.ru)?(:\d+)?$"
    )

    # на 2 уровня выше
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    _ENV_FILES: list[str] = [
        f"{BASE_DIR}/.env.local.base",
        f"{BASE_DIR}/.env.local",
        f"{BASE_DIR}/.env",  # последний перезапишет
    ]

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        env_file=_ENV_FILES,
        # env_file=(f"{BASE_DIR}/.env2", f"{BASE_DIR}/.env.local", f"{BASE_DIR}/.env"),
    )


APP_CONFIG = AppConfig()
