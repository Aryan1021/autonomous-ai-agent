"""
Integration test for structured JSON generation.
"""

import asyncio

from agent.llm import LLMService
from agent.models import PlannerOutput
from core.logging_config import configure_logging, get_logger
from core.prompts import build_planner_prompt

configure_logging()

logger = get_logger(__name__)


async def main() -> None:
    """
    Verify JSON generation and validation.
    """

    llm = LLMService()

    prompt = build_planner_prompt(
        "Create a business proposal for an AI healthcare chatbot."
    )

    plan = await llm.generate_json(
        prompt=prompt,
        output_model=PlannerOutput,
    )

    logger.info("Goal: %s", plan.goal)

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