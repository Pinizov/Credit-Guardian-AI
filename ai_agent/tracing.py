"""
Enhanced tracing with OpenTelemetry for AI agent observability.
Provides detailed instrumentation for LLM calls, agent operations, and performance monitoring.
"""
import time
import json
import os
from functools import wraps
from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager

# OpenTelemetry imports with fallback
try:
    from opentelemetry import trace as otel_trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE_BASIC = True
except ImportError:
    OTEL_AVAILABLE_BASIC = False
    otel_trace = None

# Optional imports (not critical)
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False
    OTLPSpanExporter = None

try:
    from opentelemetry.instrumentation.openai import OpenAIInstrumentor
    OPENAI_INST_AVAILABLE = True
except ImportError:
    OPENAI_INST_AVAILABLE = False
    OpenAIInstrumentor = None

OTEL_AVAILABLE = OTEL_AVAILABLE_BASIC

# Fallback in-memory trace storage
TRACES = {}

# Initialize OpenTelemetry
_tracer = None
_initialized = False


def initialize_tracing(
    service_name: str = "credit-guardian-ai-agent",
    otlp_endpoint: Optional[str] = None,
    console_export: bool = True
) -> None:
    """
    Initialize OpenTelemetry tracing with configurable exporters.
    
    Args:
        service_name: Name of the service for trace identification
        otlp_endpoint: Optional OTLP collector endpoint (e.g., "http://localhost:4317")
        console_export: Whether to export traces to console for debugging
    """
    global _tracer, _initialized
    
    if not OTEL_AVAILABLE:
        print("WARNING: OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-openai")
        return
    
    if _initialized:
        return
    
    # Create resource with service information
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })
    
    # Set up tracer provider
    provider = TracerProvider(resource=resource)
    
    # Add console exporter for debugging
    if console_export:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # Add OTLP exporter if endpoint provided and available
    if OTLP_AVAILABLE and (otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")):
        endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    otel_trace.set_tracer_provider(provider)
    _tracer = otel_trace.get_tracer(__name__)
    
    # Instrument OpenAI SDK automatically if available
    if OPENAI_INST_AVAILABLE:
        try:
            OpenAIInstrumentor().instrument()
            print("OpenAI instrumentation enabled")
        except Exception as e:
            print(f"WARNING: OpenAI instrumentation failed: {e}")
    
    _initialized = True
    print(f"Tracing initialized for {service_name}")


def get_tracer():
    """Get the configured tracer instance."""
    global _tracer
    if not _initialized:
        initialize_tracing()
    return _tracer


@contextmanager
def trace_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    trace_llm: bool = False
):
    """
    Context manager for creating trace spans.
    
    Args:
        name: Name of the span
        attributes: Optional attributes to attach to the span
        trace_llm: Whether this is an LLM operation (adds specific attributes)
    """
    if OTEL_AVAILABLE and _initialized:
        tracer = get_tracer()
        with tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))
            
            if trace_llm:
                span.set_attribute("llm.request.type", "chat.completion")
            
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    else:
        # Fallback: simple timing
        start = time.time()
        try:
            yield None
        finally:
            duration_ms = int((time.time() - start) * 1000)
            TRACES[f"{name}_{int(time.time()*1000)}"] = {
                "op": name,
                "status": "ok",
                "ms": duration_ms,
                "attributes": attributes or {}
            }


def trace(op_name: str, trace_llm: bool = False) -> Callable:
    """
    Decorator for tracing function calls.
    
    Args:
        op_name: Name of the operation
        trace_llm: Whether this operation involves LLM calls
    """
    def deco(fn: Callable) -> Callable:
        @wraps(fn)
        def inner(*args, **kwargs):
            attributes = {
                "function.name": fn.__name__,
                "function.module": fn.__module__,
            }
            
            with trace_span(op_name, attributes=attributes, trace_llm=trace_llm):
                return fn(*args, **kwargs)
        
        return inner
    return deco


def add_trace_event(name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
    """
    Add a trace event to the current span.
    
    Args:
        name: Name of the event
        attributes: Optional attributes for the event
    """
    if OTEL_AVAILABLE and _initialized:
        span = otel_trace.get_current_span()
        if span:
            span.add_event(name, attributes=attributes or {})


def export_traces() -> str:
    """Export fallback in-memory traces as JSON."""
    return json.dumps(TRACES, ensure_ascii=False, indent=2)


# Note: Tracing is initialized lazily on first use
# You can also call initialize_tracing() explicitly with custom parameters
