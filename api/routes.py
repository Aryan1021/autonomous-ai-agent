"""
API route definitions.
"""

from __future__ import annotations

import time

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from fastapi.responses import FileResponse

from agent.context_builder import ContextBuilder
from agent.document_generator import DocumentGenerator
from agent.executor import Executor
from agent.planner import Planner
from agent.regenerator import Regenerator
from agent.reflection import Reflection

from api.dependencies import (
    get_context_builder,
    get_document_generator,
    get_regenerator,
    get_reflection,
    get_executor,
    get_planner,
)

from api.models import (
    AgentRequest,
    ErrorResponse,
    HealthResponse,
    RootResponse,
)

from utils.workflow import create_workflow

from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Workflow"],
)


@router.get(
    "/",
    summary="API Information",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Returns basic information about the Autonomous AI Agent API."
    ),
)
async def root() -> RootResponse:
    """
    Root endpoint.
    """

    logger.info(
        "Root endpoint accessed."
    )

    return RootResponse(
        application="Autonomous AI Agent",
        version="1.0.0",
        status="running",
    )


@router.get(
    "/health",
    summary="Application Health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    description=(
        "Returns the current health status of the application."
    ),
)
async def health() -> HealthResponse:
    """
    Health check endpoint.
    """

    logger.info(
        "Health endpoint accessed."
    )

    return HealthResponse(
        status="healthy",
    )


@router.post(
    "/agent",
    summary="Execute Autonomous Workflow",
    description=(
        "Executes the complete autonomous workflow including planning, "
        "execution, reflection, regeneration, context building, "
        "and Microsoft Word document generation."
    ),
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Workflow completed successfully."
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid request."
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected server error."
        },
    },
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

    logger.info("")
    logger.info("=" * 60)
    logger.info("Workflow Started")
    logger.info("=" * 60)

    logger.info(
        "Workflow ID : %s",
        workflow.request_id,
    )

    logger.info(
        "Request     : %s",
        request.request,
    )

    logger.info("=" * 60)

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    logger.info("")
    logger.info("[STEP 1/6] Planner")

    planner_start = time.perf_counter()

    planner_output = await planner.plan(
        workflow,
        request.request,
    )

    planner_elapsed = (
        time.perf_counter()
        - planner_start
    )

    logger.info(
        "[%s] Planner completed in %.2f seconds.",
        workflow.request_id,
        planner_elapsed,
    )

    # ---------------------------------------------------------
    # Executor
    # ---------------------------------------------------------

    logger.info("")
    logger.info("[STEP 2/6] Executor")

    executor_start = time.perf_counter()

    execution_result = await executor.execute(
        workflow,
        planner_output,
    )

    executor_elapsed = (
        time.perf_counter()
        - executor_start
    )

    logger.info(
        "[%s] Executor completed in %.2f seconds.",
        workflow.request_id,
        executor_elapsed,
    )

    # ---------------------------------------------------------
    # Reflection
    # ---------------------------------------------------------

    logger.info("")
    logger.info("[STEP 3/6] Reflection")

    reflection_start = time.perf_counter()

    reflection_result = await reflection.reflect(
        workflow,
        execution_result,
    )

    reflection_elapsed = (
        time.perf_counter()
        - reflection_start
    )

    logger.info(
        "[%s] Reflection completed in %.2f seconds.",
        workflow.request_id,
        reflection_elapsed,
    )

    logger.info("")
    logger.info("[STEP 4/6] Regeneration")

    if reflection_result.needs_revision:

        logger.info(
            "[%s] Regeneration required. Starting improvement.",
            workflow.request_id,
        )

        regeneration_start = time.perf_counter()

        regeneration = await regenerator.regenerate(
            workflow=workflow,
            execution=execution_result,
            reflection=reflection_result,
        )

        execution_result = regeneration.execution

        regeneration_elapsed = (
            time.perf_counter()
            - regeneration_start
        )

        logger.info(
            "[%s] Regeneration completed in %.2f seconds.",
            workflow.request_id,
            regeneration_elapsed,
        )

        logger.info(
            "[%s] Running second reflection...",
            workflow.request_id,
        )

        second_reflection_start = time.perf_counter()

        reflection_result = await reflection.reflect(
            workflow,
            execution_result,
        )

        second_reflection_elapsed = (
            time.perf_counter()
            - second_reflection_start
        )

        logger.info(
            "[%s] Second reflection completed in %.2f seconds.",
            workflow.request_id,
            second_reflection_elapsed,
        )

    else:

        logger.info(
            "[%s] Regeneration skipped (No revision required).",
            workflow.request_id,
        )

    # ---------------------------------------------------------
    # Context Builder
    # ---------------------------------------------------------

    logger.info("")
    logger.info("[STEP 5/6] Context Builder")

    context_start = time.perf_counter()

    document_context = context_builder.build(
        workflow,
        execution_result,
        reflection_result,
    )

    context_elapsed = (
        time.perf_counter()
        - context_start
    )

    logger.info(
        "[%s] Context Builder completed in %.2f seconds.",
        workflow.request_id,
        context_elapsed,
    )

    # ---------------------------------------------------------
    # Document Generator
    # ---------------------------------------------------------

    logger.info("")
    logger.info("[STEP 6/6] Document Generator")

    document_start = time.perf_counter()

    document_result = document_generator.generate(
        workflow,
        document_context,
    )

    document_elapsed = (
        time.perf_counter()
        - document_start
    )

    logger.info(
        "[%s] Document Generator completed in %.2f seconds.",
        workflow.request_id,
        document_elapsed,
    )

    elapsed = (
        time.perf_counter()
        - start_time
    )

    logger.info("")
    logger.info("=" * 60)
    logger.info("Workflow Completed Successfully")
    logger.info("=" * 60)

    logger.info(
        "Workflow ID : %s",
        workflow.request_id,
    )

    logger.info(
        "Total Time  : %.2f seconds",
        elapsed,
    )

    logger.info(
        "Result      : SUCCESS",
    )

    logger.info("=" * 60)

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
    summary="Test Exception Handling",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    description=(
        "Utility endpoint used to verify global exception handling."
    ),
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Intentional server error.",
        },
    },
)
async def trigger_error() -> None:
    """
    Endpoint used to verify exception handling.
    """

    raise RuntimeError(
        "Unexpected crash."
    )