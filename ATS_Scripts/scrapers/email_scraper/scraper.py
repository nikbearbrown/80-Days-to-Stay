#!/usr/bin/env python3
"""
Email Scraper — 80 Days to Stay
Scrapes publicly listed email addresses from company websites using Playwright.
Takes a CSV of companies as input, visits each website and common contact pages,
and writes found emails back to a new CSV in real time.

Usage:
    python3 scraper.py --input ../../80_Days_CSV/mapped_student_employment_targets_v3.csv
    python3 scraper.py --input companies.csv --output emails.csv --limit 20
    python3 scraper.py --input companies.csv --resume
"""

import argparse
import csv
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

# ── Configuration ─────────────────────────────────────────────────────────────

CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/team",
    "/support",
]

MAX_PAGES_PER_COMPANY = 4
PAGE_TIMEOUT_MS = 12000
DELAY_BETWEEN_COMPANIES = 1.0

EMAIL_BLACKLIST = {
    "noreply", "no-reply", "donotreply", "example",
    "test", "placeholder", "yourname", "username",
}

DOMAIN_BLACKLIST = {
    "example.com", "example.org", "sentry.io",
    "w3.org", "schema.org", "github.com",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

OUTPUT_COLUMNS = ["company_name", "website", "emails_found", "pages_scraped", "status", "scraped_at"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def normalize_url(raw):
    raw = raw.strip().rstrip("/")
    if not raw or raw.lower() in {"nan", "n/a", "-", ""}:
        return None
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    if not urlparse(raw).netloc:
        return None
    return raw


def is_valid_email(addr):
    local, _, domain = addr.partition("@")
    if domain in DOMAIN_BLACKLIST:
        return False
    if any(bl in local for bl in EMAIL_BLACKLIST):
        return False
    return True


def extract_emails(page):
    found = set()
    try:
        hrefs = page.eval_on_selector_all(
            "a[href^='mailto:']",
            "els => els.map(e => e.getAttribute('href'))",
        )
        for href in hrefs:
            addr = href.replace("mailto:", "").split("?")[0].strip().lower()
            if EMAIL_RE.match(addr):
                found.add(addr)
    except Exception:
        pass
    try:
        text = page.inner_text("body")
        for match in EMAIL_RE.findall(text):
            found.add(match.lower())
    except Exception:
        pass
    return found


# ── Core scrape logic ─────────────────────────────────────────────────────────

def scrape_company(browser, base_url):
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        ignore_https_errors=True,
    )
    page = context.new_page()
    page.set_default_timeout(PAGE_TIMEOUT_MS)

    all_emails = set()
    pages_scraped = []

    urls = [base_url] + [urljoin(base_url, p) for p in CONTACT_PATHS]
    urls = urls[:MAX_PAGES_PER_COMPANY]

    for url in urls:
        try:
            resp = page.goto(url, wait_until="domcontentloaded")
            if resp and resp.status < 400:
                emails = extract_emails(page)
                all_emails.update(emails)
                pages_scraped.append(url)
        except Exception:
            pass

    context.close()

    valid = {e for e in all_emails if is_valid_email(e)}

    if not pages_scraped:
        status = "unreachable"
    elif not valid:
        status = "no_emails"
    else:
        status = "success"

    return valid, pages_scraped, status


# ── CSV I/O ───────────────────────────────────────────────────────────────────

def read_companies(input_path, limit=None):
    encodings = ["utf-8", "utf-8-sig", "utf-16", "latin-1"]
    for enc in encodings:
        try:
            rows = []
            with open(input_path, encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                if "company_name" not in (reader.fieldnames or []):
                    print(f"❌ Missing 'company_name' column. Got: {reader.fieldnames}")
                    sys.exit(1)
                if "website" not in (reader.fieldnames or []):
                    print(f"❌ Missing 'website' column. Got: {reader.fieldnames}")
                    sys.exit(1)
                for row in reader:
                    rows.append(row)
                    if limit and len(rows) >= limit:
                        break
            print(f"📋 Loaded {len(rows)} companies from {input_path}")
            return rows
        except (UnicodeDecodeError, UnicodeError):
            continue
    print(f"❌ Could not read {input_path}")
    sys.exit(1)


def already_scraped(output_path):
    done = set()
    if output_path.exists():
        with open(output_path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                done.add(row.get("company_name", "").strip())
    return done


# ── Main pipeline ─────────────────────────────────────────────────────────────

def process_companies(input_path, output_path, limit=None, delay=DELAY_BETWEEN_COMPANIES, resume=False, headless=True):
    companies = read_companies(input_path, limit)

    done = set()
    if resume:
        done = already_scraped(output_path)
        print(f"⏭️  Resuming — skipping {len(done)} already scraped")

    mode = "a" if resume and output_path.exists() else "w"
    out_file = open(output_path, mode=mode, encoding="utf-8", newline="")
    writer = csv.DictWriter(out_file, fieldnames=OUTPUT_COLUMNS)
    if mode == "w":
        writer.writeheader()
        out_file.flush()

    results = {"success": 0, "no_email": 0, "errors": 0, "skipped": 0}
    total = len(companies)

    print(f"\n🔍 Scraping emails from {total} companies...\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)

        for i, row in enumerate(companies, start=1):
            name = row.get("company_name", "").strip()
            raw_url = row.get("website", "").strip()

            if resume and name in done:
                results["skipped"] += 1
                continue

            base_url = normalize_url(raw_url)

            if not base_url:
                print(f"[{i}/{total}] ⚠️  {name} — no valid URL, skipping")
                writer.writerow({
                    "company_name": name, "website": raw_url,
                    "emails_found": "", "pages_scraped": "",
                    "status": "no_url",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                })
                out_file.flush()
                results["skipped"] += 1
                continue

            print(f"[{i}/{total}] {name}...", end=" ", flush=True)

            emails, pages_scraped, status = scrape_company(browser, base_url)

            if status == "success":
                print(f"✅ {len(emails)} email(s): {', '.join(sorted(emails))}")
                results["success"] += 1
            elif status == "no_emails":
                print("📭 no emails found")
                results["no_email"] += 1
            else:
                print(f"❌ {status}")
                results["errors"] += 1

            writer.writerow({
                "company_name": name,
                "website": raw_url,
                "emails_found": ", ".join(sorted(emails)),
                "pages_scraped": " | ".join(pages_scraped),
                "status": status,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })
            out_file.flush()

            if i < total:
                time.sleep(delay)

        browser.close()

    out_file.close()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"✅ Emails found:   {results['success']}")
    print(f"📭 No emails:      {results['no_email']}")
    print(f"❌ Errors:         {results['errors']}")
    print(f"⏭️  Skipped:        {results['skipped']}")
    print(f"\n📁 Output saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape publicly listed emails from company websites.",
        epilog="""
Examples:
  python3 scraper.py --input ../../80_Days_CSV/mapped_student_employment_targets_v3.csv
  python3 scraper.py --input companies.csv --output emails.csv --limit 20
  python3 scraper.py --input companies.csv --resume
        """
    )
    parser.add_argument("-i", "--input", required=True, type=Path)
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument("-n", "--limit", type=int, default=None)
    parser.add_argument("-d", "--delay", type=float, default=DELAY_BETWEEN_COMPANIES)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--no-headless", action="store_true")
    args = parser.parse_args()

    output = args.output or args.input.parent / (args.input.stem + "_emails.csv")
    process_companies(
        input_path=args.input,
        output_path=output,
        limit=args.limit,
        delay=args.delay,
        resume=args.resume,
        headless=not args.no_headless,
    )


if __name__ == "__main__":
    main()
