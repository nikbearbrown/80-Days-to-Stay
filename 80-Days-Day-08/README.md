# Day 08: Mapping the Treasure Map

This README outlines the technical requirements and mission for **Day 08**. Our goal is to intersect financial capacity (SEC data) with historical willingness (Department of Labor data) and deploy LLM agents to act as "Recruiting Experts" for international talent.

---

## 1. Mapping the Visa Data Goldmine

To move from "likely to hire" to "historically proven to hire," we will map our SEC startup list against official US Government datasets.

### Data Sources to Download

* **DOL LCA Disclosure Data:** [LCA Performance Data](https://www.dol.gov/agencies/eta/foreign-labor/performance). This contains every H-1B, H-1B1, and E-3 application.
* **USCIS H-1B Employer Data Hub:** [USCIS Data Hub](https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub). This provides approval/denial rates and counts for "Initial" (new hires) vs "Continuing" employment.

### The Mapping Logic

**The Challenge:** Company names in SEC filings (*Acme Bio, Inc.*) often differ from DOL filings (*Acme Bio LLC*).

1. **Normalization:** Strip suffixes (Inc, LLC, Corp), remove punctuation, and lowercase all names.
2. **Fuzzy Matching:** Use the `RapidFuzz` library to join the 25,000 SEC companies with the 100,000+ unique employers in the LCA database.
3. **Resulting Schema:**
* `company_id` (SEC Accession Number)
* `total_h1b_filings` (Last 3 years)
* `approval_rate` (%)
* `top_job_titles_sponsored` (e.g., Software Engineer, Data Scientist)
* `median_salary_offered`



---

## 2. LLM Recruiting Expert: The Inquiry Agent

We will use an LLM (Gemini 1.5 Pro or GPT-4o) to analyze the stripped website text. It will act as a **Tenacious Recruiting Advocate** for an international student.

### Expert Prompt Strategy

> "You are a Senior Technical Recruiter specializing in international talent mobility. Analyze the provided company text and generate a 'Sponsorship Intelligence Report.' If you were advising an international student, what 3 critical questions would you ask this company’s Head of Talent? Always provide the strategic 'Why' for each question."

### Sample Questions & Reasons the LLM Should Generate:

1. **"What is your policy on hiring candidates currently on STEM OPT?"**
* *Reason:* It tests if the company knows that STEM OPT requires **zero** immediate cost or paperwork for the first 3 years.


2. **"Does your legal budget currently support H-1B cap-subject petitions?"**
* *Reason:* High-growth startups often have the money but haven't allocated a "line item" for legal fees ($5k-$10k).


3. **"Have you previously used an 'Employer of Record' (EOR) for global hires?"**
* *Reason:* If they use Deel or Remote.com, they already have a "Global First" mindset, making them more open to US-based visa holders.



---

## 3. Finding "Hidden" Opportunity Startups

We want to identify startups that have **never** sponsored before but are **Prime Targets** based on Day 06 intelligence.

### Target Profile:

* **The "Talent Starved" Founder:** Series A tech startups with <20 employees and $10M+ in funding. They are likely struggling to outbid Google for US talent.
* **Modern Infrastructure:** Companies using **Greenhouse** or **Lever**. These systems make it easy to manage complex paperwork if they choose to start sponsoring.
* **International DNA:** Founders who were international students themselves (easily detectable by LLM analysis of "About" page bios mentioning non-US universities).

---

## 🚀 Google Cloud Next Steps for the Team

Since we have **Google Cloud Credits**, the team will move the pipeline from local scripts to a production-ready cloud environment:

1. **Cloud Storage (GCS):** Upload the 425k scraped HTML pages and the multi-GB DOL datasets.
2. **BigQuery:** Load the SEC and DOL datasets into BigQuery. Use **BigQuery ML** or standard SQL to handle the massive fuzzy-join operation. This is significantly faster than local Python for millions of rows.
3. **Vertex AI (Batch API):** Use the Batch Prediction API to run our "Recruiting Expert" LLM prompt against all 25,748 verified companies in one parallelized swoop.
4. **Cloud Functions:** Build a trigger that automatically scrapes and analyzes a company the moment a new Form D is filed with the SEC.

---

**Mission for tonight:** Finalize the SQL join between `startups_master.json` and the `LCA_Disclosure_Data.csv`. If a company has $5M+ and 1+ historical H-1B, they are **Tier 1 Priority**.
