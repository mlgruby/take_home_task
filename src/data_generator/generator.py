"""Realistic pageview event generator with configurable distributions."""

import random
import time
from collections.abc import Iterator
from datetime import datetime
from typing import Any

from faker import Faker

from src.common.schemas import PageviewEvent


class PageviewGenerator:
    """Generate realistic pageview events with Zipf distribution for postcodes.

    Attributes:
        postcodes: List of possible postcodes
        urls: List of possible webpage URLs
        faker: Faker instance for generating realistic data
    """

    def __init__(self, postcodes: list[str] | None = None, urls: list[str] | None = None):
        """Initialize the pageview generator.

        Args:
            postcodes: List of postcodes to use (defaults to UK postcodes)
            urls: List of URLs to use (defaults to sample website pages)
        """
        self.faker = Faker()

        # Default UK postcodes with realistic distribution
        self.postcodes = postcodes or [
            "SW19",
            "E1",
            "W1",
            "N1",
            "SE1",
            "EC1",
            "WC1",
            "NW1",
            "M1",
            "B1",
            "L1",
            "G1",
            "EH1",
            "CF1",
            "BT1",
        ]

        # Default website pages
        self.urls = urls or [
            "https://www.website.com/index.html",
            "https://www.website.com/products.html",
            "https://www.website.com/about.html",
            "https://www.website.com/contact.html",
            "https://www.website.com/blog.html",
        ]

    def _zipf_weights(self, n: int, alpha: float = 1.5) -> list[float]:
        """Generate Zipf distribution weights.

        Args:
            n: Number of items
            alpha: Zipf parameter (higher = more skewed)

        Returns:
            List of weights following Zipf distribution
        """
        return [1.0 / (i**alpha) for i in range(1, n + 1)]

    def _url_weights(self) -> list[float]:
        """Get URL weights (homepage gets more traffic).

        Returns:
            List of weights for URLs
        """
        # Homepage gets 10x traffic, products 5x, etc.
        base_weights = [10, 5, 3, 2, 1]
        return base_weights[: len(self.urls)]

    def generate_event(self) -> dict[str, Any]:
        """Generate a single pageview event.

        Returns:
            Dictionary containing pageview event data
        """
        return {
            "user_id": random.randint(1, 100000),
            "postcode": random.choices(
                self.postcodes, weights=self._zipf_weights(len(self.postcodes))
            )[0],
            "webpage": random.choices(self.urls, weights=self._url_weights())[0],
            "timestamp": int(datetime.now().timestamp() * 1000),
        }

    def generate_validated_event(self) -> PageviewEvent:
        """Generate and validate a pageview event.

        Returns:
            Validated PageviewEvent instance
        """
        event_data = self.generate_event()
        return PageviewEvent(**event_data)

    def generate_stream(
        self, rate: float = 1.16, duration_seconds: int | None = None
    ) -> Iterator[dict[str, Any]]:
        """Generate continuous stream of events at specified rate.

        Args:
            rate: Events per second (default: 1.16 for ~100K/day)
            duration_seconds: Duration to generate events (None = infinite)
        """
        interval = 1.0 / rate
        start_time = time.time()

        while True:
            if duration_seconds and (time.time() - start_time) > duration_seconds:
                break

            event = self.generate_event()
            yield event

            # Sleep to maintain rate
            time.sleep(interval)
