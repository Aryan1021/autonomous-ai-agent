"""
Main entry point for the Autonomous AI Agent API.
"""

import logging

from fastapi import FastAPI

from api.models import AgentRequest, AgentResponse
from core.logging_config import configure_logging, get_logger
from core.exceptions import AgentException, register_exception_handlers

# Configure application-wide logging
configure_logging()

logger = get_logger(__name__)

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

register_exception_handlers(app)

logger.info("Autonomous AI Agent API initialized.")

@app.get(
    "/",
    tags=["General"],
    summary="Root endpoint",
    description="Returns basic information about the API.",
)
async def root() -> dict[str, str]:
    """
    Return application metadata.
    """
    logger.info("Root endpoint accessed.")

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
async def health_check() -> dict[str, str]:
    """
    Return the health status of the application.
    """
    logger.info("Health check endpoint accessed.")

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
    logger.info(
        "Received agent request: %s",
        request.request[:100],  # Log only the first 100 characters
    )

    # TODO:
    # Replace this placeholder with the real autonomous agent workflow:
    # Planner -> Executor -> Reflection -> DOCX Generator

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

@app.get(
    "/error",
    tags=["Testing"],
    summary="Test custom exception",
)
async def trigger_error() -> None:
    """
    Endpoint used to verify custom exception handling.
    """

    raise RuntimeError("Unexpected crash")