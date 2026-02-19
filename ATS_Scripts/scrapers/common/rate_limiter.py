"""
Rate limiter for respectful scraping across all ATS platforms.

Usage:
    from scrapers.common.rate_limiter import RateLimiter

    limiter = RateLimiter(min_delay=0.5)
    for url in urls:
        limiter.wait()
        response = requests.get(url)
"""

import time
import threading
from .config import DELAY_BETWEEN_REQUESTS
from .logger import get_logger

logger = get_logger("rate_limiter", file=False)


class RateLimiter:
    """
    Thread-safe rate limiter that enforces a minimum delay between requests.

    Attributes:
        min_delay: Minimum seconds between requests.
    """

    def __init__(self, min_delay: float = DELAY_BETWEEN_REQUESTS):
        """
        Initialize rate limiter.

        Args:
            min_delay: Minimum delay in seconds between requests
                       (default from config, minimum 0.3 per project standards).
        """
        if min_delay < 0.3:
            logger.warning(
                "min_delay %.2f is below project minimum 0.3s — overriding to 0.3s",
                min_delay,
            )
            min_delay = 0.3

        self.min_delay = min_delay
        self._last_request_time: float = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        """
        Block until enough time has passed since the last request.
        Thread-safe.
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < self.min_delay:
                sleep_time = self.min_delay - elapsed
                time.sleep(sleep_time)
            self._last_request_time = time.monotonic()

    def reset(self) -> None:
        """Reset the timer (e.g., when switching to a new ATS domain)."""
        with self._lock:
            self._last_request_time = 0.0
