# ATS Job Scraper & Job Board Platform
## Product Scope Document

**Project Name:** 80 Days to Stay — ATS Job Aggregation & Job Board  
**Version:** 1.0  
**Date:** February 16, 2025  
**Prepared By:** Project Management  
**Team Size:** 8 Members  
**Status:** Active — Phase 1 In Progress

---
a
## TABLE OF CONTENTS

1. Executive Summary
2. Project Objectives & Vision
3. Current Status & Completed Work
4. System Architecture Overview
5. ATS Platform Target List & Tiering
6. Unified Output Schema
7. Phase Breakdown & Scope of Work
8. Team Roles & Work Assignment (8 Members)
9. Project Timeline & Milestones
10. Technical Standards & Conventions
11. Risk Register
12. Definition of Done
13. Appendix

---

## 1. EXECUTIVE SUMMARY

This project builds an end-to-end job aggregation platform that discovers, scrapes, normalizes, and stores job listings from all major Applicant Tracking Systems (ATS) used by companies — with a focus on companies likely to sponsor visas for international students. The scraped data will be stored in a NoSQL database and served through a public-facing job board web application.

Every ATS scraper follows a proven **two-phase architecture**:

- **Phase 1 — Discovery:** Identify live company career endpoints on a given ATS, validate them, and harvest all job listing URLs via pagination.
- **Phase 2 — Extraction:** Visit each discovered job URL, extract full structured details (title, description, location, department, apply link, etc.), and output normalized JSON + CSV.

This pattern scales across all ATS platforms. Complexity varies from simple public REST API calls (Greenhouse, Lever) to full browser-automated scraping for JavaScript-heavy enterprise systems (Workday, Taleo).

**Primary Use Case:** International students searching for jobs at companies that sponsor work visas. Greenhouse and Lever alone cover an estimated 60–70%+ of visa-sponsoring tech companies, while enterprise ATS systems like Workday, iCIMS, and Taleo cover the Fortune 500 segment.

---

## 2. PROJECT OBJECTIVES & VISION

| # | Objective | Success Metric |
|---|-----------|---------------|
| 1 | Build scrapers for all major ATS platforms, tiered by market share and complexity | Scrapers completed and tested for 10+ ATS platforms |
| 2 | Produce normalized JSON metadata for every scraped job | 100% of jobs output with unified schema (company, role, description, location, date, apply URL, etc.) |
| 3 | Build an ATS–Company mapping registry | Database of 1,000+ companies mapped to their ATS provider with URL patterns |
| 4 | Store all job data in a NoSQL database | MongoDB/DynamoDB with deduplication, timestamps, and source tracking |
| 5 | Build a cloud pipeline for scheduled scraping | Automated runs at configurable intervals (daily/hourly) |
| 6 | Launch a frontend job board application | Public web app with search, filter, and browse for end users |

---

## 3. CURRENT STATUS

### ✅ Tier 1 Scrapers — in Progress (Shared by Prof. Nik)

**Greenhouse Scraper**
- Public API endpoint: `https://boards-api.greenhouse.io/v1/boards/{company}/jobs`
- No authentication required; returns clean JSON
- Handles company name normalization (strips Inc., LLC, Corp., etc.)
- Auto-creates subdirectories; outputs `jobs.json` + `metadata.json`
- **Status: Needs testing & validation by team**

**Lever Scraper**
- Public API endpoint: `https://api.lever.co/v0/postings/{company}`
- Same architecture and ease of access as Greenhouse
- Identical input format (company list via CLI or file)
- **Status: Needs testing & validation by team**

**Technical Notes (Both Scripts):**
- Handle encoding issues (UTF-8, UTF-16, etc.)
- Rate limit respectfully (0.5s delay, configurable)
- Normalize company names intelligently
- Generate both raw data (`jobs.json`) and metadata
- Can process from CLI or file input
- ~200 lines each, clean Python

### Reference Architecture — Avature Scraper (Prior Project)

A separate prior project implemented the same two-phase pattern for the Avature ATS:

- `phase1_discovery.py` — Parses seed URLs → extracts domains/site paths → validates live endpoints → harvests job URLs via pagination → deduplicates → outputs `discovered_jobs.csv` + `live_endpoints.csv`
- `phase2_extraction.py` — Visits each job URL → extracts full details (title, location, date, department, description, apply URL) → saves progress every 100 jobs (resumable) → outputs `jobs_full_details.csv` + `jobs_full_details.json`
- Configuration: `REQUEST_TIMEOUT`, `PAGE_SIZE`, `MAX_PAGES`, `DELAY_BETWEEN_REQUESTS`, `MAX_RETRIES`, `SAVE_INTERVAL`

