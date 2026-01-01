"""Pageview Flink Processor - Optimized Table API with View Pattern.

Uses a single source view to eliminate redundant reads.
DLQ is conditional via WHERE clause (only invalid records).
"""

import os
import sys

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from config import FlinkConfig
from sql import (
    create_agg_sink,
    create_kafka_source,
    create_raw_sink,
    create_validated_view_sql,
    insert_aggregated_sql,
    insert_raw_events_sql,
)

from src.common.logging import setup_logging

logger = setup_logging("flink-pageview-processor")


def main() -> None:
    """Run the Flink pageview processing pipeline."""
    # Load configuration
    config = FlinkConfig()
    logger.info("Starting Pageview Flink Processor (Optimized Table API)")
    logger.info(f"Kafka: {config.kafka_bootstrap_servers}, Topic: {config.kafka_topic}")
    logger.info(f"S3 Endpoint: {config.s3_endpoint}")
    logger.info(f"Buckets - Raw: {config.raw_bucket}, Agg: {config.agg_bucket}")

    # Initialize Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(2)
    env.enable_checkpointing(60000)  # 1 minute checkpoints

    # Create Table environment
    settings = EnvironmentSettings.in_streaming_mode()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # Configure S3 access for LocalStack
    logger.info("Configuring S3 access...")
    cfg = t_env.get_config().get_configuration()
    cfg.set_string("fs.s3.endpoint", config.s3_endpoint)
    cfg.set_string("fs.s3a.endpoint", config.s3_endpoint)
    cfg.set_string("fs.s3a.path.style.access", "true")
    cfg.set_string(
        "fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
    )
    cfg.set_string("fs.s3a.access.key", "test")
    cfg.set_string("fs.s3a.secret.key", "test")
    cfg.set_string("fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

    # Create Kafka source table
    logger.info("Creating Kafka source table...")
    create_kafka_source(
        t_env, config.kafka_bootstrap_servers, config.kafka_topic, config.kafka_group_id
    )

    # Create sink tables
    logger.info("Creating sink tables...")
    create_raw_sink(t_env, config.raw_bucket)
    create_agg_sink(t_env, config.agg_bucket)

    # Create validated events view (filters invalid postcodes)
    logger.info("Creating validated events view...")
    t_env.execute_sql(create_validated_view_sql())

    # Build pipeline with statement set
    logger.info("Building pipeline...")
    statement_set = t_env.create_statement_set()

    # Add INSERT statements
    statement_set.add_insert_sql(insert_raw_events_sql())  # Archive valid raw events
    statement_set.add_insert_sql(insert_aggregated_sql())  # Aggregate valid events

    # Execute all statements atomically
    logger.info("Submitting job...")
    statement_set.execute().wait()
    logger.info("Pipeline completed")


if __name__ == "__main__":
    main()
