"""
Integration test for the Document Generator.
"""

from agent.document_generator import DocumentGenerator
from agent.models import (
    DocumentContext,
    DocumentResult,
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

DOCUMENT_CONTEXT_CACHE = "document_context.json"
DOCUMENT_RESULT_CACHE = "document_result.json"


def main() -> None:
    """
    Generate a Word document from the cached document context.
    """

    if not cache_exists(DOCUMENT_CONTEXT_CACHE):

        logger.error(
            "Document context cache not found."
        )

        logger.error(
            "Run 'python -m tests.test_context_builder' first."
        )

        return

    logger.info(
        "Loading document context from cache."
    )

    context = load_model(
        DOCUMENT_CONTEXT_CACHE,
        DocumentContext,
    )

    workflow = create_workflow()

    generator = DocumentGenerator()

    logger.info(
        "Generating Word document..."
    )

    result = generator.generate(
        workflow,
        context,
    )

    save_model(
        DOCUMENT_RESULT_CACHE,
        result,
    )

    logger.info(
        "Document result saved to cache."
    )

    logger.info("")

    logger.info("=" * 60)
    logger.info("Document Generation Summary")
    logger.info("=" * 60)

    logger.info(
        "Title          : %s",
        result.title,
    )

    logger.info(
        "Filename       : %s",
        result.filename,
    )

    logger.info(
        "Document Path  : %s",
        result.document_path,
    )

    logger.info(
        "Sections       : %d",
        result.section_count,
    )

    logger.info(
        "Word Count     : %d",
        result.word_count,
    )

    logger.info(
        "Generated At   : %s",
        result.generated_at.strftime(
            "%d-%m-%Y %H:%M:%S"
        ),
    )

    logger.info("")
    logger.info("Document generated successfully.")


if __name__ == "__main__":
    main()