**This two-phase (Discovery → Extraction) architecture is the template every team member should follow when building their assigned ATS scraper.**

---

## 4. SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION LAYER                            │
│                                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │Greenhouse│ │  Lever   │ │ Workday  │ │  iCIMS   │ │  Taleo   │ ... │
│  │ Scraper  │ │ Scraper  │ │ Scraper  │ │ Scraper  │ │ Scraper  │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│       │             │            │             │            │            │
│       ▼             ▼            ▼             ▼            ▼            │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │              UNIFIED JSON OUTPUT (Normalized Schema)         │       │
│  │  { company, title, location, description, apply_url,        │       │
│  │    date_posted, department, employment_type, ats_source,     │       │
│  │    source_url, scraped_at }                                  │       │
│  └──────────────────────────────┬───────────────────────────────┘       │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA STORAGE LAYER                               │
│                                                                         │
│  ┌──────────────────────┐    ┌──────────────────────────┐               │
│  │   Jobs Collection    │    │ ATS-Company Registry     │               │
│  │   (NoSQL — MongoDB)  │    │ (company → ATS + pattern │               │
│  │   - All scraped jobs │    │  + career URL + slug)    │               │
│  │   - Deduplication    │    │                          │               │
│  │   - Timestamps       │    │                          │               │
│  └──────────┬───────────┘    └──────────────────────────┘               │
└─────────────┼───────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PIPELINE & ORCHESTRATION LAYER                       │
│                                                                         │
│  ┌──────────────────────────────────────────────────┐                   │
│  │  Cloud Scheduler (cron / AWS Lambda / Cloud Fn)  │                   │
│  │  - Runs scrapers at set intervals                │                   │
│  │  - Handles retries & error logging               │                   │
│  │  - Updates DB with new/changed/removed jobs      │                   │
│  └──────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                               │
│                                                                         │
│  ┌──────────────────────────────────────────────────┐                   │
│  │  Job Board Web Application (Frontend)            │                   │
│  │  - Search & filter jobs                          │                   │
│  │  - Browse by company, ATS, location, role        │                   │
│  │  - Job detail pages with apply links             │                   │
│  │  - Responsive / mobile-friendly                  │                   │
│  └──────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. ATS PLATFORM TARGET LIST & TIERING

Each scraper is assigned a **Tier** based on complexity and a **Priority** based on market relevance.

### Tier 1 — Easy (Public REST APIs, no auth, clean JSON)

| ATS Platform | Market Coverage | API / Endpoint Pattern | Complexity | Status |
|---|---|---|---|---|
| **Greenhouse** | 15–20% of tech/startups | `boards-api.greenhouse.io/v1/boards/{company}/jobs` | LOW | ✅ Script received — needs testing |
| **Lever** | Startups & scale-ups | `api.lever.co/v0/postings/{company}` | LOW | ✅ Script received — needs testing |
| **Ashby** | Growing mid-market | Public API available | LOW | 🔲 To build |
| **SmartRecruiters** | Mid-market | Public job API available | LOW | 🔲 To build |
| **Jobvite** | Mid-market | Public career page API | LOW-MED | 🔲 To build |

### Tier 2 — Medium (Semi-structured, HTML scraping required)

| ATS Platform | Market Coverage | Approach | Complexity | Status |
|---|---|---|---|---|
| **BambooHR** | SMBs | Scrape structured career pages | MEDIUM | 🔲 To build |
| **JazzHR** | SMBs | Scrape career page feeds | MEDIUM | 🔲 To build |
| **Recruitee** | SMBs / EU market | Public API + scraping | MEDIUM | 🔲 To build |
| **Workable** | SMBs & growing cos | Scrape career site widgets | MEDIUM | 🔲 To build |
| **Teamtailor** | Growing in EU | Career site scraping | MEDIUM | 🔲 To build |
| **Avature** | Enterprise/niche | `*/SearchJobs/` pagination pattern | MEDIUM | ✅ Reference architecture exists |

### Tier 3 — Hard (No public API, JS-heavy, browser automation likely needed)

