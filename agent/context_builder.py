"""
Builds a structured document context from execution results.
"""

from __future__ import annotations

from agent.models import (
    DocumentContext,
    DocumentSection,
    ExecutionResult,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """
    Builds a structured document context from an execution result.

    The generated context is later consumed by the
    DocumentGenerator to create the final Word document.
    """

    def build(
        self,
        workflow,
        result: ExecutionResult,
    ) -> DocumentContext:
        """
        Build a document context from an execution result.

        Args:
            result:
                Execution result returned by the Executor.

        Returns:
            Structured document context.
        """

        logger.info(
            "[%s] Building document context...",
            workflow.request_id,
        )

        sections: list[DocumentSection] = []

        for task in result.tasks:

            if task.status != "completed":
                logger.warning(
                    "Skipping failed task %d: %s",
                    task.task_id,
                    task.title,
                )
                continue

            sections.append(
                DocumentSection(
                    heading=task.title,
                    content=task.output or "",
                )
            )

        logger.info(
            "[%s] Generated %d document sections.",
            workflow.request_id,
            len(sections),
        )

        context = DocumentContext(
            title=result.goal,
            goal=result.goal,
            assumptions=result.assumptions,
            sections=sections,
            summary=result.execution_summary or "",
        )

        logger.info(
            "Document context successfully created."
        )

        return context