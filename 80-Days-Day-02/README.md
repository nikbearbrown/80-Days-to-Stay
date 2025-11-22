# Day 02

# Day 2 Summary: SEC Form D Data Acquisition & Processing

## What We Built Today

# SEC Form D Analysis: Key Findings (2014-2025)

## Overall Statistics

**Total Dataset:**
- **568,707** total companies filed Form D
- **246,572** companies (43.4%) raised $5M+
- **190** states/territories covered

---

## Geographic Distribution

### Top 3 States by Volume

**1. New York**
- 91,662 total companies
- 53,355 raised $5M+ (58% high-value rate)
- Highest concentration of high-value deals

**2. California**
- 81,782 total companies
- 35,608 raised $5M+ (44% high-value rate)
- Strong tech/startup ecosystem

**3. Texas**
- 41,017 total companies
- 14,342 raised $5M+ (35% high-value rate)
- Emerging market

### Your Target Geography (MA/CA/NY)

**Combined Market Power:**
- 199,174 total companies (35% of national total)
- 103,008 companies raised $5M+ (42% of all high-value companies)
- Represents the most concentrated opportunity for high-quality prospects

---

## Industry Breakdown

### Top 5 Industries Overall

| Rank | Industry | Total Companies | % Over $5M |
|------|----------|----------------|------------|
| 1 | Pooled Investment Funds | 57,014 | 67% |
| 2 | Real Estate | 23,931 | 50% |
| 3 | Commercial | 14,507 | 40% |
| 4 | Banking & Financial Services | 11,668 | 43% |
| 5 | Other | 11,127 | 46% |

**Note:** Pooled Investment Funds includes hedge funds, VC funds, and private equity

### Tech-Related Industries (High Visa Sponsorship Potential)

| Industry | Total Companies | % Over $5M | Sponsorship Likelihood |
|----------|----------------|------------|----------------------|
| Pharmaceuticals | 5,425 | 54% | Very High |
| Biotechnology | 9,835 | 49% | Very High |
| Computers/Technology | 10,480 | 47% | High |
| Telecommunications | 8,697 | 39% | Moderate-High |

**Combined tech sector: ~34,437 companies, ~48% raised $5M+**

---

## Strategic Implications for Your Database Product

### The Filtering Funnel

```
568,707 total companies
    ↓ Filter: MA/CA/NY
199,174 companies (35% of total)
    ↓ Filter: Raised $5M+
103,008 high-value companies (42% of all $5M+ companies)
    ↓ Filter: Tech/Bio/Pharma industries
~30,000 highly relevant companies
    ↓ Filter: Filed within last 12 months
~5,000-8,000 actively hiring NOW
```

### Your $10 Database Sweet Spot

**Target Profile:**
- **Geography:** MA, CA, or NY
- **Funding Level:** $5M+ (demonstrates growth capacity)
- **Industry:** Tech, Biotech, Pharma (high sponsorship rates)
- **Recency:** <12 months (actively scaling/hiring)

**Expected Database Size:** 5,000-8,000 premium prospects

**Value Proposition:** 
- Pre-qualified for financial stability
- Geographic concentration in visa-friendly states
- Industry focus on high-sponsorship sectors
- Timing optimized for active hiring cycles

---

## Competitive Advantage

Your dataset uniquely combines:
1. **SEC validation** (verified funding levels)
2. **Geographic targeting** (highest-value states)
3. **Industry filtering** (visa-sponsorship correlation)
4. **Temporal relevance** (recent filers = active growth)

This is exponentially more valuable than generic company lists.

### 1. Understanding SEC Form D Data Structure
- **Learned the data model**: Each quarterly ZIP contains 4 key TSV files:
  - `OFFERING.tsv` - Funding amounts, industry, investor counts
  - `ISSUERS.tsv` - Company details, address, incorporation year
  - `RELATEDPERSONS.tsv` - Executives, directors, founders
  - `FORMDSUBMISSION.tsv` - Filing metadata, dates
- **Key insight**: `ACCESSIONNUMBER` is the primary key linking everything
- **Column names**: No underscores (e.g., `TOTALAMOUNTSOLD` not `TOTAL_AMOUNT_SOLD`)

### 2. Python Environment Setup (macOS Challenges)
- Dealt with macOS "externally-managed-environment" error
- Solution: `pip3 install --user --break-system-packages pandas`
- Rejected virtual environments (complexity for students)
- Installed core packages: pandas, numpy, requests, etc.

