"""
Executor service responsible for executing planner tasks.
"""

from __future__ import annotations

import time

from agent.llm import LLMService
from agent.models import (
    ExecutionResult,
    PlannerOutput,
    WorkflowContext,
)
from core.exceptions import (
    ConfigurationException,
    ExecutorException,
    LLMException,
    ValidationException,
)
from core.executor_prompts import build_executor_prompt
from core.logging_config import get_logger

logger = get_logger(__name__)


class Executor:
    """
    Executes planner-generated tasks.
    """

    def __init__(
        self,
        llm: LLMService,
    ) -> None:
        """
        Initialize the executor.

        Args:
            llm:
                LLM service instance.
        """

        self._llm = llm

    async def execute(
        self,
        workflow: WorkflowContext,
        plan: PlannerOutput,
    ) -> ExecutionResult:
        """
        Execute all tasks in a planner-generated execution plan.

        Args:
            plan:
                Planner output containing executable tasks.

        Returns:
            ExecutionResult

        Raises:
            ValidationException:
                If the execution plan is invalid.

            ExecutorException:
                If an unexpected executor error occurs.
        """

        if not plan.tasks:
            raise ValidationException(
                "Execution plan contains no tasks."
            )

        logger.info(
            "[%s] Executing %d tasks.",
            workflow.request_id,
            len(plan.tasks),
        )

        completed = 0
        failed = 0

        combined_output: list[str] = []

        total_tasks = len(plan.tasks)

        for task in plan.tasks:

            logger.info(
                "[%s] Task %d/%d started: %s",
                workflow.request_id,
                task.task_id,
                total_tasks,
                task.title,
            )

            prompt = build_executor_prompt(
                goal=plan.goal,
                assumptions=plan.assumptions,
                task_title=task.title,
            )

            start_time = time.perf_counter()

            try:

                result = await self._llm.generate(
                    prompt=prompt,
                )

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                task.status = "completed"
                task.output = result
                task.error = None
                task.execution_time = elapsed

                completed += 1

                combined_output.append(result)

                logger.info(
                    "[%s] Task %d completed in %.2f seconds (%d chars).",
                    workflow.request_id,
                    task.task_id,
                    elapsed,
                    len(result),
                )

            except (
                ConfigurationException,
                ValidationException,
                LLMException,
            ) as exc:

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                task.status = "failed"
                task.error = str(exc)
                task.execution_time = elapsed

                failed += 1

                logger.error(
                    "[%s] Task %d failed after %.2f seconds: %s",
                    workflow.request_id,
                    task.task_id,
                    elapsed,
                    exc,
                )

                # -------------------------------------------------
                # Fail fast.
                # Do not continue executing remaining tasks when the
                # LLM itself is unavailable.
                # -------------------------------------------------

                raise ExecutorException(
                    f"Execution aborted because the LLM became unavailable: {exc}"
                ) from exc

            except Exception as exc:

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                task.status = "failed"
                task.error = str(exc)
                task.execution_time = elapsed

                failed += 1

                logger.exception(
                    "Unexpected executor error while executing task %d.",
                    task.task_id,
                )

                raise ExecutorException(
                    f"Unexpected error while executing task {task.task_id}."
                ) from exc

        logger.info(
            "[%s] Execution completed (%d success, %d failed).",
            workflow.request_id,
            completed,
            failed,
        )

        try:

            return ExecutionResult(
                goal=plan.goal,
                assumptions=plan.assumptions,
                tasks=plan.tasks,
                combined_output="\n\n".join(combined_output),
                completed_tasks=completed,
                failed_tasks=failed,
                execution_summary=(
                    f"{completed} tasks completed successfully. "
                    f"{failed} tasks failed."
                ),
            )

        except Exception as exc:

            logger.exception(
                "Failed to build execution result."
            )

            raise ExecutorException(
                "Executor failed unexpectedly."
            ) from exc