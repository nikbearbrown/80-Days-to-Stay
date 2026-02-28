"""
Company name normalization and file-reading utilities.
Extracted from professor's reference scripts to avoid duplication.

Usage:
    from scrapers.common.normalize import normalize_company_name, read_companies_from_file

    slug = normalize_company_name("Databricks, Inc.")  # -> "databricks"
    companies = read_companies_from_file("companies.txt")
"""

import re
from datetime import datetime, timezone
from typing import List

from .config import COMPANY_SUFFIXES, FILE_ENCODINGS
from .logger import get_logger

logger = get_logger("normalize", file=False)


def normalize_company_name(name: str) -> str:
    """
    Convert a company name to a URL-safe slug for ATS lookups.

    Strips common legal suffixes (Inc., LLC, Corp., etc.),
    removes special characters, and lowercases.

    Args:
        name: Raw company name (e.g., "Databricks, Inc.").

    Returns:
        URL-safe slug (e.g., "databricks").
    """
    cleaned = name.strip()

    # Loop until no more suffixes match (handles chained suffixes
    # like "Mega Corporation Inc." → "Mega Corporation" → "Mega")
    changed = True
    while changed:
        changed = False
        for suffix in COMPANY_SUFFIXES:
            result = re.sub(suffix, "", cleaned, flags=re.IGNORECASE)
            if result != cleaned:
                cleaned = result
                changed = True

    # Remove commas, periods, spaces, hyphens, ampersands, apostrophes
    cleaned = cleaned.strip()
    cleaned = re.sub(r"[,.\s\-&\']", "", cleaned)

    return cleaned.lower()


def read_companies_from_file(filepath: str) -> List[str]:
    """
    Read company names from a text file, one per line.
    Tries multiple encodings to handle various file formats.

    Args:
        filepath: Path to the company list file.

    Returns:
        List of company name strings, or an empty list if the file
        contains no non-blank lines.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file cannot be decoded with any supported encoding.
    """
    for encoding in FILE_ENCODINGS:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                companies = [line.strip() for line in f if line.strip()]
                # Successfully decoded — return even if empty
                if companies:
                    logger.info(
                        "Read %d companies from %s (encoding: %s)",
                        len(companies),
                        filepath,
                        encoding,
                    )
                else:
                    logger.warning("File %s is empty (no non-blank lines)", filepath)
                return companies
        except (UnicodeDecodeError, UnicodeError):
            continue
        except FileNotFoundError:
            logger.error("File not found: %s", filepath)
            raise

    logger.error("Could not decode file %s with any supported encoding", filepath)
    raise ValueError(f"Could not decode file {filepath} with any supported encoding")


def epoch_ms_to_iso8601(epoch_ms: int) -> str:
    """
    Convert epoch milliseconds (e.g., from Lever API) to ISO 8601 string.

    Args:
        epoch_ms: Unix timestamp in milliseconds.

    Returns:
        ISO 8601 formatted datetime string.
    """
    dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    return dt.isoformat()
