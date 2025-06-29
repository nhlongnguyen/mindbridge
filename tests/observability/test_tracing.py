"""Tests for OpenTelemetry tracing setup."""

from unittest.mock import MagicMock, patch

from mindbridge.observability.tracing import configure_tracing, get_tracer
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


class TestTracingConfiguration:
    """Test cases for OpenTelemetry tracing configuration."""

    def test_configure_tracing_sets_tracer_provider(self) -> None:
        """Expected use case: configure_tracing should set up TracerProvider."""
        configure_tracing(service_name="test-service")

        tracer_provider = trace.get_tracer_provider()
        assert isinstance(tracer_provider, TracerProvider)

    @patch("mindbridge.observability.tracing.trace.set_tracer_provider")
    @patch("mindbridge.observability.tracing.TracerProvider")
    def test_configure_tracing_with_custom_service_name(
        self, mock_tracer_provider_class: MagicMock, mock_set_tracer_provider: MagicMock
    ) -> None:
        """Expected use case: Should use provided service name in resource."""
        mock_tracer_provider = MagicMock()
        mock_tracer_provider_class.return_value = mock_tracer_provider

        configure_tracing(service_name="custom-service")

        # Verify TracerProvider was created with correct resource
        mock_tracer_provider_class.assert_called_once()
        resource_arg = mock_tracer_provider_class.call_args[1]["resource"]
        assert resource_arg.attributes.get("service.name") == "custom-service"

    @patch("mindbridge.observability.tracing.trace.set_tracer_provider")
    @patch("mindbridge.observability.tracing.TracerProvider")
    def test_configure_tracing_with_default_service_name(
        self, mock_tracer_provider_class: MagicMock, mock_set_tracer_provider: MagicMock
    ) -> None:
        """Expected use case: Should use default service name when none provided."""
        mock_tracer_provider = MagicMock()
        mock_tracer_provider_class.return_value = mock_tracer_provider

        configure_tracing()

        # Verify TracerProvider was created with correct resource
        mock_tracer_provider_class.assert_called_once()
        resource_arg = mock_tracer_provider_class.call_args[1]["resource"]
        assert resource_arg.attributes.get("service.name") == "mindbridge"

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

    @patch("mindbridge.observability.tracing.trace.set_tracer_provider")
    @patch("mindbridge.observability.tracing.TracerProvider")
    def test_configure_tracing_with_empty_service_name(
        self, mock_tracer_provider_class: MagicMock, mock_set_tracer_provider: MagicMock
    ) -> None:
        """Edge case: Empty service name should use default."""
        mock_tracer_provider = MagicMock()
        mock_tracer_provider_class.return_value = mock_tracer_provider

        configure_tracing(service_name="")

        # Verify TracerProvider was created with correct resource
        mock_tracer_provider_class.assert_called_once()
        resource_arg = mock_tracer_provider_class.call_args[1]["resource"]
        assert resource_arg.attributes.get("service.name") == "mindbridge"

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
