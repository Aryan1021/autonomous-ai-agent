"""
Main entry point for the Autonomous AI Agent API.
"""

from __future__ import annotations

from fastapi import FastAPI

from api.routes import router
from core.logging_config import (
    configure_logging,
    get_logger,
)

configure_logging()

logger = get_logger(__name__)

app = FastAPI(
    title="Autonomous AI Agent API",
    description=(
        "An autonomous AI agent capable of planning, "
        "executing tasks, and generating professional "
        "Microsoft Word documents."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)

logger.info(
    "Autonomous AI Agent API initialized."
)