| ATS Platform | Market Coverage | Approach | Complexity | Status |
|---|---|---|---|---|
| **Workday** | ~37% of Fortune 500 | Scrape `*.myworkdayjobs.com/*`; JS-heavy | HIGH | 🔲 To build |
| **iCIMS** | ~10.7% market share | Scrape career page implementations | HIGH | 🔲 To build |
| **Taleo / Oracle** | ~13.4% of Fortune 500 | Scrape public career pages; auth-gated APIs | HIGH | 🔲 To build |
| **SAP SuccessFactors** | Enterprise HR suites | Deep enterprise scraping | HIGH | 🔲 To build |
| **Cornerstone OnDemand** | Enterprise | HTML/JS scraping | HIGH | 🔲 To build |

### Strategic Note
Tier 1 platforms (especially Greenhouse + Lever) cover the companies most likely to sponsor visas for international students (tech startups, scale-ups). Tier 3 enterprise platforms add Fortune 500 coverage but require 3–4× the development effort. The team should **nail Tier 1 first**, then decide on Tier 2/3 based on data from test runs.

---

## 6. UNIFIED OUTPUT SCHEMA

**Every scraper, regardless of ATS platform, MUST output data conforming to this schema.**

### Job Record — JSON Schema

```json
{
  "job_id": "string — unique ID (ATS-native ID or generated hash)",
  "title": "string — job title",
  "company_name": "string — normalized company name",
  "company_slug": "string — URL-safe company identifier",
  "ats_source": "string — e.g. greenhouse, lever, workday, icims",
  "source_url": "string — original job listing URL",
  "apply_url": "string — direct application URL",
  "location": "string — job location (city, state, remote, etc.)",
  "department": "string — department or team (if available)",
  "employment_type": "string — Full-time, Part-time, Contract, Intern",
  "date_posted": "string — ISO 8601 date or null",
  "description_text": "string — clean plain-text job description",
  "description_html": "string — raw HTML description (if available)",
  "salary_range": "string — salary info if posted (often null)",
  "metadata": {
    "scraped_at": "string — ISO 8601 timestamp of scrape",
    "scraper_version": "string — e.g. v1.0",
    "extraction_status": "string — success | error | partial",
    "raw_response_hash": "string — MD5/SHA hash for deduplication"
  }
}
```

### ATS–Company Registry Record

```json
{
  "company_name": "string — normalized name",
  "company_slug": "string — URL-safe slug",
  "ats_platform": "string — greenhouse, lever, workday, etc.",
  "career_page_url": "string — base career page URL",
  "api_endpoint_pattern": "string — API URL template if applicable",
  "url_slug_on_ats": "string — the company's slug on the ATS platform",
  "last_scraped_at": "string — ISO 8601",
  "total_jobs_last_scrape": "integer",
  "is_active": "boolean",
  "discovery_source": "string — how we found this company (SEC, manual, etc.)",
  "notes": "string"
}
```

---

## 7. PHASE BREAKDOWN & SCOPE OF WORK

---

### PHASE 1: Research & ATS Discovery (Week 1 — Feb 16–22, 2025)

**Goal:** Every team member understands how ATS systems work, how career page URLs are structured, how job data is exposed, and what the scraping approach looks like for each platform.

| Task ID | Task | Description | Deliverable |
|---------|------|-------------|-------------|
| 1.1 | ATS Fundamentals Research | Each member studies their assigned ATS: how companies post jobs, how career pages are generated, what URL patterns exist, whether APIs are public | Research doc per ATS (1–2 pages) |
| 1.2 | URL Pattern Documentation | Document the URL structure for career pages and job listings on each ATS (e.g., `boards-api.greenhouse.io/v1/boards/{slug}/jobs`) | URL pattern cheat sheet |
| 1.3 | Compile Master Company List | Gather a list of companies and identify which ATS each uses. Sources: SEC Form D filings, public data, manual research, builtwith.com | `company_ats_mapping.csv` |
| 1.4 | Test Existing Scripts | Team members assigned to Greenhouse/Lever: pull Prof. Nik's scripts, run them against a sample company list, verify output, document bugs | Test report with pass/fail per company |
| 1.5 | Set Up Shared Repository | Create a monorepo with folder structure: `/scrapers/{ats_name}/`, `/data/`, `/docs/`, `/tests/`, shared `requirements.txt` | GitHub repo initialized |

