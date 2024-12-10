from loguru import logger
from notifiers.logging import NotificationHandler

from app.core.settings import APP_CONFIG

file_path_log = "log.log"
logger.add(file_path_log, level="CRITICAL", rotation="10 MB")

# send Notifications TG
if APP_CONFIG.tg.token and APP_CONFIG.tg.chat_id:
    TG_HANDLER = NotificationHandler("telegram", defaults=APP_CONFIG.tg.model_dump())
    logger.add(TG_HANDLER, level="ERROR")
    logger.info("Telegram notifier handler added successfully.")
else:
    logger.warning(
        "Telegram notification handler not added: token or chat_id is missing.",
    )
