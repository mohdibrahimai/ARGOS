"""Structured logging utilities for ARGOS services.

All services use `structlog` for structured JSON logging.  This module
configures a consistent logger with fields such as `trace_id` and `service`.
"""

import sys
from typing import Optional

import structlog


def configure_logging(service_name: str) -> structlog.BoundLogger:
    """Configure and return a structured logger.

    Args:
        service_name: Name of the service emitting logs (e.g., "answer-api").

    Returns:
        A bound structlog logger instance.
    """
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(10),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger(service=service_name)


__all__ = ["configure_logging"]