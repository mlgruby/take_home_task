"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineConfig(BaseSettings):
    """Pipeline configuration with environment variable support.

    All settings can be overridden via environment variables.
    """

    # AWS Configuration
    aws_region: str = "us-east-1"
    localstack_endpoint: str = "http://localhost:4566"

    # Kafka Configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "pageview-events"
    kafka_consumer_group: str = "flink-pageview-processor"

    # S3 Configuration
    raw_events_bucket: str = "pageview-raw-events"
    aggregated_bucket: str = "pageview-aggregated"
    dlq_bucket: str = "pageview-dlq"
    flink_code_bucket: str = "flink-app-code"

    # Processing Configuration
    window_size_seconds: int = 60
    checkpoint_interval_ms: int = 60000
    parallelism: int = 2

    # Data Generator
    event_rate: float = 1.16  # Events per second (~100K/day)

    # Monitoring
    metrics_port: int = 9090
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
