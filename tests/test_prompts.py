"""
Tests for prompt builders.
"""

from core.prompts import build_planner_prompt


def main() -> None:
    """
    Verify the planner prompt.
    """

    prompt = build_planner_prompt(
        "Create a business proposal for an AI healthcare chatbot."
    )

    print(prompt)


if __name__ == "__main__":
    main()