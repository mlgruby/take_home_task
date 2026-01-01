"""Prometheus metrics definitions for pipeline monitoring."""

from prometheus_client import Counter, start_http_server

# Producer metrics
events_generated = Counter("pageview_events_generated_total", "Total pageview events generated")
events_published = Counter(
    "pageview_events_published_total", "Events successfully published to Kafka"
)
publish_errors = Counter("pageview_publish_errors_total", "Kafka publish errors")


def start_metrics_server(port: int = 9090) -> None:
    """Start Prometheus metrics HTTP server.

    Args:
        port: Port number for metrics endpoint (default: 9090)
    """
    start_http_server(port)
