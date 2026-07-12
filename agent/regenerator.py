"""
Regenerator service responsible for improving execution results
using reflection feedback.
"""

from __future__ import annotations

from agent.llm import LLMService
from agent.models import (
    ExecutionResult,
    RegenerationResult,
    ReflectionResult,
    WorkflowContext,
)
from core.exceptions import (
    ConfigurationException,
    LLMException,
    RegenerationException,
    ValidationException,
)
from core.logging_config import get_logger
from core.regeneration_prompt import (
    build_regeneration_prompt,
)

from core.config import settings

logger = get_logger(__name__)


class Regenerator:
    """
    Improves execution results using reflection feedback.
    """

    def __init__(
        self,
        llm: LLMService,
    ) -> None:
        """
        Initialize the regenerator.

        Args:
            llm:
                LLM service instance.
        """

        self._llm = llm

    async def regenerate(
        self,
        workflow: WorkflowContext,
        execution: ExecutionResult,
        reflection: ReflectionResult,
        iteration: int = 1,
    ) -> RegenerationResult:
        """
        Improve an execution result using reflection feedback.

        Args:
            workflow:
                Shared workflow context.

            execution:
                Original execution result.

            reflection:
                Reflection feedback.

            iteration:
                Current regeneration iteration.

        Returns:
            RegenerationResult

        Raises:
            ValidationException
            ConfigurationException
            LLMException
            RegenerationException
        """

        if iteration > settings.MAX_REGENERATION_ITERATIONS:

            logger.warning(
                "[%s] Maximum regeneration iterations reached.",
                workflow.request_id,
            )

            return RegenerationResult(
                execution=execution,
                iteration=iteration,
                improved=False,
            )

        if not reflection.needs_revision:

            logger.info(
                "[%s] Reflection indicates no regeneration required.",
                workflow.request_id,
            )

            return RegenerationResult(
                execution=execution,
                iteration=iteration,
                improved=False,
            )

        logger.info(
            "[%s] Starting regeneration iteration %d.",
            workflow.request_id,
            iteration,
        )

        try:

            prompt = build_regeneration_prompt(
                execution,
                reflection,
            )

            improved_document = await self._llm.generate(
                prompt=prompt,
            )

            if not improved_document.strip():

                raise ValidationException(
                    "Regenerated document is empty."
                )

            improved_execution = execution.model_copy(
                deep=True,
            )

            improved_execution.regenerated_output = (
                improved_document
            )

            logger.info(
                "[%s] Regeneration iteration %d completed.",
                workflow.request_id,
                iteration,
        )

            return RegenerationResult(
                execution=improved_execution,
                iteration=iteration,
                improved=True,
            )

        except (
            ValidationException,
            ConfigurationException,
            LLMException,
        ):
            raise

        except Exception as exc:

            logger.exception(
                "Unexpected regeneration error."
            )

            raise RegenerationException(
                "Regeneration failed unexpectedly."
            ) from exc