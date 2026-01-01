"""Unit tests for SQL generation logic."""

from unittest.mock import MagicMock

from src.sql.tables import create_agg_sink, create_kafka_source, create_raw_sink


def test_create_kafka_source() -> None:
    """Test Kafka source DDL generation."""
    mock_t_env = MagicMock()

    create_kafka_source(mock_t_env, "localhost:9092", "test-topic", "test-group")

    # Verify execute_sql was called
    mock_t_env.execute_sql.assert_called_once()

    # Inspect argument to ensure it contains key DDL parts
    call_args = mock_t_env.execute_sql.call_args[0][0]
    assert "CREATE TABLE pageviews" in call_args
    assert "'connector' = 'kafka'" in call_args
    assert "'topic' = 'test-topic'" in call_args
    assert "'properties.bootstrap.servers' = 'localhost:9092'" in call_args


def test_create_raw_sink() -> None:
    """Test Raw S3 Sink DDL generation."""
    mock_t_env = MagicMock()

    create_raw_sink(mock_t_env, "s3://test-bucket")

    mock_t_env.execute_sql.assert_called_once()
    call_args = mock_t_env.execute_sql.call_args[0][0]
    assert "CREATE TABLE raw_sink" in call_args
    assert "'connector' = 'filesystem'" in call_args
    assert "'path' = 's3://test-bucket'" in call_args
    assert "PARTITIONED BY (dt, event_hour)" in call_args


def test_create_agg_sink() -> None:
    """Test Aggregated S3 Sink DDL generation."""
    mock_t_env = MagicMock()

    create_agg_sink(mock_t_env, "s3://agg-bucket")

    mock_t_env.execute_sql.assert_called_once()
    call_args = mock_t_env.execute_sql.call_args[0][0]
    assert "CREATE TABLE agg_sink" in call_args
    assert "'path' = 's3://agg-bucket'" in call_args
    assert "window_start TIMESTAMP(3)" in call_args
