"""
Tests for the rate limiter.
Run: pytest tests/test_rate_limiter.py -v
"""

import pytest
from unittest.mock import patch
from scrapers.common.rate_limiter import RateLimiter


def _make_fake_time():
    """Create a fake time source and sleep function for deterministic tests.

    Starts at 1000.0 (not 0.0) because RateLimiter._last_request_time
    initializes to 0.0, so the first call needs a large elapsed time
    to behave as "immediate" (same as real time.monotonic()).
    """
    current_time = {"value": 1000.0}

    def fake_monotonic():
        return current_time["value"]

    def fake_sleep(seconds):
        current_time["value"] += seconds

    return current_time, fake_monotonic, fake_sleep


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_enforces_minimum_delay(self):
        current_time, fake_monotonic, fake_sleep = _make_fake_time()
        with patch(
            "scrapers.common.rate_limiter.time.monotonic",
            side_effect=fake_monotonic,
        ), patch(
            "scrapers.common.rate_limiter.time.sleep",
            side_effect=fake_sleep,
        ):
            limiter = RateLimiter(min_delay=0.3)
            start = current_time["value"]
            limiter.wait()
            limiter.wait()
            elapsed = current_time["value"] - start
        assert elapsed == pytest.approx(0.3, abs=1e-6), "Should enforce 0.3s between calls"

    def test_first_call_is_immediate(self):
        current_time, fake_monotonic, fake_sleep = _make_fake_time()
        with patch(
            "scrapers.common.rate_limiter.time.monotonic",
            side_effect=fake_monotonic,
        ), patch(
            "scrapers.common.rate_limiter.time.sleep",
            side_effect=fake_sleep,
        ):
            limiter = RateLimiter(min_delay=0.5)
            start = current_time["value"]
            limiter.wait()
            elapsed = current_time["value"] - start
        assert elapsed == 0.0, "First call should be immediate with no enforced delay"

    def test_minimum_0_3_enforced(self):
        limiter = RateLimiter(min_delay=0.1)  # below minimum
        assert limiter.min_delay == 0.3, "Should override to 0.3s minimum"

    def test_reset(self):
        current_time, fake_monotonic, fake_sleep = _make_fake_time()
        with patch(
            "scrapers.common.rate_limiter.time.monotonic",
            side_effect=fake_monotonic,
        ), patch(
            "scrapers.common.rate_limiter.time.sleep",
            side_effect=fake_sleep,
        ):
            limiter = RateLimiter(min_delay=1.0)
            limiter.wait()  # first call
            limiter.reset()
            start = current_time["value"]
            limiter.wait()  # should be immediate after reset
            elapsed = current_time["value"] - start
        assert elapsed == 0.0, "Call after reset should be immediate"
