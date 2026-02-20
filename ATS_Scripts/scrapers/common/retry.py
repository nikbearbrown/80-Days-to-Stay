"""
Retry logic with exponential backoff for HTTP requests.

Usage:
    from scrapers.common.retry import retry_request

    response = retry_request("https://api.example.com/jobs", timeout=10)
"""

import time
from typing import Optional, Dict, Any

import requests

from .config import (
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF_FACTOR,
    RETRYABLE_STATUS_CODES,
    USER_AGENT,
)
from .logger import get_logger

logger = get_logger("retry", file=False)


def retry_request(
    url: str,
    method: str = "GET",
    max_retries: int = MAX_RETRIES,
    timeout: int = REQUEST_TIMEOUT,
    backoff_factor: float = RETRY_BACKOFF_FACTOR,
    retryable_status_codes: Optional[list] = None,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Optional[requests.Response]:
    """
    Make an HTTP request with automatic retry and exponential backoff.

    Args:
        url: The URL to request.
        method: HTTP method (default: "GET").
        max_retries: Maximum number of retry attempts.
        timeout: Request timeout in seconds.
        backoff_factor: Multiplier for exponential backoff
                        (wait = backoff_factor ** attempt).
        retryable_status_codes: HTTP status codes that should trigger a retry.
        headers: Optional request headers.
        params: Optional query parameters.
        **kwargs: Additional arguments passed to requests.request().

    Returns:
        requests.Response on success or after all retries are exhausted
        (including error responses, so callers can inspect the status code).
        Returns None only if a network-level error (timeout, connection
        error, or unrecoverable exception) occurs and all retries are
        exhausted.
    """
    if retryable_status_codes is None:
        retryable_status_codes = RETRYABLE_STATUS_CODES

    if headers is None:
        headers = {}
    headers.setdefault("User-Agent", USER_AGENT)

    for attempt in range(max_retries + 1):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=timeout,
                **kwargs,
            )

            # Success
            if response.status_code < 400:
                return response

            # Non-retryable client error (e.g., 404)
            if response.status_code not in retryable_status_codes:
                logger.warning(
                    "Non-retryable status %d for %s", response.status_code, url
                )
                return response

            # Retryable server error
            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    "Status %d for %s — retrying in %.1fs (attempt %d/%d)",
                    response.status_code,
                    url,
                    wait_time,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    "All %d retries exhausted for %s (last status: %d)",
                    max_retries,
                    url,
                    response.status_code,
                )
                return response

        except requests.exceptions.Timeout:
            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    "Timeout for %s — retrying in %.1fs (attempt %d/%d)",
                    url,
                    wait_time,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(wait_time)
            else:
                logger.error("All %d retries exhausted for %s (timeout)", max_retries, url)
                return None

        except requests.exceptions.ConnectionError:
            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    "Connection error for %s — retrying in %.1fs (attempt %d/%d)",
                    url,
                    wait_time,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    "All %d retries exhausted for %s (connection error)",
                    max_retries,
                    url,
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error("Unrecoverable request error for %s: %s", url, e)
            return None

    return None
