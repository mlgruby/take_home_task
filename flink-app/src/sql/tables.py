"""SQL table definitions (DDL) for Flink pipeline."""

from pyflink.table import TableEnvironment


def create_kafka_source(
    t_env: TableEnvironment, bootstrap_servers: str, topic: str, group_id: str
) -> None:
    """Create Kafka source table for pageview events.

    Args:
        t_env: Flink table environment
        bootstrap_servers: Kafka bootstrap servers
        topic: Kafka topic name
        group_id: Consumer group ID
    """
    ddl = f"""
        CREATE TABLE pageviews (
            user_id INT,
            postcode STRING,
            webpage STRING,
            `timestamp` BIGINT,
            ts AS TO_TIMESTAMP_LTZ(`timestamp`, 3),
            WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{topic}',
            'properties.bootstrap.servers' = '{bootstrap_servers}',
            'properties.group.id' = '{group_id}',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(ddl)


def create_raw_sink(t_env: TableEnvironment, bucket: str) -> None:
    """Create S3 sink for raw events (partitioned by date/hour)."""
    ddl = f"""
        CREATE TABLE raw_sink (
            user_id INT,
            postcode STRING,
            webpage STRING,
            `timestamp` BIGINT,
            dt STRING,
            event_hour STRING
        ) PARTITIONED BY (dt, event_hour) WITH (
            'connector' = 'filesystem',
            'path' = '{bucket}',
            'format' = 'parquet',
            'sink.partition-commit.policy.kind' = 'success-file'
        )
    """
    t_env.execute_sql(ddl)


def create_agg_sink(t_env: TableEnvironment, bucket: str) -> None:
    """Create S3 sink for aggregated results."""
    ddl = f"""
        CREATE TABLE agg_sink (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            postcode STRING,
            pageview_count BIGINT
        ) WITH (
            'connector' = 'filesystem',
            'path' = '{bucket}',
            'format' = 'parquet'
        )
    """
    t_env.execute_sql(ddl)
