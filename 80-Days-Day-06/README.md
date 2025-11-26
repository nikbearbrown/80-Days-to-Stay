# Day 06

# 80 Days to Stay - Day 6 Progress Report

> *"We're not just finding jobs. We're cracking the entire application system."*

## 🎯 Mission Status: The ATS Revelation

**Progress:** Week 1 → Week 2 Transition  
**New Discovery:** ATS systems are a **triple win**, not just a data source

---

## 💡 The Big Realization

We started thinking Greenhouse was just about **job listings**. But it's actually three critical insights in one API call:

### Win #1: Live Job Postings ✅
*"What jobs are open RIGHT NOW?"*

### Win #2: Resume Strategy Intelligence ✅
*"What format should my resume be in?"*

### Win #3: Company Sophistication Signal ✅
*"How modern is their hiring process?"*

Let's break down why each matters for international students.

---

## 🎯 Win #1: Live Job Postings (The Obvious One)

### What We Get
```json
GET https://boards-api.greenhouse.io/v1/boards/{company}/jobs

Returns:
{
  "jobs": [
    {
      "title": "Senior Software Engineer",
      "location": "Cambridge, MA",
      "department": "Engineering",
      "updated_at": "2025-11-25",
      "absolute_url": "https://boards.greenhouse.io/company/jobs/123",
      "content": "Full job description..."
    }
  ]
}
```

### Why It Matters
- **Real-time openings** - Apply today, not "someday"
- **Structured data** - Clean JSON, no HTML parsing
- **Direct apply links** - One-click applications
- **Auto-updates** - Jobs appear/disappear as posted/filled
- **Zero scraping** - APIs are faster and more reliable

### The Impact
```
Before: "This company might be hiring"
After:  "This company has 5 open positions posted 2 days ago"
```

**For students with 60-day unemployment clocks:** Every day counts. Real-time job data means zero wasted applications on filled positions.

---

## 📝 Win #2: Resume Strategy Intelligence (The Hidden Gold)

### The ATS Problem (From Prof. Bear's Research)

**The reality:**
- Big companies (Microsoft, Amazon, Tesla) often use **legacy ATS systems**
- Some still use **pre-2020 technology**, even OCR-based parsers
- These systems **can't read sophisticated resumes**
- They look for **keyword matching**, simple layouts, plain text

**The paradox:**
> *"Modern LLMs can read any resume format. But companies use 10-year-old systems that can't."*

### Strategic Minimalism Approach

**What works for BOTH humans and ATS:**
- ✅ Clear typefaces (readable by OCR and humans)
- ✅ Clean layouts (parseable by ATS, pleasant for humans)
- ✅ Standard section headers (EXPERIENCE, EDUCATION, SKILLS)
- ✅ Simple formatting (no tables, columns, or graphics)

**What works for humans but FAILS ATS:**
- ❌ Creative layouts
- ❌ Multiple columns
- ❌ Graphics and icons
- ❌ Embedded tables
- ❌ Fancy fonts

**The strategy:** Research which ATS the company uses, then format accordingly.

### How ATS Detection Changes Resume Strategy

#### Scenario A: Company Uses Greenhouse (Modern)
```
Company: Crossbow Therapeutics
ATS: Greenhouse (2023)

Resume Strategy:
├── Modern LLM-based parsing ✅
├── Can handle sophisticated layouts
├── Reads PDFs perfectly
├── Extracts structured data reliably
└── RECOMMENDATION: Use "Strategic Minimalism" 
    → Clean but professional design
    → Stand out visually while staying parseable
```

#### Scenario B: Company Uses Legacy Workday (Pre-2020)
```
Company: [Large Corporation]
ATS: Workday (2018 version)

Resume Strategy:
├── OCR-based parsing ⚠️
├── Keywords matter heavily
├── Simple layout required
├── Plain text preferred
└── RECOMMENDATION: Use "ATS-Optimized"
    → Plain text format
    → Keyword-heavy
    → No creativity, pure function
```

