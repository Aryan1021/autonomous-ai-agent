"""
Custom exceptions and global exception handlers for the Autonomous AI Agent.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.logging_config import get_logger

logger = get_logger(__name__)


class AgentException(Exception):
    """
    Base exception for the Autonomous AI Agent.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all application exception handlers.
    """

    @app.exception_handler(AgentException)
    async def agent_exception_handler(
        request: Request,
        exc: AgentException,
    ) -> JSONResponse:
        """
        Handle custom application exceptions.
        """

        logger.warning(
            "AgentException on %s %s: %s",
            request.method,
            request.url.path,
            exc.message,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Handle unexpected exceptions.
        """

        logger.exception(
            "Unhandled exception on %s %s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Internal Server Error",
                "detail": (
                    "An unexpected error occurred while processing the request."
                ),
            },
        )