"""
Tests for the rate limiter.
Run: pytest tests/test_rate_limiter.py -v
"""

import time
from scrapers.common.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_enforces_minimum_delay(self):
        limiter = RateLimiter(min_delay=0.3)
        start = time.monotonic()
        limiter.wait()
        limiter.wait()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.3, "Should enforce at least 0.3s between calls"

    def test_first_call_is_immediate(self):
        limiter = RateLimiter(min_delay=0.5)
        start = time.monotonic()
        limiter.wait()
        elapsed = time.monotonic() - start
        assert elapsed < 0.1, "First call should be nearly immediate"

    def test_minimum_0_3_enforced(self):
        limiter = RateLimiter(min_delay=0.1)  # below minimum
        assert limiter.min_delay == 0.3, "Should override to 0.3s minimum"

    def test_reset(self):
        limiter = RateLimiter(min_delay=1.0)
        limiter.wait()  # first call
        limiter.reset()
        start = time.monotonic()
        limiter.wait()  # should be immediate after reset
        elapsed = time.monotonic() - start
        assert elapsed < 0.1, "Call after reset should be nearly immediate"
