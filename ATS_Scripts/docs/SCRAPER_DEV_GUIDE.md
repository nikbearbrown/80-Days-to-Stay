# Scraper Development Guide

How to build a new ATS scraper using the two-phase template.

## Prerequisites

```bash
cd ATS_Scripts
pip install -r requirements.txt
```

## Step-by-Step

### 1. Start with your scraper directory

Your scraper directory already has an `__init__.py` package marker. You need to create:
```
scrapers/{ats_name}/
    __init__.py       # Already set up
    config.py         # Create: ATS_NAME, URL patterns, override global defaults
    discovery.py      # Create: implement discover()
    extraction.py     # Create: implement extract() + transform_to_unified_schema()
    README.md         # Create: document your work as you go
```

### 2. Research your ATS

Before writing code, answer these questions:
- Is there a public API? What's the endpoint format?
- How are career pages structured? (URL patterns)
- How is pagination handled?
- What data is available on listing vs. detail pages?
- Are pages JS-rendered? (If yes, you may need `playwright`)

### 3. Implement discovery.py

This is Phase 1: find companies on your ATS and harvest job URLs.

```python
from scrapers.common.logger import get_logger
from scrapers.common.normalize import normalize_company_name, read_companies_from_file
from scrapers.common.rate_limiter import RateLimiter
from scrapers.common.retry import retry_request
from .config import ATS_NAME, BASE_API_URL, DELAY_BETWEEN_REQUESTS

logger = get_logger(ATS_NAME)

def discover(companies, output_dir):
    limiter = RateLimiter(min_delay=DELAY_BETWEEN_REQUESTS)

    for company in companies:
        slug = normalize_company_name(company)
        limiter.wait()

        # Make your API call / scrape the page
        response = retry_request(url)

        # Process response...
        # Write to discovered_jobs.csv and live_endpoints.csv
```

**Output files:**
- `discovered_jobs.csv` — columns: `company_name`, `company_slug`, `job_id`, `job_url`, `title`
- `live_endpoints.csv` — columns: `company_name`, `company_slug`, `endpoint_url`, `job_count`
- `discovery_summary.json` — run metadata

Reference: `script_for_reference/greenhouse_scraper.py` for a working example of Greenhouse API usage.

### 4. Implement extraction.py

This is Phase 2: fetch full details and output the unified schema.

```python
def transform_to_unified_schema(job, company_name, company_slug):
    return {
        "job_id": ...,
        "title": ...,
        "company_name": company_name,
        "company_slug": company_slug,
        "ats_source": ATS_NAME,
        "source_url": ...,
        "apply_url": ...,
        "location": ...,
        "department": ...,
        "employment_type": ...,   # "Full-time", "Part-time", "Contract", "Intern", or ""
        "date_posted": ...,       # ISO 8601 format
        "description_text": ...,
        "description_html": ...,
        "salary_range": ...,
        "metadata": {
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "scraper_version": SCRAPER_VERSION,
            "extraction_status": "success",  # or "error" or "partial"
            "raw_response_hash": hashlib.md5(...).hexdigest(),
        },
    }
```

**Key points:**
- Always validate output: `validate_job_record(record)`
- Save progress periodically for resumability
- Handle errors gracefully (log and continue, don't crash)

Reference: `script_for_reference/greenhouse_scraper.py` and `script_for_reference/lever_scraper.py` for working examples of API response handling.

### 5. Validate output

```python
from scrapers.common.schema_validator import validate_job_record, validate_batch

# Single record
is_valid, errors = validate_job_record(job)

# Full batch
report = validate_batch(all_jobs, strict=True)
print(f"Pass rate: {report['pass_rate']}")
```

### 6. Test against 20+ companies

Run your scraper against at least 20 companies and verify:
- [ ] Discovery finds active companies
- [ ] Extraction produces valid JSON
- [ ] Output passes schema validation
- [ ] Rate limiting works (check delay between requests)
- [ ] Error handling works (test with invalid companies)
- [ ] Resume capability works (stop and restart extraction)

### 7. Create a PR

```bash
git checkout -b {your_name}/feature-{ats_name}-scraper
git add ATS_Scripts/scrapers/{ats_name}/
git commit -m "[{ATS_NAME}] Implement discovery and extraction"
git push -u origin {your_name}/feature-{ats_name}-scraper
# Create PR on GitHub, tag @abhinavpklg as reviewer
```

## Shared Utilities Reference

| Module | Import | Use for |
|--------|--------|---------|
| Logger | `from scrapers.common.logger import get_logger` | Structured logging |
| Normalizer | `from scrapers.common.normalize import normalize_company_name` | Company slug generation |
| Rate Limiter | `from scrapers.common.rate_limiter import RateLimiter` | Respectful request throttling |
| Retry | `from scrapers.common.retry import retry_request` | HTTP with exponential backoff |
| Validator | `from scrapers.common.schema_validator import validate_job_record, validate_batch` | Output validation |
| Config | `from scrapers.common.config import *` | Global defaults |
| Timestamp | `from scrapers.common.normalize import epoch_ms_to_iso8601` | Convert epoch ms to ISO 8601 |

## Tier-Specific Notes

### Tier 1 (API-based: Greenhouse, Lever, Ashby, SmartRecruiters)
- Use `retry_request()` for HTTP calls
- JSON responses — straightforward parsing
- Focus on pagination handling

### Tier 2 (HTML scraping: BambooHR, JazzHR, Workable)
- Use `beautifulsoup4` + `lxml` for parsing
- Check for JSON-LD structured data before scraping HTML
- Handle inconsistent HTML structures across companies

### Tier 3 (JS-heavy: Workday, iCIMS, Taleo)
- Try to find hidden JSON APIs first (browser network tab)
- Fall back to `playwright` for browser automation
- Use longer delays (2.0s+) and higher retry counts
- These are the hardest — budget extra R&D time
