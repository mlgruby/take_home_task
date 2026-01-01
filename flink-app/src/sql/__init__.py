"""SQL module for Flink pipeline.

Organized into:
- tables: Table DDL (CREATE TABLE)
- views: View definitions (CREATE VIEW)
- inserts: Data queries (INSERT)
"""

from .inserts import insert_aggregated_sql, insert_raw_events_sql
from .tables import create_agg_sink, create_kafka_source, create_raw_sink
from .views import create_validated_view_sql

__all__ = [
    # Tables
    "create_kafka_source",
    "create_raw_sink",
    "create_agg_sink",
    # Views
    "create_validated_view_sql",
    # Inserts
    "insert_raw_events_sql",
    "insert_aggregated_sql",
]
