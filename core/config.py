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

from core.exceptions import ConfigurationException

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Application settings.

    All configuration values can be overridden using environment variables.
    Configuration is validated during application startup.
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

    def __post_init__(self) -> None:
        """
        Validate application configuration.
        """

        if not self.GEMINI_API_KEY.strip():
            raise ConfigurationException(
                "GEMINI_API_KEY cannot be empty."
            )

        if not self.PRIMARY_MODEL.strip():
            raise ConfigurationException(
                "PRIMARY_MODEL cannot be empty."
            )

        if not self.FALLBACK_MODELS:
            raise ConfigurationException(
                "At least one fallback model must be configured."
            )

        if any(
            not model.strip()
            for model in self.FALLBACK_MODELS
        ):
            raise ConfigurationException(
                "Fallback model names cannot be empty."
            )

        if not 0.0 <= self.TEMPERATURE <= 2.0:
            raise ConfigurationException(
                "TEMPERATURE must be between 0.0 and 2.0."
            )

        if self.MAX_RETRIES < 1:
            raise ConfigurationException(
                "MAX_RETRIES must be at least 1."
            )

        if self.INITIAL_RETRY_DELAY <= 0:
            raise ConfigurationException(
                "INITIAL_RETRY_DELAY must be greater than 0."
            )

        if self.MAX_REGENERATION_ITERATIONS < 1:
            raise ConfigurationException(
                "MAX_REGENERATION_ITERATIONS must be at least 1."
            )

        valid_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if self.LOG_LEVEL.upper() not in valid_levels:
            raise ConfigurationException(
                f"Invalid LOG_LEVEL '{self.LOG_LEVEL}'."
            )


settings = Settings()