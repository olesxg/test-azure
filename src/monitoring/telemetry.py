import logging
from typing import Dict, Any
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from azure.monitor.opentelemetry import configure_azure_monitor
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
tracer = None
meter = None
event_counter = None
metric_recorder = None


def init_telemetry(app_insights_connection_string: str):
    global tracer, meter, event_counter, metric_recorder

    configure_azure_monitor(connection_string=app_insights_connection_string)

    trace_provider = TracerProvider()
    trace.set_tracer_provider(trace_provider)
    tracer = trace.get_tracer(__name__)

    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(), export_interval_millis=60000
    )
    meter_provider = MeterProvider(metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    meter = metrics.get_meter(__name__)

    event_counter = meter.create_counter(
        "arbitrage_events", description="Count of arbitrage events"
    )
    metric_recorder = meter.create_histogram(
        "arbitrage_metrics", description="Arbitrage metrics"
    )

    logging.basicConfig(level=logging.INFO)
    logger.addHandler(AzureLogHandler(connection_string=app_insights_connection_string))


def track_event(event_name: str, properties: Dict[str, Any] = None):
    if event_counter:
        event_counter.add(1, {"event_name": event_name})

    logger.info(f"Event: {event_name}", extra={"custom_dimensions": properties or {}})


def track_metric(metric_name: str, value: float, properties: Dict[str, Any] = None):
    if metric_recorder:
        metric_recorder.record(value, {"metric_name": metric_name})

    logger.info(
        f"Metric: {metric_name}={value}", extra={"custom_dimensions": properties or {}}
    )


def create_span(span_name: str):
    if tracer:
        return tracer.start_as_current_span(span_name)
    return None