---

### PHASE 2: Scraper Development — Tier 1 & Tier 2 (Week 1–2 — Feb 16–Mar 1, 2025)

**Goal:** All assigned scrapers built, tested, and producing valid JSON output conforming to the unified schema.

**Every scraper must implement:**

1. **Discovery Module** (`discovery.py`)
   - Accept a company list (file or CLI)
   - Normalize company names (strip Inc., LLC, Corp., etc.)
   - Construct ATS-specific career page / API URL
   - Validate if endpoint is live and has active jobs
   - Handle pagination to discover ALL job URLs
   - Output: `discovered_jobs.csv` + `live_endpoints.csv`

2. **Extraction Module** (`extraction.py`)
   - Read `discovered_jobs.csv`
   - Visit each job URL and extract full details
   - Map extracted data to the unified JSON schema
   - Save progress periodically (resumable)
   - Output: `jobs_full_details.json` + `jobs_full_details.csv` + `metadata.json`

3. **Configuration**
   - `REQUEST_TIMEOUT`, `DELAY_BETWEEN_REQUESTS`, `MAX_RETRIES`, `MAX_PAGES`, `SAVE_INTERVAL`
   - All configurable at top of script

4. **Error Handling & Rate Limiting**
   - Respectful delays between requests (minimum 0.3–0.5s)
   - Retry logic with exponential backoff
   - Graceful handling of 404s, timeouts, encoding issues
   - Logging to file

| Task ID | Task | Assignee Guidance | Deliverable |
|---------|------|-------------------|-------------|
| 2.1 | Test & Validate Greenhouse Scraper | Run against 50+ companies, fix bugs, ensure schema compliance | Validated `greenhouse_scraper.py` + test results JSON |
| 2.2 | Test & Validate Lever Scraper | Same as above for Lever | Validated `lever_scraper.py` + test results JSON |
| 2.3 | Build Ashby Scraper | Research Ashby's public API, build discovery + extraction | `ashby_scraper.py` + output samples |
| 2.4 | Build SmartRecruiters Scraper | Research SmartRecruiters API, build full scraper | `smartrecruiters_scraper.py` + output samples |
| 2.5 | Build Workable Scraper | Research Workable's career widget/API, build scraper | `workable_scraper.py` + output samples |
| 2.6 | Build BambooHR Scraper | Research career page structure, build scraper | `bamboohr_scraper.py` + output samples |
| 2.7 | Build Jobvite Scraper | Research Jobvite career pages/API, build scraper | `jobvite_scraper.py` + output samples |
| 2.8 | Begin Workday Scraper R&D | Research `*.myworkdayjobs.com` patterns, prototype discovery (browser automation may be needed) | Research doc + prototype script |
| 2.9 | ATS–Company Registry Population | Continuously add companies to the registry as scrapers discover them | Growing `company_ats_mapping.csv` → DB import ready |

---

### PHASE 3: Testing, Validation & JSON Output (End of Week 2 — Feb 28–Mar 1, 2025)

**Goal:** All Tier 1 scrapers pass validation. Output JSONs conform to unified schema. Metadata is accurate.

| Task ID | Task | Description | Deliverable |
|---------|------|-------------|-------------|
| 3.1 | Schema Validation Script | Build a Python script that validates any scraper's JSON output against the unified schema | `validate_schema.py` |
| 3.2 | Cross-ATS Test Suite | Run all scrapers against a shared list of 100 known companies, compare results | Test report: hit rate per ATS, error rate, data completeness |
| 3.3 | Deduplication Logic | Implement hash-based deduplication across scrapers (same job posted on multiple ATS) | Dedup utility function |
| 3.4 | Metadata Quality Audit | Verify metadata fields: `company_name` normalization, `date_posted` parsing, `location` extraction | Audit report with fix list |
| 3.5 | Generate Sample Result JSONs | Produce clean, validated sample outputs for each ATS scraper (10 companies each) | `/samples/{ats}/` directory with JSONs |

---

### PHASE 4: Database Design & Data Storage (Week 3 — Mar 2–8, 2025)

**Goal:** NoSQL database is designed, provisioned, and populated with scraped job data + ATS registry.

