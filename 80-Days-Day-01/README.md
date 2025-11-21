# Day 1: Understanding The Data

## What We're Building With

> *"Follow the money. Every startup that raises venture capital leaves a paper trail—and that trail leads straight to the SEC."*

## What is SEC Form D?

**Form D** is a notice that U.S. companies must file with the Securities and Exchange Commission (SEC) within **15 days** of raising private capital from investors. Think of it as the government's registry of who's raising money, how much, and when.

### The Law in Plain English:

When a startup raises money from VCs or angel investors, they have two choices:
1. **Register publicly** like an IPO (expensive, complex, public disclosure)
2. **Claim an exemption** under Regulation D (simpler, stays private)

Nearly **every VC-backed startup** in America chooses option 2 and files Form D to document the exemption.

## Why This Data is Gold for Visa Sponsorship

**The Simple Truth:** Companies that just raised $5M+ have money. Companies with money can afford to:
- Hire new employees
- Pay visa sponsorship fees ($5K-$10K)
- Navigate immigration paperwork
- Take risks on H1B lottery

**But here's the problem:** These companies don't show up on traditional job boards with "visa sponsorship" tags. They're growing quietly, building teams, and often overlooked by visa holders searching on LinkedIn or Indeed.

**That's where we come in.** We're turning SEC filings into job leads.

## What Information Form D Contains

Every Form D filing gives us:

### Company Identity
- **Legal name** - Exact company name
- **Location** - City and state (Boston biotech? SF AI startup?)
- **Year incorporated** - How new/established they are
- **Industry group** - Biotech, software, medical devices, etc.

### Funding Details
- **Total offering amount** - How much they're trying to raise
- **Amount sold** - How much they've actually raised (the key number!)
- **Amount remaining** - Is the round still open?
- **Date of first sale** - When did money start flowing?

### Investor Information
- **Number of investors** - 3 investors = institutional VCs, 50+ = party round
- **Exemption type** - 506(b) vs 506(c) (tells us their strategy)

### Leadership
- **Executive officers** - The founders and C-suite
- **Directors** - Board members (often includes VC partners!)
- **Names and titles** - Direct contact points

## Why This is Better Than Alternatives

| Feature | Form D (Free) | Crunchbase ($99/mo) | LinkedIn | AngelList |
|---------|---------------|---------------------|----------|-----------|
| **Cost** | $0 | $99/month | $0 | $0 |
| **Funding amounts** | ✅ Exact | ✅ Exact | ❌ Approximate | ❌ Varies |
| **Recency** | ✅ 15 days | ⚠️ Delayed | ❌ No data | ⚠️ Self-reported |
| **Completeness** | ✅ All US companies | ⚠️ Curated subset | ❌ No financial | ⚠️ Opt-in only |
| **Official source** | ✅ Government | ❌ Aggregated | ❌ User-generated | ❌ Self-reported |
| **Founder names** | ✅ Yes | ⚠️ Sometimes | ✅ Yes | ⚠️ Sometimes |
| **Investor count** | ✅ Yes | ⚠️ Sometimes | ❌ No | ❌ No |

**Bottom line:** Form D is the **most complete, most current, most reliable** source of startup funding data in America. And it's completely free.

## Accessing the Data

### Main Portal
🔗 **https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets**

### Direct Download Format
```
https://www.sec.gov/files/structureddata/data/form-d-data-sets/[YEAR]q[QUARTER]_d.zip
```

### For Our Week 1 MVP (Last 9 Months)

**2025 Q1** (Jan-Mar 2025)  
https://www.sec.gov/files/structureddata/data/form-d-data-sets/2025q1_d.zip

**2024 Q4** (Oct-Dec 2024)  
https://www.sec.gov/files/structureddata/data/form-d-data-sets/2024q4_d.zip

**2024 Q3** (Jul-Sep 2024)  
https://www.sec.gov/files/structureddata/data/form-d-data-sets/2024q3_d.zip

**2024 Q2** (Apr-Jun 2024)  
https://www.sec.gov/files/structureddata/data/form-d-data-sets/2024q2_d.zip

## What's Inside Each Zip File

When you download a quarterly file, you get:

```
2024q4_d.zip
├── OFFERING.tsv          # Main company/offering data
├── SIGNATURES.tsv        # Who signed the filing
├── PRIMARY_ISSUER.tsv    # Company details
├── RELATED_PERSONS.tsv   # Founders, executives, directors
├── SUBMISSION.tsv        # Filing metadata
└── [XML files/]          # Raw filings (if you want them)
```

**The TSV files are already parsed!** You don't have to deal with XML unless you want to. The SEC has done the heavy lifting for us.

## Data Coverage & Quality

### Historical Coverage
- **Start date:** 2008 (17 years of data!)
- **Update frequency:** Quarterly
- **Total filings:** ~2 million+ Form D submissions
- **Cost:** FREE (no API key, no limits)

