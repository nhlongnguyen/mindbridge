"""Tests for OpenTelemetry tracing setup."""

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from mindbridge.observability.tracing import configure_tracing, get_tracer


class TestTracingConfiguration:
    """Test cases for OpenTelemetry tracing configuration."""

    def test_configure_tracing_sets_tracer_provider(self) -> None:
        """Expected use case: configure_tracing should set up TracerProvider."""
        configure_tracing(service_name="test-service")
        
        tracer_provider = trace.get_tracer_provider()
        assert isinstance(tracer_provider, TracerProvider)

    def test_configure_tracing_with_custom_service_name(self) -> None:
        """Expected use case: Should use provided service name in resource."""
        configure_tracing(service_name="custom-service")
        
        tracer_provider = trace.get_tracer_provider()
        resource = tracer_provider.resource
        assert resource.attributes.get("service.name") == "custom-service"

    def test_configure_tracing_with_default_service_name(self) -> None:
        """Expected use case: Should use default service name when none provided."""
        configure_tracing()
        
        tracer_provider = trace.get_tracer_provider()
        resource = tracer_provider.resource
        assert resource.attributes.get("service.name") == "mindbridge"

    def test_get_tracer_returns_tracer_instance(self) -> None:
        """Expected use case: get_tracer should return a valid tracer."""
        configure_tracing()
        tracer = get_tracer(__name__)
        
        assert tracer is not None
        assert hasattr(tracer, "start_span")

    def test_tracing_creates_spans(self) -> None:
        """Expected use case: Should be able to create and end spans."""
        configure_tracing()
        tracer = get_tracer(__name__)
        
        with tracer.start_as_current_span("test-span") as span:
            assert span is not None
            assert span.is_recording()
            span.set_attribute("test.attribute", "test-value")


class TestTracingEdgeCases:
    """Test edge cases for tracing configuration."""

    def test_configure_tracing_with_empty_service_name(self) -> None:
        """Edge case: Empty service name should use default."""
        configure_tracing(service_name="")
        
        tracer_provider = trace.get_tracer_provider()
        resource = tracer_provider.resource
        assert resource.attributes.get("service.name") == "mindbridge"

    def test_configure_tracing_multiple_calls(self) -> None:
        """Edge case: Multiple configuration calls should not fail."""
        configure_tracing(service_name="service1")
        configure_tracing(service_name="service2")
        
        # Should not raise any exceptions
        tracer_provider = trace.get_tracer_provider()
        assert isinstance(tracer_provider, TracerProvider)


class TestTracingFailureCases:
    """Test failure cases for tracing configuration."""

    def test_get_tracer_without_configuration(self) -> None:
        """Failure case: get_tracer without configuration should still work."""
        # Reset to default state
        trace.set_tracer_provider(trace.NoOpTracerProvider())
        
        tracer = get_tracer(__name__)
        assert tracer is not None
        # Should be NoOp tracer when not configured