"""Unit tests for data generator."""

from src.data_generator.generator import PageviewGenerator


class TestPageviewGenerator:
    """Tests for PageviewGenerator."""

    def test_generate_event(self) -> None:
        """Test that generated events have required fields."""
        generator = PageviewGenerator()
        event = generator.generate_event()

        assert "user_id" in event
        assert "postcode" in event
        assert "webpage" in event
        assert "timestamp" in event

        assert isinstance(event["user_id"], int)
        assert event["user_id"] > 0
        assert isinstance(event["postcode"], str)
        assert isinstance(event["webpage"], str)
        assert isinstance(event["timestamp"], int)

    def test_generate_validated_event(self) -> None:
        """Test that validated events pass schema validation."""
        generator = PageviewGenerator()
        event = generator.generate_validated_event()

        assert event.user_id > 0
        assert len(event.postcode) >= 2
        assert event.webpage.startswith("http")
        assert event.timestamp > 0

    def test_custom_postcodes(self) -> None:
        """Test generator with custom postcodes."""
        custom_postcodes = ["TEST1", "TEST2", "TEST3"]
        generator = PageviewGenerator(postcodes=custom_postcodes)

        event = generator.generate_event()
        assert event["postcode"] in custom_postcodes

    def test_custom_urls(self) -> None:
        """Test generator with custom URLs."""
        custom_urls = ["https://test.com/page1", "https://test.com/page2"]
        generator = PageviewGenerator(urls=custom_urls)

        event = generator.generate_event()
        assert event["webpage"] in custom_urls

    def test_zipf_weights(self) -> None:
        """Test Zipf distribution weights."""
        generator = PageviewGenerator()
        weights = generator._zipf_weights(5)

        assert len(weights) == 5
        assert all(w > 0 for w in weights)
        # Zipf distribution should be decreasing
        assert weights[0] > weights[-1]

    def test_url_weights(self) -> None:
        """Test URL weights favor homepage."""
        generator = PageviewGenerator()
        weights = generator._url_weights()

        assert len(weights) == len(generator.urls)
        # Homepage should have highest weight
        assert weights[0] == 10
