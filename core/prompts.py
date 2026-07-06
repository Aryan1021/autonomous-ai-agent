"""
Prompt builder functions used by the Autonomous AI Agent.
"""

from __future__ import annotations


def build_planner_prompt(request: str) -> str:
    """
    Build the planner prompt.

    Args:
        request:
            User's natural language request.

    Returns:
        A prompt instructing the planner to generate a structured execution plan.
    """

    return f"""
You are an expert autonomous AI planning agent.

The user submitted the following request:

"{request}"

Your job is to create a structured execution plan.

Instructions:

1. Understand the user's objective.
2. Make reasonable assumptions when information is missing.
3. Break the work into 6–10 high-level executable tasks.
4. Arrange the tasks in the correct execution order.
5. Every task must represent exactly one logical unit of work.

Each task MUST contain:

- task_id (integer starting from 1)
- title (5–12 words)
- status ("pending")

Return ONLY valid JSON matching EXACTLY this schema:

{{
    "goal": "string",

    "assumptions": [
        "string"
    ],

    "tasks": [
        {{
            "task_id": 1,
            "title": "string",
            "status": "pending"
        }}
    ]
}}

Rules:

- Return JSON only.
- Do NOT use Markdown.
- Do NOT use code fences.
- Do NOT include explanations.
- Do NOT add extra fields.
- Do NOT rename any field.
- Use "task_id" exactly as written.
- Ensure the JSON is syntactically valid.
""".strip()