#### Scenario C: Startup (No ATS / Manual Review)
```
Company: [3-person startup]
ATS: None (founders read directly)

Resume Strategy:
├── Human review only 👤
├── Design matters more than keywords
├── Storytelling > bullet points
└── RECOMMENDATION: Use "Human-First"
    → Creative, memorable design
    → Show personality
    → Make it stand out
```

### The Intelligence Layer We're Building

**For each company in our database:**
```python
company_profile = {
    'name': 'Crossbow Therapeutics',
    'ats_system': 'greenhouse',  # ← NEW!
    'ats_version': '2023',        # ← NEW!
    'ats_capabilities': {
        'pdf_parsing': True,
        'llm_based': True,
        'legacy_ocr': False
    },
    'resume_recommendation': 'strategic_minimalism'  # ← NEW!
}
```

**What this enables:**
```
User uploads resume → Platform detects format → 
Analyzes target company's ATS →
Suggests: "This company uses Greenhouse. Your creative resume 
          will work fine, but consider moving skills section 
          higher for better keyword matching."

vs.

"This company uses legacy Workday. Your resume has 
 multiple columns and graphics that will fail parsing. 
 Here's an ATS-safe version optimized for their system."
```

### Real-World Example

**Student applying to two companies:**

**Company A: Modern Biotech Startup (Greenhouse)**
- ✅ Uses resume with clean design, subtle colors, clear sections
- ✅ ATS parses it perfectly
- ✅ Hiring manager sees professional, readable resume
- ✅ Gets interview

**Company B: Fortune 500 (Legacy Workday 2017)**
- ❌ Uses same creative resume
- ❌ ATS fails to parse columns correctly
- ❌ Data extracted incorrectly (experience years wrong)
- ❌ Auto-rejected before human sees it

**With our platform:**
- Platform detects Company B uses legacy ATS
- Suggests: "Convert to plain-text format for this application"
- Student submits ATS-optimized version
- ✅ Gets past ATS filter
- ✅ Human reviewer sees correct data

---

## 🔍 Win #3: Company Sophistication Signal (The Surprise)

### Why ATS Choice Reveals Company Culture

**Modern ATS (Greenhouse, Lever, Ashby) = Progressive Company**
```
Signals:
├── Invested in modern hiring tools ($$)
├── Cares about candidate experience
├── Likely uses data-driven hiring
├── Probably tech-savvy organization
└── More likely to understand visa processes? 🤔
```

**Legacy ATS (Old Workday, iCIMS) = Traditional Company**
```
Signals:
├── Resistant to change
├── "If it ain't broke..." mentality
├── May have bureaucratic processes
├── Possibly less flexible on visa policies
└── More likely to auto-reject "requires sponsorship"? 🤔
```

**No ATS / Custom System = Wild Card**
```
Signals:
├── Either very small OR very custom
├── Could be cutting-edge tech company
├── Could be disorganized startup
└── Need to research case-by-case
```

### Hypothesis: ATS Modernity Correlates with Visa Friendliness

**Our theory (to be tested):**

Companies that invest in modern hiring infrastructure are **more likely** to:
- Understand complex employment regulations (like OPT vs. H1B)
- Have HR capacity to handle sponsorship
- Be data-driven about candidate evaluation (less bias)
- Have experience with international hiring

**We can test this:**
```python
# Cross-reference our data:
modern_ats_companies = companies.filter(ats IN ['greenhouse', 'lever', 'ashby'])
legacy_ats_companies = companies.filter(ats IN ['workday_old', 'icims'])

# Compare H1B sponsorship rates:
modern_ats_h1b_rate = calculate_h1b_sponsorship_rate(modern_ats_companies)
legacy_ats_h1b_rate = calculate_h1b_sponsorship_rate(legacy_ats_companies)

# Our hypothesis: modern_ats_h1b_rate > legacy_ats_h1b_rate
```

If true, this becomes **another scoring factor** in our algorithm.

---

## 🛠️ Major ATS Systems: The Landscape

### Tier 1: Modern, API-Friendly (Target These First)

