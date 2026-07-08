"""
Request and response models for the FastAPI API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """
    Incoming API request.
    """

    request: str = Field(
        ...,
        min_length=10,
        description="Natural language request from the user.",
        examples=[
            "Create a business proposal for an AI healthcare chatbot."
        ],
    )