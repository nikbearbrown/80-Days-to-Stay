# Day 05
# 80 Days to Stay - Day 5 Progress Report

> *"Data collected. Now we separate the willing from the wealthy."*

## 🎯 Mission Status: Week 1 Complete

**Progress:** 45% of Week 1 goals achieved

---

## 📊 Scraping Results: Beyond Expectations

### What We Built
✅ **Complete company website scraper** using public SEC Form D data  
✅ **Zero failures** - 100% success rate on data collection  
✅ **Automated domain verification** - 62% of companies have working websites  

### The Numbers

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 SCRAPING STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Companies Processed:      25,748 / 25,748 (100%)
Failed Attempts:          0
Total HTML Pages:         425,233
Average Pages/Company:    16.5
Total Runtime:            3,549.8 minutes (59.2 hours)
Processing Rate:          0.12 companies/second

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 VERIFICATION PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Initial Companies:        41,299 (from filtered SEC data)
Domains Attempted:        141,236
Verified Companies:       25,748
Success Rate:             62.3%
Budget Spent:             $0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### What This Means

**Before this scrape:**
- International students searching blind
- No way to know which funded startups are hiring
- Companies with capital remain invisible

**After this scrape:**
- 25,748 funded companies mapped
- 425,233 pages of hiring signals
- Complete website content for LLM analysis

---

## 🔄 Strategic Pivot: Adding H1B Sponsorship Data

### The Realization

We have **companies with money** (SEC data). But we need **companies with willingness** (H1B data).

**The gap:** 
- A company raising $50M doesn't automatically mean they sponsor visas
- Some well-funded startups have NEVER sponsored
- Others sponsor dozens of H1Bs every year

**The solution:** Cross-reference our SEC companies with proven H1B sponsors

### New Data Sources: Official US Government

#### 1. **Department of Labor - Labor Condition Applications (LCA)**
**Link:** https://www.dol.gov/agencies/eta/foreign-labor/performance

**What it contains:**
- Every H1B sponsorship application filed
- Company names, job titles, salaries
- Approval/denial status
- Historical data back to 2001

**Why it matters:**
- Proves which companies actually sponsor
- Shows sponsorship frequency (1 vs. 100+ per year)
- Reveals job titles they sponsor (engineer, scientist, analyst)

**Data volume:** 6+ million LCA records

---

#### 2. **USCIS - H1B Employer Data Hub**
**Link:** https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub

**What it contains:**
- Top H1B employers by volume
- Approval rates by company
- Quarterly processing trends
- Geographic distribution

**Why it matters:**
- Identifies reliable sponsors (high approval rates)
- Shows seasonal hiring patterns
- Filters out companies with low success rates

**Updated:** Quarterly

---

#### 3. **DOL - PERM Labor Certification Data**
**Link:** https://www.dol.gov/agencies/eta/foreign-labor/performance

**What it contains:**
- Green card sponsorship applications
- Companies willing to sponsor permanent residency
- Job requirements and qualifications

**Why it matters:**
- PERM sponsorship = long-term commitment
- Shows companies investing in international talent
- Even stronger signal than H1B alone

**Data volume:** Millions of applications

---

#### 4. **DOL - Prevailing Wage Determinations**
**Link:** https://www.dol.gov/agencies/eta/foreign-labor/performance

**What it contains:**
- Required salary ranges by job/location
- Skill level classifications
- Industry wage standards

**Why it matters:**
- Helps students know realistic salary expectations
- Shows which jobs qualify for sponsorship
- Validates company job postings

---

## 🎯 The Killer Combination

### What We're Building

```
SEC Form D Data              H1B/LCA Data              Smart Matching
─────────────────────   +   ──────────────────   =   ─────────────────────

• Company just raised       • Sponsored 15 H1Bs       HIGH PROBABILITY
  $50M Series B              last year                 MATCH! 🌟🌟🌟
                            • All software roles
                            • 95% approval rate

vs.

• Company raised            • Zero H1B history        Maybe needs education
  $30M Series A             • Never filed LCA          Lower priority ⭐
```

