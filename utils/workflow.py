"""
Workflow utilities.
"""

from __future__ import annotations

from agent.models import WorkflowContext


def create_workflow() -> WorkflowContext:
    """
    Create a new workflow context.
    """

    return WorkflowContext()