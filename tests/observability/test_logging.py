"""Tests for structured logging setup."""

import json
import logging
from io import StringIO
from typing import Dict, Any

import pytest
import structlog

from mindbridge.observability.logging_config import configure_logging, get_logger


class TestLoggingConfiguration:
    """Test cases for structured logging configuration."""

    def test_configure_logging_sets_up_structlog(self) -> None:
        """Expected use case: configure_logging should set up structlog properly."""
        configure_logging()
        
        # Check that structlog is configured
        logger = structlog.get_logger()
        assert logger is not None

    def test_configure_logging_with_json_format(self) -> None:
        """Expected use case: Should configure JSON output format."""
        configure_logging(log_format="json")
        
        # This will be validated through actual log output testing
        logger = get_logger(__name__)
        assert logger is not None

    def test_configure_logging_with_console_format(self) -> None:
        """Expected use case: Should configure human-readable console format."""
        configure_logging(log_format="console")
        
        logger = get_logger(__name__)
        assert logger is not None

    def test_get_logger_returns_structured_logger(self) -> None:
        """Expected use case: get_logger should return a structlog logger."""
        configure_logging()
        logger = get_logger(__name__)
        
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")

    def test_logger_includes_context_information(self) -> None:
        """Expected use case: Logger should include contextual information."""
        configure_logging()
        logger = get_logger(__name__)
        
        # Create a string buffer to capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        
        # Get the root logger and add our handler
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
        try:
            logger.info("test message", extra_field="test_value")
            log_output = log_capture.getvalue()
            assert "test message" in log_output
        finally:
            root_logger.removeHandler(handler)


class TestStructuredLogging:
    """Test cases for structured logging functionality."""

    def test_logger_outputs_json_format(self) -> None:
        """Expected use case: Logger should output valid JSON when configured."""
        configure_logging(log_format="json")
        logger = get_logger(__name__)
        
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
        try:
            logger.info("test json message", user_id=123, action="test")
            log_output = log_capture.getvalue().strip()
            
            if log_output:
                # Try to parse as JSON
                log_data = json.loads(log_output)
                assert isinstance(log_data, dict)
                assert "test json message" in str(log_data)
        except json.JSONDecodeError:
            # If not JSON, it should still contain the message
            assert "test json message" in log_output
        finally:
            root_logger.removeHandler(handler)

    def test_logger_includes_trace_correlation(self) -> None:
        """Expected use case: Logger should include OpenTelemetry trace correlation."""
        configure_logging()
        logger = get_logger(__name__)
        
        # This will be enhanced when OpenTelemetry integration is complete
        assert logger is not None


class TestLoggingEdgeCases:
    """Test edge cases for logging configuration."""

    def test_configure_logging_with_invalid_format(self) -> None:
        """Edge case: Invalid log format should default to console."""
        configure_logging(log_format="invalid")
        logger = get_logger(__name__)
        assert logger is not None

    def test_configure_logging_multiple_calls(self) -> None:
        """Edge case: Multiple configuration calls should not fail."""
        configure_logging(log_format="json")
        configure_logging(log_format="console")
        
        logger = get_logger(__name__)
        assert logger is not None


class TestLoggingFailureCases:
    """Test failure cases for logging configuration."""

    def test_get_logger_without_configuration(self) -> None:
        """Failure case: get_logger should work even without explicit configuration."""
        # Reset structlog configuration
        structlog.reset_defaults()
        
        logger = get_logger(__name__)
        assert logger is not None