### 3. Single Quarter Parser (`sec_form_d.py`)
- Parses one quarterly folder of TSV files
- Auto-detects column names (handles variations)
- Outputs MongoDB-ready JSON with nested structure:
  - Company info with full address
  - Funding details with amounts and dates
  - Related persons array (executives with roles)
  - Metadata placeholders for ML predictions
- **First run**: 87 companies from 2025Q1

### 4. Bulk Data Acquisition
- **Manual approach**: Downloaded 10+ years via browser (2014-2025)
- Created `download_sec_data.py` script (handles SEC's User-Agent requirements)
- **Challenge**: SEC returns 403 without proper headers
- **Total dataset**: 40+ quarterly folders, ~10 years of filings

### 5. Multi-Quarter Batch Processor (`process_all_quarters.py`)
**Key philosophy shift**: Don't filter for "startups" - capture ALL companies with recent funding. A 10-year-old company that raised $75M yesterday has more hiring budget than a 2-month-old seed company.

**Features:**
- **No filtering** - outputs everything, filter later
- Automatically walks current directory for quarterly folders
- Processes all quarters in one run (~40 quarters)
- Deduplicates companies (if multiple rounds, keeps most recent)
- **Adds enrichment metadata**:
  - `years_since_incorporation` - company age
  - `months_since_funding` - how recent is the money?
  - `funding_recency` - categorical (very_recent, recent, moderate, older)
  - `stage_estimate` - Pre-Seed, Seed, Series A/B/C/D+ based on amount

**Outputs:**
1. **`startups_master.json`** - Complete dataset, all companies (~10,000+)
2. **`startups_stats.csv`** - Descriptive statistics:
   - Overall totals (all vs. >$5M)
   - **By State**: Every state, total + over $5M breakdown
   - **By Industry**: Every industry, total + over $5M breakdown
   - By Stage: Distribution across funding stages
   - By Recency: How fresh is the funding?
   - Target States: MA/CA/NY special breakdown

### 6. Data Quality & Insights
- **Expected output**: 1,000-1,500 unique companies over 10 years
- **Deduplication**: Same company raising multiple rounds = one record (most recent)
- **Age distribution**: Mix from fresh (<6 months) to established (5+ years)
- **Stage distribution**: Seed through Series D+, based on funding amounts
- **Geographic spread**: All 50 states, but concentrated in tech hubs

## Key Decisions Made

1. **No filtering during processing** - Output everything, let users filter by state/industry/amount later based on statistics
2. **Company age matters less than funding recency** - A 10-year-old company with fresh $50M is better than a 3-month-old with $2M
3. **Stage estimation** - Algorithmic based on amount ($5-15M = Series A, etc.)
4. **Recency categories** - <6mo = very_recent (actively hiring NOW)

## File Structure Created

```
sec_data/
├── 2014Q1_d/ ... 2025Q3_d/     # 40+ quarterly folders (TSV files)
├── startups_master.json         # Complete dataset (~10K companies)
├── startups_stats.csv           # Descriptive statistics
└── process_all_quarters.py      # Batch processor script
```

## What's Next (Day 2)

**Enrichment Pipeline:**
1. Find company websites (Google search, domain inference)
2. Scrape career pages for job postings
3. Extract company descriptions and tech stack
4. Identify international team members (LinkedIn)
5. Build ML models for prediction scores:
   - `international_hiring` likelihood (0-1)
   - `recent_grad_hiring` likelihood (0-1)

## Commands to Reproduce

```bash
# Setup
pip3 install --user --break-system-packages pandas numpy requests

# Download data (manual or script)
# Extract to sec_data/

# Process everything
cd sec_data
python3 ../process_all_quarters.py

# Output: startups_master.json + startups_stats.csv
```

## Student Takeaways

- **GIGO principles**: Government data is high-quality (filed under penalty of law) but has limitations
- **Data enrichment strategy**: Start with authoritative source, enrich with other public data
- **Filter late, not early**: Capture everything, analyze statistics, then decide what to filter
- **Practical ML**: Company age + funding amount + time since funding = strong hiring likelihood proxy

---

*Total time investment: ~2 hours of development, ~10 minutes of processing for 10 years of data*
