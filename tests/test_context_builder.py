"""
Integration test for the Context Builder.
"""

from agent.context_builder import ContextBuilder
from agent.models import (
    DocumentContext,
    ExecutionResult,
    ReflectionResult,
)
from core.logging_config import (
    configure_logging,
    get_logger,
)
from utils.cache import (
    cache_exists,
    load_model,
    save_model,
)

from utils.workflow import create_workflow

configure_logging()

logger = get_logger(__name__)

EXECUTION_CACHE = "execution_result.json"
REFLECTION_CACHE = "reflection_result.json"
DOCUMENT_CACHE = "document_context.json"


def main() -> None:
    """
    Build a document context from a cached execution result.
    """

    workflow = create_workflow()

    builder = ContextBuilder()

    # ---------------------------------------------------------
    # Load cached execution result
    # ---------------------------------------------------------

    if not cache_exists(EXECUTION_CACHE):

        logger.error(
            "Execution cache not found."
        )

        logger.error(
            "Run 'python -m tests.test_executor' first."
        )

        return

    logger.info(
        "Loading execution result from cache."
    )

    execution_result = load_model(
        EXECUTION_CACHE,
        ExecutionResult,
    )

    reflection = load_model(
        REFLECTION_CACHE,
        ReflectionResult,
    )

    # ---------------------------------------------------------
    # Build document context
    # ---------------------------------------------------------

    logger.info(
        "Building document context."
    )

    context = builder.build(
        workflow,
        execution_result,
        reflection,
    )

    # ---------------------------------------------------------
    # Save context
    # ---------------------------------------------------------

    save_model(
        DOCUMENT_CACHE,
        context,
    )

    logger.info(
        "Document context saved to cache."
    )

    # ---------------------------------------------------------
    # Display summary
    # ---------------------------------------------------------

    logger.info("")

    logger.info("=" * 60)
    logger.info("Document Context")
    logger.info("=" * 60)

    logger.info(
        "Title: %s",
        context.title,
    )

    logger.info(
        "Goal: %s",
        context.goal,
    )

    logger.info("")

    logger.info("Assumptions:")

    for assumption in context.assumptions:

        logger.info(
            "- %s",
            assumption,
        )

    logger.info("")

    logger.info(
        "Sections: %d",
        len(context.sections),
    )

    logger.info("")

    for index, section in enumerate(
        context.sections,
        start=1,
    ):

        logger.info(
            "%d. %s",
            index,
            section.heading,
        )

    logger.info("")

    logger.info("Summary:")

    logger.info(
        context.summary,
    )


if __name__ == "__main__":
    main()