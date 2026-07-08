"""
API route definitions.
"""

from __future__ import annotations

import time

from fastapi import (
    APIRouter,
    Depends,
)

from fastapi.responses import FileResponse

from agent.context_builder import ContextBuilder
from agent.document_generator import DocumentGenerator
from agent.executor import Executor
from agent.planner import Planner

from api.dependencies import (
    get_context_builder,
    get_document_generator,
    get_executor,
    get_planner,
)

from api.models import AgentRequest

from utils.workflow import create_workflow

from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Autonomous AI Agent"],
)


@router.get(
    "/",
    summary="Root Endpoint",
)
async def root() -> dict[str, str]:
    """
    Root endpoint.
    """

    logger.info(
        "Root endpoint accessed."
    )

    return {
        "application": "Autonomous AI Agent",
        "version": "1.0.0",
        "status": "running",
    }


@router.get(
    "/health",
    summary="Health Check",
)
async def health() -> dict[str, str]:
    """
    Health check endpoint.
    """

    logger.info(
        "Health endpoint accessed."
    )

    return {
        "status": "healthy",
    }


@router.post(
    "/agent",
    summary="Run Autonomous AI Agent",
)
async def run_agent(
    request: AgentRequest,
    planner: Planner = Depends(
        get_planner,
    ),
    executor: Executor = Depends(
        get_executor,
    ),
    context_builder: ContextBuilder = Depends(
        get_context_builder,
    ),
    document_generator: DocumentGenerator = Depends(
        get_document_generator,
    ),
) -> FileResponse:
    """
    Execute the complete autonomous AI workflow.
    """

    logger.info(
        "Received agent request."
    )

    start_time = time.perf_counter()

    workflow = create_workflow()

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    logger.info(
        "Running planner..."
    )

    planner_output = await planner.plan(
        workflow,
        request.request,
    )

    # ---------------------------------------------------------
    # Executor
    # ---------------------------------------------------------

    logger.info(
        "Running executor..."
    )

    execution_result = await executor.execute(
        workflow,
        planner_output,
    )

    # ---------------------------------------------------------
    # Context Builder
    # ---------------------------------------------------------

    logger.info(
        "Building document context..."
    )

    document_context = context_builder.build(
        workflow,
        execution_result,
    )

    # ---------------------------------------------------------
    # Document Generator
    # ---------------------------------------------------------

    logger.info(
        "Generating Microsoft Word document..."
    )

    document_result = document_generator.generate(
        workflow,
        document_context,
    )

    elapsed = (
        time.perf_counter()
        - start_time
    )

    logger.info(
        "Workflow completed successfully in %.2f seconds.",
        elapsed,
    )

    return FileResponse(
        path=document_result.document_path,
        filename=document_result.filename,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
    )


@router.get(
    "/error",
    summary="Trigger Test Exception",
)
async def trigger_error() -> None:
    """
    Endpoint used to verify exception handling.
    """

    raise RuntimeError(
        "Unexpected crash."
    )