### What We'll Find for Week 1

Based on typical quarterly patterns:

**Expected in 3 quarters (Q2-Q4 2024, Q1 2025):**
- ~40,000-50,000 total Form D filings
- ~500-700 biotech companies nationwide
- **~200-300 in Boston/SF/NYC with $5M+ funding**

**Industries well-represented:**
- ✅ Biotechnology (our focus!)
- ✅ Pharmaceutical  
- ✅ Medical devices
- ✅ Software/AI
- ✅ Financial services
- ✅ Real estate funds

### Data Limitations (Important!)

What Form D **DOES NOT** give us:
- ❌ Job openings (we'll scrape career pages - Day 3)
- ❌ Company websites (we'll infer/search - Day 2)
- ❌ Employee headcount (we'll estimate from funding/age)
- ❌ Company descriptions (we'll scrape websites - Day 2)
- ❌ Email addresses (we'll find on LinkedIn - Day 4)
- ❌ Post-money valuation (we can infer from amount/stage)

**But that's okay!** Form D gives us the **foundation**: who raised money, how much, and when. We'll enrich it with other free sources.

## The Filing Timeline

Understanding when companies file helps us prioritize:

```
Day 0:  Company closes funding round (wires money)
Day 1:  Starts hiring (they have cash now!)
↓
Day 15: MUST file Form D with SEC (legally required)
↓
Day 16-30: SEC processes and publishes data
↓
Day 31-90: Appears in quarterly bulk download
↓
Day 91: WE find them and add to our database!
```

**The sweet spot:** Companies that filed 1-6 months ago are actively hiring but haven't been picked over yet.

## Why Companies File Form D

This isn't optional—it's federal law:

**Securities Act of 1933** says:
- You can't sell securities without registering them with the SEC
- **UNLESS** you claim an exemption (Regulation D)
- To claim the exemption, you **must** file Form D within 15 days
- Penalty for not filing: Up to $10,000 + potential loss of exemption

**Translation:** If a company raised VC money, they filed Form D. It's not a suggestion—it's the law.

## Real Example: What We Can Learn

Let's decode a real Form D filing:

**Company:** BioTech Therapeutics Inc  
**CIK:** 0001234567  
**Location:** Boston, MA  
**Amount sold:** $15,000,000  
**Investors:** 3  
**Date:** October 15, 2024  
**Exemption:** Rule 506(b)  

**What this tells us:**

✅ **Recently funded** (3 months ago) = actively hiring  
✅ **Significant capital** ($15M) = can afford sponsorship  
✅ **Few investors** (3) = institutional VC backing, not a party round  
✅ **Series A stage** (based on amount) = establishing core team  
✅ **Boston biotech** = matches our target  
✅ **Traditional raise** (506b) = professional, experienced founders  

**Our action:** HIGH PRIORITY for database, find their website, scrape jobs, get founder contacts.

## Day 1 Mission: Data Team

Your job today:

1. ✅ **Download** 3-4 recent quarters (Q2 2024 - Q1 2025)
2. ✅ **Parse** the TSV files (or use our Python script)
3. ✅ **Filter** for:
   - States: MA, CA, NY (Boston, SF, NYC)
   - Amount sold: $5M+
   - Industry: Biotech, pharmaceutical, medical devices
   - Filed: Last 18 months
4. ✅ **Export** to CSV for database loading
5. ✅ **Target:** 200-300 companies by end of day

**No coding experience?** That's fine—our Python script automates all of this. Just run it and watch it work.

## The Bottom Line

Form D filings are **treasure maps** to funded startups. Every filing represents:
- A company that just got money
- Founders who are hiring
- An opportunity that visa holders are missing

**Our mission:** Turn these public filings into private job offers. Turn bureaucratic data into second chances. Turn 80 days into a lifetime of opportunity.

---

## Resources

📄 **SEC Form D Overview:** https://www.sec.gov/smallbusiness/exemptofferings  
📊 **Data Sets Page:** https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets  
📖 **Form D Instructions:** https://www.sec.gov/about/forms/formd.pdf  
🔍 **Search Individual Filings:** https://www.sec.gov/edgar/searchedgar/companysearch.html  

## Questions?

**"How accurate is this data?"**  
Very. It's filed under penalty of law, with company executives signing under oath.

**"Do ALL startups file?"**  
About 95% compliance for Series A+. Smaller seed rounds (~$500K) have spottier filing.

**"How fast is it updated?"**  
Companies must file within 15 days. SEC publishes quarterly (3-month lag for bulk data).

**"Can we trust the amounts?"**  
Yes. The "Amount Sold" field is what actually closed, not aspirational.

**"What if a company raised more later?"**  
They file an amendment (Form D/A). We'll catch it in the next quarter.

---

**Next:** [Day 2 - Building the Pipeline](DAY2_PIPELINE.md)

*"Data without action is just noise. Let's turn this into signal."* - Nik Bear Brown
