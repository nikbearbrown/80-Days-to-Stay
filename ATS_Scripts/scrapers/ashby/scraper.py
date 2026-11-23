#!/usr/bin/env python3
"""
Ashby ATS Scraper — 80 Days to Stay
Finds open job listings at funded startups that use Ashby HQ via its public API.

Ashby exposes job boards at:
  https://api.ashbyhq.com/posting-api/job-board/{slug}

No auth is required. The slug is the company's Ashby board name, which is usually
a cleaned version of the company name. This scraper derives candidate slugs from
each company name and tries them in order.

Usage:
    python3 scraper.py --input ../../../80_Days_CSV/mapped_student_employment_targets_v3.csv
    python3 scraper.py --input companies.csv --output ashby_jobs.csv --limit 20
    python3 scraper.py --input companies.csv --resume
"""

import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

# ── Configuration ──────────────────────────────────────────────────────────────

ASHBY_API_BASE = "https://api.ashbyhq.com/posting-api/job-board"
REQUEST_TIMEOUT = 10
DELAY_BETWEEN_COMPANIES = 0.5   # seconds — polite to the API

OUTPUT_COLUMNS = [
    "company_name",
    "ashby_slug",
    "job_id",
    "job_title",
    "department",
    "team",
    "location",
    "employment_type",
    "is_remote",
    "compensation",
    "apply_url",
    "scraped_at",
]

SUMMARY_COLUMNS = [
    "company_name",
    "ashby_slug",
    "jobs_found",
    "status",
    "scraped_at",
]


# ── Slug derivation ────────────────────────────────────────────────────────────

def _clean(name: str) -> str:
    """Strip punctuation and lower-case."""
    return re.sub(r"[^a-z0-9\s-]", "", name.lower()).strip()


def candidate_slugs(company_name: str, website: str | None = None) -> list[str]:
    """
    Return slugs to try in priority order.
    Most Ashby slugs are '<company-name>' with spaces → hyphens.
    Some orgs use their domain prefix.
    """
    slugs: list[str] = []

    cleaned = _clean(company_name)

    # Primary: spaces → hyphens
    hyphen = re.sub(r"\s+", "-", cleaned)
    if hyphen:
        slugs.append(hyphen)

    # Secondary: no separator
    nospace = cleaned.replace(" ", "").replace("-", "")
    if nospace and nospace != hyphen:
        slugs.append(nospace)

    # Tertiary: domain prefix (e.g. "acme.io" → "acme")
    if website:
        try:
            domain = urlparse(website if "://" in website else "https://" + website).netloc
            prefix = domain.split(".")[0].lower()
            if prefix and prefix not in slugs and len(prefix) > 2:
                slugs.append(prefix)
        except Exception:
            pass

    return slugs


# ── API helpers ────────────────────────────────────────────────────────────────

_session = requests.Session()
_session.headers.update({"Accept": "application/json", "User-Agent": "80DaysToStay/1.0"})


def fetch_jobs(slug: str) -> list[dict] | None:
    """
    Call Ashby's public job-board API.
    Returns a list of job dicts, or None if the slug doesn't resolve.
    """
    url = f"{ASHBY_API_BASE}/{slug}"
    try:
        resp = _session.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            return None
        data = resp.json()
        jobs = data.get("results") or data.get("jobs") or []
        # Ashby returns [] for a valid board with no openings — treat as found
        if isinstance(jobs, list):
            return jobs
        return None
    except (requests.RequestException, json.JSONDecodeError, ValueError):
        return None


