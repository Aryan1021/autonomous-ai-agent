"""
Utility functions for caching Pydantic models during development.

This helps reduce Gemini API usage by storing generated results
locally and reusing them across test runs.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from core.exceptions import CacheException
from core.logging_config import get_logger

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)

# ---------------------------------------------------------------------
# Cache Configuration
# ---------------------------------------------------------------------

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def cache_exists(filename: str) -> bool:
    """
    Return True if the cache file exists.
    """

    return (CACHE_DIR / filename).exists()


def save_model(
    filename: str,
    model: BaseModel,
) -> None:
    """
    Save a Pydantic model to the cache directory.
    """

    path = CACHE_DIR / filename

    try:
        path.write_text(
            model.model_dump_json(indent=4),
            encoding="utf-8",
        )

    except Exception as exc:
        logger.exception(
            "Failed to save cache '%s'.",
            filename,
        )

        raise CacheException(
            f"Failed to save cache '{filename}'."
        ) from exc


def load_model(
    filename: str,
    model_type: type[T],
) -> T:
    """
    Load a cached Pydantic model.

    Raises:
        CacheException:
            If the cache cannot be loaded or validated.
    """

    path = CACHE_DIR / filename

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        return model_type.model_validate(data)

    except Exception as exc:
        logger.exception(
            "Failed to load cache '%s'.",
            filename,
        )

        raise CacheException(
            f"Failed to load cache '{filename}'."
        ) from exc


def delete_cache(filename: str) -> None:
    """
    Delete a cache file if it exists.
    """

    path = CACHE_DIR / filename

    try:

        if path.exists():
            path.unlink()

    except Exception as exc:

        logger.exception(
            "Failed to delete cache '%s'.",
            filename,
        )

        raise CacheException(
            f"Failed to delete cache '{filename}'."
        ) from exc


def clear_cache() -> None:
    """
    Remove all cache files.
    """

    try:

        for file in CACHE_DIR.glob("*.json"):
            file.unlink()

    except Exception as exc:

        logger.exception(
            "Failed to clear cache directory."
        )

        raise CacheException(
            "Failed to clear cache."
        ) from exc


async def load_or_generate(
    filename: str,
    model_type: type[T],
    generator: Callable[..., Awaitable[T]],
    *args,
    force_refresh: bool = False,
    **kwargs,
) -> T:
    """
    Load a cached model if available.
    Otherwise generate it, cache it, and return it.

    Args:
        filename:
            Cache filename.

        model_type:
            Pydantic model class.

        generator:
            Async function that generates the model.

        force_refresh:
            Ignore cache and regenerate the model.

    Returns:
        Cached or newly generated model.
    """

    if not force_refresh and cache_exists(filename):

        logger.info(
            "Loading '%s' from cache.",
            filename,
        )

        return load_model(
            filename,
            model_type,
        )

    if force_refresh:

        logger.info(
            "Force refresh enabled for '%s'.",
            filename,
        )

    else:

        logger.info(
            "Cache miss for '%s'.",
            filename,
        )

    logger.info(
        "Generating new data..."
    )

    model = await generator(
        *args,
        **kwargs,
    )

    save_model(
        filename,
        model,
    )

    logger.info(
        "Saved '%s' to cache.",
        filename,
    )

    return model