### Proposed Scoring System

**🌟🌟🌟 VERY LIKELY (Score: 80-100)**
- ✅ Raised $5M+ (last 2 years)
- ✅ Sponsored 10+ H1Bs (last 2 years)
- ✅ High approval rate (>80%)
- ✅ Multiple relevant job titles

**🌟🌟 LIKELY (Score: 60-79)**
- ✅ Raised $5M+ (last 2 years)
- ✅ Sponsored 3-10 H1Bs (last 3 years)
- ✅ Some relevant roles

**🌟 POSSIBLE (Score: 40-59)**
- ✅ Raised $5M+ (last 2 years)
- ❓ Limited or old H1B history
- ❓ No recent LCA filings

**❌ UNLIKELY (Score: <40)**
- ⚠️ Has funding but never sponsored
- ⚠️ Or low approval rates

---

## 📈 Why This Changes Everything

### Before (SEC Data Only)
```
User searches: "Biotech companies in Boston"
Results: 500 companies with funding
Problem: Which ones actually sponsor?
User action: Apply to all 500, hope for best
```

### After (SEC + H1B Data)
```
User searches: "Biotech companies in Boston"
Results: 500 companies with funding
Filtered: 127 have H1B history 🌟🌟🌟
         89 sponsored recently 🌟🌟
         284 unknown (worth trying) 🌟
User action: Focus on proven 127 first
```

### The Impact

**For students:**
- Stop wasting time on companies that never sponsor
- Focus on proven sponsors first
- See which job titles get sponsored

**For companies:**
- Get matched with qualified candidates
- Learn they're already in H1B databases
- Discover their sponsorship reputation

**For the mission:**
- Higher success rate per application
- Better use of students' limited time
- Faster path to that first success story

---

## 🛠️ Technical Implementation Plan

### Phase 1: Data Collection (Days 5-7)
```python
# Target datasets to download/scrape:
1. DOL LCA Disclosure Data (2022-2025)
2. USCIS H1B Employer Data Hub
3. PERM Labor Certification Data
4. Prevailing Wage Data

# Estimated volume:
- LCA records: 6M+ rows
- Companies: 100K+ unique employers
- Our intersection: ~10-15K matches expected
```

### Phase 2: Cross-Reference (Days 8-10)
```python
# Match SEC companies with H1B sponsors
sec_companies = 25,748
h1b_sponsors = 100,000+

# Expected outcomes:
- Exact matches: 8,000-12,000 companies
- Fuzzy matches: 3,000-5,000 companies
- No H1B history: 10,000-14,000 companies
```

### Phase 3: Scoring Engine (Days 11-14)
```python
# Calculate sponsorship likelihood
factors = {
    'h1b_count_recent': 0.30,      # Volume (last 2 years)
    'approval_rate': 0.25,          # Success rate
    'recency': 0.20,                # Recent activity
    'relevant_titles': 0.15,        # Job match
    'perm_history': 0.10           # Green card signal
}

# Output: Score 0-100 per company
```

---

## 📊 Current Data Assets

### What We Have Now
1. ✅ **25,748 company profiles** (SEC Form D + websites)
2. ✅ **425,233 HTML pages** for LLM analysis
3. ✅ **Funding data** (amounts, stages, dates)
4. ✅ **Geographic data** (city, state)
5. ✅ **Industry classifications**

### What We're Adding (Days 5-10)
1. 🔄 **H1B sponsorship history** per company
2. 🔄 **LCA filing patterns** (frequency, recency)
3. 🔄 **Approval rates** (success metrics)
4. 🔄 **Job title data** (which roles sponsored)
5. 🔄 **Salary ranges** (prevailing wage data)

