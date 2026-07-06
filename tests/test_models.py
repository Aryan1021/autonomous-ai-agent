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

    print("PlannerOutput Validation Successful\n")

    print(planner.model_dump_json(indent=4))


if __name__ == "__main__":
    main()