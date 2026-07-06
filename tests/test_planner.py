"""
Integration test for the Planner service.
"""

import asyncio

from agent.llm import LLMService
from agent.planner import Planner
from core.logging_config import configure_logging, get_logger

configure_logging()

logger = get_logger(__name__)


async def main() -> None:

    planner = Planner(
        LLMService(),
    )

    plan = await planner.plan(
        "Create a business proposal for an AI healthcare chatbot."
    )

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