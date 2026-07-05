"""
Integration test for the Gemini LLM service.
"""

import asyncio

from agent.llm import LLMService
from core.logging_config import configure_logging, get_logger

configure_logging()

logger = get_logger(__name__)


async def main() -> None:
    """
    Verify that the Gemini LLM service returns a valid response.
    """

    logger.info("Starting Gemini integration test.")

    llm_service = LLMService()

    response = await llm_service.generate(
        "Reply with exactly one short sentence saying hello."
    )

    assert response.strip(), "Gemini returned an empty response."

    logger.info(
        "Response Length: %d",
        len(response),
    )

    logger.info(
        "Gemini Response: %s",
        response,
    )

    logger.info(
        "Gemini integration test completed successfully."
    )


if __name__ == "__main__":
    asyncio.run(main())