# Shared Utilities — `scrapers/common/`

Common modules used by all ATS scrapers. Import from here instead of duplicating code.

## Modules

| Module | Purpose | Key Functions/Classes |
|--------|---------|----------------------|
| `config.py` | Global defaults (timeouts, delays, retries) | Constants only |
| `logger.py` | Structured logging (replaces `print()`) | `get_logger(name)` |
| `normalize.py` | Company name normalization, file reading | `normalize_company_name()`, `read_companies_from_file()`, `epoch_ms_to_iso8601()` |
| `rate_limiter.py` | Thread-safe request throttling | `RateLimiter(min_delay)` |
| `retry.py` | HTTP requests with exponential backoff | `retry_request(url)` |
| `schema_validator.py` | Validate output against unified schema | `validate_job_record()`, `validate_batch()` |

## Quick Start

```python
from scrapers.common import (
    get_logger,
    normalize_company_name,
    RateLimiter,
    retry_request,
    validate_job_record,
    validate_batch,
)

logger = get_logger("greenhouse")
limiter = RateLimiter(min_delay=0.5)

slug = normalize_company_name("Databricks, Inc.")  # -> "databricks"

limiter.wait()
response = retry_request(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")

# After building your job record:
is_valid, errors = validate_job_record(job_record)
```

## Overriding Defaults

Each scraper can override global config values in its own `config.py`:

```python
# scrapers/workday/config.py
from scrapers.common.config import *

# Override for Workday (slower, more cautious)
DELAY_BETWEEN_REQUESTS = 2.0
MAX_RETRIES = 5
REQUEST_TIMEOUT = 30
```
