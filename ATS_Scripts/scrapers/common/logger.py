"""
Centralized logging configuration for all ATS scrapers.
Replaces print() statements with structured logging.

Usage:
    from scrapers.common.logger import get_logger
    logger = get_logger("greenhouse")
    logger.info("Found %d jobs for %s", job_count, company)
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: str = "logs",
    console: bool = True,
    file: bool = True,
) -> logging.Logger:
    """
    Create a configured logger for a scraper module.

    Args:
        name: Logger name, typically the ATS platform name
              (e.g., "greenhouse", "lever").
        level: Logging level (default: INFO).
        log_dir: Directory for log files (default: "logs").
        console: Whether to log to console (default: True).
        file: Whether to log to file (default: True).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(f"ats_scraper.{name}")

    # Clear existing handlers so the logger is fully reconfigured
    # with the current console/file/level settings on every call.
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = log_path / f"{name}_{today}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