#### **Greenhouse** 🌟🌟🌟
**API:** https://developers.greenhouse.io/  
**Public Jobs:** `https://boards-api.greenhouse.io/v1/boards/{company}/jobs`  
**Market:** Startups, mid-size tech, modern biotech  
**Parsing:** LLM-based, excellent PDF handling  
**Resume Strategy:** Strategic minimalism works well

**Estimated coverage in our data:** 8,000-12,000 companies (30-45%)

#### **Lever** 🌟🌟🌟
**API:** https://hire.lever.co/developer/documentation  
**Public Jobs:** `https://api.lever.co/v0/postings/{company}?mode=json`  
**Market:** Startups, tech companies  
**Parsing:** Modern, good PDF support  
**Resume Strategy:** Similar to Greenhouse

**Estimated coverage:** 3,000-5,000 companies (12-20%)

#### **Ashby** 🌟🌟
**API:** https://developers.ashbyhq.com/  
**Market:** Newer, growing fast in startup world  
**Parsing:** Very modern, AI-powered  
**Resume Strategy:** Most flexible

**Estimated coverage:** 1,000-2,000 companies (4-8%)

---

### Tier 2: Enterprise Systems (Require Research)

#### **Workday**
**Market:** Large corporations, universities  
**Parsing:** **Highly variable** - depends on version  
**Modern versions (2022+):** Good parsing  
**Legacy versions (2020-):** OCR-based, problematic  
**Resume Strategy:** **Research version first!**

**Key issue:** Same name, dramatically different capabilities depending on when deployed.

#### **iCIMS**
**Market:** Mid-large companies  
**Parsing:** Generally good, but can be keyword-heavy  
**Resume Strategy:** Keyword optimization important

#### **SmartRecruiters**
**Market:** Enterprise  
**Public Jobs:** XML feeds available  
**Parsing:** Decent

---

### Tier 3: Unknown / Custom

**Many companies:** ~5,000-10,000 in our dataset (20-40%)
- Custom built systems
- Very old systems
- No public job board
- Manual HR processes

**Strategy:** Case-by-case research needed

---

## 📊 The Triple-Win Data Model

### Enhanced Company Profile

```json
{
  "company": {
    "name": "Crossbow Therapeutics",
    "industry": "Biotechnology",
    "location": "Cambridge, MA"
  },
  
  "funding": {
    "amount": 80000000,
    "stage": "Series B",
    "date": "2025-09-17"
  },
  
  "h1b_history": {
    "total_sponsored": 23,
    "recent_2_years": 18,
    "approval_rate": 0.91,
    "job_titles": ["Research Scientist", "Bioinformatics", "Lab Tech"]
  },
  
  "ats_data": {  // ← NEW SECTION!
    "system": "greenhouse",
    "system_modernity": "modern",
    "public_api": true,
    "resume_parsing": "llm_based",
    "pdf_support": true,
    
    "live_jobs": [
      {
        "title": "Senior Research Scientist",
        "location": "Cambridge, MA",
        "department": "R&D",
        "posted": "2025-11-23",
        "url": "https://boards.greenhouse.io/crossbow/jobs/123",
        "matches_h1b_history": true  // ← SMART!
      }
    ],
    
    "resume_recommendation": {
      "format": "strategic_minimalism",
      "reason": "Modern ATS can handle clean designs",
      "tips": [
        "Use clear section headers",
        "PDF format recommended",
        "Subtle design elements okay",
        "Ensure keywords match job description"
      ]
    },
    
    "hiring_sophistication_score": 85  // ← NEW METRIC!
  },
  
  "overall_score": 95
}
```

### How This Transforms User Experience

#### Before (Just SEC + H1B Data)
```
User: "Show me biotech jobs in Boston"

Platform: "Here are 50 companies with H1B history"

User: "Which ones are hiring?"
Platform: "Check their websites"

User: "What resume should I use?"
Platform: "¯\_(ツ)_/¯"
```

