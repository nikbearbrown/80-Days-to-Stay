import asyncio
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, BrowserContext

# ── Config ────────────────────────────────────────────────────────────────────

INPUT_CSV = "companies.csv"
OUTPUT_CSV = "companies_with_emails.csv"
WEBSITE_COL = "website"
CONCURRENCY = 10  # simultaneous browser pages (keep lower with Playwright)
TIMEOUT = 15_000  # ms per page navigation
USER_AGENT = "Mozilla/5.0 (compatible; EmailScraper/1.0)"

CONTACT_PATHS = [
    "",
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/team",
    "/people",
    "/reach-us",
    "/get-in-touch",
    "/support",
]

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE
)
IGNORED_DOMAINS = {"sentry.io", "wixpress.com", "example.com", "domain.com"}

# ── Helpers ───────────────────────────────────────────────────────────────────


def normalize_url(url: str) -> str | None:
    url = url.strip()
    if not url or url.lower() in ("n/a", "none", "-"):
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else None


def extract_emails(html: str, base_domain: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    raw = set(EMAIL_RE.findall(text))

    for tag in soup.select("a[href^='mailto:']"):
        href = tag["href"].replace("mailto:", "").split("?")[0].strip()
        if EMAIL_RE.match(href):
            raw.add(href)

    filtered = []
    for email in raw:
        domain = email.split("@")[-1].lower()
        if domain in IGNORED_DOMAINS or any(
            domain.endswith(d) for d in IGNORED_DOMAINS
        ):
            continue
        if base_domain in domain or domain in base_domain:
            filtered.insert(0, email)
        else:
            filtered.append(email)

    return filtered


async def scrape_company(context: BrowserContext, base_url: str) -> list[str]:
    base_domain = urlparse(base_url).netloc.lstrip("www.")
    emails: list[str] = []
    page = await context.new_page()

    try:
        for path in CONTACT_PATHS:
            url = urljoin(base_url, path)
            try:
                await page.goto(url, timeout=TIMEOUT, wait_until="domcontentloaded")
                # Wait briefly for any lazy-rendered content
                await page.wait_for_timeout(1000)
                html = await page.content()
                found = extract_emails(html, base_domain)
                for e in found:
                    if e not in emails:
                        emails.append(e)
            except Exception:
                continue

            if emails:
                break
    finally:
        await page.close()

    return emails


# ── Main ──────────────────────────────────────────────────────────────────────


async def main():
    input_path = Path(INPUT_CSV)
    output_path = Path(OUTPUT_CSV)

    with input_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if WEBSITE_COL not in fieldnames:
        sys.exit(f"Column '{WEBSITE_COL}' not found. Available: {fieldnames}")

    out_fields = fieldnames + (["emails"] if "emails" not in fieldnames else [])

    # Resume support
    processed: set[int] = set()
    if output_path.exists():
        with output_path.open(newline="", encoding="utf-8") as f:
            for i, _ in enumerate(csv.DictReader(f)):
                processed.add(i)
        print(f"Resuming — {len(processed)} rows already done.")
        out_file = output_path.open("a", newline="", encoding="utf-8")
        writer = csv.DictWriter(out_file, fieldnames=out_fields)
    else:
        out_file = output_path.open("w", newline="", encoding="utf-8")
        writer = csv.DictWriter(out_file, fieldnames=out_fields)
        writer.writeheader()

    sem = asyncio.Semaphore(CONCURRENCY)

    async def process_row(i: int, row: dict, context: BrowserContext):
        if i in processed:
            return
        async with sem:
            url = normalize_url(row.get(WEBSITE_COL, ""))
            if url:
                emails = await scrape_company(context, url)
            else:
                emails = []
            row["emails"] = "; ".join(emails)
            writer.writerow(row)
            out_file.flush()

            status = f"✓ {emails[0]}" if emails else "✗ none"
            print(f"[{i+1}/{len(rows)}] {url or 'SKIP'} → {status}")

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            java_script_enabled=True,
            ignore_https_errors=True,
        )
        # Block images/fonts/media to speed things up
        await context.route(
            "**/*",
            lambda route: (
                route.abort()
                if route.request.resource_type
                in ("image", "media", "font", "stylesheet")
                else route.continue_()
            ),
        )

        await asyncio.gather(
            *[process_row(i, row, context) for i, row in enumerate(rows)]
        )

        await context.close()
        await browser.close()

    out_file.close()
    print(f"\nDone. Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
