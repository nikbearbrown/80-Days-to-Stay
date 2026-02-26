# Workable — Week 1 Research (Bharath)

## Example Company Pages Tested
- https://apply.workable.com/futureplc/
- https://apply.workable.com/tetrascience/

---

## How Job Listings Load

Job listings load dynamically via a POST request (Fetch/XHR).

When the page loads or filters are applied, the frontend sends a POST request to a public API endpoint that returns job data in JSON format.

This confirms that Workable uses a REST-style API rather than embedded static HTML.

---

## Job Listing Endpoint
 
Endpoint Pattern:
https://apply.workable.com/api/v3/accounts/{company_slug}/jobs

Example:
https://apply.workable.com/api/v3/accounts/futureplc/jobs

Request Method: POST  
Status Code: 200 OK  
Returns: JSON array of job objects  
Authentication Required: No (public endpoint accessible from browser context)

---

## Request Payload Structure

{
  "query": "",
  "department": [],
  "location": [],
  "workplace": [],
  "worktype": []
}

Payload Meaning:
- query → keyword search
- department → department filter
- location → location filter
- workplace → remote/on-site filter
- worktype → employment type filter

When empty, the API returns all jobs.

---

## Response Structure (Observed Fields)

Each job object includes:
- id (numeric internal ID)
- shortcode (string public identifier)
- title
- remote (boolean)
- workplace
- location:
  - country
  - countryCode
  - city
  - region

This confirms structured JSON job metadata.

---

## Pagination

No explicit page, limit, or offset parameters were observed in the POST payload.

For the tested companies, all jobs appear to be returned in a single request.

Pagination behavior may differ for companies with a very large number of listings.

---

## Job ID Format

Two identifiers exist:
- Numeric ID (example: 5567662)
- Shortcode (example: E89BF8A47E)

The shortcode likely maps to the job detail URL.

---

## API Pattern Consistency Verification

Tested across:
- futureplc
- tetrascience

Both follow the identical structure:

/api/v3/accounts/{company_slug}/jobs

Only the company slug changes.

This confirms a standardized API structure across Workable accounts.

---

## Complexity Rating

LOW

Reasons:
- Clean REST API
- Public endpoint
- No authentication required
- Structured JSON response
- Predictable URL pattern

---

## Summary

Workable exposes a standardized REST API for job listings via:

/api/v3/accounts/{company_slug}/jobs

It uses POST requests with a JSON payload to control filtering.

The structure is consistent across companies and is straightforward to integrate into a scraping or ingestion pipeline.