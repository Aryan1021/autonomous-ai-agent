"""
Tests for agent data models.
"""

from agent.models import PlannerOutput, Task


def main() -> None:
    """
    Verify PlannerOutput validation.
    """

    planner = PlannerOutput(
        goal="Create Business Proposal",
        assumptions=[
            "Budget is moderate",
            "Audience is executives",
        ],
        tasks=[
            Task(
                task_id=1,
                title="Understand the request",
            ),
            Task(
                task_id=2,
                title="Generate execution plan",
            ),
            Task(
                task_id=3,
                title="Generate document",
            ),
        ],
    )

    print("=" * 60)
    print("PlannerOutput Validation Successful")
    print("=" * 60)

    print(planner.model_dump_json(indent=4))

    print("\n" + "=" * 60)
    print("Simulating Task Execution")
    print("=" * 60)

    planner.tasks[0].status = "completed"

    planner.tasks[0].output = (
        "Request analyzed successfully."
    )

    planner.tasks[1].status = "failed"

    planner.tasks[1].error = (
        "Unable to generate execution plan."
    )

    print("\nCompleted Task:\n")

    print(
        planner.tasks[0].model_dump_json(
            indent=4,
        )
    )

    print("\nFailed Task:\n")

    print(
        planner.tasks[1].model_dump_json(
            indent=4,
        )
    )


if __name__ == "__main__":
    main()