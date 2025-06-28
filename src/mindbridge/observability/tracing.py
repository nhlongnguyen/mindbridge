"""OpenTelemetry tracing configuration."""

import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def configure_tracing(service_name: Optional[str] = None) -> None:
    """Configure OpenTelemetry tracing with OTLP exporter.
    
    Args:
        service_name: Name of the service for resource identification.
                     Defaults to "mindbridge" if not provided.
    """
    if not service_name or service_name.strip() == "":
        service_name = "mindbridge"
    
    # Create resource with service information
    resource = Resource.create(
        attributes={
            "service.name": service_name,
            "service.version": "0.1.0",
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
        }
    )
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Configure OTLP exporter
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    
    # Add batch span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Add console exporter for development
    if os.getenv("OTEL_CONSOLE_EXPORTER", "false").lower() == "true":
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(console_processor)


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for the given name.
    
    Args:
        name: Name of the tracer, typically __name__ of the calling module.
        
    Returns:
        OpenTelemetry Tracer instance.
    """
    return trace.get_tracer(name)