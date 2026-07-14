"""
backend/logger.py

Application-wide logging configuration. Logs to both console and a
rotating file, so production issues can be traced after the fact.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from backend.config import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # avoid duplicate handlers on reload

    logger.setLevel(settings.log_level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            settings.log_file, maxBytes=2_000_000, backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        # File logging is best-effort; console logging still works.
        pass

    return logger
