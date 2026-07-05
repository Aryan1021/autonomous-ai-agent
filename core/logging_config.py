"""
Centralized logging configuration for the Autonomous AI Agent.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import colorlog

# ----------------------------------------------------------------------
# Logging Constants
# ----------------------------------------------------------------------

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

LOG_FORMAT = (
    "%(log_color)s"
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)-20s | "
    "%(message)s"
)

FILE_LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)-20s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3


def configure_logging() -> None:
    """
    Configure application-wide logging.
    """

    console_formatter = colorlog.ColoredFormatter(
        LOG_FORMAT,
        datefmt=DATE_FORMAT,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    file_formatter = logging.Formatter(
        FILE_LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)

    root_logger = logging.getLogger()

    root_logger.setLevel(logging.INFO)

    # Prevent duplicate handlers during reload
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance.
    """
    return logging.getLogger(name)