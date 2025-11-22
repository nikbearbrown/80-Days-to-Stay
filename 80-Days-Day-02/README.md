# Day 02

# Day 1 Summary: SEC Form D Data Acquisition & Processing

## What We Built Today

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