def flatten_job(company_name: str, slug: str, job: dict, ts: str) -> dict:
    """Turn one Ashby job dict into a flat output row."""
    comp = job.get("compensation") or {}
    comp_str = ""
    if comp:
        lo = comp.get("minValue")
        hi = comp.get("maxValue")
        unit = comp.get("compensationTierSummary") or comp.get("currency") or ""
        if lo and hi:
            comp_str = f"${lo:,.0f}–${hi:,.0f} {unit}".strip()
        elif lo:
            comp_str = f"${lo:,.0f}+ {unit}".strip()

    locs = [job.get("locationName") or ""]
    for sec in job.get("secondaryLocations") or []:
        loc = sec.get("locationName")
        if loc and loc not in locs:
            locs.append(loc)
    location = "; ".join(filter(None, locs))

    return {
        "company_name": company_name,
        "ashby_slug": slug,
        "job_id": job.get("id", ""),
        "job_title": job.get("title", ""),
        "department": job.get("department", ""),
        "team": (job.get("team") or {}).get("name", "") if isinstance(job.get("team"), dict) else job.get("team", ""),
        "location": location,
        "employment_type": job.get("employmentType", ""),
        "is_remote": str(job.get("isRemote", "")),
        "compensation": comp_str,
        "apply_url": job.get("applicationLink", ""),
        "scraped_at": ts,
    }


# ── CSV helpers ────────────────────────────────────────────────────────────────

def load_companies(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_done_companies(summary_path: Path) -> set[str]:
    if not summary_path.exists():
        return set()
    with open(summary_path, newline="", encoding="utf-8") as f:
        return {row["company_name"] for row in csv.DictReader(f)}


def write_row(writer: csv.DictWriter, row: dict) -> None:
    writer.writerow(row)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Ashby ATS scraper — 80 Days to Stay")
    parser.add_argument("--input", required=True, help="Master company CSV")
    parser.add_argument("--output", default="ashby_jobs.csv", help="Jobs output CSV")
    parser.add_argument("--summary", default="ashby_summary.csv", help="Per-company summary CSV")
    parser.add_argument("--limit", type=int, default=0, help="Stop after N companies (0 = all)")
    parser.add_argument("--resume", action="store_true", help="Skip companies already in summary CSV")
    args = parser.parse_args()

    input_path = Path(args.input)
    jobs_path = Path(args.output)
    summary_path = Path(args.summary)

    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    companies = load_companies(input_path)
    done = load_done_companies(summary_path) if args.resume else set()

    jobs_exists = jobs_path.exists() and args.resume
    summary_exists = summary_path.exists() and args.resume

    jobs_file = open(jobs_path, "a" if jobs_exists else "w", newline="", encoding="utf-8")
    summary_file = open(summary_path, "a" if summary_exists else "w", newline="", encoding="utf-8")

    jobs_writer = csv.DictWriter(jobs_file, fieldnames=OUTPUT_COLUMNS)
    summary_writer = csv.DictWriter(summary_file, fieldnames=SUMMARY_COLUMNS)

    if not jobs_exists:
        jobs_writer.writeheader()
    if not summary_exists:
        summary_writer.writeheader()

    total = 0
    found = 0

    try:
        for company in companies:
            name = company.get("company_name", "").strip()
            website = company.get("website", "").strip()

            if not name:
                continue
            if name in done:
                continue

            if args.limit and total >= args.limit:
                break

            total += 1
            ts = datetime.now(timezone.utc).isoformat()
            slugs = candidate_slugs(name, website)
            matched_slug: str | None = None
            jobs: list[dict] = []

            for slug in slugs:
                result = fetch_jobs(slug)
                if result is not None:
                    matched_slug = slug
                    jobs = result
                    break

            if matched_slug is not None:
                status = "found" if jobs else "found_empty_board"
                found += 1
                for job in jobs:
                    jobs_writer.writerow(flatten_job(name, matched_slug, job, ts))
                jobs_file.flush()
                print(f"  [{total}] {name} → {matched_slug} ({len(jobs)} jobs)")
            else:
                status = "not_on_ashby"
                print(f"  [{total}] {name} → not on Ashby")

            summary_writer.writerow({
                "company_name": name,
                "ashby_slug": matched_slug or "",
                "jobs_found": len(jobs),
                "status": status,
                "scraped_at": ts,
            })
            summary_file.flush()

            time.sleep(DELAY_BETWEEN_COMPANIES)

    finally:
        jobs_file.close()
        summary_file.close()

    print(f"\nDone. {total} companies checked, {found} on Ashby.")
    print(f"Jobs: {jobs_path}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
