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
_LOG_CONTEXT = threading.local()


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


def _exception_event(logger, event, **fields):
    logger.exception(
        event,
        extra={
            "event": event,
            "fields": fields,
        },
    )


def _install_runtime_instrumentation(logger):
    """Instrument output operations without recording dictated text."""

    try:
        import pyperclip

        original_copy = pyperclip.copy
        if not getattr(original_copy, "_ditado_logged", False):

            def logged_copy(text):
                text_length = len(text) if isinstance(text, str) else None
                try:
                    result = original_copy(text)
                except Exception:
                    _exception_event(
                        logger,
                        "output_copy_error",
                        text_length=text_length,
                        value_type=type(text).__name__,
                    )
                    raise

                log_event(
                    logger,
                    "output_copy",
                    text_length=text_length,
                    value_type=type(text).__name__,
                )
                return result

            logged_copy._ditado_logged = True
            logged_copy._ditado_original = original_copy
            pyperclip.copy = logged_copy

            log_event(
                logger,
                "runtime_instrumentation_installed",
                target="pyperclip.copy",
            )
    except Exception:
        _exception_event(
            logger,
            "runtime_instrumentation_error",
            target="pyperclip.copy",
        )

    try:
        import keyboard

        original_press_and_release = keyboard.press_and_release
        if not getattr(original_press_and_release, "_ditado_logged", False):

            def logged_press_and_release(hotkey, *args, **kwargs):
                key_name = str(hotkey)
                normalized = key_name.lower().replace(" ", "")
                is_paste = normalized in ("ctrl+v", "control+v")

                try:
                    result = original_press_and_release(hotkey, *args, **kwargs)
                except Exception:
                    _exception_event(
                        logger,
                        "output_paste_error" if is_paste else "keyboard_action_error",
                        keys=key_name,
                    )
                    raise

                log_event(
                    logger,
                    "output_paste" if is_paste else "keyboard_action",
                    level=logging.INFO if is_paste else logging.DEBUG,
                    keys=key_name,
                )
                return result

            logged_press_and_release._ditado_logged = True
            logged_press_and_release._ditado_original = original_press_and_release
            keyboard.press_and_release = logged_press_and_release

            log_event(
                logger,
                "runtime_instrumentation_installed",
                target="keyboard.press_and_release",
            )
    except Exception:
        _exception_event(
            logger,
            "runtime_instrumentation_error",
            target="keyboard.press_and_release",
        )


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
    _install_runtime_instrumentation(logger)
    return logger


def log_event(logger, event, level=logging.INFO, **fields):
    if event == "whisper_empty":
        _LOG_CONTEXT.whisper_empty_pending = True
    elif event in ("whisper_success", "whisper_error"):
        _LOG_CONTEXT.whisper_empty_pending = False
    elif event == "transcript_available" and getattr(
        _LOG_CONTEXT, "whisper_empty_pending", False
    ):
        event = "transcript_empty_display"
        fields = dict(fields)
        fields["text_length"] = 0
        fields["empty"] = True
        fields["display_placeholder"] = True
        _LOG_CONTEXT.whisper_empty_pending = False

    logger.log(
        level,
        event,
        extra={
            "event": event,
            "fields": fields,
        },
    )
