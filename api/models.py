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

class RootResponse(BaseModel):
    application: str
    version: str
    status: str

class HealthResponse(BaseModel):
    status: str

class ErrorResponse(BaseModel):
    """
    Standard API error response.
    """

    error: str = Field(
        ...,
        description="Short error category.",
        examples=["Validation Error"],
    )

    detail: str = Field(
        ...,
        description="Detailed error message.",
        examples=["Execution plan contains no tasks."],
    )

    request_id: str | None = Field(
        default=None,
        description="Workflow identifier for troubleshooting.",
        examples=["b51cbff2-f2d6-45cf-b2ef-1eb6b4f87c76"],
    )