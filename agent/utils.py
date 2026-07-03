"""
Utility functions used across the Autonomous AI Agent project.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path("output")


def ensure_output_directory() -> None:
    """
    Create the output directory if it does not already exist.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_filename(prefix: str, extension: str) -> str:
    """
    Generate a timestamp-based filename.

    Example:
        proposal_20260703_143015.docx
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def save_text_file(filename: str, content: str) -> Path:
    """
    Save plain text content inside the output directory.
    """
    ensure_output_directory()

    file_path = OUTPUT_DIR / filename

    file_path.write_text(content, encoding="utf-8")

    return file_path


def safe_json_parse(text: str) -> dict[str, Any]:
    """
    Safely parse JSON returned by the LLM.

    Raises:
        ValueError: If parsing fails.
    """
    try:
        return json.loads(text)

    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON returned by the LLM.") from exc