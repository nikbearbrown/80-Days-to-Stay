# Email Scraper — 80 Days to Stay

Closes [Issue #9](https://github.com/nikbearbrown/80-Days-to-Stay/issues/9).

Scrapes **publicly listed email addresses** from funded startup websites using Playwright, so international students can reach founders directly — bypassing the ATS filters that auto-reject them before a human ever sees their application.

---

## The problem it solves

The rest of the pipeline identifies *which* companies have money to hire, historically sponsor H1B, and are actively hiring. But knowing that doesn't help a candidate if the only path in is an ATS portal that auto-rejects anyone who checks "requires sponsorship."

This scraper adds the missing piece: **direct contact information**. A cold email to `founders@company.com` explaining that you're on OPT, need no sponsorship for 2–3 years, and save the company 7.65% in FICA taxes is a fundamentally different conversation than an ATS application.

---

## What it does

1. Reads the master company CSV (`80_Days_CSV/mapped_student_employment_targets_v3.csv`)
2. Launches a real Chromium browser (headless) via Playwright
3. For each company, visits up to 4 pages:
   - Homepage
   - `/contact` and `/contact-us`
   - `/about` and `/about-us`
   - `/team`
4. Extracts emails two ways:
   - `mailto:` href links — most reliable signal
   - Regex over visible page text — catches plain-text emails in paragraphs, footers, etc.
5. Filters out false positives: `noreply@`, `test@`, `example.com`, file extension artifacts
6. Writes each result to the output CSV **immediately** after each company — safe to kill and resume

---

## Why Playwright instead of requests

Most startup contact pages are JavaScript-rendered. A plain `requests.get()` returns the raw HTML shell — the actual content (including email addresses) is injected by React/Vue after the page loads. Playwright runs a real browser, waits for the DOM to settle, then reads what a human would see.

---

## Setup

```bash
cd ATS_Scripts
pip install -r requirements.txt
playwright install chromium
```

---

## Usage

```bash
# Full run — all companies in master CSV
python3 scrapers/email_scraper/scraper.py \
  --input ../80_Days_CSV/mapped_student_employment_targets_v3.csv

# Test run — first 20 companies only
python3 scrapers/email_scraper/scraper.py \
  --input ../80_Days_CSV/mapped_student_employment_targets_v3.csv \
  --limit 20

# Custom output location
python3 scrapers/email_scraper/scraper.py \
  --input ../80_Days_CSV/mapped_student_employment_targets_v3.csv \
  --output ../data/company_emails.csv

# Resume an interrupted run — skips companies already in output CSV
python3 scrapers/email_scraper/scraper.py \
  --input ../80_Days_CSV/mapped_student_employment_targets_v3.csv \
  --resume

# Debug — shows the browser window so you can see what it's doing
python3 scrapers/email_scraper/scraper.py \
  --input ../80_Days_CSV/mapped_student_employment_targets_v3.csv \
  --limit 5 --no-headless
```

---

## Output

Results are written to `<input_stem>_emails.csv` by default (next to the input file).

| Column | Description |
|--------|-------------|
| `company_name` | Company name from input |
| `website` | Website from input |
| `emails_found` | Comma-separated emails found (empty if none) |
| `pages_scraped` | Pipe-separated list of URLs visited |
| `status` | `success` / `no_emails` / `unreachable` / `no_url` |
| `scraped_at` | ISO 8601 UTC timestamp |

### Example output

```
company_name,website,emails_found,pages_scraped,status,scraped_at
0XCORD INC,0xcord.com,contact@0xcord.com,https://0xcord.com | https://0xcord.com/contact,success,2026-10-18T17:58:15Z
$AVY INC,avy.com,,https://avy.com | https://avy.com/contact,no_emails,2026-10-18T17:58:13Z
```

### Console output

```
📋 Loaded 1024 companies from mapped_student_employment_targets_v3.csv

🔍 Scraping emails from 1024 companies...

[1/1024] 0XCORD INC... ✅ 1 email(s): contact@0xcord.com
[2/1024] $AVY INC... 📭 no emails found
[3/1024] SLOW SITE INC... ❌ unreachable

==================================================
SUMMARY
==================================================
✅ Emails found:   287
📭 No emails:      601
❌ Errors:         136
⏭️  Skipped:        0

📁 Output saved to: mapped_student_employment_targets_v3_emails.csv
```

---

## Realistic expectations on the full dataset

Out of ~1,000 companies you can expect roughly:
- **250–300** with at least one email (startups that list `hello@`, `founders@`, `info@` publicly)
- **500–600** with no emails found (JS contact forms, Calendly links, no contact page)
- **100–150** unreachable (dead domains, heavy bot protection, slow load times)

The 250–300 with emails are the actionable leads — direct contacts that bypass the ATS entirely.

---

## Configuration

All settings are at the top of `scraper.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `CONTACT_PATHS` | `/contact`, `/about`, `/team`, ... | URL paths tried on each domain |
| `MAX_PAGES_PER_COMPANY` | `4` | Max pages visited per company |
| `PAGE_TIMEOUT_MS` | `12000` | Page load timeout (ms) |
| `DELAY_BETWEEN_COMPANIES` | `1.0` | Seconds between companies |
| `EMAIL_BLACKLIST` | `noreply`, `test`, ... | Local-part substrings to filter |
| `DOMAIN_BLACKLIST` | `example.com`, `sentry.io`, ... | Domains always discarded |

---

## How it fits into the pipeline

```
SEC Form D data → Master company CSV → ATS scrapers (jobs) → Email scraper (contacts)
                                                                        ↓
                                                          Candidate cold-emails founder
                                                          (no ATS, no auto-reject)
```

The email scraper is the last mile — turning a research database into a direct outreach tool.

---

## Files

```
email_scraper/
├── scraper.py   — main script (standalone, no external package dependencies)
└── README.md    — this file
```

**Built by:** Tanmay Sangam ([@TanmaySangam18](https://github.com/TanmaySangam18))  
**Addresses:** [Issue #9](https://github.com/nikbearbrown/80-Days-to-Stay/issues/9)