| Task ID | Task | Description | Deliverable |
|---------|------|-------------|-------------|
| 4.1 | Database Selection & Setup | Select NoSQL DB (MongoDB Atlas recommended), create cluster, set up access | Running DB instance |
| 4.2 | Collections Design | Design collections: `jobs`, `companies`, `ats_registry`, `scrape_runs` | Schema documentation |
| 4.3 | Ingestion Script | Build a script that reads scraper JSON output and upserts into the database (handles dedup, updates, new inserts) | `ingest_to_db.py` |
| 4.4 | Indexing Strategy | Create indexes on key query fields: `company_name`, `ats_source`, `location`, `date_posted`, `title` | Index configuration doc |
| 4.5 | ATS–Company Registry DB | Import the ATS–Company mapping into a dedicated collection | Populated `ats_registry` collection |
| 4.6 | Data Validation & Integrity Checks | Ensure no orphan records, no schema violations, counts match scraper output | Validation report |

**Database Collections Overview:**

```
┌─────────────────────────────────────────────────────────┐
│  MongoDB Database: ats_job_board                        │
│                                                         │
│  ├── jobs              (all scraped job listings)       │
│  ├── companies         (company profiles + metadata)    │
│  ├── ats_registry      (company → ATS mapping)          │
│  ├── scrape_runs       (log of each scraper execution)  │
│  └── scrape_errors     (failed extractions for retry)   │
└─────────────────────────────────────────────────────────┘
```

---

### PHASE 5: Cloud Pipeline & Scheduled Scraping (Week 4 — Mar 9–15, 2025)

**Goal:** Scrapers run automatically in the cloud on a schedule, with logging, error handling, and DB writes.

| Task ID | Task | Description | Deliverable |
|---------|------|-------------|-------------|
| 5.1 | Containerize Scrapers | Dockerize each scraper for consistent cloud execution | `Dockerfile` per scraper + `docker-compose.yml` |
| 5.2 | Cloud Deployment | Deploy to AWS (Lambda / ECS / EC2) or GCP (Cloud Run / Cloud Functions) | Running cloud instances |
| 5.3 | Scheduler Setup | Configure cron-based scheduler (CloudWatch Events / Cloud Scheduler) for daily or hourly runs | Scheduler config + documentation |
| 5.4 | Pipeline Orchestration | Build a master runner script that: triggers scrapers → collects output → runs ingestion → logs results | `run_pipeline.py` |
| 5.5 | Monitoring & Alerting | Set up logging (CloudWatch / Stackdriver), error alerts (email/Slack), and a dashboard for scrape stats | Monitoring dashboard |
| 5.6 | Retry & Recovery | Implement retry queues for failed scrapes, dead-letter handling for persistent errors | Retry logic in pipeline |

---

### PHASE 6: Frontend Job Board Application (Weeks 5–7 — Mar 16–Apr 5, 2025)

**Goal:** A public-facing web application where users can search, filter, and browse aggregated job listings.

| Task ID | Task | Description | Deliverable |
|---------|------|-------------|-------------|
| 6.1 | API Layer (Backend-for-Frontend) | Build a REST API that queries the MongoDB `jobs` collection with search, filter, pagination | `/api/jobs`, `/api/companies`, `/api/stats` endpoints |
| 6.2 | Frontend Framework Setup | Initialize frontend (React / Next.js recommended), configure routing, state management | Scaffolded frontend project |
| 6.3 | Job Listing Page | Paginated list of jobs with search bar, filters (location, company, ATS, employment type, date) | Working listing page |
| 6.4 | Job Detail Page | Full job detail view: title, company, description, location, apply button (links to original) | Working detail page |
| 6.5 | Company Profile Page | Page showing all jobs from a given company, their ATS, career page link | Working company page |
| 6.6 | Search & Filter Engine | Full-text search on title + description, faceted filters, sort by date/relevance | Working search |
| 6.7 | Responsive Design & Polish | Mobile-friendly, accessibility basics, loading states, error handling | Polished UI |
| 6.8 | Deployment | Deploy frontend (Vercel / Netlify / AWS Amplify) + backend API | Live URL |

---

## 8. TEAM ROLES & WORK ASSIGNMENT (8 Members)

### Role Assignments

