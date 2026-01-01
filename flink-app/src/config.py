"""Flink job configuration using Pydantic."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FlinkConfig(BaseSettings):
    """Flink-specific configuration with environment variable support.

    All settings can be overridden via environment variables.
    """

    # Kafka
    kafka_bootstrap_servers: str = Field(
        default="kafka:29092", description="Kafka bootstrap servers"
    )
    kafka_topic: str = Field(default="pageview-events", description="Kafka topic name")
    kafka_group_id: str = Field(default="flink-pageview-processor", description="Consumer group ID")

    # S3
    s3_endpoint: str = Field(
        default="http://localstack:4566", description="S3 endpoint URL (LocalStack)"
    )
    raw_bucket: str = Field(
        default="s3://pageview-pipeline-local-raw-events/", description="S3 bucket for raw events"
    )
    agg_bucket: str = Field(
        default="s3://pageview-pipeline-local-aggregated/",
        description="S3 bucket for aggregated data",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Map environment variables to fields
        env_prefix="",
    )
