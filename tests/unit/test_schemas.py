"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from src.common.schemas import AggregatedResult, PageviewEvent


class TestPageviewEvent:
    """Tests for PageviewEvent schema."""

    def test_valid_pageview_event(self) -> None:
        """Test that a valid event passes validation."""
        event = PageviewEvent(
            user_id=1234,
            postcode="SW19",
            webpage="https://www.website.com/index.html",
            timestamp=1611662684,
        )
        assert event.user_id == 1234
        assert event.postcode == "SW19"
        assert event.webpage == "https://www.website.com/index.html"
        assert event.timestamp == 1611662684

    def test_invalid_user_id(self) -> None:
        """Test that invalid user_id fails validation."""
        with pytest.raises(ValidationError):
            PageviewEvent(
                user_id=0,  # Must be > 0
                postcode="SW19",
                webpage="https://www.website.com",
                timestamp=1611662684,
            )

    def test_invalid_postcode(self) -> None:
        """Test that invalid postcode fails validation."""
        with pytest.raises(ValidationError):
            PageviewEvent(
                user_id=1234,
                postcode="invalid!",  # Contains invalid characters
                webpage="https://www.website.com",
                timestamp=1611662684,
            )

    def test_invalid_webpage_url(self) -> None:
        """Test that invalid webpage URL fails validation."""
        with pytest.raises(ValidationError):
            PageviewEvent(
                user_id=1234,
                postcode="SW19",
                webpage="not-a-url",  # Missing http/https
                timestamp=1611662684,
            )

    def test_invalid_timestamp_too_old(self) -> None:
        """Test that timestamp before year 2000 fails validation."""
        with pytest.raises(ValidationError):
            PageviewEvent(
                user_id=1234,
                postcode="SW19",
                webpage="https://www.website.com",
                timestamp=100,  # Too old (before year 2000)
            )

    def test_invalid_timestamp_too_future(self) -> None:
        """Test that timestamp after year 2100 fails validation."""
        with pytest.raises(ValidationError):
            PageviewEvent(
                user_id=1234,
                postcode="SW19",
                webpage="https://www.website.com",
                timestamp=5000000000,  # Too far in future (after year 2100)
            )


class TestAggregatedResult:
    """Tests for AggregatedResult schema."""

    def test_valid_aggregated_result(self) -> None:
        """Test that a valid aggregation passes validation."""
        from datetime import datetime

        result = AggregatedResult(
            postcode="SW19",
            window_start=datetime(2025, 1, 1, 12, 0, 0),
            window_end=datetime(2025, 1, 1, 12, 1, 0),
            pageview_count=42,
        )
        assert result.postcode == "SW19"
        assert result.pageview_count == 42

    def test_invalid_negative_count(self) -> None:
        """Test that negative pageview count fails validation."""
        from datetime import datetime

        with pytest.raises(ValidationError):
            AggregatedResult(
                postcode="SW19",
                window_start=datetime(2025, 1, 1, 12, 0, 0),
                window_end=datetime(2025, 1, 1, 12, 1, 0),
                pageview_count=-1,  # Must be >= 0
            )
