"""Prometheus metrics definitions for pipeline monitoring."""

from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Producer metrics
events_generated = Counter("pageview_events_generated_total", "Total pageview events generated")
events_published = Counter(
    "pageview_events_published_total", "Events successfully published to Kafka"
)
publish_errors = Counter("pageview_publish_errors_total", "Kafka publish errors")

# Flink metrics (exposed via Flink's metrics system)
events_processed = Counter("flink_events_processed_total", "Events processed by Flink application")
events_invalid = Counter("flink_events_invalid_total", "Invalid events rejected by Flink")
processing_latency = Histogram(
    "flink_processing_latency_seconds",
    "Event processing latency in seconds",
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)
window_events = Gauge("flink_window_events", "Number of events in current window", ["postcode"])
aggregations_produced = Counter("flink_aggregations_produced_total", "Total aggregations produced")

# S3 sink metrics
s3_writes_success = Counter("s3_writes_success_total", "Successful S3 writes", ["bucket"])
s3_writes_failed = Counter("s3_writes_failed_total", "Failed S3 writes", ["bucket"])


def start_metrics_server(port: int = 9090) -> None:
    """Start Prometheus metrics HTTP server.

    Args:
        port: Port number for metrics endpoint (default: 9090)
    """
    start_http_server(port)
