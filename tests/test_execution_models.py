"""
Tests for execution models.
"""

from agent.models import ExecutionResult, Task


def main() -> None:
    """
    Verify ExecutionResult validation.
    """

    result = ExecutionResult(
        goal="Create Business Proposal",
        assumptions=[
            "Budget is moderate",
            "Audience is executives",
        ],
        tasks=[
            Task(
                task_id=1,
                title="Market Analysis",
                status="completed",
                output="Healthcare market analysis...",
            ),
            Task(
                task_id=2,
                title="Revenue Strategy",
                status="failed",
                error="LLM timeout.",
            ),
        ],
        combined_output="""
Healthcare market analysis...

Revenue strategy could not be generated.
""",
        completed_tasks=1,
        failed_tasks=1,
        execution_summary=(
            "Execution completed with one successful "
            "task and one failed task."
        ),
    )

    print("=" * 60)
    print("ExecutionResult Validation Successful")
    print("=" * 60)

    print(result.model_dump_json(indent=4))


if __name__ == "__main__":
    main()