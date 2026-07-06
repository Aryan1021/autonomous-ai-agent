"""
Planner service responsible for generating execution plans.
"""

from __future__ import annotations

from agent.llm import LLMService
from agent.models import PlannerOutput
from core.logging_config import get_logger
from core.prompts import build_planner_prompt

logger = get_logger(__name__)


class Planner:
    """
    Autonomous planning service.
    """

    def __init__(self, llm: LLMService) -> None:
        """
        Initialize the planner.

        Args:
            llm:
                LLM service instance.
        """

        self._llm = llm

    async def plan(
        self,
        request: str,
    ) -> PlannerOutput:
        """
        Generate an execution plan for the user's request.

        Args:
            request:
                User's natural language request.

        Returns:
            PlannerOutput
        """

        logger.info("Planning request...")

        prompt = build_planner_prompt(request)

        plan = await self._llm.generate_json(
            prompt=prompt,
            output_model=PlannerOutput,
        )

        logger.info(
            "Planner generated %d tasks.",
            len(plan.tasks),
        )

        return plan