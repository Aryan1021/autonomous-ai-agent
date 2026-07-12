"""
Integration test for the Reflection service.
"""

from __future__ import annotations

import asyncio

from agent.executor import Executor
from agent.llm import LLMService
from agent.models import (
    ExecutionResult,
    PlannerOutput,
    ReflectionResult,
    RegenerationResult,
)
from agent.planner import Planner
from agent.reflection import Reflection
from agent.regenerator import Regenerator

from core.logging_config import (
    configure_logging,
    get_logger,
)

from utils.cache import (
    load_or_generate,
    save_model,
)

from utils.workflow import create_workflow

configure_logging()

logger = get_logger(__name__)

PLANNER_CACHE = "planner_output.json"
EXECUTION_CACHE = "execution_result.json"
REFLECTION_CACHE = "reflection_result.json"
REGENERATION_CACHE = "regeneration_result.json"

USER_REQUEST = (
    "Create a business proposal "
    "for an AI healthcare chatbot."
)


async def main() -> None:
    """
    Verify Reflection generation and cache the result.
    """

    workflow = create_workflow()

    llm = LLMService()

    planner = Planner(llm)
    executor = Executor(llm)
    reflection = Reflection(llm)
    regenerator = Regenerator(llm)

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    plan = await load_or_generate(
        filename=PLANNER_CACHE,
        model_type=PlannerOutput,
        generator=planner.plan,
        workflow=workflow,
        request=USER_REQUEST,
    )

    # ---------------------------------------------------------
    # Executor
    # ---------------------------------------------------------

    execution = await load_or_generate(
        filename=EXECUTION_CACHE,
        model_type=ExecutionResult,
        generator=executor.execute,
        workflow=workflow,
        plan=plan,
    )

    # ---------------------------------------------------------
    # Reflection
    # ---------------------------------------------------------

    reflection_result = await load_or_generate(
        filename=REFLECTION_CACHE,
        model_type=ReflectionResult,
        generator=reflection.reflect,
        workflow=workflow,
        result=execution,
        force_refresh=True,
    )

    # ---------------------------------------------------------
    # Regeneration
    # ---------------------------------------------------------

    if reflection_result.needs_revision:

        regeneration = await regenerator.regenerate(
            workflow=workflow,
            execution=execution,
            reflection=reflection_result,
        )

        execution = regeneration.execution

        save_model(
            EXECUTION_CACHE,
            execution,
        )

        save_model(
            REGENERATION_CACHE,
            regeneration,
        )

    logger.info("")

    logger.info("=" * 60)
    logger.info("Reflection Result")
    logger.info("=" * 60)

    logger.info(
        "Overall Score : %d",
        reflection_result.overall_score,
    )

    logger.info(
        "Confidence    : %d",
        reflection_result.confidence,
    )

    logger.info(
        "Needs Revision: %s",
        reflection_result.needs_revision,
    )

    logger.info("")

    logger.info("Strengths")

    logger.info("-" * 60)

    for strength in reflection_result.strengths:

        logger.info(
            "• %s",
            strength,
        )

    logger.info("")

    logger.info("Issues")

    logger.info("-" * 60)

    for issue in reflection_result.issues:

        logger.info(
            "[%s] %s",
            issue.severity.upper(),
            issue.title,
        )

        logger.info(
            "Description : %s",
            issue.description,
        )

        logger.info(
            "Evidence    : %s",
            issue.evidence,
        )

        logger.info("")

    logger.info("Suggestions")

    logger.info("-" * 60)

    for suggestion in reflection_result.suggestions:

        logger.info(
            "%s",
            suggestion.title,
        )

        logger.info(
            "%s",
            suggestion.description,
        )

        logger.info("")

    logger.info("Summary")

    logger.info("-" * 60)

    logger.info(
        reflection_result.summary,
    )


if __name__ == "__main__":
    asyncio.run(main())