#### After (SEC + H1B + ATS Intelligence)
```
User: "Show me biotech jobs in Boston"

Platform: 
"Found 50 companies with H1B history
 → 34 are actively hiring (127 open positions)
 → Sorted by best match for your profile
 
🌟🌟🌟 Crossbow Therapeutics (Score: 95/100)
├── Funding: $80M Series B
├── H1B History: 23 sponsored (91% approval)
├── ATS: Greenhouse (modern, candidate-friendly)
│
├── 📋 5 LIVE JOBS:
│   ├── Senior Research Scientist [APPLY NOW]
│   │   Posted: 2 days ago
│   │   Match: HIGH (they've sponsored 15x for this role)
│   │
│   ├── Computational Biologist [APPLY NOW]
│   │   Posted: 5 days ago
│   │   Match: MEDIUM (they've sponsored 5x similar)
│   │
│   └── Associate Scientist [APPLY NOW]
│       Posted: 1 week ago
│       Match: HIGH (entry-level, often sponsored)
│
└── 📝 RESUME TIPS FOR THIS COMPANY:
    ├── Format: Use your professional design resume
    ├── Their ATS: Greenhouse (reads PDFs perfectly)
    ├── Keywords: Include "antibody discovery", "protein engineering"
    ├── Tip: They value research publications - list yours prominently
    └── [OPTIMIZE MY RESUME FOR THIS JOB] ← button

User: *clicks optimize, gets tailored resume, applies in 5 minutes*
```

---

## 🎯 The Complete Intelligence Stack

### Layer 1: Financial Capability
**Source:** SEC Form D  
**Question:** Can they afford to hire?  
**Answer:** $80M raised = Yes ✅

### Layer 2: Historical Willingness
**Source:** H1B/LCA Database  
**Question:** Do they actually sponsor?  
**Answer:** 23 H1Bs in 2 years = Yes ✅

### Layer 3: Current Openings
**Source:** ATS APIs (Greenhouse, Lever)  
**Question:** Are they hiring NOW?  
**Answer:** 5 open positions = Yes ✅

### Layer 4: Application Strategy (NEW!)
**Source:** ATS System Detection  
**Question:** How should I apply?  
**Answer:** Modern ATS + keyword optimization = Strategic minimalism ✅

### Layer 5: Success Prediction (NEW!)
**Source:** Cross-referencing all data  
**Question:** Will my application succeed?  
**Answer:** 
- Job matches past H1B sponsorships ✅
- Company actively hiring for this role ✅
- Modern ATS won't auto-reject ✅
- Resume optimized for their system ✅
= **HIGH PROBABILITY** 🎯

---

## 🚀 Implementation Roadmap

### Days 6-8: ATS Detection & Integration

**Task 1: Build ATS Detection**
```python
def detect_ats(domain):
    """
    Check which ATS system a company uses
    """
    ats_endpoints = {
        'greenhouse': f'https://boards.greenhouse.io/{domain}',
        'lever': f'https://jobs.lever.co/{domain}',
        'ashby': f'https://jobs.ashbyhq.com/{domain}',
        'workday': f'https://{domain}.wd1.myworkdayjobs.com'
    }
    
    for ats, url in ats_endpoints.items():
        if check_url_exists(url):
            return {
                'system': ats,
                'url': url,
                'api_available': ats in ['greenhouse', 'lever', 'ashby']
            }
    
    return {'system': 'unknown', 'api_available': False}
```

**Task 2: Fetch Live Jobs**
```python
def get_greenhouse_jobs(company_slug):
    """
    Get all current openings from Greenhouse
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    response = requests.get(url)
    
    if response.status_code == 200:
        return parse_greenhouse_jobs(response.json())
    return []

def parse_greenhouse_jobs(data):
    """
    Extract relevant fields from Greenhouse response
    """
    return [
        {
            'id': job['id'],
            'title': job['title'],
            'location': job['location']['name'],
            'department': job['departments'][0]['name'] if job['departments'] else 'Other',
            'posted_date': job['updated_at'],
            'url': job['absolute_url'],
            'description': job['content']
        }
        for job in data['jobs']
    ]
```

