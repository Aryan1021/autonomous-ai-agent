"""
Regression tests for critical utility behavior.

These tests protect behavior that should never change during
future refactoring.
"""

from __future__ import annotations

import pytest

from agent.document_generator import DocumentGenerator
from agent.llm import LLMService
from agent.models import (
    DocumentContext,
    ReflectionContext,
    WorkflowContext,
)
from core.exceptions import ValidationException


# ============================================================================
# LLM JSON Normalization
# ============================================================================


def test_normalize_json_old_field_names():
    """
    Ensure legacy field names are normalized.
    """

    data = {
        "tasks": [
            {
                "id": 1,
                "description": "Collect requirements",
                "state": "completed",
            }
        ]
    }

    LLMService._normalize_json(data)

    task = data["tasks"][0]

    assert task["task_id"] == 1
    assert task["title"] == "Collect requirements"
    assert task["status"] == "completed"

    assert "id" not in task
    assert "description" not in task
    assert "state" not in task


def test_normalize_json_adds_default_fields():
    """
    Missing optional fields should receive defaults.
    """

    data = {
        "tasks": [
            {
                "task_id": 1,
                "title": "Example Task",
            }
        ]
    }

    LLMService._normalize_json(data)

    task = data["tasks"][0]

    assert task["status"] == "pending"
    assert task["output"] is None
    assert task["error"] is None
    assert task["execution_time"] is None


def test_normalize_json_ignores_invalid_tasks():
    """
    Invalid task collections should not crash normalization.
    """

    data = {
        "tasks": [
            "invalid",
            123,
            None,
        ]
    }

    # Should not raise
    LLMService._normalize_json(data)


# ============================================================================
# Filename Generation
# ============================================================================


def test_filename_generation():
    """
    Generated filename should be filesystem-safe.
    """

    generator = DocumentGenerator()

    filename = generator._create_filename(
        "AI & ML: Future/2026?"
    )

    assert filename.endswith(".docx")

    stem = filename[:-5]

    assert " " not in stem
    assert "&" not in stem
    assert "/" not in stem
    assert ":" not in stem
    assert "?" not in stem


def test_filename_length_limit():
    """
    Very long titles should be truncated.
    """

    generator = DocumentGenerator()

    title = "A" * 200

    filename = generator._create_filename(title)

    assert filename.endswith(".docx")

    stem = filename[:-5]

    assert len(stem) <= 60


# ============================================================================
# Validation
# ============================================================================


@pytest.mark.asyncio
async def test_generate_empty_prompt():
    """
    Empty prompts should fail before contacting Gemini.
    """

    llm = LLMService()

    with pytest.raises(ValidationException):
        await llm.generate("")


def test_generate_empty_document():
    """
    Document generation should fail when no sections exist.
    """

    generator = DocumentGenerator()

    context = DocumentContext(
        title="Regression Test",
        goal="Testing",
        assumptions=[],
        sections=[],
        reflection=ReflectionContext(
            overall_score=100,
            confidence=100,
            needs_revision=False,
            strengths=[],
            issues=[],
            suggestions=[],
            summary="Everything looks good.",
        ),
        summary="Workflow completed.",
    )

    with pytest.raises(ValidationException):
        generator.generate(
            WorkflowContext(),
            context,
        )