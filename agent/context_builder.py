"""
Builds a structured document context from execution results.
"""

from __future__ import annotations

from agent.models import (
    DocumentContext,
    DocumentSection,
    ExecutionResult,
    ReflectionResult,
    ReflectionContext,
    WorkflowContext,
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
        workflow: WorkflowContext,
        result: ExecutionResult,
        reflection: ReflectionResult,
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

        reflection_context = ReflectionContext(
            overall_score=reflection.overall_score,
            confidence=reflection.confidence,
            needs_revision=reflection.needs_revision,
            strengths=reflection.strengths,
            issues=reflection.issues,
            suggestions=reflection.suggestions,
            summary=reflection.summary,
        )

        sections: list[DocumentSection] = []

        if result.regenerated_output:

            logger.info(
                "[%s] Using regenerated proposal.",
                workflow.request_id,
            )

            sections.append(
                DocumentSection(
                    heading="Business Proposal",
                    content=result.regenerated_output,
                )
            )

        else:

            for task in result.tasks:

                if task.status != "completed":
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
            reflection=reflection_context,
            summary=result.execution_summary or "",
        )

        logger.info(
            "Document context successfully created."
        )

        return context