**Task 3: Resume Strategy Recommendations**
```python
def generate_resume_strategy(ats_data, job_posting):
    """
    Generate resume optimization tips based on ATS system
    """
    if ats_data['system'] == 'greenhouse':
        return {
            'format': 'strategic_minimalism',
            'tips': [
                'PDF format recommended',
                'Clean, professional design works well',
                'Clear section headers (EXPERIENCE, EDUCATION, SKILLS)',
                f"Include keywords: {extract_keywords(job_posting['description'])}",
                'Highlight metrics and achievements'
            ]
        }
    
    elif ats_data['system'] == 'workday':
        # Need to check version...
        return {
            'format': 'ats_optimized',
            'tips': [
                'Plain text formatting recommended',
                'Avoid tables, columns, graphics',
                'Heavy keyword optimization needed',
                'Standard fonts only (Arial, Times New Roman)',
                'Single column layout'
            ],
            'warning': 'This company may use legacy Workday - research their version'
        }
    
    elif ats_data['system'] == 'unknown':
        return {
            'format': 'safe_default',
            'tips': [
                'Use strategic minimalism approach',
                'Optimize for both humans and parsers',
                'Include keywords but maintain readability',
                'PDF or DOCX both acceptable'
            ]
        }
```

### Days 9-10: Cross-Reference with H1B Data

**Match job postings with H1B history:**
```python
def match_jobs_with_h1b_history(job_posting, h1b_history):
    """
    Check if current job matches previously sponsored roles
    """
    job_title_normalized = normalize_job_title(job_posting['title'])
    
    matching_sponsorships = [
        sponsorship for sponsorship in h1b_history
        if similar_job_titles(job_title_normalized, sponsorship['title'])
    ]
    
    return {
        'matches_history': len(matching_sponsorships) > 0,
        'times_sponsored': len(matching_sponsorships),
        'confidence': calculate_confidence(matching_sponsorships),
        'message': f"This company has sponsored {len(matching_sponsorships)} " 
                  f"{job_title_normalized}s in the past 3 years"
    }
```

### Days 11-14: Build Resume Optimization Tool

**The "Strategic Minimalism" resume analyzer:**
```python
def analyze_resume(resume_pdf, target_job, target_ats):
    """
    Analyze resume and provide optimization suggestions
    """
    # Extract text from PDF
    resume_text = extract_text_from_pdf(resume_pdf)
    
    # Parse resume structure
    resume_data = parse_resume_structure(resume_text)
    
    # Check ATS compatibility
    ats_issues = check_ats_compatibility(resume_data, target_ats)
    
    # Keyword analysis
    job_keywords = extract_keywords(target_job['description'])
    resume_keywords = extract_keywords(resume_text)
    missing_keywords = set(job_keywords) - set(resume_keywords)
    
    return {
        'ats_compatibility': {
            'score': calculate_ats_score(ats_issues),
            'issues': ats_issues,
            'recommendations': generate_ats_fixes(ats_issues)
        },
        'keyword_match': {
            'score': len(resume_keywords & job_keywords) / len(job_keywords),
            'missing': list(missing_keywords),
            'suggestions': f"Add these keywords: {', '.join(list(missing_keywords)[:5])}"
        },
        'overall_recommendation': generate_overall_recommendation(
            ats_issues, missing_keywords, target_ats
        )
    }
```

---

## 📊 Expected Impact

### On Our 25,748 Companies

**ATS Detection Results (Projected):**
```
Estimated ATS Distribution:
├── Greenhouse: ~10,000 companies (38%)
│   └── Can fetch ~40,000-60,000 live jobs
├── Lever: ~4,000 companies (16%)
│   └── Can fetch ~15,000-25,000 live jobs
├── Ashby: ~1,500 companies (6%)
│   └── Can fetch ~5,000-8,000 live jobs
├── Other modern ATS: ~3,000 companies (12%)
├── Legacy/unknown: ~7,248 companies (28%)
└── Total API-accessible jobs: 60,000-93,000 positions
```

### On User Success Rates

**Current (without ATS intelligence):**
```
100 applications sent →
  80 pass ATS (20% auto-rejected due to format)
  40 seen by human (50% filtered by keywords)
  4 interviews (10% response rate)
  1 offer (25% conversion)
= 1% overall success rate
```

