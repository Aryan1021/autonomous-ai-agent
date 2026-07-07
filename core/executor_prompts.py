"""
Prompt builders used by the Executor.
"""

from __future__ import annotations


def build_executor_prompt(
    goal: str,
    assumptions: list[str],
    task_title: str,
) -> str:
    """
    Build the execution prompt for a single task.
    """

    assumptions_text = "\n".join(
        f"- {item}"
        for item in assumptions
    )

    return f"""
You are an expert business consultant.

Overall Goal:

{goal}

Planner Assumptions:

{assumptions_text}

Current Task:

{task_title}

Instructions:

- Complete ONLY this task.
- Write between 200 and 400 words.
- Use professional business language.
- Organize the response using headings and bullet points where appropriate.
- Do NOT repeat information from previous tasks.
- Do NOT complete other tasks.
- Return plain text only.
- Do NOT use Markdown code fences.
""".strip()