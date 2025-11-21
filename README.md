# 80 Days to Stay

> *"A wager against time, a race against bureaucracy, and an adventure in data for good."*

## The Challenge

Like Phileas Fogg's famous 80-day race around the world, we're on a mission against the clock. But instead of circumnavigating the globe, we're building a lifeline for international students and skilled workers facing visa deadlines.

**The stakes?** H1B and OPT visa holders have limited time to find sponsorship before they must leave the country they've come to call home. Traditional job platforms don't show which companies can actually sponsor visas. Time is running out.

**The solution?** A database connecting visa holders with funded startups capable of sponsorship—companies that have the resources but remain invisible to those who need them most.

## The Problem (By The Numbers)

The employment gap for international students isn't about talent—it's about structural barriers:

**The Lottery System:**
- Only **25% chance** of H-1B lottery selection (2024)
- International students must navigate F-1 → OPT → STEM OPT → H-1B pipeline
- Policy threats: $100K H-1B fees proposed, OPT restrictions looming

**The Employment Gap:**
- **44.6%** of international students employed after graduation
- **62.1%** of domestic students employed (same degrees, same schools)
- International students apply to **2x as many jobs** (45 vs 22 applications)
- But receive **30% fewer offers**
- Only **38.1%** land full-time roles vs **53.1%** of domestic peers

**The Real Problem:**
This isn't a skills gap—it's an information gap. International students are MORE engaged with career services and recruiting. The difference? **Employer ignorance and automated filtering.**

## Why Startups Don't Sponsor (Even Though They Should)

Funded startups desperately need talent. They have the money. But they don't hire international students because:

**1. Misconceptions About Cost & Complexity**
- Reality: OPT/STEM OPT requires NO employer sponsorship
- Reality: Students on F-1/OPT are FICA-exempt (saves employers ~7.65% in payroll taxes)
- Perception: "Immigration sponsorship is expensive and legally risky"
- Result: ATS systems auto-reject anyone who checks "requires sponsorship"

**2. No In-House Immigration Knowledge**
- Big tech has dedicated immigration counsel and standardized policies
- Startups have no HR/legal capacity to understand visa regulations
- Unfamiliarity breeds fear: "What if we make a mistake?"

**3. Perceived Risk of Training & Loss**
- Worry: "We'll train them for a year, then lose them in the H-1B lottery"
- Reality: 1-3 years of OPT/STEM OPT work authorization before lottery
- But startups with 12-18 month runways see visa uncertainty as existential risk

**4. Path Dependence**
- Employers who have hired international students before do it again
- Employers who never have stay that way
- Only ~25-33% of US employers even consider international candidates

**The Result:** All international talent funnels to the same 100 companies with established immigration pipelines, while thousands of funded startups that NEED talent sit on the sidelines due to misconceptions.

## The Mission

Build a searchable platform that reveals:
- **Funded startups** ($5M+) with resources to sponsor
- **Real-time job openings** at these companies  
- **Direct founder contacts** to bypass HR gatekeepers
- **Sponsorship likelihood scores** based on funding, growth, and hiring patterns

All using **free, public SEC data** and open-source tools.

## The Timeline

- **Week 1:** MVP with 300+ companies (Boston, SF, NYC biotech)
- **Week 4:** 500+ companies, 10+ active users, validation metrics
- **Week 11:** Proof of concept—at least one H1B transfer secured
- **Day 80:** Success stories, growth metrics, sustainable model

## Why This Matters

**The Structural Mismatch:**

