"""
Main entry point for the Autonomous AI Agent API.
"""

from fastapi import FastAPI
from api.models import AgentRequest, AgentResponse

app = FastAPI(
    title="Autonomous AI Agent API",
    description=(
        "An autonomous AI agent capable of understanding natural "
        "language requests, generating execution plans, executing "
        "tasks, performing self-reflection, and generating "
        "professional Microsoft Word documents."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get(
    "/",
    tags=["General"],
    summary="Root endpoint",
    description="Returns basic information about the API.",
)
async def root():
    """Return application metadata."""
    return {
        "application": "Autonomous AI Agent",
        "version": "1.0.0",
        "status": "running",
    }


@app.get(
    "/health",
    tags=["General"],
    summary="Health check",
    description="Returns the current health status of the API.",
)
async def health_check():
    """Return the health status of the application."""
    return {
        "status": "healthy",
        "service": "Autonomous AI Agent API",
    }


@app.post(
    "/agent",
    response_model=AgentResponse,
    tags=["Agent"],
    summary="Process an autonomous AI request",
    description=(
        "Accepts a natural language request and returns "
        "an execution plan along with document information."
    ),
)
async def run_agent(request: AgentRequest) -> AgentResponse:
    """
    Process a user request using the autonomous AI agent.
    """

    return AgentResponse(
        status="success",
        goal="Business Proposal",
        assumptions=[
            "Budget is medium",
            "Audience is executives",
        ],
        plan=[
            "Understand the request",
            "Create execution plan",
            "Generate document",
        ],
        document_path="output/proposal.docx",
    )