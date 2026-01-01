"""SQL INSERT queries for data pipeline."""


def insert_raw_events_sql() -> str:
    """Create SQL to archive valid raw events.

    Returns:
        SQL INSERT statement for raw events
    """
    return """
        INSERT INTO raw_sink
        SELECT user_id, postcode, webpage, `timestamp`, dt, event_hour
        FROM validated_events
    """


def insert_aggregated_sql() -> str:
    """Create SQL to aggregate valid events by postcode.

    Returns:
        SQL INSERT statement for aggregated results
    """
    return """
        INSERT INTO agg_sink
        SELECT window_start, window_end, postcode, COUNT(*) AS pageview_count
        FROM TABLE(
            TUMBLE(TABLE validated_events, DESCRIPTOR(ts), INTERVAL '1' MINUTE)
        )
        GROUP BY window_start, window_end, postcode
    """
