"""
Global configuration defaults for all ATS scrapers.
Individual scrapers can override these in their own config.py.
"""

# --- HTTP Request Settings ---
REQUEST_TIMEOUT = 10          # seconds
DELAY_BETWEEN_REQUESTS = 0.5  # seconds (minimum 0.3 per project standards)
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2      # exponential backoff multiplier
RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504]

# --- Pagination ---
MAX_PAGES = 100               # safety limit to prevent infinite pagination
PAGE_SIZE = 100               # default page size where applicable

# --- Output ---
SAVE_INTERVAL = 100           # save progress every N jobs (for resumability)
OUTPUT_ENCODING = "utf-8"

# --- Scraper Metadata ---
SCRAPER_VERSION = "1.0.0"

# --- User Agent ---
USER_AGENT = (
    "80DaysToStay-JobScraper/1.0 "
    "(+https://github.com/nikbearbrown/80-Days-to-Stay; "
    "research project; respectful scraping)"
)

# --- File Encodings to Try ---
FILE_ENCODINGS = [
    "utf-8", "utf-8-sig", "utf-16",
    "utf-16-le", "utf-16-be", "latin-1"
]

# --- Company Name Suffixes to Strip ---
# IMPORTANT: Longer patterns MUST come before shorter ones
# (e.g., "Corporation" before "Corp", "Company" before "Co")
# All patterns are anchored to end-of-string ($) to avoid partial matches
# (e.g., "Co" in "Cola" should NOT be stripped)
COMPANY_SUFFIXES = [
    r',?\s+Ltd\s+Liability\s+Co\.?$',
    r',?\s+Liability\s+Co\.?$',
    r',?\s+Corporation$',
    r',?\s+Corp\.?$',
    r',?\s+Company$',
    r',?\s+Co\.?$',
    r',?\s+Limited$',
    r',?\s+Ltd\.?$',
    r',?\s+LTD\.?$',
    r',?\s+L\.L\.C\.?$',
    r',?\s+LLC\.?$',
    r',?\s+Inc\.?$',
    r',?\s+L\.P\.?$',
    r',?\s+LP\.?$',
    r',?\s+PLC\.?$',
]
