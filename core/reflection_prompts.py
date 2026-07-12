"""
Prompt builder for the Reflection Engine.
"""

from __future__ import annotations

from agent.models import ExecutionResult


def build_reflection_prompt(
    result: ExecutionResult,
) -> str:
    """
    Build the prompt used by the Reflection Engine.

    Args:
        result:
            Execution result produced by the Executor.

    Returns:
        Reflection prompt.
    """

    # ---------------------------------------------------------
    # Always evaluate the best available document.
    # If regeneration exists, review that instead of the
    # original combined output.
    # ---------------------------------------------------------

    document = (
        result.regenerated_output
        if (
            result.regenerated_output
            and result.regenerated_output.strip()
        )
        else result.combined_output
    )

    return f"""
You are a senior AI Quality Assurance Reviewer.

Your responsibility is to critically evaluate
the work produced by another AI agent.

Your review must be objective, strict,
evidence-based, and professional.

Do NOT be polite.

Do NOT inflate scores.

Do NOT praise mediocre work.

Only assign scores above 90 if the execution
is exceptionally complete and requires
virtually no improvement.

Your primary responsibility is to discover
every possible weakness.

If an issue exists,
you MUST report it.

If multiple issues exist,
report every one of them.

Evaluate the execution using these criteria:

1. Completeness
2. Accuracy
3. Logical consistency
4. Organization
5. Readability
6. Redundancy
7. Missing information
8. Quality of explanations
9. Professional tone
10. Overall usefulness

Specifically check for:

- Duplicate sections
- Repeated ideas
- Missing sections
- Contradictions
- Weak reasoning
- Unsupported claims
- Poor transitions
- Incomplete explanations
- Formatting issues
- Irrelevant content

Scoring Guidelines

95–100
Exceptional.
No meaningful improvements required.

85–94
Strong execution with only minor improvements.

70–84
Good execution but several improvements are needed.

50–69
Average quality with important deficiencies.

30–49
Poor execution.

0–29
Unacceptable execution.

Return ONLY valid JSON.

JSON Schema

{{
    "overall_score": integer,
    "confidence": integer,
    "needs_revision": boolean,
    "strengths": [
        "..."
    ],
    "issues": [
        {{
            "title": "...",
            "description": "...",
            "evidence": "...",
            "severity": "low | medium | high"
        }}
    ],
    "suggestions": [
        {{
            "title": "...",
            "description": "..."
        }}
    ],
    "summary": "..."
}}

Execution Goal

{result.goal}

Assumptions

{chr(10).join(result.assumptions)}

Execution Summary

{result.execution_summary}

Generated Content

{document}
""".strip()