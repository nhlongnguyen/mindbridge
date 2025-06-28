"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from opentelemetry import trace


def configure_logging(
    log_level: str = "INFO", 
    log_format: str = "console"
) -> None:
    """Configure structured logging with OpenTelemetry correlation.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Output format ("json" or "console").
    """
    # Set logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=numeric_level)
    
    # Configure processors based on format
    if log_format == "json":
        processors = [
            structlog.contextvars.merge_contextvars,
            add_trace_context,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.JSONRenderer()
        ]
    elif log_format == "console":
        processors = [
            structlog.contextvars.merge_contextvars,
            add_trace_context,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Default to console format for invalid inputs
        processors = [
            structlog.contextvars.merge_contextvars,
            add_trace_context,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def add_trace_context(
    logger: Any, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add OpenTelemetry trace context to log records.
    
    Args:
        logger: The logger instance.
        method_name: The name of the logging method.
        event_dict: The event dictionary to be logged.
        
    Returns:
        Updated event dictionary with trace context.
    """
    # Get current span context
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        span_context = current_span.get_span_context()
        if span_context.is_valid:
            event_dict["trace_id"] = format(span_context.trace_id, "032x")
            event_dict["span_id"] = format(span_context.span_id, "016x")
    
    return event_dict


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Name of the logger, typically __name__ of the calling module.
        
    Returns:
        Structured logger instance.
    """
    return structlog.get_logger(name)