**With ATS intelligence:**
```
100 applications sent →
  95 pass ATS (optimized for each system)
  60 seen by human (better keyword matching)
  9 interviews (15% response rate - better targeting)
  2-3 offers (higher quality matches)
= 2-3% overall success rate

PLUS: Less time wasted per application
PLUS: Applications only to companies actually hiring
PLUS: Focus on companies with H1B history
```

**Net result:** 2-3x more offers with 50% less time spent applying

---

## 🎯 Week 2 Goals (Revised)

### Original Week 2 Goals
- [🔄] Expand to 500+ companies
- [ ] Build searchable API
- [ ] Launch frontend MVP

### Enhanced Week 2 Goals
- [✅] 25,748 companies (exceeded goal!)
- [🔄] ATS detection for all companies (Days 6-8)
- [🔄] Integrate live job feeds (Days 6-8)
- [🔄] Build resume optimization engine (Days 9-14)
- [ ] Launch MVP with "triple-win" features (Day 14)

### The New MVP Features

**Core features:**
1. Search companies by location, industry, funding
2. Filter by H1B sponsorship history
3. See live job openings (Greenhouse, Lever, Ashby)
4. Get ATS-specific resume recommendations
5. Track which jobs match your profile

**Killer feature:**
> *"Upload your resume → Select target job → Get optimized version for that company's ATS → Apply with confidence"*

---

## 💡 Why This Is Revolutionary

### Before: Spray and Pray
```
Student approach:
1. Find 100 random companies
2. Send same resume to all
3. 80% auto-rejected by ATS
4. 15% wrong format for that company
5. 5% actually considered
6. Hope for the best
```

### After: Surgical Precision
```
Our platform approach:
1. Show only funded companies with H1B history
2. Show only companies actively hiring NOW
3. Show only jobs matching your background
4. Optimize resume for each company's ATS
5. Apply with confidence to 10-20 best matches
6. 2-3x higher success rate
```

### The Time Savings

**Without our platform:**
- Research 100 companies: 20 hours
- Apply to 100 jobs: 40 hours
- Wait for responses: 4-6 weeks
- Result: 1-2 interviews maybe

**With our platform:**
- Platform pre-researched 25,748 companies
- Find 20 perfect matches: 30 minutes
- Optimize resume for each: 2 hours
- Apply to 20 jobs: 3 hours
- Result: 3-6 interviews likely

**Savings:** 55 hours + higher success rate + less stress

---

## 🎬 The Story So Far

**Days 1-3:** Built SEC scraper, filtered 568K companies  
**Day 4:** Verified 25,748 working domains  
**Day 5:** Scraped 425K pages, discovered H1B data goldmine  
**Day 6:** Realized ATS systems are a triple-win intelligence source  
**Next:** Build the smartest job platform for international students ever created

**The mission:** Every feature we add increases the probability that someone finds sponsorship before their visa expires.

**Days remaining:** 74  
**Companies mapped:** 25,748  
**Live jobs accessible:** 60,000-93,000  
**Success stories:** 0 (yet)  
**Probability of success:** Increasing daily 📈

---

## 🚀 Volunteer Opportunities

**New roles needed for Week 2:**

### ATS Integration Specialists
- Build Greenhouse/Lever API integrations
- Parse job postings into structured data
- Create job matching algorithms

### Resume Optimization Engineers  
- Build resume parsing (PDF → text → structure)
- Implement keyword extraction
- Create ATS compatibility checkers
- Design optimization algorithms

### Data Scientists
- Analyze ATS vs. H1B sponsorship correlations
- Build scoring algorithms
- Create prediction models

**Time commitment:** 5-10 hours/week  
**Impact:** Help international students beat the ATS systems that reject them

**Join:** https://www.humanitarians.ai/fellows

---

*"The difference between a good job platform and a great one isn't the quantity of listings. It's understanding the entire system - the money, the willingness, the process, and how to beat it."*

**Project Lead:** Nik Bear Brown  
**Organization:** Humanitarians AI (501c3)  
**Day:** 6 of 80  
**Budget:** Still $0  
**Innovation:** Triple-win ATS strategy  
**Impact:** Building...
