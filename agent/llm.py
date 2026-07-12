"""
LLM service responsible for communicating with the Gemini API.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import TypeVar

from google import genai
from google.genai import types
from google.genai import errors
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

    # ---------------------------------------------------------
    # Circuit Breaker Configuration
    # ---------------------------------------------------------

    MAX_FAILURES = 3

    BLOCK_SECONDS = 300

    def __init__(self) -> None:
        """
        Initialize the service without creating the Gemini client.
        """
        self._client: genai.Client | None = None

        # Preferred model from previous successful request
        self._active_model: str | None = None

        # Consecutive failures for each model
        self._failure_counts: dict[str, int] = {}

        # Temporarily blocked models
        self._blocked_until: dict[str, float] = {}

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
                settings.PRIMARY_MODEL,
            )

            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
            )

        return self._client
    
    def _get_models(
        self,
    ) -> list[str]:
        """
        Return models ordered by priority.

        Previously successful models are tried first.
        Models blocked by the circuit breaker
        are skipped.
        """

        models = [
            settings.PRIMARY_MODEL,
            *settings.FALLBACK_MODELS,
        ]

        # Remove duplicates while preserving order

        models = list(
            dict.fromkeys(models)
        )

        # Move active model to front

        if (
            self._active_model
            and self._active_model in models
        ):

            models.remove(
                self._active_model,
            )

            models.insert(
                0,
                self._active_model,
            )

        available_models = [
            model
            for model in models
            if self._is_available(model)
        ]

        if available_models:

            return available_models

        logger.warning(
            "All configured Gemini models are "
            "currently blocked. Ignoring circuit "
            "breaker."
        )

        return models

    # ---------------------------------------------------------
    # Circuit Breaker
    # ---------------------------------------------------------

    def _is_available(
        self,
        model: str,
    ) -> bool:
        """
        Return whether a model is currently available.
        """

        blocked_until = self._blocked_until.get(
            model,
        )

        if blocked_until is None:
            return True

        if time.time() >= blocked_until:

            self._blocked_until.pop(
                model,
                None,
            )

            self._failure_counts.pop(
                model,
                None,
            )

            logger.info(
                "Circuit breaker reset for '%s'.",
                model,
            )

            return True

        return False

    def _record_success(
        self,
        model: str,
    ) -> None:
        """
        Record a successful request.
        """

        self._failure_counts.pop(
            model,
            None,
        )

        self._blocked_until.pop(
            model,
            None,
        )

        self._active_model = model

        logger.info(
            "Active Gemini model changed to '%s'.",
            model,
        )

    def _record_failure(
        self,
        model: str,
    ) -> None:
        """
        Record a failed request.
        """

        failures = (
            self._failure_counts.get(
                model,
                0,
            )
            + 1
        )

        self._failure_counts[
            model
        ] = failures

        logger.warning(
            "Model '%s' failure count: %d/%d.",
            model,
            failures,
            self.MAX_FAILURES,
        )

        if failures >= self.MAX_FAILURES:

            self._blocked_until[
                model
            ] = (
                time.time()
                + self.BLOCK_SECONDS
            )

            logger.warning(
                "Circuit breaker OPEN for '%s' "
                "for %d seconds.",
                model,
                self.BLOCK_SECONDS,
            )
    
    async def _request_with_retry(
        self,
        prompt: str,
        temperature: float,
    ) -> types.GenerateContentResponse:
        """
        Send a request to Gemini using retry,
        exponential backoff, automatic model
        fallback and circuit breaker support.

        Returns:
            Gemini response.

        Raises:
            ConfigurationException:
                Invalid API key or configuration.

            LLMException:
                If every configured model fails.
        """

        client = self._get_client()

        last_exception: Exception | None = None

        for model in self._get_models():

            logger.info(
                "Trying Gemini model '%s'%s.",
                model,
                " (preferred)"
                if model == self._active_model
                else "",
            )

            delay = settings.INITIAL_RETRY_DELAY

            for attempt in range(
                1,
                settings.MAX_RETRIES + 1,
            ):

                try:

                    logger.info(
                        "[%s] Request attempt %d/%d.",
                        model,
                        attempt,
                        settings.MAX_RETRIES,
                    )

                    response = await client.aio.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                        ),
                    )

                    self._record_success(
                       model,
                    )

                    logger.info(
                        "Successfully generated response "
                        "using '%s'.",
                        model,
                    )

                    return response

                # -------------------------------------------------
                # Client errors (4xx)
                # -------------------------------------------------

                except errors.ClientError as exc:

                    last_exception = exc

                    status = getattr(
                        exc,
                        "code",
                        None,
                    )

                    message = str(exc)

                    # -----------------------------------------
                    # Authentication
                    # -----------------------------------------

                    if status in (
                        401,
                        403,
                    ):

                        logger.error(
                            "Gemini authentication failed."
                        )

                        raise ConfigurationException(
                            "Invalid Gemini API key."
                        ) from exc

                    # -----------------------------------------
                    # Model not found
                    # -----------------------------------------

                    if status == 404:

                        logger.warning(
                            "Model '%s' not found.",
                            model,
                        )

                        break

                    # -----------------------------------------
                    # Quota exceeded
                    # -----------------------------------------

                    if status == 429:

                        logger.warning(
                            "Quota exceeded for '%s'.",
                            model,
                        )

                    else:

                        logger.warning(
                            "Client error using '%s': %s",
                            model,
                            message,
                        )

                    self._record_failure(
                        model,
                    )

                # -------------------------------------------------
                # Temporary server errors
                # -------------------------------------------------

                except errors.ServerError as exc:

                    last_exception = exc

                    logger.warning(
                        "Gemini service unavailable "
                        "for '%s' "
                        "(attempt %d/%d).",
                        model,
                        attempt,
                        settings.MAX_RETRIES,
                    )

                    self._record_failure(
                        model,
                    )

                # -------------------------------------------------
                # Timeout / Network
                # -------------------------------------------------

                except (
                    TimeoutError,
                    ConnectionError,
                    OSError,
                ) as exc:

                    last_exception = exc

                    logger.warning(
                        "Network error while using '%s': %s",
                        model,
                        exc,
                    )

                    self._record_failure(
                        model,
                    )

                # -------------------------------------------------
                # Unknown error
                # -------------------------------------------------

                except Exception as exc:

                    last_exception = exc

                    logger.exception(
                        "Unexpected Gemini error "
                        "using '%s'.",
                        model,
                    )

                    self._record_failure(
                        model,
                    )

                # ---------------------------------------------
                # Retry current model
                # ---------------------------------------------

                if attempt == settings.MAX_RETRIES:

                    logger.warning(
                        "Giving up on '%s'.",
                        model,
                    )

                    break

                logger.info(
                    "Retrying '%s' in %.1f seconds...",
                    model,
                    delay,
                )

                await asyncio.sleep(
                    delay,
                )

                delay *= 2

            logger.info(
                "Trying next fallback model..."
            )

        logger.exception(
           "All configured Gemini models failed."
        )

        raise LLMException(
            "Unable to communicate with any configured Gemini model."
        ) from last_exception
    
    async def generate(
        self,
        prompt: str,
        temperature: float | None = None,
    ) -> str:
        """
        Generate text using Gemini.

        Args:
            prompt:
                Prompt sent to Gemini.

            temperature:
                Optional sampling temperature.

        Returns:
            Generated response text.

       Raises:
           ValidationException:
                If the prompt is empty.

            ConfigurationException:
                If Gemini is not configured.

            LLMException:
                If generation fails.
        """

        if not prompt.strip():
            raise ValidationException("Prompt cannot be empty.")

        temperature = (
            temperature
            if temperature is not None
            else settings.TEMPERATURE
        )

        logger.info(
            "Sending prompt to Gemini "
            "(length=%d).",
            len(prompt),
        )

        try:
            response = await self._request_with_retry(
                prompt=prompt,
                temperature=temperature,
            )

            text = getattr(response, "text", None)

            if text is None:
                raise LLMException("Gemini returned no response.")

            text = text.strip()

            if not text:
                raise LLMException("Gemini returned an empty response.")

            logger.info(
                "Received Gemini response "
                "(%d characters).",
                len(text),
            )

            return text

        except (
            ValidationException,
            ConfigurationException,
            LLMException,
        ):
            raise

        except Exception as exc:
            logger.exception("Unexpected error while generating text.")
            raise LLMException("Unexpected Gemini error.") from exc


    @staticmethod
    def _extract_json(
        text: str,
    ) -> str:
        """
        Remove Markdown code fences from
        Gemini responses.
        """

        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()


    @staticmethod
    def _normalize_json(
        data: dict,
    ) -> None:
        """
        Normalize common LLM field variations.

        The planner occasionally returns
        slightly different field names.
        """

        tasks = data.get(
            "tasks",
        )

        if not isinstance(
            tasks,
            list,
        ):
            return

        for task in tasks:

            if not isinstance(
                task,
                dict,
            ):
                continue

            # -------------------------------
            # id -> task_id
            # -------------------------------

            if (
                "id" in task
                and "task_id" not in task
            ):
                task["task_id"] = task.pop(
                    "id",
                )

            # -------------------------------
            # state -> status
            # -------------------------------

            if (
                "state" in task
                and "status" not in task
            ):
                task["status"] = task.pop(
                    "state",
                )

            # -------------------------------
            # description -> title
            # -------------------------------

            if (
                "description" in task
                and "title" not in task
            ):
                task["title"] = task.pop(
                    "description",
                )

            # -------------------------------
            # Default values
            # -------------------------------

            task.setdefault(
                "status",
                "pending",
            )

            task.setdefault(
                "output",
                None,
            )

            task.setdefault(
                "error",
                None,
            )

            task.setdefault(
                "execution_time",
                None,
            )
    
    async def generate_json(
        self,
        prompt: str,
        output_model: type[T],
        temperature: float | None = None,
    ) -> T:
        """
        Generate structured JSON from Gemini and validate
        it using the supplied Pydantic model.

        Args:
            prompt:
                Prompt instructing Gemini to return JSON.

            output_model:
                Pydantic model used for validation.

            temperature:
                Optional temperature override.

        Returns:
            Validated Pydantic model instance.

        Raises:
            ValidationException:
                If Gemini returns invalid JSON or the
                response does not match the expected schema.

            LLMException:
                If Gemini generation fails.
        """

        logger.info(
            "Generating structured JSON using '%s'.",
            output_model.__name__,
        )

        response = await self.generate(
            prompt=prompt,
            temperature=temperature,
        )

        try:

            cleaned_response = self._extract_json(
                response,
            )

            data = json.loads(
                cleaned_response,
            )

        except json.JSONDecodeError as exc:

            logger.exception(
                "Gemini returned invalid JSON."
            )

            logger.error(
                "Raw Gemini response:\n%s",
                response,
            )

            raise ValidationException(
                "Gemini returned invalid JSON."
            ) from exc

        if isinstance(
            data,
            dict,
        ):

            self._normalize_json(
                data,
            )

        try:

            validated = output_model.model_validate(
                data,
            )

            logger.info(
                "Successfully validated response "
                "into '%s'.",
                output_model.__name__,
            )

            return validated

        except ValidationError as exc:

            logger.exception(
                "Gemini response failed schema validation."
            )

            logger.error(
                "Expected Model: %s",
                output_model.__name__,
            )

            logger.error(
                "Parsed JSON:\n%s",
                json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False,
                ),
            )

            raise ValidationException(
                "Gemini returned an unexpected JSON structure."
            ) from exc

        except Exception as exc:

            logger.exception(
                "Unexpected error while validating JSON."
            )

            raise LLMException(
                "Failed to validate Gemini response."
            ) from exc