| Member | Role | Primary Responsibilities |
|--------|------|------------------------|
| **Member 1** | Scraper Lead — Tier 1 API Scrapers | Test & validate Greenhouse + Lever scripts from Prof. Nik; build Ashby scraper; own Tier 1 quality |
| **Member 2** | Scraper Dev — Mid-Market ATS | Build SmartRecruiters + Workable scrapers; research their APIs and career page structures |
| **Member 3** | Scraper Dev — SMB ATS | Build BambooHR + JazzHR scrapers; research career page HTML patterns |
| **Member 4** | Scraper Dev — Enterprise ATS (Workday) | Deep R&D on Workday scraping (`*.myworkdayjobs.com`); prototype browser automation approach; this is the hardest scraper |
| **Member 5** | Scraper Dev — Enterprise ATS (iCIMS + Taleo) | Research and build iCIMS and Taleo/Oracle scrapers; career page scraping focus |
| **Member 6** | Data & Database Engineer | Design NoSQL schema; build ingestion scripts; populate ATS–Company registry; handle dedup and data integrity |
| **Member 7** | Pipeline & DevOps Engineer | Containerize scrapers; set up cloud deployment, scheduler, monitoring, retry logic; own the pipeline |
| **Member 8** | Frontend & API Developer | Build the REST API layer; build the frontend job board UI; deploy the web application |

### Work Distribution — Phase by Phase

#### PHASE 1 (Week 1): Research & Discovery — ALL MEMBERS

| Member | Phase 1 Task |
|--------|-------------|
| Member 1 | Research Greenhouse + Lever + Ashby; test existing scripts; document URL patterns |
| Member 2 | Research SmartRecruiters + Workable; document APIs and URL patterns |
| Member 3 | Research BambooHR + JazzHR; document career page structures |
| Member 4 | Deep research on Workday scraping approaches; document `myworkdayjobs.com` patterns |
| Member 5 | Research iCIMS + Taleo; document career page scraping strategies |
| Member 6 | Compile master company list (SEC filings, public data); begin ATS–Company mapping; set up MongoDB |
| Member 7 | Set up GitHub monorepo; establish project structure, CI/CD skeleton; research cloud options |
| Member 8 | Research frontend frameworks; wireframe job board UI; study API design for job search |

#### PHASE 2 (Weeks 1–2): Scraper Development — SCRAPER DEVS

| Member | Phase 2 Task |
|--------|-------------|
| Member 1 | Validate Greenhouse + Lever; build Ashby scraper; ensure all output matches unified schema |
| Member 2 | Build SmartRecruiters scraper; build Workable scraper |
| Member 3 | Build BambooHR scraper; build JazzHR scraper |
| Member 4 | Prototype Workday scraper (discovery phase at minimum); document browser automation needs |
| Member 5 | Prototype iCIMS scraper; begin Taleo research |
| Member 6 | Build `company_ats_mapping.csv`; build schema validation script; support scrapers with data questions |
| Member 7 | Set up shared test infrastructure; write common utility functions (rate limiting, logging, retry); Dockerfiles |
| Member 8 | Begin API layer design; mock endpoints for frontend work |

#### PHASE 3 (End of Week 2): Testing & Validation — ALL MEMBERS

| Member | Phase 3 Task |
|--------|-------------|
| Members 1–5 | Run their scrapers against shared 100-company test list; fix bugs; produce validated sample JSONs |
| Member 6 | Run schema validation across all outputs; produce data quality audit report |
| Member 7 | Set up automated test runner; integrate scraper tests into CI |
| Member 8 | Build frontend prototype with mock data from sample JSONs |

#### PHASE 4 (Week 3): Database — MEMBER 6 leads, ALL support

| Member | Phase 4 Task |
|--------|-------------|
| Member 6 | Lead: design collections, indexing, build ingestion scripts, load data |
| Members 1–5 | Support: run scrapers to produce data for DB load; fix any schema issues |
| Member 7 | Support: set up DB infrastructure in cloud; manage access/networking |
| Member 8 | Connect API endpoints to live database instead of mock data |

#### PHASE 5 (Week 4): Cloud Pipeline — MEMBER 7 leads

| Member | Phase 5 Task |
|--------|-------------|
| Member 7 | Lead: containerize all scrapers, deploy to cloud, set up scheduler and monitoring |
| Members 1–5 | Support: ensure their scrapers work in Docker containers; test cloud runs |
| Member 6 | Support: validate DB writes from pipeline; monitor data integrity |
| Member 8 | Continue frontend development |

#### PHASE 6 (Weeks 5–7): Frontend — MEMBER 8 leads, MEMBERS 6–7 support

