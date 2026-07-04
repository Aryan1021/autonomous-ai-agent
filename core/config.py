"""
Application configuration.

This module loads environment variables from the .env file and exposes them through a centralized Settings object.
"""

from dataclasses import dataclass
import os

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings."""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")


# Singleton settings instance
settings = Settings()