### Combined Power
```
Company Profile:
├── SEC Data
│   ├── Funding: $80M Series B
│   ├── Location: Cambridge, MA
│   └── Industry: Biotechnology
├── Website Data
│   ├── 23 pages scraped
│   ├── "Careers" page exists
│   └── "We're hiring!" signals
└── H1B Data (NEW!)
    ├── 47 H1Bs sponsored (2022-2024)
    ├── 43 approved (91% rate) 🌟
    ├── Job titles: Research Scientist (23), 
    │   Biotech Engineer (15), Data Analyst (9)
    └── Avg salary: $95K

Score: 95/100 - VERY LIKELY TO SPONSOR 🌟🌟🌟
```

---

## 🎯 Success Metrics Update

### Week 1 Goals (Original)
- [x] Build SEC data pipeline
- [x] Verify 300+ company domains → **Achieved 25,748** ✅
- [x] Scrape company websites
- [ ] Create searchable database (in progress)

### Week 1 Goals (Revised)
- [x] SEC data pipeline (complete)
- [x] Website scraping (complete)
- [🔄] Integrate H1B data sources (Days 5-7)
- [ ] Build cross-reference matching (Days 8-10)
- [ ] Deploy MVP with sponsorship scores (Days 11-14)

### The North Star
**Can we help one international student find visa sponsorship in 80 days?**

**Answer so far:** We have 25,748 funded companies mapped. Now we're adding H1B data to show which ones actually sponsor. This dramatically improves our odds.

---

## 💡 Key Insights from Day 5

### What Worked
1. **Async scraping at scale** - 25K companies in 59 hours
2. **Zero budget** - All free, public data sources
3. **High-quality data** - 16.5 pages per company average
4. **Stable pipeline** - 0 failures, clean runs

### What We Learned
1. **Funding ≠ Sponsorship** - Need to verify actual H1B history
2. **Government data is treasure** - 6M+ LCA records available free
3. **Combination is key** - SEC + H1B = actionable insights
4. **Quality over quantity** - 25K with scores > 40K without

### What's Next
1. **Days 5-7:** Download and clean H1B/LCA data
2. **Days 8-10:** Cross-reference SEC companies with sponsors
3. **Days 11-14:** Build scoring engine and deploy MVP
4. **Days 15-20:** User testing and validation

---

## 📚 Resources

### Official Data Sources
- [DOL Foreign Labor Certification](https://www.dol.gov/agencies/eta/foreign-labor/performance)
- [USCIS H1B Employer Data Hub](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub)
- [H1B Salary Database](https://h1bdata.info/) (community-maintained)
- [My Visa Jobs](https://www.myvisajobs.com/) (aggregated H1B data)

### Technical Stack
```
Data Pipeline:    Python + Pandas + asyncio
H1B Data:         CSV processing (6M+ rows)
Matching:         Fuzzy string matching (company names)
Database:         PostgreSQL (Supabase)
API:              FastAPI
Frontend:         React + Tailwind
Hosting:          Railway (backend) + Vercel (frontend)
Budget:           Still $0/month
```

---

## 🎬 The Story So Far

**Day 1-3:** Built SEC scraper, filtered 568K companies to 41K targets  
**Day 4:** Verified domains, discovered 25,748 working websites  
**Day 5:** Scraped 425K pages, discovered H1B data goldmine  
**Next:** Combine funding data with sponsorship history for smart matching

**The mission:** Turn data into second chances. Every company profile we complete is another opportunity for someone to stay with their family, continue their research, build their career in America.

**Days remaining:** 75  
**Companies mapped:** 25,748  
**Success stories:** 0 (yet)

---

## 🚀 Join the Mission

**Current needs:**
- Data engineers (H1B data processing)
- Backend developers (scoring algorithms)
- Frontend developers (search interface)
- Researchers (company validation)

**Time commitment:** 5-10 hours/week  
**Skills learned:** Data pipelines, web scraping, matching algorithms, production deployment  
**Impact:** Help someone stay in America

**Get involved:** https://www.humanitarians.ai/fellows

---

*"The best time to plant a tree was 20 years ago. The second best time is now. The third best time is when you're racing a 60-day unemployment clock."*

**Project Lead:** Nik Bear Brown  
**Organization:** Humanitarians AI (501c3)  
**Day:** 5 of 80  
**Budget:** $0  
**Impact:** Building...