| Member | Phase 6 Task |
|--------|-------------|
| Member 8 | Lead: build complete job board frontend + API |
| Member 6 | Support: optimize DB queries for frontend performance; add any needed indexes |
| Member 7 | Support: deploy frontend; set up CDN, SSL, domain |
| Members 1–5 | Tier 2/3 scraper improvements; add more companies to registry; fix bugs from pipeline runs |

---

## 9. PROJECT TIMELINE & MILESTONES

```
WEEK 1: Feb 16 – Feb 22, 2025
├── M1: Research complete — all ATS research docs submitted ✦ Feb 20
├── M2: Repo & project structure set up ✦ Feb 18
├── M3: Greenhouse + Lever tested & validated ✦ Feb 22
└── All Tier 1 scraper development begins

WEEK 2: Feb 23 – Mar 1, 2025
├── M4: All Tier 1 scrapers complete & producing valid JSON ✦ Feb 28
├── M5: Workday/iCIMS R&D prototypes documented ✦ Feb 28
├── M6: Schema validation passing for all scrapers ✦ Mar 1
├── M7: ATS–Company registry has 500+ entries ✦ Mar 1
└── M8: Sample result JSONs generated for all ATS ✦ Mar 1

WEEK 3: Mar 2 – Mar 8, 2025
├── M9: MongoDB fully set up with all collections ✦ Mar 4
├── M10: Ingestion scripts working; DB populated ✦ Mar 7
└── M11: API endpoints connected to live DB ✦ Mar 8

WEEK 4: Mar 9 – Mar 15, 2025
├── M12: All scrapers containerized and running in cloud ✦ Mar 12
├── M13: Scheduler running daily automated scrapes ✦ Mar 14
└── M14: Monitoring & alerting operational ✦ Mar 15

WEEK 5–6: Mar 16 – Mar 29, 2025
├── M15: Frontend MVP live (search, listing, detail pages) ✦ Mar 22
├── M16: Company pages and filters working ✦ Mar 29
└── Tier 2/3 scrapers continue improving in parallel

WEEK 7: Mar 30 – Apr 5, 2025
├── M17: Frontend polished, responsive, deployed ✦ Apr 3
├── M18: Full end-to-end system operational ✦ Apr 5
└── M19: PROJECT LAUNCH ✦ Apr 5
```

### Summary Timeline Table

| Phase | Duration | Dates | Key Milestone |
|-------|----------|-------|--------------|
| Phase 1: Research & Discovery | 1 week | Feb 16–22 | All ATS research docs + Greenhouse/Lever tested |
| Phase 2: Scraper Development | 2 weeks | Feb 16–Mar 1 | All Tier 1 scrapers complete with valid JSON output |
| Phase 3: Testing & Validation | Overlaps with Phase 2 end | Feb 28–Mar 1 | Schema validation passing; sample JSONs generated |
| Phase 4: Database & Storage | 1 week | Mar 2–8 | MongoDB live; data ingested; API connected |
| Phase 5: Cloud Pipeline | 1 week | Mar 9–15 | Automated scheduled scraping in production |
| Phase 6: Frontend Job Board | 3 weeks | Mar 16–Apr 5 | Public job board live and deployed |

---

## 10. TECHNICAL STANDARDS & CONVENTIONS

