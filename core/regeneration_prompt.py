"""
Prompt builder for the Regeneration Engine.
"""

from __future__ import annotations

from agent.models import (
    ExecutionResult,
    ReflectionResult,
)


def build_regeneration_prompt(
    execution: ExecutionResult,
    reflection: ReflectionResult,
) -> str:
    """
    Build the prompt used by the Regeneration Engine.

    The model receives the original execution result together
    with structured reflection feedback and is instructed to
    improve the content while preserving correct information.

    Args:
        execution:
            Original execution result.

        reflection:
            Reflection feedback.

    Returns:
        Prompt for the LLM.
    """

    completed_tasks = "\n\n".join(
        [
            f"{task.title}\n\n{task.output or ''}"
            for task in execution.tasks
            if task.status == "completed"
        ]
    )

    strengths = "\n".join(
        f"- {item}"
        for item in reflection.strengths
    )

    issues = "\n".join(
        (
            f"- [{issue.severity.upper()}] "
            f"{issue.title}: {issue.description}"
        )
        for issue in reflection.issues
    )

    suggestions = "\n".join(
        f"- {item.title}: {item.description}"
        for item in reflection.suggestions
    )

    return f"""
You are an expert business consultant and technical writer.

Your task is to improve an existing document using expert review
feedback.

Rewrite the entire proposal into one polished final version.

Do not append.

Do not preserve duplicated sections.

Do not include QA reports.

Do not include changelogs.

Keep one consistent product name.

Keep one executive summary.

Return only the final document.

Instead:

- Preserve all correct information.
- Improve weak sections.
- Fix every issue identified during review.
- Apply every recommendation.
- Remove repetition.
- Improve logical flow.
- Produce a polished, professional document.

=========================
GOAL
=========================

{execution.goal}

=========================
CURRENT DOCUMENT
=========================

{completed_tasks}

=========================
REVIEW SCORE
=========================

Overall Score: {reflection.overall_score}/100

Confidence: {reflection.confidence}/100

Needs Revision: {reflection.needs_revision}

=========================
STRENGTHS
=========================

{strengths}

=========================
ISSUES
=========================

{issues}

=========================
SUGGESTIONS
=========================

{suggestions}

=========================
YOUR TASK
=========================

Improve the document by applying every suggestion.

Return ONLY the improved document.

Do not explain what you changed.

Do not mention that this is a revised version.

Produce professional report-quality writing.
""".strip()