"""
Application configuration.

Loads environment variables from the .env file and exposes them
through a centralized Settings object.
"""

from dataclasses import dataclass
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

    MODEL_NAME: str = os.getenv(
        "MODEL_NAME",
        "gemini-2.5-flash",
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


settings = Settings()