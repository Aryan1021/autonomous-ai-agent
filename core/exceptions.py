"""
Custom exceptions used throughout the Autonomous AI Agent.
"""

from __future__ import annotations


class AgentException(Exception):
    """
    Base exception for the Autonomous AI Agent.
    """


class ConfigurationException(AgentException):
    """
    Raised when application configuration is invalid.
    """


class LLMException(AgentException):
    """
    Raised when communication with the LLM fails.
    """


class PlannerException(AgentException):
    """
    Raised when the Planner fails.
    """


class ExecutorException(AgentException):
    """
    Raised when task execution fails.
    """


class DocumentException(AgentException):
    """
    Raised when document generation fails.
    """

class ReflectionException(AgentException):
    """
    Raised when the Reflection service fails unexpectedly.
    """

class RegenerationException(AgentException):
    """
    Raised when the regeneration process fails.
    """

class CacheException(AgentException):
    """
    Raised when cache operations fail.
    """

class ValidationException(AgentException):
    """
    Raised when model validation fails.
    """