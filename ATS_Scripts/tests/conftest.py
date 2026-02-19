"""
Shared pytest fixtures for ATS scraper tests.
"""

import pytest
import sys
from pathlib import Path

# Ensure the ATS_Scripts directory is on the Python path
# so that `from scrapers.common import ...` works in tests
ats_scripts_dir = Path(__file__).parent.parent
if str(ats_scripts_dir) not in sys.path:
    sys.path.insert(0, str(ats_scripts_dir))


@pytest.fixture
def sample_valid_job():
    """A valid job record conforming to the unified schema."""
    return {
        "job_id": "12345",
        "title": "Software Engineer",
        "company_name": "Acme Corp",
        "company_slug": "acmecorp",
        "ats_source": "greenhouse",
        "source_url": "https://boards.greenhouse.io/acmecorp/jobs/12345",
        "apply_url": "https://boards.greenhouse.io/acmecorp/jobs/12345",
        "location": "San Francisco, CA",
        "department": "Engineering",
        "employment_type": "Full-time",
        "date_posted": "2025-02-15T00:00:00+00:00",
        "description_text": "We are looking for a software engineer...",
        "description_html": "<p>We are looking for a software engineer...</p>",
        "salary_range": "",
        "metadata": {
            "scraped_at": "2025-02-16T12:00:00+00:00",
            "scraper_version": "1.0.0",
            "extraction_status": "success",
            "raw_response_hash": "abc123def456",
        },
    }
