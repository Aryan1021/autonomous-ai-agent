"""
Main entry point for the Autonomous AI Agent API.
"""

from __future__ import annotations

import time

from contextlib import asynccontextmanager

from core.exceptions import ConfigurationException

from fastapi import (
    FastAPI,
    Request,
)

from api.exception_handlers import (
    register_exception_handlers,
)
from api.routes import router

from core.config import settings
from core.logging_config import (
    configure_logging,
    get_logger,
)

configure_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Validate configuration and log startup information.
    """

    logger.info("")
    logger.info("=" * 60)
    logger.info("Autonomous AI Agent API")
    logger.info("=" * 60)

    try:
        _ = settings

    except ConfigurationException:
        logger.exception(
            "Application startup failed due to invalid configuration."
        )
        raise

    logger.info(
        "Version          : %s",
        app.version,
    )

    logger.info(
        "Primary Model    : %s",
        settings.PRIMARY_MODEL,
    )

    logger.info(
        "Fallback Models  : %s",
        ", ".join(settings.FALLBACK_MODELS),
    )

    logger.info(
        "Temperature      : %.1f",
        settings.TEMPERATURE,
    )

    logger.info(
        "Max Retries      : %d",
        settings.MAX_RETRIES,
    )

    logger.info(
        "Log Level        : %s",
        settings.LOG_LEVEL,
    )

    logger.info("")
    logger.info(
        "Application startup completed successfully."
    )
    logger.info("=" * 60)

    yield

    logger.info("")
    logger.info("=" * 60)
    logger.info("Application shutdown completed.")
    logger.info("=" * 60)


app = FastAPI(
    lifespan=lifespan,
    title="Autonomous AI Agent API",
    description=(
        "An AI-powered autonomous workflow capable of planning, "
        "executing, evaluating, regenerating, and generating "
        "professional Microsoft Word documents."
    ),
    version="1.0.0",
    contact={
        "name": "Aryan Raj",
        "url": "https://github.com/Aryan1021",
    },
    license_info={
        "name": "MIT License",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)

register_exception_handlers(app)


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):
    """
    Log the complete lifecycle of every HTTP request.
    """

    start_time = time.perf_counter()

    logger.info("")
    logger.info("=" * 60)
    logger.info("Incoming Request")
    logger.info("=" * 60)

    logger.info(
        "Method      : %s",
        request.method,
    )

    logger.info(
        "Path        : %s",
        request.url.path,
    )

    if request.client:

        logger.info(
            "Client      : %s",
            request.client.host,
        )

    response = None

    try:

        response = await call_next(
            request,
        )

        return response

    finally:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        logger.info("")
        logger.info("=" * 60)
        logger.info("Request Completed")
        logger.info("=" * 60)

        if response is not None:

            logger.info(
                "Status Code : %d",
                response.status_code,
            )

        else:

            logger.error(
                "Status Code : ERROR",
            )

        logger.info(
            "Duration    : %.2f seconds",
            elapsed,
        )

        logger.info("=" * 60)