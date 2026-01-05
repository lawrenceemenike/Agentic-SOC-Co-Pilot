from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server, Counter, Histogram, Gauge

# Prometheus Metrics
# We use prometheus_client directly for simple metrics, 
# but OpenTelemetry can also bridge to Prometheus.
# For this MVP, we'll use prometheus_client for explicit control over the metrics listed in PRD.

AGENT_LATENCY = Histogram('agent_latency_seconds', 'Time spent in agent processing', ['agent', 'name'])
AGENT_THROUGHPUT = Counter('agent_throughput_total', 'Total number of requests processed by agent', ['agent'])
DECISION_CONFIDENCE = Histogram('decision_confidence_distribution', 'Distribution of decision confidence scores')
PROMPT_INJECTION_ATTEMPTS = Counter('prompt_injection_attempts_total', 'Total prompt injection attempts', ['result'])
APPROVAL_WAIT_SECONDS = Histogram('approval_wait_seconds', 'Time waiting for human approval')

# FinOps & Governance Metrics
TOKEN_USAGE_TOTAL = Counter('token_usage_total', 'Total tokens consumed', ['model', 'type']) # type=prompt/completion
BUDGET_SPEND_DAILY = Gauge('budget_spend_daily_usd', 'Current daily spend in USD')
POLICY_VIOLATIONS_TOTAL = Counter('policy_violations_total', 'Total policy violations detected', ['policy_type']) # type=regex/guardrail
CACHE_HITS_TOTAL = Counter('cache_hits_total', 'Total cache hits', ['cache_type']) # type=redis/vector

def setup_observability(service_name: str = "soc-copilot"):
    resource = Resource.create({"service.name": service_name})

    # Tracing
    trace_provider = TracerProvider(resource=resource)
    # processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
    # Fallback to console if OTLP not available or for debug
    processor = BatchSpanProcessor(ConsoleSpanExporter()) 
    trace_provider.add_span_processor(processor)
    trace.set_tracer_provider(trace_provider)

    # Metrics (OTLP)
    # metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://localhost:4317"))
    # meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    # metrics.set_meter_provider(meter_provider)
    
    # Start Prometheus client server
    # In a real app, this might be on a separate port or mounted on FastAPI
    try:
        start_http_server(8001)
    except Exception:
        pass # Already started

    return trace.get_tracer(__name__)

tracer = setup_observability()
