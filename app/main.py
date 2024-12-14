import sentry_sdk
import uvicorn

from app.application import create_app
from app.core.settings import APP_CONFIG

if APP_CONFIG.sentry_dsn and APP_CONFIG.environment != "local":
    sentry_sdk.init(dsn=str(APP_CONFIG.sentry_dsn), enable_tracing=True)


app = create_app(APP_CONFIG)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
