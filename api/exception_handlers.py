"""
Global exception handlers for the FastAPI application.
"""

from __future__ import annotations

from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.responses import JSONResponse

from api.models import ErrorResponse

from core.exceptions import (
    AgentException,
    ConfigurationException,
    DocumentException,
    ExecutorException,
    LLMException,
    PlannerException,
    ReflectionException,
    RegenerationException,
    ValidationException,
)

from core.logging_config import get_logger

logger = get_logger(__name__)


def register_exception_handlers(
    app: FastAPI,
) -> None:
    """
    Register global exception handlers.
    """

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Request,
        exc: ValidationException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error="Validation Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(ConfigurationException)
    async def configuration_exception_handler(
        request: Request,
        exc: ConfigurationException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Configuration Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(PlannerException)
    async def planner_exception_handler(
        request: Request,
        exc: PlannerException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Planner Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(ExecutorException)
    async def executor_exception_handler(
        request: Request,
        exc: ExecutorException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Executor Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(ReflectionException)
    async def reflection_exception_handler(
        request: Request,
        exc: ReflectionException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Reflection Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(RegenerationException)
    async def regeneration_exception_handler(
        request: Request,
        exc: RegenerationException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Regeneration Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(DocumentException)
    async def document_exception_handler(
        request: Request,
        exc: DocumentException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Document Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(LLMException)
    async def llm_exception_handler(
        request: Request,
        exc: LLMException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="LLM Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(AgentException)
    async def agent_exception_handler(
        request: Request,
        exc: AgentException,
    ) -> JSONResponse:

        logger.error(
            "%s",
            exc,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Agent Error",
                detail=str(exc),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:

        logger.exception("Unexpected exception.")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                detail=str(exc),
            ).model_dump(),
        )