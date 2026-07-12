"""
Integration test for the Executor service.
"""

import asyncio

from agent.executor import Executor
from agent.llm import LLMService
from agent.models import (
    ExecutionResult,
    PlannerOutput,
)
from agent.planner import Planner
from core.logging_config import (
    configure_logging,
    get_logger,
)
from utils.cache import load_or_generate

from utils.workflow import create_workflow

configure_logging()

logger = get_logger(__name__)

PLANNER_CACHE = "planner_output.json"
EXECUTION_CACHE = "execution_result.json"

USER_REQUEST = (
    "Create a business proposal for an AI healthcare chatbot."
)


async def main() -> None:
    """
    Verify executor generation and cache the result.
    """

    llm = LLMService()

    workflow = create_workflow()

    planner = Planner(llm)
    executor = Executor(llm)

    # ---------------------------------------------------------
    # Load or generate planner output
    # ---------------------------------------------------------

    plan = await load_or_generate(
        filename=PLANNER_CACHE,
        model_type=PlannerOutput,
        generator=planner.plan,
        request=USER_REQUEST,
    )

    # ---------------------------------------------------------
    # Load or generate execution result
    # ---------------------------------------------------------

    result = await load_or_generate(
        filename=EXECUTION_CACHE,
        model_type=ExecutionResult,
        generator=executor.execute,
        workflow=workflow,
        plan=plan,
    )

    # ---------------------------------------------------------
    # Display summary
    # ---------------------------------------------------------

    logger.info("")

    logger.info("=" * 60)
    logger.info("Execution Summary")
    logger.info("=" * 60)

    logger.info(
        "Goal: %s",
        result.goal,
    )

    logger.info(
        "Completed Tasks : %d",
        result.completed_tasks,
    )

    logger.info(
        "Failed Tasks    : %d",
        result.failed_tasks,
    )

    logger.info(
        "Combined Output : %d characters",
        len(result.combined_output),
    )

    logger.info("")

    logger.info("Task Details")

    logger.info("-" * 60)

    for task in result.tasks:

        logger.info(
            "[%d] %-45s %-10s %.2fs",
            task.task_id,
            task.title,
            task.status,
            task.execution_time or 0.0,
        )


if __name__ == "__main__":
    asyncio.run(main())