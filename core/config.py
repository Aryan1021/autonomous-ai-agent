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

    MAX_RETRIES: int = int(
        os.getenv(
            "MAX_RETRIES",
            "3",
        )
    )

    INITIAL_RETRY_DELAY: float = float(
        os.getenv(
            "INITIAL_RETRY_DELAY",
            "2",
        )
    )


settings = Settings()