# Email Scraper

Scrapes publicly listed email addresses from company websites using Playwright. Takes a CSV of companies as input, visits each website and common contact pages, and writes found emails back to a new CSV in real time.

## Requirements

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuration

Edit the constants at the top of the script:

| Variable      | Default                     | Description                 |
| ------------- | --------------------------- | --------------------------- |
| `INPUT_CSV`   | `companies.csv`             | Path to your input file     |
| `OUTPUT_CSV`  | `companies_with_emails.csv` | Path for results            |
| `WEBSITE_COL` | `website`                   | Column name containing URLs |
| `CONCURRENCY` | `10`                        | Simultaneous browser pages  |
| `TIMEOUT`     | `15000`                     | Per-page timeout in ms      |

## Input Format

A CSV file with at least one column containing company website URLs. URLs can be bare domains (`company.com`) — the script normalizes them automatically.

## Usage

```bash
python scraper.py
```

Results are written to the output CSV row by row as they complete. If the script is interrupted, re-running it will skip already-processed rows automatically.

## Output

The original CSV with an added `emails` column. Multiple emails found on the same site are separated by `;`.

## Notes

- Images, fonts, and stylesheets are blocked to speed up page loads
- The scraper checks the homepage plus 9 common contact paths per site (`/contact`, `/about`, `/team`, etc.)
- Emails are filtered to prefer addresses matching the company's own domain
