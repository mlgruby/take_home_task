"""SQL view definitions for data transformation."""


def create_validated_view_sql() -> str:
    """Create SQL for validated events view.

    Filters out invalid postcodes (NULL or length not in 2-10 range).

    Returns:
        SQL CREATE VIEW statement
    """
    return """
        CREATE VIEW validated_events AS
        SELECT
            user_id,
            postcode,
            webpage,
            `timestamp`,
            ts,
            DATE_FORMAT(ts, 'yyyy-MM-dd') AS dt,
            DATE_FORMAT(ts, 'HH') AS event_hour
        FROM pageviews
        WHERE postcode IS NOT NULL
          AND CHAR_LENGTH(postcode) >= 2
          AND CHAR_LENGTH(postcode) <= 10
    """