### Language & Dependencies
- **Python 3.9+** for all scrapers
- `requests` for HTTP (Tier 1/2); `playwright` or `selenium` for Tier 3 (JS-heavy)
- `beautifulsoup4` / `lxml` for HTML parsing
- `pymongo` for MongoDB interaction
- **Node.js / React / Next.js** for frontend (Member 8's choice with team input)

### Code Standards
- All scrapers live in `/scrapers/{ats_name}/` within the monorepo
- Each scraper folder contains: `discovery.py`, `extraction.py`, `config.py`, `README.md`
- Use Python logging module (not print statements)
- All configurable values at top of script or in `config.py`
- Type hints on all functions
- Docstrings on all public functions

### Rate Limiting & Ethics
- Minimum 0.3s delay between requests (configurable per ATS)
- Respect `robots.txt` where applicable
- Identify as a bot in User-Agent string where appropriate
- Do NOT scrape pages that require login or authentication bypass
- Do NOT store personal candidate data — only job posting data

### Git Workflow
- `main` branch is protected; no direct pushes
- Feature branches: `feature/{ats_name}-scraper`, `feature/db-setup`, etc.
- Pull requests require 1 reviewer before merge
- Commit messages: `[ATS_NAME] Brief description` (e.g., `[GREENHOUSE] Fix pagination edge case`)

---

## 11. RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Workday scraping is too complex for 2-week timeline | HIGH | MEDIUM | Designate as R&D in Phase 2; defer full build to Phase 5 if needed; consider third-party (Apify) as fallback |
| ATS platforms change their URL patterns or APIs | MEDIUM | HIGH | Store patterns in the registry DB; build monitoring for broken scrapers; alert on failure |
| Rate limiting / IP blocking by ATS providers | MEDIUM | HIGH | Respectful delays; rotating user agents; proxy rotation if needed; exponential backoff |
| Company name normalization inconsistencies across ATS | HIGH | MEDIUM | Centralized normalization utility; fuzzy matching library; human review for edge cases |
| Team members unfamiliar with web scraping | MEDIUM | MEDIUM | Phase 1 research week provides ramp-up; pair programming; reference architecture as template |
| MongoDB schema changes needed mid-project | LOW | MEDIUM | NoSQL is flexible by design; version the schema; use migration scripts |
| Frontend scope creep | MEDIUM | LOW | Strict MVP feature set defined in Phase 6; polish in final week only |

---

## 12. DEFINITION OF DONE

### For Each Scraper:
- [ ] Discovery module runs successfully against 20+ companies
- [ ] Extraction module produces valid JSON for all discovered jobs
- [ ] Output passes schema validation script (`validate_schema.py`)
- [ ] Rate limiting is implemented (≥ 0.3s delay)
- [ ] Error handling covers: timeouts, 404s, encoding issues, empty responses
- [ ] Resume capability works (extraction can be stopped and restarted)
- [ ] README.md documents: usage, config, known limitations
- [ ] Code reviewed and merged to `main` via PR

### For Database:
- [ ] All collections created with proper indexes
- [ ] Ingestion script handles upserts (insert new, update existing, skip duplicates)
- [ ] Data count in DB matches scraper output counts
- [ ] Queries run in <500ms for common frontend operations

### For Pipeline:
- [ ] All scrapers run successfully in Docker
- [ ] Scheduler triggers automated runs at configured intervals
- [ ] Logs are centralized and searchable
- [ ] Failed scrapes are retried; persistent failures are alerted

### For Frontend:
- [ ] Users can search jobs by keyword
- [ ] Users can filter by location, company, ATS source, employment type
- [ ] Job detail page shows full description + apply link
- [ ] Page loads in <2 seconds
- [ ] Mobile responsive

---

## 13. APPENDIX

### A. Useful Research Links

| Resource | URL |
|----------|-----|
| Greenhouse Boards API Docs | `https://developers.greenhouse.io/job-board.html` |
| Lever Postings API | `https://github.com/lever/postings-api` |
| Ashby Job Board API | `https://developers.ashbyhq.com` |
| SmartRecruiters Public API | `https://dev.smartrecruiters.com` |
| Workday Job Search Pattern | `*.myworkdayjobs.com/*/job/*` |
| iCIMS Career Sites | Various `careers.{company}.icims.com` patterns |
| Apify ATS Scrapers (Tier 2/3 fallback) | `https://apify.com/fantastic-jobs/career-site-job-listing-api` |
| BuiltWith (identify ATS used) | `https://builtwith.com` |

### B. Company List Sources
- SEC EDGAR Form D filings (companies that have raised capital — likely hiring)
- Crunchbase (funded startups)
- Y Combinator company directory
- Manual research / LinkedIn career pages

### C. Quick-Start for New Scraper Development

```
1. Create folder: /scrapers/{ats_name}/
2. Copy template: discovery.py, extraction.py, config.py, README.md
3. Research the ATS:
   - How do career pages work?
   - Is there a public API?
   - What URL pattern do company career pages follow?
   - How is pagination handled?
   - What data is available on listing vs. detail pages?
4. Implement discovery.py — find companies + harvest job URLs
5. Implement extraction.py — visit each URL + extract to unified schema
6. Test against 20+ companies
7. Run validate_schema.py against output
8. Write README, create PR, request review
```

---

**END OF DOCUMENT**

*This is a living document. It will be updated as the project progresses, decisions are made on Tier 2/3 priorities, and the ATS–Company registry grows.*