There are thousands of funded startups with:
- ✅ Fresh capital ($5M-$50M+ recently raised)
- ✅ Urgent hiring needs (they're scaling)
- ✅ Resources to sponsor (they can afford $5K-$10K in fees)
- ❌ Zero visibility to international candidates

Meanwhile, there are talented international students who:
- ✅ Have advanced degrees from top US universities
- ✅ Are STEM-trained and work-authorized (OPT/STEM OPT)
- ✅ Cost LESS to hire than domestic workers (FICA exemption)
- ❌ Get auto-rejected before their skills are even evaluated

**The Hidden Opportunity:**

When employers learn the truth about OPT:
- "Wait, I don't need to sponsor them NOW?"
- "They save me payroll taxes?"
- "I have 1-3 years before sponsorship is even needed?"
- "Why isn't HR telling me this?"

**What We're Building:**

We're not just a database—we're fixing information asymmetry:
- Show international candidates which startups have money to hire
- Show startups which candidates don't need immediate sponsorship
- Turn "only big tech sponsors" into "funded startups are my best bet"

Every year, talented professionals—researchers, engineers, healthcare workers—face deportation not because they lack skills, but because they lack information. We're turning SEC filings into second chances.

## The Technology

**Data Pipeline:** Python + SEC EDGAR API (free)  
**Database:** PostgreSQL on Supabase (free tier)  
**Backend:** FastAPI on Railway (free tier)  
**Frontend:** React + Tailwind on Vercel (free tier)  
**Budget:** ~$0/month (vs $99/month for commercial data)

## Who This Helps

**International Students & Workers:**
- PhD researchers who can't find biotech sponsors
- STEM grads applying to 50+ jobs with no responses
- OPT holders with 60-day "unemployment clocks" ticking
- H-1B lottery losers who need backup options fast

**Funded Startups:**
- Series A biotech companies desperate for PhD-level scientists
- AI startups that need ML engineers but "don't sponsor"
- Medical device companies that don't know OPT exists
- Any founder who's rejected great candidates due to visa myths

**The Broader Impact:**
- Keep talent in the US innovation ecosystem
- Help startups access overlooked talent pools
- Reduce brain drain of US-trained professionals
- Make the "American Dream" accessible beyond just FAANG

## The Opportunity (By The Numbers)

**What we're revealing:**
```
SEC Form D Filings (Last 12 months):
├── ~15,000 total private offerings in US
├── ~1,500 biotech/pharma companies
├── ~500 raised $5M+ (our target)
└── ~200-300 in Boston/SF/NYC biotech hubs

Hidden from traditional job searches:
├── 90% don't advertise "visa sponsorship"
├── 75% have no immigration keywords on job posts
├── Most auto-reject "requires sponsorship" candidates
└── Zero visibility on platforms like LinkedIn/Indeed

The match:
├── These companies JUST raised capital
├── They're actively hiring (that's what the money is for)
├── They CAN afford sponsorship ($5K-10K << $5M-50M raised)
└── They just don't know OPT doesn't require it
```

**Our thesis:** Every Form D filing represents a company that's invisible to international job seekers but desperately needs talent. We're making them visible.

## Join the Adventure

**Why volunteer with us?**

**For the mission:**
- Help people stay with families instead of forced deportation
- Fix a broken system that wastes US-trained talent
- Turn data into human impact in real-time
- See your code save someone's visa status

**For the skills:**
- Real-world data engineering (SEC APIs, ETL pipelines, PostgreSQL)
- Full-stack development (FastAPI, React, modern deployment)
- Work with production data serving actual users
- Build portfolio projects that demonstrate social impact

**We need:**
- **Data engineers** - Python, web scraping, API integration, ETL pipelines
- **Backend developers** - FastAPI, PostgreSQL, RESTful APIs
- **Frontend developers** - React, Tailwind CSS, responsive design
- **Researchers** - Company validation, contact enrichment, data quality
- **Community builders** - Testing, documentation, user feedback

**No experience required—just commitment.** If you can code "Hello World" or write a clear README, you can contribute. We'll teach the rest.

**Time commitment:** 5-10 hours/week for 80 days. More if you want, less if you need. This is agile, async, and built around real lives.

## Why We Know This Will Work

**The data doesn't lie:**

Our thesis is backed by research from NAFSA, Interstride, IZA, and multiple employer surveys showing:

1. **Employers who hire international students once, do it again** - The barrier is ignorance, not capability
2. **75% of employers don't understand OPT/CPT rules** - Education works
3. **Startups with recent funding ARE hiring** - That's what Series A/B money is for
4. **International students are MORE qualified, not less** - Same degrees, higher engagement, lower offers
5. **The cost myth is false** - F-1/OPT students save employers payroll taxes

**The market failure is information asymmetry.** We're fixing it with public data.

**Sources:** NAFSA International Student Employment Survey, Interstride 2025 Career Outcomes Report, IZA Institute Employment Research, SciTech Minnesota Employer Guides, multiple industry surveys on visa sponsorship attitudes.

## The Wager

**Can we build a platform that saves at least one person's visa status in 80 days?**

The odds are in our favor:
- 200-300 funded biotech companies in our Week 1 database
- Each company averages 5-10 open roles
- That's 1,000-3,000 jobs invisible to international candidates
- We only need to facilitate ONE successful match

Unlike Phileas Fogg's £20,000 wager, ours costs $0 in data fees. But the stakes? Someone gets to stay with their family, continue their research, build their career in America.

**That's a bet worth taking.**

---

**Project Lead:** Nik Bear Brown  
**Organization:** Humanitarians AI (501c3)  
**Timeline:** 80 days  
**Budget:** ~$0/month  
**Impact:** Priceless

## Get Involved

🚀 **Ready to join?** Check our [https://www.humanitarians.ai/fellows](https://www.humanitarians.ai/fellows)  
📊 **Follow progress:** [https://github.com/nikbearbrown/80-Days-to-Stay](https://github.com/nikbearbrown/80-Days-to-Stay)

*"In this adventure, the real treasure isn't reaching the destination—it's the lives we change along the way."*

**The facts:**
- International students: 44.6% employment rate, 2x applications, 30% fewer offers
- Funded startups: Thousands with capital, desperate for talent, don't sponsor due to myths
- The gap: Information asymmetry we can fix with public data and code

**80 days. Zero budget. One mission: Turn SEC filings into second chances.**

---

### Project Status

```
Week 1: [████░░░░░░] 40% - Data pipeline built, 300+ companies loaded
Week 2: [░░░░░░░░░░]  0% - Expand coverage, build API
Week 3: [░░░░░░░░░░]  0% - Launch frontend, onboard users
Week 4: [░░░░░░░░░░]  0% - Validate with real applications
```

**Next Milestone:** Week 1 MVP - Launch by Day 7

---

*This project is part of Humanitarians AI's commitment to using technology and data for social good.*
