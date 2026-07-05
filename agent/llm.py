"""
LLM service responsible for communicating with the Gemini API.
"""

from __future__ import annotations

from google import genai
from google.genai import types

from core.config import settings
from core.exceptions import AgentException
from core.logging_config import get_logger

logger = get_logger(__name__)


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

            response = await client.aio.models.generate_content(
                model=settings.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                ),
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