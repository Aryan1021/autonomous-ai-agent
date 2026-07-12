"""
Application configuration.

Loads environment variables from the .env file and exposes them
through a centralized Settings object.
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Application settings.
    """

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    PRIMARY_MODEL: str = os.getenv(
        "PRIMARY_MODEL",
        "gemini-3.5-flash",
    )

    FALLBACK_MODELS: list[str] = field(
        default_factory=lambda: [
            model.strip()
            for model in os.getenv(
                "FALLBACK_MODELS",
                "gemini-flash-latest,gemini-2.5-flash",
            ).split(",")
            if model.strip()
            ]
    )

    TEMPERATURE: float = float(
        os.getenv(
            "TEMPERATURE",
            "0.3",
        )
    )

    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "INFO",
    )

    MAX_RETRIES: int = int(
        os.getenv(
            "MAX_RETRIES",
            "5",
        )
    )

    INITIAL_RETRY_DELAY: float = float(
        os.getenv(
            "INITIAL_RETRY_DELAY",
            "5",
        )
    )

    MAX_REGENERATION_ITERATIONS: int = int(
        os.getenv(
            "MAX_REGENERATION_ITERATIONS",
            "2",
        )
    )

    SHOW_REFLECTION_REPORT: bool = bool(
        int(
            os.getenv(
                "SHOW_REFLECTION_REPORT",
                "1",
            )
        )
    )


settings = Settings()