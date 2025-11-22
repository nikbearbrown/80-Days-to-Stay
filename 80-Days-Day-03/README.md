# Day 03
# Development Sprint Abstract 

Over the next steps, we will transform raw SEC Form D data into a functional, crowdsourced verification platform. The sprint begins with data filtering: processing the 568,707 company dataset to extract 8,000-12,000 high-potential targets by applying funding thresholds ($1M+), geographic filters (MA/CA/NY/WA/TX/IL), and industry exclusions (removing real estate, pooled investment funds, and other low-sponsorship sectors). Days 2-3 focus on domain discovery and verification: implementing pattern-based inference to generate candidate domains for each company, validating existence through DNS and HTTP checks, and supplementing with CommonCrawl API searches to achieve 80%+ domain coverage, establish the technical infrastructure: setting up Vercel Postgres database with three-tier schema (companies, verification_submissions, published_companies), deploying a Next.js application to Vercel, and building the public-facing verification form interface. The latter half of the week implements the quality control pipeline: developing bot validation functions that automatically verify domain existence, careers page accessibility, visa text claims, and spam detection; creating submission APIs that trigger asynchronous bot checks; and building aggregation logic that publishes company data only after 3+ bot-verified human submissions with no spam flags. By week's end, we'll have a working prototype where users can submit verifications, bots automatically validate submissions, and verified data publishes to a searchable database—establishing the foundation for volunteer recruitment and Google Ads campaigns that will scale verification through crowdsourced traffic.


**Week Development Goals:**
- **Data Pipeline:** Filter SEC data from 568K → 10K companies, infer and verify domains (80% coverage), extract careers pages and ATS platforms
- **Database Infrastructure:** Deploy Vercel Postgres with three-tier schema, migrate filtered companies, establish verification workflow tables
- **Web Application:** Build Next.js verification form, deploy to Vercel, create submission API with bot validation triggers
- **Quality Control:** Implement automated bot checks (domain, careers page, visa text, spam detection), aggregation logic for publishing verified data
- **Milestone:** Working prototype where users verify companies → bots validate → data publishes automatically after 3+ confirmations
# 80 Days to Stay - Evening Work ToDo List

## Day 1 (Tonight) - Data Filtering & Setup (2-3 hours)

### Priority 1: Filter SEC Data
```
☐ Load your startups_master.json from SEC processing
☐ Apply filters:
   - Funding >= $1M
   - Remove Europe/non-US addresses
   - Keep only: MA, CA, NY (maybe WA, TX, IL)
   - Remove industries: Real Estate, Pooled Investment, Oil/Gas, Agriculture, Retail, Construction
☐ Output: filtered_companies.json (~8,000-12,000 companies)
☐ Generate stats: How many companies per state, per industry, per funding range

Expected Output: Clean dataset ready for domain discovery
```

### Priority 2: Domain Inference Script
```
☐ Write/refine infer_domain() function
   - Handle: "Inc", "LLC", "Corp", "Ltd" removal
   - Try patterns: .com, .io, .bio, -bio.com, etc.
☐ Run on filtered dataset
☐ For each company, test 3-5 domain patterns
☐ Output: companies_with_domains.json (70-80% should have guesses)

Expected Output: Most companies have inferred domains to check
```

## Day 2 (Tomorrow Night) - Domain Verification (2-3 hours)

### Priority 1: DNS/HTTP Verification
```
☐ Write verify_domain_exists() function
   - DNS check (socket.gethostbyname)
   - HTTP HEAD request
☐ Run on all inferred domains
☐ Mark which domains actually exist
☐ Output: domains_verified.json

Expected Output: Know which 70-80% of domains are real
```

### Priority 2: CommonCrawl Check (If Time)
```
☐ Write CommonCrawl CDX API search function
☐ For companies with no verified domain, search CommonCrawl
☐ Extract domain from any results
☐ Add to verified list

Expected Output: Another 5-10% of domains found
```

## Day 3 (Next Night) - Web Scraping Setup (2-3 hours)

### Priority 1: Basic Crawler
```
☐ Write fetch_homepage() function
☐ Write verify_company_match() function
   - Check if company name appears on page
   - Extract title, meta description
☐ Test on 20 companies manually
☐ Refine matching logic

Expected Output: Working verification system
```

### Priority 2: Find Important Pages
```
☐ Write find_important_pages() function
   - Look for /careers, /jobs, /team URLs
   - Check for Greenhouse/Lever/Workday
☐ Test on 50 companies
☐ Save results

Expected Output: Know which companies have careers pages
```

