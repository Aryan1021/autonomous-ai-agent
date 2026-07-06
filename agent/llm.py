"""
LLM service responsible for communicating with the Gemini API.
"""

from __future__ import annotations

import asyncio
import json
from typing import TypeVar
from pydantic import BaseModel, ValidationError

from google import genai
from google.genai import types

from core.config import settings
from core.exceptions import AgentException
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
        """
        if self._client is None:
            if not settings.GEMINI_API_KEY:
                raise AgentException(
                    "Gemini API key is not configured."
                )

            logger.info(
                "Initializing Gemini client with model '%s'.",
                settings.MODEL_NAME,
            )

            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

        return self._client
    
    async def _request_with_retry(
        self,
        prompt: str,
        temperature: float,
    ):
        """
        Send a request to Gemini with retry and exponential backoff.
        """

        client = self._get_client()

        delay = settings.INITIAL_RETRY_DELAY

        last_exception = None

        for attempt in range(1, settings.MAX_RETRIES + 1):

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

        raise AgentException(
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
            prompt: Prompt to send to Gemini.
            temperature: Optional temperature override.

        Returns:
            Generated text response.

        Raises:
            AgentException:
                If the prompt is invalid or the Gemini request fails.
        """

        if not prompt.strip():
            raise AgentException(
                "Prompt cannot be empty."
            )

        temperature = (
            temperature
            if temperature is not None
            else settings.TEMPERATURE
        )

        try:
            client = self._get_client()

            logger.info(
                "Sending request to Gemini using model '%s' (prompt_length=%d).",
                settings.MODEL_NAME,
                len(prompt),
            )

            temperature = (
                temperature
                if temperature is not None
                else settings.TEMPERATURE
            )

            response = await self._request_with_retry(
                prompt=prompt,
                temperature=temperature,
            )

            text = response.text

            if text is None or not text.strip():
                raise AgentException(
                    "Gemini returned an empty response."
                )

            logger.info(
                "Received response from Gemini (response_length=%d).",
                len(text),
            )

            return text

        except AgentException:
            raise

        except Exception as exc:
            logger.exception(
                "Gemini request failed while generating content."
            )

            raise AgentException(
                "Failed to communicate with Gemini."
            ) from exc
        
    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Extract JSON from a Gemini response.
        """

        text = text.strip()

        if text.startswith("```json"):
            text = text.removeprefix("```json")

        if text.startswith("```"):
            text = text.removeprefix("```")

        if text.endswith("```"):
            text = text.removesuffix("```")

        return text.strip()
        
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
            response = self._extract_json(response)

            data = json.loads(response)

        except json.JSONDecodeError as exc:

            logger.exception(
                "Failed to parse JSON returned by Gemini."
            )

            raise AgentException(
                "Gemini returned invalid JSON."
            ) from exc

        # ------------------------------------------------------------
        # Normalize common LLM field variations
        # ------------------------------------------------------------

        if isinstance(data, dict):

            tasks = data.get("tasks")

            if isinstance(tasks, list):

                for task in tasks:

                    if (
                        isinstance(task, dict)
                        and "id" in task
                        and "task_id" not in task
                    ):
                        task["task_id"] = task.pop("id")

        try:

            return output_model.model_validate(data)

        except ValidationError as exc:

            logger.exception(
                "Gemini JSON failed validation."
            )

            logger.error(
                "Gemini Response:\n%s",
                json.dumps(
                    data,
                    indent=4,
                ),
            )

            raise AgentException(
                "Gemini returned an invalid response structure."
            ) from exc