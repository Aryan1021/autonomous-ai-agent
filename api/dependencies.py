"""
Dependency providers for the API.
"""

from __future__ import annotations

from functools import lru_cache

from agent.context_builder import ContextBuilder
from agent.document_generator import DocumentGenerator
from agent.executor import Executor
from agent.llm import LLMService
from agent.planner import Planner


@lru_cache
def get_llm() -> LLMService:
    return LLMService()


@lru_cache
def get_planner() -> Planner:
    return Planner(get_llm())


@lru_cache
def get_executor() -> Executor:
    return Executor(get_llm())


@lru_cache
def get_context_builder() -> ContextBuilder:
    return ContextBuilder()


@lru_cache
def get_document_generator() -> DocumentGenerator:
    return DocumentGenerator()