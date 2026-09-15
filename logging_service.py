import json
import logging
import os
import sys
import threading
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler


LOGGER_NAME = "ditado_f8"
LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "ditado_f8.log"
MAX_LOG_BYTES = 2 * 1024 * 1024
LOG_BACKUP_COUNT = 5


class JsonEventFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "event": getattr(record, "event", record.getMessage()),
            "thread": threading.current_thread().name,
        }

        fields = getattr(record, "fields", None)
        if fields:
            payload.update(fields)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def get_logger():
    return logging.getLogger(LOGGER_NAME)


def configure_logging(base_dir):
    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if getattr(logger, "_ditado_configured", False):
        return logger

    log_dir = os.path.join(base_dir, LOG_DIR_NAME)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, LOG_FILE_NAME)

    formatter = JsonEventFormatter()

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if sys.stderr is not None:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger._ditado_configured = True
    log_event(logger, "logging_configured", log_path=log_path)
    return logger


def log_event(logger, event, level=logging.INFO, **fields):
    logger.log(
        level,
        event,
        extra={
            "event": event,
            "fields": fields,
        },
    )
