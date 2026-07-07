"""
Integration test for the Planner service.
"""

import asyncio

from agent.llm import LLMService
from agent.models import PlannerOutput
from agent.planner import Planner
from core.logging_config import (
    configure_logging,
    get_logger,
)
from utils.cache import load_or_generate

from utils.workflow import create_workflow

configure_logging()

logger = get_logger(__name__)

CACHE_FILE = "planner_output.json"

USER_REQUEST = (
    "Create a business proposal for an AI healthcare chatbot."
)


async def main() -> None:
    """
    Verify planner generation and cache the result.
    """

    llm = LLMService()

    planner = Planner(llm)

    plan = await load_or_generate(
        filename=CACHE_FILE,
        model_type=PlannerOutput,
        generator=planner.plan,
        request=USER_REQUEST,
    )

    logger.info("")

    logger.info("=" * 60)
    logger.info("Planner Output")
    logger.info("=" * 60)

    logger.info("Goal:")
    logger.info(plan.goal)

    logger.info("")

    logger.info("Assumptions:")

    for assumption in plan.assumptions:
        logger.info("- %s", assumption)

    logger.info("")

    logger.info("Execution Plan:")

    for task in plan.tasks:
        logger.info(
            "[%d] %s (%s)",
            task.task_id,
            task.title,
            task.status,
        )


if __name__ == "__main__":
    asyncio.run(main())