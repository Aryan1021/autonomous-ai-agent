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
from agent.regenerator import Regenerator
from agent.models import RegenerationResult
from utils.cache import save_model
from agent.reflection import Reflection

from api.dependencies import (
    get_context_builder,
    get_document_generator,
    get_regenerator,
    get_reflection,
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
    reflection: Reflection = Depends(
        get_reflection,
    ),
    regenerator: Regenerator = Depends(
        get_regenerator,
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

    start_time = time.perf_counter()

    workflow = create_workflow()

    logger.info(
        "[%s] Received agent request.",
        workflow.request_id,
    )

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    logger.info(
        "[%s] Running planner...",
        workflow.request_id,
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
    # Reflection
    # ---------------------------------------------------------

    logger.info(
        "[%s] Running reflection...",
        workflow.request_id,
    )

    reflection_result = await reflection.reflect(
        workflow,
        execution_result,
    )

    if reflection_result.needs_revision:

        logger.info(
            "[%s] Regenerating proposal...",
            workflow.request_id,
        )

        regeneration = await regenerator.regenerate(
            workflow=workflow,
            execution=execution_result,
            reflection=reflection_result,
        )

        execution_result = regeneration.execution

        logger.info(
            "[%s] Running second reflection...",
            workflow.request_id,
        )

        reflection_result = await reflection.reflect(
            workflow,
            execution_result,
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
        reflection_result,
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