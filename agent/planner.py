"""
Planner service responsible for generating execution plans.
"""

from __future__ import annotations

from agent.llm import LLMService
from agent.models import PlannerOutput, WorkflowContext
from core.exceptions import (
    ConfigurationException,
    LLMException,
    PlannerException,
    ValidationException,
)
from core.logging_config import get_logger
from core.prompts import build_planner_prompt

logger = get_logger(__name__)


class Planner:
    """
    Autonomous planning service.
    """

    def __init__(
        self,
        llm: LLMService,
    ) -> None:
        """
        Initialize the planner.

        Args:
            llm:
                LLM service instance.
        """

        self._llm = llm

    async def plan(
        self,
        workflow: WorkflowContext,
        request: str,
    ) -> PlannerOutput:
        """
        Generate an execution plan for the user's request.

        Args:
            request:
                User's natural language request.

        Returns:
            PlannerOutput

        Raises:
            ValidationException:
                If the request is empty.

            ConfigurationException:
                If Gemini is not configured.

            LLMException:
                If communication with Gemini fails.

            PlannerException:
                If an unexpected planner error occurs.
        """

        if not request.strip():
            raise ValidationException(
                "Request cannot be empty."
            )

        logger.info(
            "[%s] Planning request...",
            workflow.request_id,
        )

        try:

            prompt = build_planner_prompt(
                request,
            )

            plan = await self._llm.generate_json(
                prompt=prompt,
                output_model=PlannerOutput,
            )

            logger.info(
                "[%s] Planner generated %d tasks.",
                workflow.request_id,
                len(plan.tasks),
            )

            return plan

        except (
            ConfigurationException,
            ValidationException,
            LLMException,
        ):
            raise

        except Exception as exc:

            logger.exception(
                "[%s] Unexpected planner error.",
                workflow.request_id,
            )

            raise PlannerException(
                "Planner failed unexpectedly."
            ) from exc