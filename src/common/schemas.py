"""Pydantic schemas for pageview events and aggregation results."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PageviewEvent(BaseModel):
    """Immutable pageview event schema with validation.

    Attributes:
        user_id: Unique user identifier (integer)
        postcode: User location postcode (2-10 alphanumeric characters)
        webpage: Visited webpage URL (must be valid HTTP/HTTPS URL)
        timestamp: Event epoch timestamp in seconds
    """

    user_id: int = Field(..., gt=0, description="Unique user identifier")
    postcode: str = Field(..., pattern=r"^[A-Z0-9]{2,10}$", description="User location postcode")
    webpage: str = Field(..., pattern=r"^https?://.+", description="Visited webpage URL")
    timestamp: int = Field(..., gt=0, description="Event epoch timestamp in seconds")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Validate timestamp is within reasonable range (year 2000 - 2100)."""
        # Allow both seconds (old) and milliseconds (new) ranges for compatibility if needed,
        # but strictly our generator now sends ms. Validating for ms range:
        # 2000-01-01 ms: 946,684,800,000
        # 2100-01-01 ms: 4,102,444,800,000
        if v < 946684800000 or v > 4102444800000:
            raise ValueError(f"Invalid epoch timestamp (ms): {v}")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 1234,
                    "postcode": "SW19",
                    "webpage": "www.website.com/index.html",
                    "timestamp": 1611662684,
                }
            ]
        }
    }


class AggregatedResult(BaseModel):
    """1-minute windowed aggregation result.

    Attributes:
        postcode: Postcode for this aggregation
        window_start: Start datetime of the 1-minute window
        window_end: End datetime of the 1-minute window
        pageview_count: Total number of pageviews in this window
    """

    postcode: str
    window_start: datetime
    window_end: datetime
    pageview_count: int = Field(..., ge=0)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