## Day 4 - Database Schema & Setup (2 hours)

### Priority 1: Choose Database
```
☐ Decide: Vercel Postgres vs MongoDB Atlas vs Supabase
☐ Create free tier account
☐ Set up database

Recommendation: Vercel Postgres (best integration)
```

### Priority 2: Create Tables
```
☐ Create companies table (from SEC data)
☐ Create verification_submissions table
☐ Create published_companies table
☐ Insert filtered companies into database

Expected Output: Data in database, ready for verification system
```

## Day 5 - Verification Form Prototype (3 hours)

### Priority 1: Next.js Setup on Vercel
```
☐ Create new Next.js project
☐ Deploy to Vercel (should take 10 minutes)
☐ Connect to database
☐ Test basic query

Expected Output: Live website at [yourproject].vercel.app
```

### Priority 2: Single Company Verification Page
```
☐ Create /verify/[companyId] page
☐ Display company info
☐ Show verification checklist form
☐ Submit button (doesn't need to work yet)

Expected Output: Can see a company and the form
```

## Day 6 - Backend API Setup (2-3 hours)

### Priority 1: Submission Endpoint
```
☐ Create /api/submit-verification
☐ Accept form data
☐ Insert into verification_submissions table
☐ Return success
☐ Test with Postman or curl

Expected Output: Can submit verification data to database
```

### Priority 2: Bot Check Functions (Start)
```
☐ Write verifyDomain() bot function
☐ Write verifyCareersPage() bot function
☐ Test both manually

Expected Output: Bot checks work independently
```

## Day 7 - Bot Pipeline (2-3 hours)

### Priority 1: Complete Bot Checks
```
☐ Write verifyVisaText() function
☐ Write checkForSpam() function
☐ Wire all bot checks together
☐ Test on real submissions

Expected Output: Full bot verification pipeline works
```

### Priority 2: Aggregation Logic
```
☐ Write aggregateAndPublish() function
☐ Test with 3+ submissions for same company
☐ Verify data appears in published_companies

Expected Output: Can publish verified companies
```

## Weekend Milestone Check

**By end of Week 1, you should have:**
- [ ] 8,000-12,000 filtered companies in database
- [ ] 70-80% with verified domains
- [ ] Working verification form (live on Vercel)
- [ ] Bot validation pipeline functional
- [ ] Can manually test full submission → verification → publication flow

## Week 2 Preview - Google Ads & Volunteer Setup

```
☐ Apply for Google Ad Grants (if not done)
☐ Create volunteer onboarding guide
☐ Set up Airtable or Google Sheet for volunteer assignments
☐ Create landing page explaining the mission
☐ Write Google Ads campaigns
☐ Recruit first 20 volunteers (Humanitarians AI fellows)
```

## Quick Reference - Estimated Time Per Task

```
Data Filtering:           1 hour
Domain Inference:         1.5 hours
DNS/HTTP Verification:    2 hours
CommonCrawl Check:        1.5 hours
Basic Crawler:            2 hours
Find Important Pages:     1.5 hours
Database Setup:           1 hour
Next.js + Vercel Deploy:  1 hour
Verification Form UI:     2 hours
Submission API:           1.5 hours
Bot Check Functions:      3 hours
Aggregation Logic:        2 hours

Total: ~19 hours = about 7 evening sessions (2-3 hours each)
```

## Priority Order (If Short on Time)

**Must Have (Week 1):**
1. Filter SEC data
2. Domain inference + verification
3. Database setup
4. Basic verification form (even if just UI)

**Should Have (Week 1):**
5. Bot validation pipeline
6. Submit endpoint working

**Nice to Have (Can Wait to Week 2):**
7. CommonCrawl integration
8. Aggregation/publication logic
9. Admin review interface

## Tools You'll Need Installed

```
☐ Node.js 18+ (for Next.js)
☐ Python 3.9+ (for data processing)
☐ PostgreSQL client (or use Vercel dashboard)
☐ Git (for version control)
☐ VS Code or your preferred editor

Python packages:
☐ pandas
☐ requests
☐ beautifulsoup4
```

## First Thing Tonight

**Start here (30 minutes):**
1. Open your SEC data: `startups_master.json`
2. Count total companies: `len(data)`
3. Apply $1M+ filter: see how many remain
4. Apply MA/CA/NY filter: see how many remain
5. Print sample of 10 companies to verify data looks good

This gives you immediate progress and validates your approach.
