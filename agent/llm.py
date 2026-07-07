"""
LLM service responsible for communicating with the Gemini API.
"""

from __future__ import annotations

import asyncio
import json
from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from core.config import settings
from core.exceptions import (
    ConfigurationException,
    LLMException,
    ValidationException,
)
from core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """
    Service responsible for communicating with the Gemini API.
    """

    def __init__(self) -> None:
        """
        Initialize the service without creating the Gemini client.
        """
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        """
        Lazily initialize and return the Gemini client.

        Raises:
            ConfigurationException:
                If the Gemini API key is missing.
        """

        if self._client is None:

            if not settings.GEMINI_API_KEY:
                raise ConfigurationException(
                    "Gemini API key is not configured."
                )

            logger.info(
                "Initializing Gemini client with model '%s'.",
                settings.MODEL_NAME,
            )

            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
            )

        return self._client

    async def _request_with_retry(
        self,
        prompt: str,
        temperature: float,
    ) -> types.GenerateContentResponse:
        """
        Send a request to Gemini with retry and exponential backoff.

        Args:
            prompt:
                Prompt to send.

            temperature:
                Sampling temperature.

        Returns:
            Gemini response.

        Raises:
            LLMException:
                If all retry attempts fail.
        """

        client = self._get_client()

        delay = settings.INITIAL_RETRY_DELAY

        last_exception: Exception | None = None

        for attempt in range(
            1,
            settings.MAX_RETRIES + 1,
        ):

            try:

                logger.info(
                    "Gemini request attempt %d/%d.",
                    attempt,
                    settings.MAX_RETRIES,
                )

                response = await client.aio.models.generate_content(
                    model=settings.MODEL_NAME,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                    ),
                )

                return response

            except Exception as exc:

                last_exception = exc

                logger.warning(
                    "Gemini request failed (attempt %d/%d).",
                    attempt,
                    settings.MAX_RETRIES,
                )

                if attempt == settings.MAX_RETRIES:
                    break

                logger.info(
                    "Retrying in %.1f seconds...",
                    delay,
                )

                await asyncio.sleep(delay)

                delay *= 2

        logger.exception(
            "Gemini request failed after %d attempts.",
            settings.MAX_RETRIES,
        )

        raise LLMException(
            "Failed to communicate with Gemini after multiple retries."
        ) from last_exception
    
    async def generate(
        self,
        prompt: str,
        temperature: float | None = None,
    ) -> str:
        """
        Generate text using the Gemini model.

        Args:
            prompt:
                Prompt to send to Gemini.

            temperature:
                Optional temperature override.

        Returns:
            Generated text.

        Raises:
            ValidationException:
                If the prompt is empty.

            ConfigurationException:
                If Gemini is not configured.

            LLMException:
                If Gemini communication fails.
        """

        if not prompt.strip():
            raise ValidationException(
                "Prompt cannot be empty."
            )

        temperature = (
            temperature
            if temperature is not None
            else settings.TEMPERATURE
        )

        try:

            logger.info(
                "Sending request to Gemini using model '%s' "
                "(prompt_length=%d).",
                settings.MODEL_NAME,
                len(prompt),
            )

            response = await self._request_with_retry(
                prompt=prompt,
                temperature=temperature,
            )

            text = response.text

            if text is None or not text.strip():
                raise LLMException(
                    "Gemini returned an empty response."
                )

            logger.info(
                "Received response from Gemini "
                "(response_length=%d).",
                len(text),
            )

            return text

        except (
            ConfigurationException,
            ValidationException,
            LLMException,
        ):
            raise

        except Exception as exc:

            logger.exception(
                "Unexpected error while generating content."
            )

            raise LLMException(
                "Failed to communicate with Gemini."
            ) from exc

    @staticmethod
    def _extract_json(
        text: str,
    ) -> str:
        """
        Extract a JSON object from a Gemini response.

        Gemini sometimes wraps JSON inside Markdown
        code fences. This helper removes them.
        """

        text = text.strip()

        if text.startswith("```json"):
            text = text.removeprefix("```json")

        if text.startswith("```"):
            text = text.removeprefix("```")

        if text.endswith("```"):
            text = text.removesuffix("```")

        return text.strip()
    
    @staticmethod
    def _normalize_json(
        data: dict,
    ) -> None:
        """
        Normalize common variations in LLM-generated JSON.

        This improves robustness against minor differences
        in field names returned by the model.
        """

        tasks = data.get("tasks")

        if not isinstance(tasks, list):
            return

        for task in tasks:

            if not isinstance(task, dict):
                continue

            # -------------------------------------------------
            # id -> task_id
            # -------------------------------------------------

            if (
                "id" in task
                and "task_id" not in task
            ):
                task["task_id"] = task.pop("id")

            # -------------------------------------------------
            # Default status
            # -------------------------------------------------

            task.setdefault(
                "status",
                "pending",
            )
    
    async def generate_json(
        self,
        prompt: str,
        output_model: type[T],
        temperature: float | None = None,
    ) -> T:
        """
        Generate structured JSON and validate it using a Pydantic model.
        """

        response = await self.generate(
            prompt=prompt,
            temperature=temperature,
        )

        try:

            response = self._extract_json(
                response,
            )

            data = json.loads(
                response,
            )

        except json.JSONDecodeError as exc:

            logger.exception(
                "Failed to parse JSON returned by Gemini."
            )

            logger.error(
                "Raw Gemini response:\n%s",
                response,
            )

            raise ValidationException(
                "Gemini returned invalid JSON."
            ) from exc

        if isinstance(data, dict):

            self._normalize_json(
                data,
            )

        try:

            validated = output_model.model_validate(
                data,
            )

            logger.info(
                "Successfully validated Gemini JSON into '%s'.",
                output_model.__name__,
            )

            return validated

        except ValidationError as exc:

            logger.exception(
                "Gemini JSON failed validation."
            )

            logger.error(
                "Gemini JSON:\n%s",
                json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False,
                ),
            )

            raise ValidationException(
                "Gemini returned an invalid response structure."
            ) from exc