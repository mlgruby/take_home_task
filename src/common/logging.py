"""Structured logging configuration using loguru."""

import sys
from typing import Any

from loguru import logger


def setup_logging(service_name: str, level: str = "INFO") -> Any:
    """Configure structured logging with JSON output for CloudWatch compatibility.

    Args:
        service_name: Name of the service for log context
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured loguru logger instance
    """
    # Remove default handler
    logger.remove()

    # Add JSON-formatted handler for production
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=level.upper(),
        serialize=False,  # Set to True for JSON output in production
        backtrace=True,
        diagnose=True,
    )

    # Add service context to all logs
    configured_logger = logger.bind(service=service_name)

    return configured_logger
